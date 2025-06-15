import tensorflow as tf
import json

from rotation_models.ffxiv_system.combat_status import CombatStatus
from rotation_models.ninja.ninja_combat_data import NinjaSkills, NinjaBuffs, NinjaDebuffs, NinjaResources

class InferenceLogger:
    """Keeps track of model's state at each inference and saves the final result as a csv file
    """

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.logs = []

    def log(self, action_id, action_output, state_output, ninja_state, valid_actions, total_reward):
        self.logs.append({
            "selected_action": str(NinjaSkills(action_id).name) if action_id > 0 else "Hold",
            "action_output": self._to_readable_action_output(action_output),
            "ninja_state": self._to_readable_ninja_state(ninja_state),
            "valid_actions": valid_actions.tolist(),
            "total_reward": total_reward,
        })

    def _to_readable_action_output(self, action_output: tf.Tensor):
        action_list = tf.reshape(action_output, (-1)).numpy().tolist()

        action_outputs = dict() 

        for i, action in enumerate(action_list):
            skill_name = str(NinjaSkills(i).name) if i > 0 else "Hold"
            action_outputs[skill_name] = float(action)

        return action_outputs

    def _to_readable_ninja_state(self, ninja_state: CombatStatus):
        return {
            "combo": ninja_state.combo,
            "combo_duration_millisecond": ninja_state.combo_duration_millisecond,
            "gcd_cooldown_millisecond": ninja_state.gcd_cooldown_millisecond,
            "start_time_millisecond": ninja_state.start_time_millisecond,
            "combat_time_millisecond": ninja_state.combat_time_millisecond,
            "target_time_millisecond": ninja_state.target_time_millisecond,
            "resources": self._to_readable_resources(ninja_state.resources),
            "cooldowns": self._to_readable_cooldowns(ninja_state.cooldowns),
        }

    def _to_readable_resources(self, resources: List[int]):
        return {
            "ninki": resources[NinjaResources.NINKI.value],
            "shuriken": resources[NinjaResources.SHURIKEN.value],
            "tcj_fuma": resources[NinjaResources.TCJ_FUMA.value],
            "tcj_raiton": resources[NinjaResources.TCJ_RAITON.value],
            "tcj_suiton": resources[NinjaResources.TCJ_SUITON.value],
        }

    def _to_readable_cooldowns(self, cooldowns: List[int]):
        return {
            NinjaSkills(i).name: cooldowns[i] for i in range(len(NinjaSkills))
        }

    def save(self):
        with open(self.output_path, "w") as f:
            json.dump(self.logs, f)
