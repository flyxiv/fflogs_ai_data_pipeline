"""Script for training the ninja agent"""

from .ninja_dqn_agent import NinjaDQNAgent
from .ninja_environment import NinjaEnvironment, NinjaGCDSkills, NinjaOGCDSkills, ninja_gcd_to_all_skill, ninja_ogcd_to_all_skill, DEFAULT_DELAY_MILLISECOND
from tqdm import tqdm
import logging


def train(target_time_millisecond: int):
    ninja_environment = NinjaEnvironment(target_time_millisecond)
    agent = NinjaDQNAgent(state_size=54)

    for episode in tqdm(range(32)):
        ninja_environment.reset()
        possible_gcd_actions = ninja_environment.get_possible_gcd_actions()
        possible_ogcd_actions = ninja_environment.get_possible_ogcd_actions()
        is_gcd = ninja_environment.is_gcd()
        done = False
        state = ninja_environment._get_state()
        gcd_cooldown_millisecond = 0
        current_time_millisecond = 0
        cast_time_offset = 0
        delay = 0
        possible_gcd_actions = ninja_environment.get_possible_gcd_actions()
        possible_ogcd_actions = ninja_environment.get_possible_ogcd_actions()

        while not done:
            delay = agent.act1(
                state, is_gcd)

            logging.info(f"delay: {delay}")

            if gcd_cooldown_millisecond == 0:
                cast_time_offset = 0
            else:
                earliest_possible_time = 0
                latest_possible_time = gcd_cooldown_millisecond - DEFAULT_DELAY_MILLISECOND
                cast_time_offset = delay * latest_possible_time

            ninja_environment._advance_time(cast_time_offset)
            possible_gcd_actions = ninja_environment.get_possible_gcd_actions()
            possible_ogcd_actions = ninja_environment.get_possible_ogcd_actions()
            state = ninja_environment._get_state()

            logging.debug(
                f"possible_gcd_actions: {[NinjaGCDSkills(action).name for action in possible_gcd_actions]}")
            logging.debug(
                f"possible_ogcd_actions: {[NinjaOGCDSkills(action).name for action in possible_ogcd_actions]}")

            if is_gcd:
                action = agent.act_skill(
                    state, possible_gcd_actions)

                action_total_id = ninja_gcd_to_all_skill(
                    NinjaGCDSkills(action)).value
            else:
                action = agent.act_skill(
                    state, possible_ogcd_actions)

                action_total_id = ninja_ogcd_to_all_skill(
                    NinjaOGCDSkills(action)).value

            assert (is_gcd and action < 13) or ((not is_gcd) and action <
                                                11), f"action_id: {action}, is_gcd: {is_gcd}"

            next_state, possible_gcd_actions, possible_ogcd_actions, next_is_gcd, current_time_millisecond, gcd_cooldown_millisecond, reward, next_done = ninja_environment.step(
                action_total_id, cast_time_offset)

            logging.info(current_time_millisecond)

            agent.remember(state, action, reward, next_state, done, is_gcd)

            state = next_state
            is_gcd = next_is_gcd
            done = next_done

            if done:
                print(
                    f"Episode {episode} finished after {current_time_millisecond}ms")
                break

            agent.replay(32)

    if len(agent.memory) > 32:
        agent.save("ninja_model.h5")


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.INFO,
        datefmt='%m/%d/%Y %I:%M:%S %p',
    )

    train(10000)
