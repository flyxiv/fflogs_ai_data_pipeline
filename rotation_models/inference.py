"""Inference training rotation up to target time and store the rotation log into csv file.
"""

import argparse
import logging
import pandas as pd

from dataclasses import dataclass
from .train_agents.dqn_agent import DQNAgent
from .train_agents.ppo_agent import PPOAgent
from .create_ffxiv_environment import create_ffxiv_environment
from .experience import Experience

@dataclass
class InferenceLog:
    action_name: str
    cast_time_millisecond: int

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-type", type=str, required=True, choices=["dqn", "ppo"], help="type of model to train(dqn or ppo)")
    parser.add_argument("--target_time_millisecond", type=int, required=False, default=360000, help="target combatime in milliseconds")
    parser.add_argument("--model-path", type=str, required=True, help="path to the trained model")
    parser.add_argument("--class-name", type=str, required=False, default="Ninja", help="class the model will train on")
    parser.add_argument("--output-path", type=str, required=False, default="rotation_log.csv", help="path to the output csv file")
    return parser.parse_args()


def inference(model_type: str, target_time_millisecond: int, class_name: str, model_path: str, output_path: str):
    ninja_environment = create_ffxiv_environment(class_name, target_time_millisecond)

    if model_type == "dqn":
        agent = DQNAgent(state_size=ninja_environment.state_size, action_size=ninja_environment.action_size, model_path=model_path)
    elif model_type == "ppo":
        agent = PPOAgent(state_size=ninja_environment.state_size, action_size=ninja_environment.action_size, model_path=model_path)
    else:
        raise ValueError(f"Invalid model type: {model_type}")

    action_log = []

    valid_actions = ninja_environment.get_valid_actions()
    done = False
    state = ninja_environment._get_state()
    current_time_millisecond = 0
    next_valid_actions= None 
    total_reward = 0

    while not done:
        logging.info(f"progress: {current_time_millisecond / target_time_millisecond * 100}%")
        action_id = agent.get_action(state, valid_actions)

        if action_id > 0:
            action_log.append(InferenceLog(action_name=NinjaSkills(action_id).name, cast_time_millisecond=current_time_millisecond))

        next_state, next_valid_actions, current_time_millisecond, reward, done = ninja_environment.step(action_id)
        total_reward += int(reward * MAX_POTENCY)

        if done:
            break

        valid_actions = next_valid_actions
        state = next_state

    action_logs = {
        "action_name": [log.action_name for log in action_log],
        "cast_time_millisecond": [log.cast_time_millisecond for log in action_log]
    }

    pd.DataFrame(action_logs).to_csv(output_path, index=False)

    logging.info(f"saved rotation log to {output_path}")


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.INFO,
        datefmt='%m/%d/%Y %I:%M:%S %p',
    )

    args = parse_args()

    inference(args.model_type, args.target_time_millisecond, args.class_name, args.model_path, args.output_path)