"""Simulates ninja's skill usages and the corresponding status effects.
"""

import logging
import numpy as np
import tensorflow as tf
import math

from rotation_models.ffxiv_environment import FFXIVEnvironment
from rotation_models.const import DO_NOTHING_ACTION_ID, UNIT_TIME_PER_ACTION_MILLISECOND, COMBO_TIMER_MAX_MILLISECOND, DEFAULT_DELAY_MILLISECOND, MAX_POTENCY
from enum import Enum

from .ninja_combat_data import NinjaSkills, NinjaStatus, NinjaDebuffs, NinjaStacks, NinjaResources, NINJA_SKILL_COOLDOWN_MILLISECONDS, MAX_STATUS_DURATION_MILLISECOND, DEFAULT_GCD_MILLISECOND, MAX_STACKS, MAX_COOLDOWN_MILLISECOND,  MUDRA_GCD_MILLISECOND, TCJ_GCD_MILLISECOND

class NinjaEnvironment(FFXIVEnvironment):
    """Environment for Ninja rotation to give feedback to the Reinforcement Learning models.
    Simulates Ninja's actual mechanisms(cooldowns, debuff, combos) 
    
    Rewards are the potency of the actions
    """

    def __init__(self, target_time_millisecond):
        super().__init__(target_time_millisecond)
        self.resources = NinjaResources()
        self.current_time_millisecond = 0
        self.action_size = 1 + len(NinjaSkills)

        # do a blind get state to dynamically set the state size
        state = self.get_state()
        self.state_size = state.shape[1]

    def reset(self):
        self.resources = NinjaResources()
        self.current_time_millisecond = 0

    def get_state(self):
        status_encoded = []
        debuffs_encoded = []

        for i in range(len(self.resources.status)):
            status_duration = 0
            status_stacks = 0

            if self.resources.status[i]:
                status_duration = self.resources.status[i][0] / MAX_STATUS_DURATION_MILLISECOND
                status_stacks = self.resources.status[i][1] / MAX_STACKS
            
            status_encoded.append(status_duration)
            status_encoded.append(status_stacks)

        for i in range(len(self.resources.debuffs)):
            debuff_duration = 0 
            debuff_stacks = 0

            if self.resources.debuffs[i]:
                debuff_duration = self.resources.debuffs[i][0] / MAX_STATUS_DURATION_MILLISECOND
                debuff_stacks = self.resources.debuffs[i][1] / MAX_STACKS

            debuffs_encoded.append(debuff_duration)
            debuffs_encoded.append(debuff_stacks)

        resources_normalized = [self.resources.cooldowns[i] /
                                MAX_COOLDOWN_MILLISECOND for i in range(1, len(self.resources.cooldowns) + 1)]

        stacks_normalized = [self.resources.stacks[NinjaStacks.NINKI.value] / 100, self.resources.stacks[NinjaStacks.SHURIKEN.value] / 5,
                             self.resources.stacks[NinjaStacks.MUDRA.value] / 2, self.resources.stacks[NinjaStacks.TCJ_FUMA.value], self.resources.stacks[NinjaStacks.TCJ_RAITON.value]]

        combo_normalized = [self.resources.combo / 3, self.resources.combo_timer / COMBO_TIMER_MAX_MILLISECOND]

        gcd_cooldown_normalized = [self.resources.gcd_cooldown_millisecond / DEFAULT_GCD_MILLISECOND]
        current_time_millisecond_normalized = [self.current_time_millisecond / self.target_time_millisecond]

        r = tf.expand_dims(tf.constant(np.array(resources_normalized + stacks_normalized +
                           status_encoded + debuffs_encoded + combo_normalized + gcd_cooldown_normalized + current_time_millisecond_normalized)), axis=0)

        return r


    def get_valid_actions(self):
        possible_actions = [0] * self.action_size

        for skill_id in range(1, len(NinjaSkills) + 1):
            if self._has_requirements_for_skill(skill_id) and self.resources.cooldowns[skill_id] == 0:
                possible_actions[skill_id] = 1

        possible_actions[DO_NOTHING_ACTION_ID] = 1
        return tf.convert_to_tensor(possible_actions)


    def step(self, action_id, debug_mode=False):
        logging.debug(f'{self.current_time_millisecond}, action: {action_id}')

        if debug_mode:
            self.resources.debug_print()

        reward = 0

        if action_id > 0:
            assert action_id <= len(NinjaSkills) + 1, f'action_id: {action_id} is greater than: {len(NinjaSkills) + 1}'

            reward = self._calculate_potency(action_id) / MAX_POTENCY
            self._update_state(action_id)

            delay = self._calculate_delay(action_id)
            self._advance_time(delay)

        else:
            self._advance_time(UNIT_TIME_PER_ACTION_MILLISECOND)

        return self.get_state(), self.get_valid_actions(), self.current_time_millisecond,  reward, self.current_time_millisecond >= self.target_time_millisecond

    def _advance_time(self, time_elapsed_millisecond):
        # TODO: Refactor to common combat system. 
        for skill in self.resources.cooldowns.keys():
            if self.resources.cooldowns[skill]:
                self.resources.cooldowns[skill] = max(
                    self.resources.cooldowns[skill] - time_elapsed_millisecond, 0)

        for status_key, value in self.resources.status.items():
            if not self.resources.status[status_key]:
                continue

            self.resources.status[status_key][0] = value[0] - \
                time_elapsed_millisecond
            if self.resources.status[status_key][0] <= 0:
                self.resources.status[status_key] = None

        for debuff_key, value in self.resources.debuffs.items():
            if not self.resources.debuffs[debuff_key]:
                continue

            self.resources.debuffs[debuff_key][0] = value[0] - \
                time_elapsed_millisecond

            if self.resources.debuffs[debuff_key][0] <= 0:
                self.resources.debuffs[debuff_key] = None

        self.current_time_millisecond += time_elapsed_millisecond
        self.resources.gcd_cooldown_millisecond = max(
            0, self.resources.gcd_cooldown_millisecond - time_elapsed_millisecond)
        mudra_timer_before = self.resources.mudra_timer

        self.resources.mudra_timer = max(
            0, self.resources.mudra_timer - time_elapsed_millisecond)

        if int(math.ceil(mudra_timer_before / 20000)) != int(math.ceil(self.resources.mudra_timer / 20000)):
            self.resources.stacks[NinjaStacks.MUDRA.value] += 1

    def _calculate_delay(self, action):
        delay = DEFAULT_DELAY_MILLISECOND

        if action == NinjaSkills.RAITON.value or action == NinjaSkills.HYOSHO_RANRYU.value:
            delay += 1000

        elif action == NinjaSkills.SUITON.value:
            delay += 1500

        elif action == NinjaSkills.FUMA_SHURIKEN.value:
            delay += 500

        return delay

    def _has_requirements_for_skill(self, skill_id):
        assert skill_id > 0

        if skill_id in NinjaSkills.get_gcd_skills():
            if self.resources.gcd_cooldown_millisecond > 0:
                return False

        if skill_id == NinjaSkills.BHAVACAKRA.value:
            return self.resources.stacks[NinjaStacks.NINKI.value] >= 50
        elif skill_id == NinjaSkills.KUNAIS_BANE.value:
            return self.resources.status[NinjaStatus.SUITON_STATUS.value] is not None
        elif skill_id == NinjaSkills.ZESHO_MEPPO.value:
            return (self.resources.stacks[NinjaStacks.NINKI.value] >= 50) and (self.resources.status[NinjaStatus.HIGI_STATUS.value])
        elif skill_id == NinjaSkills.RAITON.value or skill_id == NinjaSkills.SUITON.value or skill_id == NinjaSkills.FUMA_SHURIKEN.value:
            return (self.resources.stacks[NinjaStacks.MUDRA.value] >= 1) or (self.resources.status[NinjaStatus.KASSATSU_STATUS.value] is not None)
        elif skill_id == NinjaSkills.TCJ_FUMA_SHURIKEN.value:
            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is not None
        elif skill_id == NinjaSkills.TCJ_RAITON.value:
            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is not None and self.resources.stacks[NinjaStacks.TCJ_FUMA.value] == 1
        elif skill_id == NinjaSkills.TCJ_SUITON.value:
            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is not None and self.resources.stacks[NinjaStacks.TCJ_FUMA.value] == 1 and self.resources.stacks[NinjaStacks.TCJ_RAITON.value] == 1
        elif skill_id == NinjaSkills.FLEETING_RAIJU.value:
            return self.resources.status[NinjaStatus.RAIJU_READY.value] is not None
        elif skill_id == NinjaSkills.HYOSHO_RANRYU.value:
            return self.resources.status[NinjaStatus.KASSATSU_STATUS.value] is not None
        elif skill_id == NinjaSkills.PHANTOM_KAMAITACHI.value:
            return self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value] is not None
        elif skill_id == NinjaSkills.TENRI_JINDO.value:
            return self.resources.status[NinjaStatus.TENRI_JINDO_READY.value] is not None
        elif skill_id == NinjaSkills.TENCHIJIN.value:
            return self.resources.status[NinjaStatus.KASSATSU_STATUS.value] is None
        elif skill_id == NinjaSkills.KASSATSU.value:
            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is None
        elif skill_id == NinjaSkills.MEISUI.value:
            return self.resources.status[NinjaStatus.SUITON_STATUS.value] is not None

        return True

    def _add_bunshin_potency(self, potency):
        if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:
            return 160
        return 0

    def _calculate_potency(self, action):
        """Calculate potency = reward of the action chosen by the DQN.
        """
        potency = 0

        if action == NinjaSkills.AEOLIAN_EDGE.value:
            if self.resources.combo != 2:
                potency = 280
            else:
                potency = 460

            if self.resources.stacks[NinjaStacks.SHURIKEN.value] >= 1:
                potency += 100
            potency += self._add_bunshin_potency(potency)

        elif action == NinjaSkills.ARMOR_CRUSH.value:
            if self.resources.combo != 2:
                potency = 300 
            else:
                potency = 500 

            potency += self._add_bunshin_potency(potency)

        elif action == NinjaSkills.BHAVACAKRA.value:
            potency = 380

            if self.resources.status[NinjaStatus.MEISUI_STATUS.value] is not None:
                potency += 150

        elif action == NinjaSkills.ZESHO_MEPPO.value:
            potency = 700

            if self.resources.status[NinjaStatus.MEISUI_STATUS.value] is not None:
                potency += 150

        elif action == NinjaSkills.DOKUMORI.value:
            potency = 300

        elif action == NinjaSkills.DREAM_WITHIN_A_DREAM.value:
            potency = 540

        elif action == NinjaSkills.FLEETING_RAIJU.value:
            potency = 700
            potency += self._add_bunshin_potency(potency)

        elif action == NinjaSkills.FUMA_SHURIKEN.value or action == NinjaSkills.TCJ_FUMA_SHURIKEN.value:
            potency = 500

            if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:
                potency = potency * 1.3

        elif action == NinjaSkills.GUST_SLASH.value:
            if self.resources.combo != 1:
                potency = 240
            else:
                potency = 400

            potency += self._add_bunshin_potency(potency)

        elif action == NinjaSkills.HYOSHO_RANRYU.value:
            potency = 1690

        elif action == NinjaSkills.KUNAIS_BANE.value:
            potency = 600

        elif action == NinjaSkills.PHANTOM_KAMAITACHI.value:
            potency = 600

        elif action == NinjaSkills.RAITON.value or action == NinjaSkills.TCJ_RAITON.value:
            potency = 740

            if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:
                potency = potency * 1.3

        elif action == NinjaSkills.SUITON.value or action == NinjaSkills.TCJ_SUITON.value:
            potency = 580

            if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:
                potency = potency * 1.3

        elif action == NinjaSkills.SPINNING_EDGE.value:
            potency = 300

            if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:
                potency += 160

        elif action == NinjaSkills.TENRI_JINDO.value:
            potency = 1100

        if self.resources.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value]:
            potency *= 1.05

        if self.resources.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value]:
            potency *= 1.1

        if self.resources.status[NinjaStatus.MEDICATED_STATUS.value]:
            potency *= 1.08

        return potency

    def _update_bunshin_status(self):
        if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:
            assert self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][
                1] >= 1, "bunshin status didn't disappear when stack is 0"

            self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] -= 1
            self.resources.stacks[NinjaStacks.NINKI.value] = min(
                100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

    def _update_state(self, action):
        """Update Markov State of the Ninja character.

        """
        if action == NinjaSkills.AEOLIAN_EDGE.value:
            if self.resources.combo == 2:
                self.resources.stacks[NinjaStacks.NINKI.value] = min(
                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 15)
                
            if self.resources.stacks[NinjaStacks.SHURIKEN.value] > 0:
                self.resources.stacks[NinjaStacks.SHURIKEN.value] = max(
                    self.resources.stacks[NinjaStacks.SHURIKEN.value] - 1, 0)

            self._update_bunshin_status()

            self.resources.status[NinjaStatus.RAIJU_READY.value] = None
            self.resources.combo = 0
            self.resources.gcd_cooldown_millisecond = DEFAULT_GCD_MILLISECOND

        elif action == NinjaSkills.ARMOR_CRUSH.value:
            if self.resources.combo == 2:
                self.resources.stacks[NinjaStacks.SHURIKEN.value] = min(
                    self.resources.stacks[NinjaStacks.SHURIKEN.value] + 2, 5)

                self.resources.stacks[NinjaStacks.NINKI.value] = min(
                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 15)

            self._update_bunshin_status()

            self.resources.status[NinjaStatus.RAIJU_READY.value] = None
            self.resources.combo = 0
            self.resources.gcd_cooldown_millisecond = DEFAULT_GCD_MILLISECOND

        elif action == NinjaSkills.BHAVACAKRA.value:
            assert self.resources.stacks[
                NinjaStacks.NINKI.value] >= 50, f'using bhavacakra @ _update_state, but ninki={self.resources.stacks[NinjaStacks.NINKI.value]} < 50'

            self.resources.stacks[NinjaStacks.NINKI.value] = self.resources.stacks[NinjaStacks.NINKI.value] - 50

            if self.resources.status[NinjaStatus.MEISUI_STATUS.value]:
                self.resources.status[NinjaStatus.MEISUI_STATUS.value][1] -= 1

        elif action == NinjaSkills.BUNSHIN.value:
            assert self.resources.cooldowns[NinjaSkills.BUNSHIN.value] == 0, 'bunshin used when Cooldown > 0'
            assert self.resources.stacks[NinjaStacks.NINKI.value] >= 50, f'using bunshin @ _update_state, but ninki={self.resources.stacks[NinjaStacks.NINKI.value]} < 50'

            self.resources.cooldowns[NinjaSkills.BUNSHIN.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.BUNSHIN.value]
            self.resources.stacks[NinjaStacks.NINKI.value] = max(0, self.resources.stacks[NinjaStacks.NINKI.value] - 50)
            self.resources.status[NinjaStatus.BUNSHIN_STATUS.value] = [
                30000, 5]

            self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value] = [
                45000, 1]

        elif action == NinjaSkills.DREAM_WITHIN_A_DREAM.value:
            assert self.resources.cooldowns[NinjaSkills.DREAM_WITHIN_A_DREAM.value] == 0, 'dream within a dream used when Cooldown > 0'
            self.resources.cooldowns[NinjaSkills.DREAM_WITHIN_A_DREAM.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.DREAM_WITHIN_A_DREAM.value]

        elif action == NinjaSkills.DOKUMORI.value:
            assert self.resources.cooldowns[NinjaSkills.DOKUMORI.value] == 0, 'dokumori used when Cooldown > 0'

            self.resources.stacks[NinjaStacks.NINKI.value] = min(
                100, self.resources.stacks[NinjaStacks.NINKI.value] + 40)

            self.resources.cooldowns[NinjaSkills.DOKUMORI.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.DOKUMORI.value]

            # https://github.com/flyxiv/fflogs_ai_data_pipeline/issues/4#issuecomment-2692502549
            # Dokumori lasts 21 seconds
            self.resources.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value] = [
                21000, 1]

            self.resources.status[NinjaStatus.HIGI_STATUS.value] = [30000, 1]

        elif action == NinjaSkills.KUNAIS_BANE.value:
            # https://github.com/flyxiv/fflogs_ai_data_pipeline/issues/4#issuecomment-2692502549
            # Kunai's bane lasts 16.25 seconds
            assert self.resources.cooldowns[NinjaSkills.KUNAIS_BANE.value] == 0, "kunai's bane used when Cooldown > 0"
            assert self.resources.status[NinjaStatus.SUITON_STATUS.value], 'don\'t have suiton when using kunai\'s bane'

            self.resources.cooldowns[NinjaSkills.KUNAIS_BANE.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.KUNAIS_BANE.value]
            self.resources.status[NinjaStatus.SUITON_STATUS.value] = None
            self.resources.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value] = [
                16250, 1]

        elif action == NinjaSkills.FLEETING_RAIJU.value:
            assert self.resources.status[NinjaStatus.RAIJU_READY.value], "don't have raiju ready when fleeting raiju is used"

            self._update_bunshin_status()

            self.resources.stacks[NinjaStacks.NINKI.value] = min(100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)
            self.resources.status[NinjaStatus.RAIJU_READY.value][1] -= 1
            self.resources.gcd_cooldown_millisecond = DEFAULT_GCD_MILLISECOND

        elif action == NinjaSkills.FUMA_SHURIKEN.value or action == NinjaSkills.RAITON.value or action == NinjaSkills.SUITON.value:
            if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:
                self.resources.status[NinjaStatus.KASSATSU_STATUS.value][1] -= 1
            else:
                assert self.resources.stacks[NinjaStacks.MUDRA.value] > 0, f"don't have mudra ready when using {NinjaSkills(action).name}"

                self.resources.stacks[NinjaStacks.MUDRA.value] -= 1
                self.resources.mudra_timer += 20000

            if action == NinjaSkills.RAITON.value:
                if self.resources.status[NinjaStatus.RAIJU_READY.value]:
                    self.resources.status[NinjaStatus.RAIJU_READY.value] = [30000, self.resources.status[NinjaStatus.RAIJU_READY.value][1] + 1]
                else:
                    self.resources.status[NinjaStatus.RAIJU_READY.value] = [30000, 1]

            if action == NinjaSkills.SUITON.value:
                self.resources.status[NinjaStatus.SUITON_STATUS.value] = [20000, 1]

            self.resources.gcd_cooldown_millisecond = MUDRA_GCD_MILLISECOND

        elif action == NinjaSkills.TCJ_SUITON.value:
            assert self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value], "don't have TCJ when using TCJ_suiton"

            self.resources.status[NinjaStatus.SUITON_STATUS.value] = [20000, 1]
            self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value][1] -= 1
            self.resources.stacks[NinjaStacks.TCJ_FUMA.value] = 0
            self.resources.stacks[NinjaStacks.TCJ_RAITON.value] = 0
            self.resources.gcd_cooldown_millisecond = TCJ_GCD_MILLISECOND

        elif action == NinjaSkills.GUST_SLASH.value:
            if self.resources.combo == 1:
                self.resources.stacks[NinjaStacks.NINKI.value] = min(
                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)
                self.resources.combo = 2
            else:
                self.resources.combo = 0

            self._update_bunshin_status()

            self.resources.status[NinjaStatus.RAIJU_READY.value] = None
            self.resources.gcd_cooldown_millisecond = DEFAULT_GCD_MILLISECOND

        elif action == NinjaSkills.HYOSHO_RANRYU.value:
            assert self.resources.status[NinjaStatus.KASSATSU_STATUS.value], 'No kassatsu when using hyosho ranryu'

            self.resources.status[NinjaStatus.KASSATSU_STATUS.value][1] -= 1
            self.resources.gcd_cooldown_millisecond = MUDRA_GCD_MILLISECOND

        elif action == NinjaSkills.KASSATSU.value:
            assert self.resources.cooldowns[NinjaSkills.KASSATSU.value] == 0, 'kassatsu used when Cooldown > 0'
            self.resources.cooldowns[NinjaSkills.KASSATSU.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.KASSATSU.value]
            self.resources.status[NinjaStatus.KASSATSU_STATUS.value] = [
                15000, 1]

        elif action == NinjaSkills.MEDICATED.value:
            self.resources.cooldowns[NinjaSkills.MEDICATED.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.MEDICATED.value]
            self.resources.status[NinjaStatus.MEDICATED_STATUS.value] = [
                30000, 1]

        elif action == NinjaSkills.MEISUI.value:
            assert self.resources.cooldowns[NinjaSkills.MEISUI.value] == 0, 'meisui used when Cooldown > 0'
            assert self.resources.status[NinjaStatus.SUITON_STATUS.value], 'don\'t have suiton when using meisui'

            self.resources.cooldowns[NinjaSkills.MEISUI.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.MEISUI.value]
            self.resources.stacks[NinjaStacks.NINKI.value] = min(
                100, self.resources.stacks[NinjaStacks.NINKI.value] + 50)
            self.resources.status[NinjaStatus.SUITON_STATUS.value] = None

            self.resources.status[NinjaStatus.MEISUI_STATUS.value] = [30000, 1]

        elif action == NinjaSkills.PHANTOM_KAMAITACHI.value:
            assert self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value], "using Phantom Kamaitachi, but doesn't have Phantom Kamaitachi Ready Status"

            self.resources.stacks[NinjaStacks.NINKI.value] = min(
                100, self.resources.stacks[NinjaStacks.NINKI.value] + 10)

            self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value][1] -= 1
            self.resources.gcd_cooldown_millisecond = DEFAULT_GCD_MILLISECOND

        elif action == NinjaSkills.SPINNING_EDGE.value:
            self.resources.stacks[NinjaStacks.NINKI.value] = min(
                100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            self._update_bunshin_status()

            self.resources.gcd_cooldown_millisecond = DEFAULT_GCD_MILLISECOND
            self.resources.status[NinjaStatus.RAIJU_READY.value] = None
            self.resources.combo = 1

        elif action == NinjaSkills.TENCHIJIN.value:
            self.resources.cooldowns[action] = NINJA_SKILL_COOLDOWN_MILLISECONDS[action]
            self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] = [
                10000, 1]

        elif action == NinjaSkills.TCJ_FUMA_SHURIKEN.value:
            self.resources.stacks[NinjaStacks.TCJ_FUMA.value] += 1
            self.resources.gcd_cooldown_millisecond = TCJ_GCD_MILLISECOND

        elif action == NinjaSkills.TCJ_RAITON.value:
            self.resources.stacks[NinjaStacks.TCJ_RAITON.value] += 1
            self.resources.gcd_cooldown_millisecond = TCJ_GCD_MILLISECOND

            if self.resources.status[NinjaStatus.RAIJU_READY.value]:
                self.resources.status[NinjaStatus.RAIJU_READY.value] = [30000, self.resources.status[NinjaStatus.RAIJU_READY.value][1] + 1]
            else:
                self.resources.status[NinjaStatus.RAIJU_READY.value] = [30000, 1]

        elif action == NinjaSkills.TENRI_JINDO.value:
            self.resources.status[NinjaStatus.TENRI_JINDO_READY.value] = [
                30000, 1]

        elif action == NinjaSkills.ZESHO_MEPPO.value:
            assert self.resources.status[NinjaStatus.HIGI_STATUS.value], "using zesho meppo but doesn't have Higi"

            self.resources.status[NinjaStatus.HIGI_STATUS.value][1] -= 1

            assert self.resources.stacks[
                NinjaStacks.NINKI.value] >= 50, f'using zesho meppo @ _update_state, but ninki={self.resources.stacks[NinjaStacks.NINKI.value]} < 50'

            self.resources.stacks[NinjaStacks.NINKI.value] = max(0, self.resources.stacks[NinjaStacks.NINKI.value] - 50)

            if self.resources.status[NinjaStatus.MEISUI_STATUS.value]:
                self.resources.status[NinjaStatus.MEISUI_STATUS.value][1] -= 1

        for status_id, status in self.resources.status.items():
            if status and status[1] <= 0:
                self.resources.status[status_id] = None
