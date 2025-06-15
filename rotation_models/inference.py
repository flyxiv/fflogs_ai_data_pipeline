"""Inference training rotation up to target time and store the rotation log into csv file.

run ex)
```sh
$ python -m rotation_models.inference --model-type dqn --model-path .\ninja_model_dqn.keras --output-path .\ninja_rotation_log_dqn.csv

$ python -m rotation_models.inference --model-type ppo --model-path .\ninja_model_ppo.keras --output-path .\ninja_rotation_log_ppo.csv
```
"""

import argparse
import logging
import pandas as pd

from dataclasses import dataclass
from .train_agents.ffxiv_dqn_agent import FFXIVDQNAgent 
from .train_agents.ffxiv_ppo_agent import FFXIVPPOAgent
from .create_ffxiv_environment import create_ffxiv_environment
from .experience import Experience
from .ninja.ninja_combat_data import NinjaSkills
from .const import MAX_POTENCY
from .inference_logger import InferenceLogger

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-type",
        type=str,
        required=True,
        choices=["dqn", "ppo"],
        help="type of model to train(dqn or ppo)",
    )
    parser.add_argument(
        "--target_time_millisecond",
        type=int,
        required=False,
        default=360000,
        help="target combatime in milliseconds",
    )
    parser.add_argument(
        "--model-path", type=str, required=True, help="path to the trained model"
    )
    parser.add_argument(
        "--class-name",
        type=str,
        required=False,
        default="ninja",
        help="class the model will train on",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=False,
        default="rotation_log.csv",
        help="path to the output csv file",
    )
    return parser.parse_args()


def inference(
    model_type: str,
    target_time_millisecond: int,
    class_name: str,
    model_path: str,
    output_path: str,
):
    ninja_environment = create_ffxiv_environment(class_name, target_time_millisecond, -2000)
    inference_logger = InferenceLogger(output_path)

    if model_type == "dqn":
        agent = FFXIVDQNAgent(
            state_sizes=ninja_environment.state_sizes,
            action_sizes=ninja_environment.action_sizes,
            model_path=model_path,
        )
        logging.info(agent.epsilon)
        agent.epsilon = 0
    elif model_type == "ppo":
        agent = FFXIVPPOAgent(
            state_size=ninja_environment.state_size,
            action_size=ninja_environment.action_size,
            model_path=model_path,
        )
    else:
        raise ValueError(f"Invalid model type: {model_type}")

    action_log = []

    valid_actions = ninja_environment.get_valid_skills()
    done = False
    state = ninja_environment.get_state()
    current_time_millisecond = -2000
    next_valid_actions = None
    total_reward = 0

    while not done:
        action_id, action_outputs, state_output = agent.get_action(state, valid_actions, debug=True)

        next_state, next_valid_actions, current_time_millisecond, reward, done = (
            ninja_environment.use_skill(action_id)
        )
        total_reward += int(reward * MAX_POTENCY)

        inference_logger.log(action_id, action_outputs, state_output, ninja_environment, valid_actions, total_reward)

        if done:
            break

        valid_actions = next_valid_actions
        state = next_state

    if output_path:
        inference_logger.save()

    logging.info(f"total reward: {total_reward}")
    logging.info(f"saved rotation log to {output_path}")

    return total_reward


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    args = parse_args()

    inference(
        args.model_type,
        args.target_time_millisecond,
        args.class_name,
        args.model_path,
        args.output_path,
    )
