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

print("=== GPU 상태 확인 ===")
print("TensorFlow 버전:", tf.__version__)
print("GPU 사용 가능:", tf.config.list_physical_devices('GPU'))
print("CUDA 빌드:", tf.test.is_built_with_cuda())

def pretrain(
    class_name: str,
    model_type: str,
    num_epochs: int,
    save_path: str,
    log_dir: str,
):
    with tf.device('/GPU:0'):
        environment = create_ffxiv_environment(class_name, 10000, COMBAT_START_TIME_MILLISECOND)
        if model_type == "dqn":
            network = FFXIVDQNAgent(
                state_size=environment.state_size,
                action_size=environment.action_size,
                replay_period=10,
            ).duel_q_network
        elif model_type == "ppo":
            network = FFXIVPPOAgent(
                state_size=environment.state_size,
                action_size=environment.action_size,
                epsilon=0.2,
            ).new_model
        else:
            raise ValueError(f"Invalid model type: {model_type}")

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        fflogs_rotation = NinjaFflogsRotation(log_dir)

        num_actions = 0

        loss_function = tf.keras.losses.CategoricalCrossentropy()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        for epoch in range(num_epochs):

            for rotation_idx, rotations in tqdm(enumerate(fflogs_rotation.ninja_dataset)):
                environment.reset()
                valid_actions = environment.get_valid_skills()
                state = environment.get_state()
                current_time_millisecond = environment.combat_time_millisecond 
                next_valid_actions = None

                rotation_cnt = 0
                consecutive_rests = 0

                while rotation_cnt < len(rotations):
                    if valid_actions[rotations[rotation_cnt]] == 1:
                        consecutive_rests = 0

                        with tf.GradientTape() as tape:
                            if model_type == "dqn":
                                action_outputs, _ = network(state)
                                action_outputs_percentage = tf.nn.softmax(action_outputs)
                            elif model_type == "ppo":
                                action_outputs, _ = network([state, tf.reshape(valid_actions, [1, -1])])
                                action_outputs_percentage = tf.nn.softmax(action_outputs)

                            answer = tf.reshape(tf.one_hot(rotations[rotation_cnt], action_outputs_percentage.shape[1]), action_outputs_percentage.shape)
                            assert answer.shape == action_outputs_percentage.shape, f"answer.shape: {answer.shape} != action_outputs_percentage.shape: {action_outputs_percentage.shape}"

                            loss = loss_function(answer, action_outputs_percentage)
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
                        next_state, next_valid_actions, current_time_millisecond, _, _ = environment.use_skill(0)
                        valid_actions = next_valid_actions
                        state = next_state

                        consecutive_rests += 1

                        if consecutive_rests > 500:
                            break

            network.save(save_path)


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
