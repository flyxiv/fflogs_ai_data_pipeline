"""Script for training dqn/ppo agents

run ex)

```sh
# run dqn model
$ python -m rotation_models.pretrain_from_fflogs --save-path ./trained_models/ninja_model_dqn.keras --log-dir ./data --num-epochs 10
```
"""

import argparse
import logging
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import os
import tensorflow as tf
from rotation_models.ninja.ninja_combat_data import NinjaSkills, NinjaBuffs, NinjaResources
from rotation_models.ninja.parse_fflogs_to_ninja_rotation import NinjaFflogsRotation

from .train_agents.ffxiv_dqn_agent import FFXIVDQNAgent
from .train_agents.ffxiv_ppo_agent import FFXIVPPOAgent
from .create_ffxiv_environment import create_ffxiv_environment
from .experience import Experience
from .inference import inference 

tf.get_logger().setLevel('ERROR')
CHECKPOINT_EPOCHS = 10

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--save-path", type=str, required=True, help="path to save the model"
    )
    parser.add_argument(
        "--log-dir", type=str, required=True, help="path to the log directory"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        required=False,
        default="dqn",
        choices=["dqn", "ppo"],
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
        "--num-epochs",
        type=int,
        required=False,
        default=10,
        help="number of epochs to train",
    )
    return parser.parse_args()

COMBAT_START_TIME_MILLISECOND = -2000

def pretrain(
    class_name: str,
    model_type: str,
    num_epochs: int,
    save_path: str,
    log_dir: str,
):
    model_path = None# f"{save_path}/dqn_model_pretrain.keras"

    with tf.device('/GPU:0'):
        environment = create_ffxiv_environment(class_name, 10000, COMBAT_START_TIME_MILLISECOND)
        if model_type == "dqn":
            network = FFXIVDQNAgent(
                state_sizes=environment.state_sizes,
                action_sizes=environment.action_sizes,
                replay_period=10,
                model_path=model_path
            ).duel_q_network
        elif model_type == "ppo":
            network = FFXIVPPOAgent(
                state_sizes=environment.state_sizes,
                action_size=environment.action_size,
                epsilon=0.2,
            ).new_model
        else:
            raise ValueError(f"Invalid model type: {model_type}")

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)

        fflogs_rotation = NinjaFflogsRotation(log_dir)

        num_actions = 0

        loss_function = tf.keras.losses.CategoricalCrossentropy()

        save_path = Path(save_path) / 'pretrain'
        os.makedirs(save_path, exist_ok=True)

        for epoch in range(num_epochs):

            for rotation_idx, (rotations, target_time_millisecond) in tqdm(enumerate(fflogs_rotation.ninja_dataset)):
                environment.reset()
                environment.target_time_millisecond = target_time_millisecond

                logging.info(f"target_time: {environment.target_time_millisecond}")
                valid_actions = environment.get_valid_skills()
                state = environment.get_state()
                current_time_millisecond = environment.combat_time_millisecond 
                next_valid_actions = None

                rotation_cnt = 0
                consecutive_rests = 0
                rotation_total_loss = 0

                while rotation_cnt < len(rotations):
                    if valid_actions[rotations[rotation_cnt]] == 1:
                        consecutive_rests = 0

                        with tf.GradientTape() as tape:
                            action_outputs_percentage, _ = network(state)

                            answer = tf.reshape(tf.one_hot(rotations[rotation_cnt], action_outputs_percentage.shape[1]), action_outputs_percentage.shape)
                            assert answer.shape == action_outputs_percentage.shape, f"answer.shape: {answer.shape} != action_outputs_percentage.shape: {action_outputs_percentage.shape}"

                            loss = loss_function(answer, action_outputs_percentage)
                            rotation_total_loss += loss
                            gradients = tape.gradient(loss, network.trainable_variables)
                            optimizer.apply_gradients(zip(gradients, network.trainable_variables))

                        next_state, next_valid_actions, current_time_millisecond, _, _ = (
                            environment.use_skill(rotations[rotation_cnt])
                        )

                        logging.debug(
                            f"valid_actions: {[NinjaSkills(idx).name for idx, action in enumerate(valid_actions) if action > 0 and idx > 0]}"
                        )
                        logging.debug(current_time_millisecond)

                        valid_actions = next_valid_actions
                        state = next_state

                        rotation_cnt += 1

                        if rotation_cnt <= len(rotations) - 1:
                            logging.debug(f"NINKI: {environment.resources[NinjaResources.NINKI.value].current_stacks}")
                            logging.debug(NinjaSkills(rotations[rotation_cnt]).name)
                    else:
                        if sum(valid_actions) > 1:
                            with tf.GradientTape() as tape:
                                action_outputs_percentage, _ = network(state)

                                answer = tf.reshape(tf.one_hot(0, action_outputs_percentage.shape[1]), action_outputs_percentage.shape)
                                loss = loss_function(answer, action_outputs_percentage) / 5 
                                gradients = tape.gradient(loss, network.trainable_variables)

                                if consecutive_rests < 15:
                                    optimizer.apply_gradients(zip(gradients, network.trainable_variables))

                        next_state, next_valid_actions, current_time_millisecond, _, _ = environment.use_skill(0)
                        valid_actions = next_valid_actions
                        state = next_state

                        consecutive_rests += 1

                        if consecutive_rests > 500:
                            break
            
                if rotation_cnt > 0:
                    logging.info(f"rotation_average_loss: {rotation_total_loss / rotation_cnt}")
                
                if rotation_idx % 10 == 0:
                    network.save(f"{save_path}/dqn_model_pretrain.keras")
                    total_reward = inference(
                        model_type=model_type,
                        target_time_millisecond=390000,
                        class_name=class_name,
                        model_path=f"{save_path}/dqn_model_pretrain.keras",
                        output_path=f"{save_path}/rotation_{rotation_idx}.csv"
                    )

        network.save(f"{save_path}/dqn_model_pretrain.keras")
        total_reward = inference(
            model_type=model_type,
            target_time_millisecond=390000,
            class_name=class_name,
            model_path=f"{save_path}/dqn_model_pretrain.keras",
            output_path=None
        )




if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    args = parse_args()

    pretrain(
        args.class_name,
        args.model_type,
        args.num_epochs,
        args.save_path,
        args.log_dir,
    )
