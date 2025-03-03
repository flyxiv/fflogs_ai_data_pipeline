"""DQN Agent for Ninja Rotation
"""

import tensorflow as tf
import numpy as np
import random
import keras
from collections import deque
from typing import List
from .ninja_environment import ninja_gcd_to_all_skill, ninja_ogcd_to_all_skill

seed_value = 42
tf.random.set_seed(seed_value)
np.random.seed(seed_value)
random.seed(seed_value)


class NinjaDQNAgent:
    def __init__(self, state_size):
        self.state_size = state_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.70
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.delay_model = self._build_delay_model()
        self.gcd_model = self._build_gcd_model()
        self.ogcd_model = self._build_ogcd_model()
        self.time_unit = 10

    def _build_delay_model(self):
        inp = keras.layers.Input(shape=(self.state_size, ))
        dense = keras.layers.Dense(24, name='dense1')(inp)
        dense2 = keras.layers.Dense(24, name='dense2')(dense)
        delay_output = keras.layers.Dense(self.time_unit, activation='softmax')(dense2)

        model = keras.Model(inputs=inp, outputs=delay_output)

        model.compile(
            optimizer=keras.optimizers.Nadam(
                learning_rate=self.learning_rate),
            loss='categorical_crossentropy',
        )

        return model

    def _build_gcd_model(self):
        inp = keras.layers.Input(shape=(self.state_size,))
        dense = keras.layers.Dense(24, name='dense1')(inp)
        dense2 = keras.layers.Dense(24, name='dense2')(dense)
        gcd_skill_output = keras.layers.Dense(
            13, activation='softmax')(dense2)

        model = keras.Model(inputs=inp, outputs=gcd_skill_output)

        model.compile(
            optimizer=keras.optimizers.Nadam(
                learning_rate=self.learning_rate),
            loss=keras.losses.categorical_crossentropy
        )

        return model

    def _build_ogcd_model(self):
        inp = keras.layers.Input(shape=(self.state_size,))
        dense = keras.layers.Dense(24, name='dense1')(inp)
        dense2 = keras.layers.Dense(24, name='dense2')(dense)
        ogcd_skill_output = keras.layers.Dense(
            11, activation='softmax')(dense2)

        model = keras.Model(inputs=inp, outputs=ogcd_skill_output)

        model.compile(
            optimizer=keras.optimizers.Nadam(
                learning_rate=self.learning_rate),
            loss=keras.losses.categorical_crossentropy
        )

        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done, is_gcd):
        self.memory.append((state, action, reward, next_state, done, is_gcd))

    def act1(self, state, is_gcd):
        if is_gcd:
            return 0
        else:
            if np.random.rand() <= self.epsilon:
                return np.random.randint(0, 10)

            delay_values = self.delay_model.predict(tf.reshape(state, (1, -1)), verbose=0)
            return np.argmax(delay_values)

    def act_skill(self, state, valid_actions=None):
        """ Select next GCD 

        Args:
            state: current state. Last element of the state must be is_gcd(1 if GCD turn, 0 if oGCD turn)
            gcd_valid_actions: valid GCD actions, the index corresponds to the GCD skill id of NinjaGCDSkills enum
        """
        if np.random.rand() <= self.epsilon:
            return self._randomly_select_actions(state, valid_actions)

        act_values = self.gcd_model.predict(
            tf.reshape(state, (1, -1)), verbose=0)

        for i in range(len(valid_actions)):
            if i not in valid_actions:
                act_values[0][i] = -100

        return np.argmax(act_values)

    def _randomly_select_actions(self, state, valid_actions: List[int]):
        return np.random.choice(valid_actions)

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)
        for state, action_delay, action_skill, reward, next_state, done, is_gcd in minibatch:
            state_input = tf.reshape(state, (1, -1))
            target = reward

            if is_gcd:
                target_f1 = self.gcd_model.predict(state_input, verbose=0)
                target_f1[0][action_skill] = target
                self.gcd_model.fit(state_input, target_f1,
                                   epochs=1, verbose=0)
            else:
                target_delay = self.delay_model.predict(state_input, verbose=0)
                target_delay[0][action_delay] = target
                
                target_f1 = self.ogcd_model.predict(state_input, verbose=0)
                target_f1[0][action_skill] = target

                self.delay_model.fit(state_input, target_delay, epochs=1, verbose=0)
                self.ogcd_model.fit(state_input, target_f1,
                                    epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
