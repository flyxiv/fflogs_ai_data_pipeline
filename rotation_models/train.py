"""Script for training dqn/ppo agents

run ex)

```sh
# run dqn model
$ python -m rotation_models.train --model-type dqn --save-path ./trained_models/ninja_model_dqn.keras --target-time-millisecond 360000 --num-episodes 100 --replay-period 32

# run ppo model
$ python -m rotation_models.train --model-type ppo --save-path ./trained_models/ninja_model_ppo.keras --target-time-millisecond 360000 --num-episodes 100
```
"""

import argparse
import logging
import pandas as pd
from tqdm import tqdm
import os
from rotation_models.ninja.ninja_combat_data import NinjaSkills

from .train_agents.ffxiv_dqn_agent import FFXIVDQNAgent
from .train_agents.ffxiv_ppo_agent import FFXIVPPOAgent
from .create_ffxiv_environment import create_ffxiv_environment
from .experience import Experience
from .inference import inference 


CHECKPOINT_EPOCHS = 10

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
        "--save-path", type=str, required=True, help="path to save the model"
    )
    parser.add_argument(
        "--class-name",
        type=str,
        required=False,
        default="ninja",
        choices=["ninja"],
        help="class the model will train on",
    )
    parser.add_argument(
        "--target-time-millisecond",
        type=int,
        required=False,
        default=360000,
        help="target combatime in milliseconds",
    )
    parser.add_argument(
        "--num-episodes",
        type=int,
        required=False,
        default=100,
        help="number of episodes to train",
    )
    parser.add_argument(
        "--replay-period",
        type=int,
        required=False,
        default=32,
        help="step interval to replay experience(for dqn only)",
    )
    return parser.parse_args()


COMBAT_START_TIME_MILLISECOND = -2000

def train_dqn(
    target_time_millisecond: int,
    class_name: str,
    num_episodes=100,
    replay_period=32,
    save_path="ninja_model_dqn.keras",
):
    environment = create_ffxiv_environment(class_name, target_time_millisecond, start_time_millisecond=COMBAT_START_TIME_MILLISECOND)
    agent = FFXIVDQNAgent(
        state_size=environment.state_size,
        action_size=environment.action_size,
        replay_period=replay_period,
    )

    agent.duel_q_network.load_weights('./trained_models/ninja_model_dqn_pretrained.keras')
    agent._update_target_network()

    num_actions = 0
    progression = {
        'episode': [],
        'total_reward': [],
    }

    for episode in tqdm(range(num_episodes)):
        environment.reset()
        valid_actions = environment.get_valid_skills()

        done = False
        state = environment.get_state()
        current_time_millisecond = COMBAT_START_TIME_MILLISECOND
        next_valid_actions = None

        if episode % CHECKPOINT_EPOCHS == 0:
            save_epsilon = agent.epsilon 
            agent.epsilon = 0.0
            agent.duel_q_network.save(save_path)
            total_reward = inference(
                model_type="dqn",
                target_time_millisecond=target_time_millisecond,
                class_name=class_name,
                model_path=save_path,
                output_path=f"rotation_log_ppo_{episode}.csv",
            )
            agent.epsilon = save_epsilon

            progression['episode'].append(episode)
            progression['total_reward'].append(total_reward)


        while not done:
            action_id = agent.get_action(state, valid_actions)

            if action_id > 0:
                logging.debug(f"action: {NinjaSkills(action_id).name}")
            assert (
                action_id < len(NinjaSkills) + 1
            ), f"action_id: {action_id} is greater than: {len(NinjaSkills) + 1}"

            next_state, next_valid_actions, current_time_millisecond, reward, done = (
                environment.use_skill(action_id)
            )

            logging.debug(
                f"valid_actions: {[NinjaSkills(idx).name for idx, action in enumerate(valid_actions) if action > 0 and idx > 0]}"
            )
            logging.debug(current_time_millisecond)

            experience = Experience(
                state=state,
                action_id=action_id,
                reward=reward,
                next_state=next_state,
                done=done,
                valid_actions=valid_actions,
                next_valid_actions=next_valid_actions,
            )
            agent.insert_to_memory(experience)

            if done:
                print(f"Episode {episode} finished after {current_time_millisecond}ms")
                break

            num_actions += 1
            valid_actions = next_valid_actions
            state = next_state

            if num_actions % agent.replay_period == 0:
                agent.replay_batch()


    pd.DataFrame(progression).to_csv(f"progression_dqn.csv", index=False)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    agent.duel_q_network.save(save_path)


