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
        self.state_size = state.shape[1]
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
            valids[20] = 1
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

        return (
            self.get_state(),
            self.get_valid_skills(),
            self.combat_time_millisecond,
            potency / MAX_POTENCY,
            self.combat_time_millisecond >= self.target_time_millisecond,
        )

    def get_state(self):
        states = []

        for buff in self.buffs:
            if buff:
                states.extend(buff.get_state())
            else:
                states.extend([0, 0])

        for debuff in self.debuffs:
            if debuff:
                states.extend(debuff.get_state())
            else:
                states.extend([0, 0])

        for resource in self.resources:
            if resource:
                states.extend(resource.get_state())
            else:
                states.extend([0, 0])

        for skill in self.skills:
            assert skill is not None
            states.extend(skill.get_state())

        states.extend(
            [
                self.combo / 3,
                (
                    self.combo_duration_millisecond / COMBO_TIMER_MAX_MILLISECOND
                    if self.combo_duration_millisecond
                    else 10
                ),
            ]
        )

        states.extend([self.gcd_cooldown_millisecond / self.max_gcd_delay])
        states.extend([self.combat_time_millisecond / self.target_time_millisecond])

        return tf.reshape(tf.constant(states), [1, -1])
