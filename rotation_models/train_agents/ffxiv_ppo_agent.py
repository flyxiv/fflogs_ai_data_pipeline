"""Defines PPO agent for FFXIV jobs.

Uses rollback method to perform online PPO training.
"""

import numpy as np
from ..const import IMPOSSIBLE_PENALTY, LOG_EPSILON
from ..experience import Experience
import itertools
import random
import logging
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import keras

FLOATING_POINT_ERROR_TOLERANCE = 1e-6

seed_value = 42
tf.random.set_seed(seed_value)
np.random.seed(seed_value)
random.seed(seed_value)

class TrainingData:
    def __init__(self, experience, gae_advantage, v_target):
        self.experience = experience
        self.gae_advantage = gae_advantage
        self.v_target = v_target

    def __len__(self):
        return len(self.rollout_buffer)


class FFXIVPPOAgent:
    """Use PPO to train the FFXIV rotation model.

    action_id 0 is the "do nothing" action.
    """

    def __init__(self, state_size, action_size, epsilon=0.2, model_path=None):
        # Neural Network 
        self.state_size = state_size
        self.action_size = action_size

        # Hyperparameters
        self.epsilon = epsilon
        
        ## GAE related
        self.gamma = 0.97
        self.lmbda = 0.95

        ## Rollout buffer related
        self.rollout_buffer = [] 
        self.L = 1024 
        self.batch_size = 64 
        self.n_epochs = 10

        # Loss/Training related
        self.learning_rate = 3e-4 
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.c1 = 0.5
        self.c2 = 0.01

        assert self.L % self.batch_size == 0, f"L: {self.L} is not divisible by batch_size: {self.batch_size}"

        # Model Initialization
        if model_path:
            self.new_model = tf.keras.models.load_model(model_path)
        else:
            self.new_model = self._build_model()

        self.old_model = self._build_model()
        self._update_target_network() 

    def _build_model(self):
        # Override this network to use a different architecture.

        state_inp = keras.Input(shape=(self.state_size,))
        valid_action_mask_inp = keras.Input(shape=(self.action_size,))
        
        dense = keras.layers.Dense(32, name='dense1', activation='relu')(state_inp)
        batch_norm = keras.layers.BatchNormalization()(dense)
        dense2 = keras.layers.Dense(64, name='dense2', activation='relu')(batch_norm)
        batch_norm2 = keras.layers.BatchNormalization()(dense2)
        dense3 = keras.layers.Dense(128, name='dense3', activation='relu')(batch_norm2)
        batch_norm3 = keras.layers.BatchNormalization()(dense3)
        dense4 = keras.layers.Dense(64, name='dense4', activation='relu')(batch_norm3)
        batch_norm4 = keras.layers.BatchNormalization()(dense4)
        action_distribution_logit = keras.layers.Dense(
            self.action_size)(batch_norm4)

        penalty_adder = (1.0 - valid_action_mask_inp) * IMPOSSIBLE_PENALTY
        action_distribution_masked = keras.layers.Softmax()(action_distribution_logit + penalty_adder)

        value_output = keras.layers.Dense(1, name='value_output')(batch_norm4)

        model = keras.Model(inputs=[state_inp, valid_action_mask_inp], outputs=[action_distribution_masked, value_output])

        return model

    def _update_target_network(self):
        self.old_model.set_weights(self.new_model.get_weights())


    def get_action(self, state, valid_actions):
        assert state.shape[1] == self.state_size, f"State size: {state.shape[1]} is not equal to state size: {self.state_size}"
        valid_actions = tf.reshape(valid_actions, [1, -1])

        action_distribution, _ = self.new_model([state, valid_actions])
        action_log_probabilities = tf.math.log(action_distribution + LOG_EPSILON)

        selected_action = tf.random.categorical(action_log_probabilities, num_samples=1)

        return int(tf.squeeze(selected_action).numpy())


    def insert_to_memory(self, experience: Experience):
        self.rollout_buffer.append(experience)


    def _calculate_gae_advantages(self, v_t_old, v_t_plus_1_old, rewards):
        """Use equation from: https://miro.medium.com/v2/resize:fit:1400/1*DN_IkNe-zjqnRFD-4Ff6JQ.png 

        Calculate in a n * n matrix to utilize vectorized operations.
        """

        buffer_size = v_t_old.shape[0]
        td_errors = rewards + self.gamma * v_t_plus_1_old - v_t_old

        i_indices = np.arange(buffer_size).reshape(buffer_size, 1)
        j_indices = np.arange(buffer_size).reshape(1, buffer_size)
        powers = j_indices - i_indices

        discount_matrix = np.where(powers >= 0, (self.lmbda * self.gamma) ** powers, 0)
        td_errors = tf.tile(tf.reshape(td_errors, [1, buffer_size]), [buffer_size, 1])
        td_errors_discounted = discount_matrix * td_errors

        return tf.reduce_sum(td_errors_discounted, axis=1)


    def _calculate_partitioned_gae_advantages(self, v_t_old, v_t_plus_1_old, rewards):
        """Partition experiences by episodes by cutting the episodes whenever a "done" experience is found.
        Calculate the GAE advantages for each partitioned episode and return the full list of GAE advantages.
        """
        gae_advantages_per_episode = []
        episode_start_idx = 0

        while episode_start_idx < len(self.rollout_buffer):
            while episode_start_idx < len(self.rollout_buffer) and not self.rollout_buffer[episode_start_idx].done:
                episode_start_idx += 1

            episode_end_idx = min(episode_start_idx + self.L, len(self.rollout_buffer))
            
            rewards = rewards[episode_start_idx:episode_end_idx, :]
            v_t_old = v_t_old[episode_start_idx:episode_end_idx, :]
            v_t_plus_1_old = v_t_plus_1_old[episode_start_idx:episode_end_idx, :]

            gae_advantages_per_episode.append(self._calculate_gae_advantages(v_t_old, v_t_plus_1_old, rewards))
            episode_start_idx = episode_end_idx

        return np.concatenate(gae_advantages_per_episode, axis=0)
 

    def train_from_rollout_buffer(self):
        assert len(self.rollout_buffer) == self.L, f"Rollout buffer size: {len(self.rollout_buffer)} is not equal to L: {self.L}"
       
        states = np.concatenate([experience.state for experience in self.rollout_buffer], axis=0)
        next_states = np.concatenate([experience.next_state for experience in self.rollout_buffer], axis=0)
        valid_actions = np.array([experience.valid_actions for experience in self.rollout_buffer])
        next_valid_actions = np.array([experience.next_valid_actions for experience in self.rollout_buffer])
        rewards = np.reshape([experience.reward for experience in self.rollout_buffer], [len(self.rollout_buffer), 1])

        assert states.shape[0] == valid_actions.shape[0] == next_states.shape[0] == next_valid_actions.shape[0] == rewards.shape[0]

        _, v_t_old = self.new_model([states, valid_actions])
        _, v_t_plus_1_old = self.new_model([next_states, next_valid_actions])

        self.gae_advantages = self._calculate_partitioned_gae_advantages(v_t_old, v_t_plus_1_old, rewards)
        assert self.gae_advantages.shape == [self.L, 1]
       
        v_target = self.gae_advantages + v_t_old
        training_dataset = [TrainingData(experience, gae_advantage, v_target) for experience, gae_advantage, v_target in zip(self.rollout_buffer, self.gae_advantages, v_target)]

        for _ in range(self.n_epochs):
            training_dataset = np.random.permutation(training_dataset)
            num_batches = len(training_dataset) // self.batch_size

            for batch_idx in range(num_batches):
                with tf.GradientTape() as tape:
                    training_batch = training_dataset[batch_idx * self.batch_size:(batch_idx + 1) * self.batch_size]
                    batch_rollout_buffer = [training_batch.experience for training_batch in training_batch]
                    batch_gae_advantage = [training_batch.gae_advantage for training_batch in training_batch]
                    batch_v_target = [training_batch.v_target for training_batch in training_batch]

                    states_batch = np.concatenate([experience.state for experience in batch_rollout_buffer], axis=0)
                    valid_actions_batch = np.array([experience.valid_actions for experience in batch_rollout_buffer])

                    _, v_t = self.new_model([states_batch, valid_actions_batch])
                    l_vf = tf.reduce_mean(tf.square(batch_v_target - v_t))

                    actions = np.array([experience.action_id for experience in batch_rollout_buffer])
                    batch_indices = np.arange(len(batch_rollout_buffer))
                    action_indices = np.stack([batch_indices, actions], axis=1)

                    all_action_prob_current = self.new_model([states_batch, valid_actions_batch])[0]
                    action_prob_current = tf.gather_nd(all_action_prob_current, action_indices)
                    action_prob_old = tf.gather_nd(self.old_model([states_batch, valid_actions_batch])[0], action_indices)

                    ratio = action_prob_current / action_prob_old
                    clipped_ratio = tf.clip_by_value(ratio, 1 - self.epsilon, 1 + self.epsilon)
                    
                    l_surrogate = tf.reduce_mean(tf.minimum(ratio * batch_gae_advantage, clipped_ratio * batch_gae_advantage))
                    l_entropy = -tf.reduce_mean(tf.reduce_sum(all_action_prob_current * tf.math.log(all_action_prob_current + LOG_EPSILON), axis=1))

                    policy_loss = -l_surrogate + self.c1 * l_vf - self.c2 * l_entropy

                gradients = tape.gradient(policy_loss, self.new_model.trainable_variables)
                self.optimizer.apply_gradients(zip(gradients, self.new_model.trainable_variables))

        if num_batches > 0:
            logging.info(f"policy loss: {policy_loss}")

        self._update_target_network()
        self.rollout_buffer = []
                