def train_ppo(
    target_time_millisecond: int,
    class_name: str,
    num_episodes=100,
    save_path="ninja_model_ppo.keras",
):
    environment = create_ffxiv_environment(class_name, target_time_millisecond, start_time_millisecond=COMBAT_START_TIME_MILLISECOND)
    agent = FFXIVPPOAgent(
        state_size=environment.state_size, action_size=environment.action_size
    )

    agent.new_model.load_weights('./trained_models/ninja_model_ppo_pretrained.keras')
    agent._update_target_network()

    progression = {
        'episode': [],
        'total_reward': [],
    }

    for episode in tqdm(range(num_episodes)):
        environment.reset()
        valid_actions = environment.get_valid_skills()
        done = False
        state = environment.get_state()
        current_time_millisecond = COMBAT_START_TIME_MILLISECOND
        next_valid_actions = None

        
        if episode % CHECKPOINT_EPOCHS == 0:
            agent.new_model.save(save_path)
            total_reward = inference(
                model_type="ppo",
                target_time_millisecond=target_time_millisecond,
                class_name=class_name,
                model_path=save_path,
                output_path=f"rotation_log_ppo_{episode}.csv",
            )

            progression['episode'].append(episode)
            progression['total_reward'].append(total_reward)


        while not done:
            action_id = agent.get_action(state, valid_actions)

            if action_id > 0:
                logging.debug(f"action: {NinjaSkills(action_id).name}")
            assert (
                action_id < len(NinjaSkills) + 1
            ), f"action_id: {action_id} is greater than: {len(NinjaSkills) + 1}"

            next_state, next_valid_actions, current_time_millisecond, reward, done = (
                environment.use_skill(action_id)
            )

            logging.debug(
                f"valid_actions: {[NinjaSkills(idx).name for idx, action in enumerate(valid_actions) if action > 0 and idx > 0]}"
            )
            logging.debug(current_time_millisecond)

            experience = Experience(
                state=state,
                action_id=action_id,
                reward=reward,
                next_state=next_state,
                done=done,
                valid_actions=valid_actions,
                next_valid_actions=next_valid_actions,
            )
            agent.insert_to_memory(experience)

            if len(agent.rollout_buffer) == agent.L:
                agent.train_from_rollout_buffer()

            if done:
                print(f"Episode {episode} finished after {current_time_millisecond}ms")
                break

            valid_actions = next_valid_actions
            state = next_state

        if episode % CHECKPOINT_EPOCHS == 0:
            total_reward = inference(
                model_type="ppo",
                target_time_millisecond=target_time_millisecond,
                class_name=class_name,
                model_path=save_path,
                output_path=f"rotation_log_ppo_{episode}.csv",
            )
            progression['episode'].append(episode)
            progression['total_reward'].append(total_reward)

    pd.DataFrame(progression).to_csv(f"progression_ppo.csv", index=False)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    agent.new_model.save(save_path)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    args = parse_args()

    if args.model_type == "dqn":
        train_dqn(
            args.target_time_millisecond,
            args.class_name,
            args.num_episodes,
            args.replay_period,
            args.save_path,
        )
    elif args.model_type == "ppo":
        train_ppo(
            args.target_time_millisecond,
            args.class_name,
            args.num_episodes,
            args.save_path,
        )
    else:
        raise ValueError(f"Invalid model type: {args.model_type}")
