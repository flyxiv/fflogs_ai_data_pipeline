"""Parses log collected by fflogs_report_parser.py and converts it into a list of only ninja casts.
"""

import argparse
import os
import json
import yaml

from rotation_models.ninja.ninja_combat_data import NinjaSkills 

with open('./rotation_models/ninja/ninja_skill_fflogs_id.yaml', 'r') as f:
    NINJA_FFLOG_SKILLS = yaml.safe_load(f)['skills']
    NINJA_FFLOG_SKILL_IDS_TO_MODEL_SKILL_IDS = {v[0]: v[1] for v in NINJA_FFLOG_SKILLS.values()}

class NinjaFflogsRotation:
    def __init__(self, log_dir: str):
        self.ninja_dataset = list()

        for log_file in os.listdir(log_dir):
            try:
                if log_file.endswith('.json'):
                    with open(os.path.join(log_dir, log_file), 'r') as f:
                        log_data = json.load(f)
                else:
                    continue
            except Exception as e:
                raise Exception(f"Error loading log file: {e}")

            for fight in log_data:
                ninja_player_id = get_ninja_player_id(fight)

                if ninja_player_id is None:
                    continue

                events = fight['events']

                ninja_casts = list() 

                for i, event in enumerate(events):
                    if not (event['type'] == 'cast' and event['sourceID'] == ninja_player_id and event['abilityGameID'] in NINJA_FFLOG_SKILL_IDS_TO_MODEL_SKILL_IDS):
                        continue

                    if i == 0:
                        prev_combat_time = event['timestamp']

                    current_combat_time = event['timestamp']

                    if i > 0 and current_combat_time - prev_combat_time > 8000:
                        break

                    ninja_casts.append((NINJA_FFLOG_SKILL_IDS_TO_MODEL_SKILL_IDS[event['abilityGameID']], event['timestamp'])) 
                    prev_combat_time = current_combat_time

                if not ninja_casts:
                    continue

                start_time = ninja_casts[0][1] + 1000
                end_time = ninja_casts[-1][1]

                if end_time - start_time <= 10000:
                    continue

                ninja_casts = [l[0] for l in ninja_casts]

                self.ninja_dataset.append((ninja_casts, end_time - start_time))


    def __repr__(self):
        debug_str = "NinjaFflogsRotation\n\n"

        for fight_number, ninja_casts in enumerate(self.ninja_dataset):
            debug_str += f"Fight {fight_number}:\n\n"

            for ninja_cast in ninja_casts:
                debug_str += f"{ninja_cast}\n"

        return debug_str


def get_ninja_player_id(fight: dict):
    mapping = fight['player_id_job_mapping']
    job_player_id_mapping = {v: k for k, v in mapping.items()}
    ninja_player_id = int(job_player_id_mapping["Ninja"]) if "Ninja" in job_player_id_mapping else None

    return ninja_player_id

