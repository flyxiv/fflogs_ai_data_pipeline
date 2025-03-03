"""DQN Agent for Ninja Rotation
"""

import tensorflow as tf
import numpy as np
import random
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from collections import deque


def custom_loss(is_gcd):
    def loss_fn(y_true, y_pred):
        gcd_true, ogcd_true, delay_true = y_true
        gcd_pred, ogcd_pred, delay_pred = y_pred

        gcd_loss = tf.keras.losses.categorical_crossentropy(gcd_true, gcd_pred)
        ogcd_loss = tf.keras.losses.categorical_crossentropy(
            ogcd_true, ogcd_pred)
        delay_loss = tf.keras.losses.mse(delay_true, delay_pred)

        masked_gcd_loss = tf.where(is_gcd, gcd_loss, 0.0)
        masked_ogcd_loss = tf.where(is_gcd, 0.0, ogcd_loss)
        masked_delay_loss = tf.where(is_gcd, 0.0, delay_loss)

        return masked_gcd_loss + masked_ogcd_loss + masked_delay_loss

    return loss_fn


class NinjaDQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        inp = tf.keras.layers.Input(input_size=(self.state_size))
        dense = tf.keras.layers.Dense(24, name='dense1')(inp)
        dense2 = tf.keras.layers.Dense(24, name='dense2')(dense)
        gcd_skill_output = tf.keras.layers.Dense(
            13, activation='softmax')(dense2)
        ogcd_skill_output = tf.keras.layers.Dense(
            11, activation='softmax')(dense2)
        delay_output = tf.keras.layers.Dense(1, activation='sigmoid')(dense2)

        loss_weights = {
            'gcd_output': 1.0,
            'ogcd_output': 1.0,
            'delay_output': 0.5
        }

        model.compile(
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=self.learning_rate),
            loss=custom_loss,
            loss_weights=loss_weights
        )

        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, is_gcd, valid_ogcd_modes=None, gcd_valid_actions=None, ogcd_valid_actions=None):
        """ Select next GCD + (oGCD and delay) actions by epsilon-greedy strategy

        Args:
            state: current state. Last element of the state must be is_gcd(1 if GCD turn, 0 if oGCD turn)
            gcd_valid_actions: valid GCD actions, the index corresponds to the GCD skill id of NinjaGCDSkills enum
            ogcd_valid_actions: valid oGCD actions, the index corresponds to the oGCD skill id of NinjaOGCDSkills enum
            delay: 0 is instantly using the ogcd skill, 1 is delaying the ogcd skill as much as possible without clipping the GCD skill.
        """
        if np.random.rand() <= self.epsilon:
            return self._randomly_select_actions(self, state, is_gcd, valid_ogcd_modes, gcd_valid_actions, ogcd_valid_actions)

        act_values = self.model.predict(state.reshape(1, -1), verbose=0)
        gcd_skill_pred = act_values[0]
        ogcd_skill_pred = act_values[1]
        delay_pred = act_values[2]

        return self._select_actions_by_model_predictions(self, is_gcd, gcd_skill_pred, ogcd_skill_pred, delay_pred)

    def _randomly_select_actions(self, state, is_gcd, valid_ogcd_modes, gcd_valid_actions, ogcd_valid_actions: List[int]):
        if is_gcd:
            gcd_skill_id = self._select_random_skills(self, gcd_valid_actions)
            return (gcd_skill_id, 0)
        else:
            ogcd_skill_id = self._select_random_skills(
                self, ogcd_valid_actions)
            delay_pred = np.random.rand()

            assert delay_pred >= 0 and delay_pred <= 1

            return (gcd_skill_id, (ogcd_skill_id, delay_pred), None)

    def _select_random_skill(self, valid_skills):
        return np.random.choice(valid_skills)

    def _select_actions_by_model_predictions(self, is_gcd, gcd_skill_pred, ogcd_skill_pred, delay_pred):
        if is_gcd:
            for gcd_skill in range(gcd_skill_pred):
                if gcd_skill not in gcd_valid_actions:
                    gcd_skill_pred[gcd_skill] = 0

            return (np.argmax(gcd_skill_pred), 0)

        else:

            for ogcd_skill in range(ogcd_skill_pred):
                if ogcd_skill not in ogcd_valid_actions:
                    ogcd_skill_pred[ogcd_skill] = 0

            return (np.argmax(ogcd_skill_pred), delay_pred)

    def replay(self, batch_size):
        # 경험 리플레이를 통한 학습
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(
                    self.target_model.predict(
                        next_state.reshape(1, -1), verbose=0)[0]
                )

            target_f = self.model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
