import numpy as np
from .resource import Resource
from rotation_models.const import (
    COMBO_TIMER_MAX_MILLISECOND,
    UNIT_TIME_PER_ACTION_MILLISECOND,
    MAX_POTENCY,
)
from .job_database import JobDatabase
from typing import List
import tensorflow as tf
import logging
from copy import deepcopy


class CombatStatus:
    """Implements basic combat status for the FFXIV combat job

    ex) combo, buffs, debuffs, etc.
    """

    def __init__(
        self,
        job_database: JobDatabase,
        skills,
        resources,
        target_time_millisecond: int = 0,
        start_time_millisecond: int = 0,
    ):
        self.job_database = job_database
        self.start_skills = skills
        self.skills = deepcopy(skills)
        self.buffs = [None] * len(job_database.buffs)
        self.debuffs = [None] * len(job_database.debuffs)
        self.resources = resources
        self.start_resources = deepcopy(resources)

        self.combo = 0
        self.combo_duration_millisecond = None

        self.gcd_cooldown_millisecond = 0
        self.start_time_millisecond = start_time_millisecond
        self.combat_time_millisecond = start_time_millisecond
        self.target_time_millisecond = target_time_millisecond
        self.max_gcd_delay = max(
            [
                skill.delay_data.gcd_cooldown_millisecond
                for skill in self.skills
                if skill.delay_data
            ]
        )

        state = self.get_state()
        self.state_sizes = {k: tf.shape(v)[1].numpy() for (k, v) in state.items()} 
        self.action_size = len(self.skills) + 1

    def reset(self):
        self.combo = 0
        self.combo_duration_millisecond = None

        self.gcd_cooldown_millisecond = 0
        self.combat_time_millisecond = self.start_time_millisecond
        self.buffs = [None] * len(self.job_database.buffs)
        self.debuffs = [None] * len(self.job_database.debuffs)
        self.resources = deepcopy(self.start_resources)
        self.skills = deepcopy(self.start_skills)

    def update_combo(self, combo: int):
        self.combo = combo

        if combo == 0:
            self.combo_duration_millisecond = None
        else:
            self.combo_duration_millisecond = COMBO_TIMER_MAX_MILLISECOND

    def get_valid_skills(self):
        valid_skills = np.zeros(len(self.skills) + 1)
        valid_skills[0] = 1

        for skill in self.skills:
            if skill.is_valid_action(self):
                valid_skills[skill.skill_id] = 1

        if self.combat_time_millisecond < 0:
            valids = np.zeros(len(self.skills) + 1)
            valids[18] = 1
            return valids

        return valid_skills

    def advance_time(self, delta_time_millisecond: int):
        if self.combo_duration_millisecond:
            self.combo_duration_millisecond = max(
                0, self.combo_duration_millisecond - delta_time_millisecond
            )

            if self.combo_duration_millisecond == 0:
                self.update_combo(0)

        for skill in self.skills:
            skill.advance_time(delta_time_millisecond)

        for buff in self.buffs:
            if buff:
                buff.advance_time(self.buffs, delta_time_millisecond)

        for debuff in self.debuffs:
            if debuff:
                debuff.advance_time(self.debuffs, delta_time_millisecond)

        self.combat_time_millisecond += delta_time_millisecond
        self.gcd_cooldown_millisecond = max(
            0, self.gcd_cooldown_millisecond - delta_time_millisecond
        )


    def use_skill(self, skill_id: int):
        if skill_id == 0:
            self.advance_time(UNIT_TIME_PER_ACTION_MILLISECOND)

            if self.gcd_cooldown_millisecond <= UNIT_TIME_PER_ACTION_MILLISECOND // 2:
                self.advance_time(self.gcd_cooldown_millisecond) 
                assert self.gcd_cooldown_millisecond == 0

            return (
                self.get_state(),
                self.get_valid_skills(),
                self.combat_time_millisecond,
                0,
                self.combat_time_millisecond >= self.target_time_millisecond,
            )

        skill = self.skills[skill_id - 1]

        potency, delay_data = skill.use_skill(self)

        self.gcd_cooldown_millisecond = max(
            delay_data.gcd_cooldown_millisecond, self.gcd_cooldown_millisecond
        )

        self.advance_time(delay_data.delay_millisecond)

        valid_actions = self.get_valid_skills()
        while self.is_not_selectable_state(valid_actions):
            logging.debug('waiting because there is no usable skill')
            self.advance_time(UNIT_TIME_PER_ACTION_MILLISECOND)
            valid_actions = self.get_valid_skills()

        return (
            self.get_state(),
            self.get_valid_skills(),
            self.combat_time_millisecond,
            potency / MAX_POTENCY,
            self.combat_time_millisecond >= self.target_time_millisecond,
        )

    @staticmethod
    def is_not_selectable_state(valid_actions):
        # if the only valid action is to hold, there is no choice we can make thus not a valid state
        return sum(valid_actions) == 1.0 and valid_actions[0] == 1.0

    def get_state(self):
        skill_states = []
        for skill in self.skills:
            assert skill is not None
            skill_states.extend(skill.get_state())
        
        status_states = []
        for buff in self.buffs:
            if buff:
                status_states.extend(buff.get_state())
            else:
                status_states.extend([0, 0])

        for debuff in self.debuffs:
            if debuff:
                status_states.extend(debuff.get_state())
            else:
                status_states.extend([0, 0])

        resource_states = []
        for resource in self.resources:
            if resource:
                resource_states.extend(resource.get_state())
            else:
                resource_states.extend([0, 0])

        combo_states = [
                self.combo / 3,
                (
                    self.combo_duration_millisecond / COMBO_TIMER_MAX_MILLISECOND
                    if self.combo_duration_millisecond
                    else 1
                ),
            ]

        gcd_state = [self.gcd_cooldown_millisecond / self.max_gcd_delay]
        time_state = [self.combat_time_millisecond / self.target_time_millisecond]

        state_dict = {
            "skill_states": skill_states,
            "status_states": status_states,
            "resource_states": resource_states,
            "combo_states": combo_states,
            "gcd_state": gcd_state,
            "time_state": time_state,
        } 

        return {
            k: tf.reshape(tf.constant(v), [1, -1]) for k, v in state_dict.items()
        }
