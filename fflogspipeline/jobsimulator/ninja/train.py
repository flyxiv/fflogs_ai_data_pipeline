"""Script for training the ninja agent"""

from .ninja_dqn_agent import NinjaDQNAgent
from .ninja_environment import NinjaEnvironment
from tqdm import tqdm


def train(target_time_millisecond: int):
    ninja_environment = NinjaEnvironment(target_time_millisecond)
    agent = NinjaDQNAgent()

    current_time_millisecond = 0
    current_gcd_cooldown_millisecond = 0

    for episode in tqdm(range(1000)):
        ninja_environment.reset()
        possible_gcd_actions = ninja_environment.get_possible_gcd_actions()
        possible_ogcd_actions = ninja_environment.get_possible_ogcd_actions()
        is_gcd = ninja_environment.is_gcd()

        while not done:
            action = agent.act(
                state, is_gcd, current_gcd_cooldown_millisecond, current_time_millisecond, possible_gcd_actions, possible_ogcd_actions)

            next_state, possible_gcd_actions, possible_ogcd_actions, is_gcd, current_time_millisecond, gcd_cooldown_millisecond, reward, done = ninja_environment.step(
                action)

            agent.remember(state, action, reward, next_state, done)

            state = next_state

            if done:
                print(
                    f"Episode {episode} finished after {current_time_millisecond}ms")
                break

    agent.replay(32)

    if len(agent.memory) > 32:
        agent.save("ninja_model.h5")
