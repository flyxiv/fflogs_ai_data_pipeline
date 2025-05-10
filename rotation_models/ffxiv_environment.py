"""Defines components needed for training environment for specific FFXIV jobs for reinforcement learning models to train on.
"""

from abc import abstractmethod
import tensorflow as tf
import numpy as np

class FFXIVEnvironment:
    """Virtual class defining common APIs for training environment of FFXIV jobs 
    """

    def __init__(self, target_time_millisecond: int):
        self.target_time_millisecond = target_time_millisecond

    @abstractmethod
    def reset(self):
        """Reset the environment to the initial state after an episode ends"""
        pass

    @abstractmethod
    def get_state(self) -> tf.Tensor:
        """Get the current state of the environment as a tensor"""
        pass

    @abstractmethod
    def get_valid_actions(self) -> np.array:
        """Get masking array for valid actions in the current state

        Output array is a list `A` of 0, 1 where
        * If the action_id i is usable, `A[i] = 1`
        * If the action_id i is not usable, `A[i] = 0`
        """
        pass
    
    @abstractmethod
    def step(self, action_id, debug_mode=False) -> tuple[tf.Tensor, np.array, int, float, bool]:
        """Do the selected action_id and return the result of the action
        
        Args:
            action_id (int): The action to do
            debug_mode (bool): Whether to print debug information

        Returns:
            1) The next state of the environment as a tensor
            2) The valid actions in the next state as a numpy array
            3) The combat time of the next step as an integer
            4) The reward for the action 
            5) Done flag as a boolean
        """
        pass
