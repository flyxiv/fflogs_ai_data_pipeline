class Experience:
    """Defines data that will be stored in the experience buffer for later training.

    For DQN, it is stored in the memory that will be later trained using DeepMind's Prioritized Experience Replay.
    For PPO, it is stored in the rollout buffer.
    """

    def __init__(
        self,
        state,
        action_id,
        reward,
        next_state,
        done,
        valid_actions,
        next_valid_actions,
    ):
        self.state = state
        self.action_id = action_id
        self.reward = reward
        self.next_state = next_state
        self.done = done
        self.valid_actions = valid_actions
        self.next_valid_actions = next_valid_actions
