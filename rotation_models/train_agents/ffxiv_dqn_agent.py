"""Duel DQN + Prioritized Experience Replay for training FFXIV rotation
"""

import logging
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import numpy as np
import random
import keras
from ..const import IMPOSSIBLE_PENALTY, EPSILON_P
from ..experience import Experience
from .build_dense_network import build_dense_network

from util.sum_tree import SumTree

seed_value = 42
tf.random.set_seed(seed_value)
np.random.seed(seed_value)
random.seed(seed_value)

class FFXIVDQNAgent:
    """Duel DQN + Prioritized Experience Replay

    Uses ranking based experience replay weight. 
    0 is the "do nothing" action
    """
    def __init__(self, state_sizes, action_size, replay_period: int = 32, model_path=None):
        self.state_sizes = state_sizes
        self.action_size = action_size

        # Replay buffer related
        self.memory = SumTree(capacity=1000)
        self.replay_period = replay_period
        self.batch_size = 16

        # Epsilon-greedy hyperparameters
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        # Value function/Prioritized Experience Replay hyperparameters
        self.gamma = 0.95
        self.alpha = 0.6
        self.beta = 0.4
        self.beta_increment = 0.001

        # Training hyperparameters
        self.learning_rate = 0.000025
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.steps = 0
        self.target_network_update_steps = 100

        # Model Initialization
        self.duel_q_network = self._build_network()

        if model_path:
            self.target_duel_q_network = tf.keras.models.load_model(model_path)
        else:
            self.target_duel_q_network = self._build_network()

        self._update_target_network()


    def _update_target_network(self):
        self.target_duel_q_network.set_weights(self.duel_q_network.get_weights())

    def _build_network(self):
        # Override this network to use a different architecture.

        skill_states = keras.layers.Input(shape=(self.state_sizes['skill_states']), name="skill_states")
        gcd_skill_states = keras.layers.Input(shape=(self.state_sizes['gcd_skill_states'],), name="gcd_skill_states")
        status_states = keras.layers.Input(shape=(self.state_sizes['status_states'],), name="status_states")
        resource_states = keras.layers.Input(shape=(self.state_sizes['resource_states'],), name="resource_states")
        combo_states = keras.layers.Input(shape=(self.state_sizes['combo_states'],), name="combo_states")
        gcd_state = keras.layers.Input(shape=(self.state_sizes['gcd_state'],), name="gcd_state")
        time_state = keras.layers.Input(shape=(self.state_sizes['time_state'],), name="time_state")

        gcd_dense_networks = build_dense_network([128, 256, 512, 1024, 512, 512, 256, 128, 64])
        ogcd_dense_networks = build_dense_network([128, 256, 512, 1024, 512, 512, 256, 128, 64])

        gcd_advantage_output_layer = keras.layers.Dense(self.action_size, name='advantage_output_gcd')
        ogcd_advantage_output_layer = keras.layers.Dense(self.action_size - 13, name='advantage_output_ogcd')

        gcd_state_output_layer = keras.layers.Dense(1, name='state_output_gcd')
        ogcd_state_output_layer = keras.layers.Dense(1, name='state_output_ogcd')

        if gcd_state == 0:
            input_tensor = skill_states
            target_network = gcd_dense_networks
            advantage_output_layer = gcd_advantage_output_layer
            state_output_layer = gcd_state_output_layer
        else:
            input_tensor = gcd_skill_states
            target_network = ogcd_dense_networks
            advantage_output_layer = ogcd_advantage_output_layer
            state_output_layer = ogcd_state_output_layer

        inp2 = target_network[0](input_tensor)
        for dense_network in target_network[1:]:
            inp2 = dense_network(inp2)

        advantage_output = advantage_output_layer(inp2)

        if gcd_state != 0:
            gcd_outputs = tf.reshape(tf.constant([0] * 13, dtype=tf.float32), (1, -1))
            advantage_output = tf.concat([gcd_outputs, advantage_output], axis=1)

        state_output = state_output_layer(inp2)

        if gcd_state != 0:
            state_output = tf.concat([gcd_outputs, state_output], axis=1)

        model = keras.Model(inputs=[skill_states, gcd_skill_states, status_states, resource_states, combo_states, gcd_state, time_state], outputs=[advantage_output, state_output])

        return model

    def get_action(self, state, valid_actions=None):
        """ Select next action 

        Args:
            state: current state. Last element of the state must be is_gcd(1 if GCD turn, 0 if oGCD turn)
            valid_actions: tensor with 1 for index of valid actions, 0 for invalid actions
        """
        assert state.shape[1] == self.state_size, f"State size: {state.shape[1]} is not equal to state size: {self.state_size}"

        if np.random.rand() <= self.epsilon:
            state = tf.squeeze(state, axis=0)
            return self._randomly_select_actions(state, valid_actions)
        
        advantages, _ = self.duel_q_network(state)

        invalid_mask = 1.0 - np.array(valid_actions, dtype=np.float32)
        advantages_masked = np.where(valid_actions == 1, advantages, IMPOSSIBLE_PENALTY)
        assert np.min(advantages_masked) >= IMPOSSIBLE_PENALTY, f"Invalid action value: {np.min(advantages_masked)}"

        return np.argmax(advantages_masked)

    def _randomly_select_actions(self, state, valid_actions):
        valid_actions_indices = np.where(valid_actions == 1)[0]
        logging.debug(f"valid_actions: {valid_actions}")
        logging.debug(f"valid_actions_indices: {valid_actions_indices}")

        if len(valid_actions_indices) == 0:
            return 0 
        else:
            return np.random.choice(valid_actions_indices)

    def _calculate_td_error(self, memory_experience: Experience):
        """Use variable names from DeepMind's Prioritized Experience Replay paper
        """
        r_t = memory_experience.reward

        if memory_experience.done:
            return r_t

        q_t = self._calculate_q_value(memory_experience.next_state, memory_experience.next_valid_actions)
        max_q_action_idx = np.argmax(q_t)

        q_target_t = self._calculate_q_value(memory_experience.next_state, memory_experience.next_valid_actions, is_target=True)
        max_action_q = q_target_t[max_q_action_idx] 

        # t_1 = t - 1
        q_t_1 = self._calculate_q_value(memory_experience.state, memory_experience.valid_actions)

        return r_t + self.gamma * max_action_q - q_t_1[memory_experience.action_id]

    def _calculate_q_value(self, state, valid_actions, is_target=False):
        advantages, states_value = self.duel_q_network(state) if not is_target else self.target_duel_q_network(state)

        advantages = tf.squeeze(advantages, axis=0)
        states_value = tf.squeeze(states_value, axis=0)

        advantages_masked = tf.where(valid_actions == 1, advantages, IMPOSSIBLE_PENALTY)
        mean_advantages = tf.reduce_mean(tf.boolean_mask(advantages_masked, valid_actions == 1))
        return states_value + (advantages_masked - mean_advantages)

    def insert_to_memory(self, experience: Experience):
        # Give current max priority to new experience
        self.memory.add(priority=self.memory.get_max_priority(), data=experience)

    def replay_batch(self):
        """Use DeepMind's Update TD-error only on sampled batch
        Variable names are from the paper Prioritized Experience Replay
        equations are organized in image: https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT26zqRUx0QEZ0YNdxYD4nMTLWkuArDUvHrLg&s
        """

        assert len(self.memory) >= self.batch_size, f"Memory size: {len(self.memory)} is less than batch size: {self.batch_size}"

        N = len(self.memory)
        
        loss = 0

        sampled_batches = []

        with tf.GradientTape() as tape:
            for j in range(self.batch_size):
                sample_experience = self.memory.sample()

                # Because of floating point precision, sometimes sampling goes through routes
                # that should have been 0 priority(=empty leaf node). Since these cases are rare, we keep
                # sampling until we get a non-zero priority(which is probably once)
                while sample_experience[1] == 0.0:
                    sample_experience = self.memory.sample()

                sampled_batches.append(sample_experience)

            min_p = min(sampled_batches, key=lambda entry: entry[1])[1]
            assert min_p > 0, f"min_p: {min_p} is not greater than 0, samples : {[p for _, p, _ in sampled_batches]}"

            for idx, p, sample_experience in sampled_batches:
                P_j = max(p / self.memory.tree[0], EPSILON_P)
                P_min = max(min_p / self.memory.tree[0], EPSILON_P)

                max_w = (N * P_min) ** (-self.beta)
                w_j = (N * P_j) ** (-self.beta) / max_w

                td_error_j = self._calculate_td_error(sample_experience)

                new_p = (abs(td_error_j) + EPSILON_P) ** self.alpha
                assert new_p > 0, f"new_p: {new_p} is not greater than 0"

                self.memory.update(idx, new_p)

                loss += w_j * (td_error_j ** 2) / self.batch_size

        logging.info(f"loss: {loss}")
        grads = tape.gradient(loss, self.duel_q_network.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.duel_q_network.trainable_variables))

        self.steps += 1

        if self.steps % self.target_network_update_steps == 0:
            self._update_target_network()
            self.steps = 0

        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        if self.beta < 1:
            self.beta = min(1, self.beta + self.beta_increment)
