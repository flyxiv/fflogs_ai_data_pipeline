"""Simulates ninja's skill usages and the corresponding status effects.

"""


from enum import Enum

import numpy as np


class NinjaSkills(Enum):

    AEOLIAN_EDGE = 0

    ARMOR_CRUSH = 1

    BHAVACAKRA = 2

    BUNSHIN = 3

    DOKUMORI = 4

    DREAM_WITHIN_A_DREAM = 5

    FLEETING_RAIJU = 6

    TCJ_FUMA_SHURIKEN = 7

    GUST_SLASH = 8

    HYOSHO_RANRYU = 9

    KASSATSU = 10

    KUNAIS_BANE = 11

    MEDICATED = 12

    MEISUI = 13

    PHANTOM_KAMAITACHI = 14

    RAITON = 15

    TCJ_RAITON = 16

    SPINNING_EDGE = 17

    TCJ_SUITON = 18

    SUITON = 19

    TENCHIJIN = 20

    TENRI_JINDO = 21

    ZESHO_MEPPO = 22

    FUMA_SHURIKEN = 23


class NinjaGCDSkills(Enum):

    AEOLIAN_EDGE = 0

    ARMOR_CRUSH = 1

    FLEETING_RAIJU = 2

    TCJ_FUMA_SHURIKEN = 3

    GUST_SLASH = 4

    HYOSHO_RANRYU = 5

    PHANTOM_KAMAITACHI = 6

    RAITON = 7

    TCJ_RAITON = 8

    SPINNING_EDGE = 9

    TCJ_SUITON = 10

    SUITON = 11

    FUMA_SHURIKEN = 12


class NinjaOGCDSkills(Enum):

    BHAVACAKRA = 0

    BUNSHIN = 1

    DOKUMORI = 2

    DREAM_WITHIN_A_DREAM = 3

    KASSATSU = 4

    KUNAIS_BANE = 5

    MEDICATED = 6

    MEISUI = 7

    TENCHIJIN = 8

    TENRI_JINDO = 9

    ZESHO_MEPPO = 10


def ninja_gcd_to_all_skill(gcd_skill: NinjaGCDSkills) -> NinjaSkills:

    if gcd_skill == NinjaGCDSkills.AEOLIAN_EDGE:

        return NinjaSkills.AEOLIAN_EDGE

    elif gcd_skill == NinjaGCDSkills.ARMOR_CRUSH:

        return NinjaSkills.ARMOR_CRUSH

    elif gcd_skill == NinjaGCDSkills.FLEETING_RAIJU:

        return NinjaSkills.FLEETING_RAIJU

    elif gcd_skill == NinjaGCDSkills.FUMA_SHURIKEN:

        return NinjaSkills.FUMA_SHURIKEN

    elif gcd_skill == NinjaGCDSkills.GUST_SLASH:

        return NinjaSkills.GUST_SLASH

    elif gcd_skill == NinjaGCDSkills.HYOSHO_RANRYU:

        return NinjaSkills.HYOSHO_RANRYU

    elif gcd_skill == NinjaGCDSkills.PHANTOM_KAMAITACHI:

        return NinjaSkills.PHANTOM_KAMAITACHI

    elif gcd_skill == NinjaGCDSkills.RAITON:

        return NinjaSkills.RAITON

    elif gcd_skill == NinjaGCDSkills.SPINNING_EDGE:

        return NinjaSkills.SPINNING_EDGE

    elif gcd_skill == NinjaGCDSkills.SUITON:

        return NinjaSkills.SUITON

    elif gcd_skill == NinjaGCDSkills.TCJ_FUMA_SHURIKEN:

        return NinjaSkills.TCJ_FUMA_SHURIKEN

    elif gcd_skill == NinjaGCDSkills.TCJ_RAITON:

        return NinjaSkills.TCJ_RAITON

    else:

        return NinjaSkills.TCJ_SUITON


def ninja_ogcd_to_all_skill(ogcd_skill: NinjaOGCDSkills) -> NinjaSkills:

    if ogcd_skill == NinjaOGCDSkills.BHAVACAKRA:

        return NinjaSkills.BHAVACAKRA

    elif ogcd_skill == NinjaOGCDSkills.BUNSHIN:

        return NinjaSkills.BUNSHIN

    elif ogcd_skill == NinjaOGCDSkills.DOKUMORI:

        return NinjaSkills.DOKUMORI

    elif ogcd_skill == NinjaOGCDSkills.DREAM_WITHIN_A_DREAM:

        return NinjaSkills.DREAM_WITHIN_A_DREAM

    elif ogcd_skill == NinjaOGCDSkills.KASSATSU:

        return NinjaSkills.KASSATSU

    elif ogcd_skill == NinjaOGCDSkills.KUNAIS_BANE:

        return NinjaSkills.KUNAIS_BANE

    elif ogcd_skill == NinjaOGCDSkills.MEDICATED:

        return NinjaSkills.MEDICATED

    elif ogcd_skill == NinjaOGCDSkills.MEISUI:

        return NinjaSkills.MEISUI

    elif ogcd_skill == NinjaOGCDSkills.TENCHIJIN:

        return NinjaSkills.TENCHIJIN

    elif ogcd_skill == NinjaOGCDSkills.TENRI_JINDO:

        return NinjaSkills.TENRI_JINDO

    else:

        return NinjaSkills.ZESHO_MEPPO


class NinjaStatus(Enum):

    BUNSHIN_STATUS = 0

    HIGI_STATUS = 1

    KASSATSU_STATUS = 2

    MEISUI_STATUS = 3

    MEDICATED_STATUS = 4

    PHANTOM_KAMAITACHI_READY = 5

    RAIJU_READY = 6

    TENCHIJIN_STATUS = 7

    TENRI_JINDO_READY = 8


class NinjaDebuffs(Enum):

    DOKUMORI_DEBUFF = 0

    KUNAIS_BANE_DEBUFF = 1


class NinjaStacks(Enum):

    NINKI = 0,

    SHURIKEN = 1,

    MUDRA = 2,

    TCJ_FUMA = 3,

    TCJ_RAITON = 4


NINJA_SKILL_COOLDOWN_MILLISECONDS = {

    NinjaSkills.AEOLIAN_EDGE.value: 0,

    NinjaSkills.ARMOR_CRUSH.value: 0,

    NinjaSkills.BHAVACAKRA.value: 0,

    NinjaSkills.BUNSHIN.value: 90000,

    NinjaSkills.DOKUMORI.value: 120000,

    NinjaSkills.DREAM_WITHIN_A_DREAM.value: 60000,

    NinjaSkills.FLEETING_RAIJU.value: 0,

    NinjaSkills.GUST_SLASH.value: 0,

    NinjaSkills.HYOSHO_RANRYU.value: 0,

    NinjaSkills.KASSATSU.value: 60000,

    NinjaSkills.KUNAIS_BANE.value: 60000,

    NinjaSkills.MEDICATED.value: 270000,

    NinjaSkills.MEISUI.value: 120000,

    NinjaSkills.PHANTOM_KAMAITACHI.value: 0,

    NinjaSkills.RAITON.value: 0,

    NinjaSkills.TCJ_RAITON.value: 0,

    NinjaSkills.SPINNING_EDGE.value: 0,

    NinjaSkills.TCJ_SUITON.value: 0,

    NinjaSkills.SUITON.value: 0,

    NinjaSkills.TENCHIJIN.value: 120000,

    NinjaSkills.TENRI_JINDO.value: 0,

    NinjaSkills.ZESHO_MEPPO.value: 0,

    NinjaSkills.FUMA_SHURIKEN.value: 0,

    NinjaSkills.TCJ_FUMA_SHURIKEN.value: 0,

}


class NinjaResources:

    def __init__(self):

        self.cooldowns = {

            NinjaSkills.AEOLIAN_EDGE.value: 0,

            NinjaSkills.ARMOR_CRUSH.value: 0,

            NinjaSkills.BHAVACAKRA.value: 0,

            NinjaSkills.BUNSHIN.value: 0,

            NinjaSkills.DOKUMORI.value: 0,

            NinjaSkills.DREAM_WITHIN_A_DREAM.value: 0,

            NinjaSkills.FLEETING_RAIJU.value: 0,

            NinjaSkills.GUST_SLASH.value: 0,

            NinjaSkills.HYOSHO_RANRYU.value: 0,

            NinjaSkills.KASSATSU.value: 0,

            NinjaSkills.KUNAIS_BANE.value: 0,

            NinjaSkills.MEDICATED.value: 0,

            NinjaSkills.MEISUI.value: 0,

            NinjaSkills.PHANTOM_KAMAITACHI.value: 0,

            NinjaSkills.RAITON.value: 0,

            NinjaSkills.TCJ_RAITON.value: 0,

            NinjaSkills.SPINNING_EDGE.value: 0,

            NinjaSkills.TCJ_SUITON.value: 0,

            NinjaSkills.SUITON.value: 0,

            NinjaSkills.TENCHIJIN.value: 0,

            NinjaSkills.TENRI_JINDO.value: 0,

            NinjaSkills.ZESHO_MEPPO.value: 0,

            NinjaSkills.FUMA_SHURIKEN.value: 0,

            NinjaSkills.TCJ_FUMA_SHURIKEN.value: 0,

        }

        # (duration, stacks)

        self.status = {

            NinjaStatus.BUNSHIN_STATUS.value: None,

            NinjaStatus.HIGI_STATUS.value: None,

            NinjaStatus.KASSATSU_STATUS.value: None,

            NinjaStatus.MEISUI_STATUS.value: None,

            NinjaStatus.MEDICATED_STATUS.value: None,

            NinjaStatus.PHANTOM_KAMAITACHI_READY .value: None,

            NinjaStatus.RAIJU_READY.value: None,

            NinjaStatus.TENCHIJIN_STATUS.value: None,

            NinjaStatus.TENRI_JINDO_READY.value: None,

        }

        self.debuffs = {

            NinjaDebuffs.DOKUMORI_DEBUFF.value: None,

            NinjaDebuffs.KUNAIS_BANE_DEBUFF.value: None,

        }

        self.stacks = {

            NinjaStacks.NINKI.value: 0,

            NinjaStacks.SHURIKEN.value: 0,

            NinjaStacks.MUDRA.value: 2,

            NinjaStacks.TCJ_FUMA.value: 0,

            NinjaStacks.TCJ_RAITON.value: 0

        }

        self.mudra_timer = 0

        self.combo = 0

        self.combo_timer = 0

        self.gcd_cooldown_millisecond = 0


MAX_COOLDOWN_MILLISECOND = 120000

MAX_STATUS_DURATION_MILLISECOND = 45

MAX_STACKS = 5


COMBO_TIMER_MAX_MILLISECOND = 30000

DEFAULT_GCD_MILLISECOND = 2120

MUDRA_GCD_MILLISECOND = 1500

TCJ_GCD_MILLISECOND = 1000

DEFAULT_DELAY_MILLISECOND = 700


class NinjaEnvironment:

    def __init__(self, target_time_millisecond):

        self.target_time_millisecond = target_time_millisecond

        self.resources = NinjaResources()

        self.current_time_millisecond = 0

    def reset(self):

        self.resources = NinjaResources()

        self.current_time_millisecond = 0

    def _get_state(self):
        status_encoded = []
        debuffs_encoded = []

        for i in range(len(self.resources.status)):
            if self.resources.status[i]:
                status_encoded.append(
                    self.resources.status[i][0] / MAX_STATUS_DURATION_MILLISECOND)
                status_encoded.append(self.resources.status[i][1] / MAX_STACKS)

            else:
                status_encoded.append(0)
                status_encoded.append(0)

        for i in range(len(self.resources.debuffs)):
            if self.resources.debuffs[i]:
                debuffs_encoded.append(
                    self.resources.debuffs[i][0] / MAX_DEBUFF_DURATION_MILLISECOND)
                debuffs_encoded.append(
                    self.resources.debuffs[i][1] / MAX_STACKS)
            else:
                debuffs_encoded.append(0)
                debuffs_encoded.append(0)

        resources_normalized = [self.resources.cooldowns[i] /

                                MAX_COOLDOWN_MILLISECOND for i in range(len(self.resources.cooldowns))]

        stacks_normalized = [self.resources.stacks[NinjaStacks.NINKI.value] / 100, self.resources.stacks[NinjaStacks.SHURIKEN.value] / 5,

                             self.resources.stacks[NinjaStacks.MUDRA.value] / 2, self.resources.stacks[NinjaStacks.TCJ_FUMA.value], self.resources.stacks[NinjaStacks.TCJ_RAITON.value]]

        combo_normalized = [self.resources.combo / 3,

                            self.resources.combo_timer / COMBO_TIMER_MAX_MILLISECOND]

        is_gcd = [1 if self.resources.gcd_cooldown_millisecond == 0 else 0]

        return tf.expand_dims(tf.constant(np.array(resources_normalized + stacks_normalized + status_encoded + debuffs_encoded + combo_normalized + is_gcd)), axis=0)

    def get_possible_gcd_actions(self):

        possible_gcd_actions = []

        for skill_id in range(len(NinjaGCDSkills)):

            skill_id_translated = ninja_gcd_to_all_skill(

                NinjaGCDSkills(skill_id))

            if self._has_requirements_for_skill(skill_id_translated) and self.resources.cooldowns[skill_id_translated] == 0:

                possible_gcd_actions.append(skill_id)

        assert set(possible_gcd_actions).issubset(set(range(13)))

        return possible_gcd_actions

    def get_possible_ogcd_actions(self):

        possible_ogcd_actions = []

        for skill_id in range(len(NinjaOGCDSkills)):

            skill_id_translated = ninja_ogcd_to_all_skill(

                NinjaOGCDSkills(skill_id))

            if self._has_requirements_for_skill(skill_id_translated) and self.resources.cooldowns[skill_id_translated] == 0:

                possible_ogcd_actions.append(skill_id)

        assert set(possible_ogcd_actions).issubset(set(range(11)))

        return possible_ogcd_actions

    def is_gcd(self):
        return self.resources.gcd_cooldown_millisecond == 0

    def step(self, action, time_elapsed_millisecond):
        reward = 0

        self._advance_time(time_elapsed_millisecond)

        is_gcd = False

        if action <= len(self.resources.cooldowns):

            reward = self._calculate_potency(action)

            self._update_state(action)

            delay = self._calculate_delay(action)

            self._advance_time(delay)

            if self.resources.gcd_cooldown_millisecond < DEFAULT_DELAY_MILLISECOND:

                self._advance_time(self.resources.gcd_cooldown_millisecond)

                is_gcd = True

        else:

            self._advance_time(self.resources.gcd_cooldown_millisecond)

            is_gcd = True

        return self._get_state(), self.get_possible_gcd_actions(), self.get_possible_ogcd_actions(), self.is_gcd(), self.current_time_millisecond, self.resources.gcd_cooldown_millisecond, reward, self.target_time_millisecond <= self.current_time_millisecond

    def _advance_time(self, time_elapsed_millisecond):

        for skill in self.resources.cooldowns.keys():
            if self.resources.cooldowns[skill]:
                self.resources.cooldowns[skill] = max(
                    self.resources.cooldowns[skill] - time_elapsed_millisecond, 0)

        for status_key, value in self.resources.status.items():

            self.resources.status[status_key][0] = value - \
                time_elapsed_millisecond
            if self.resources.status[status_key][0] <= 0:
                self.resources.status[status_key] = None

        for debuff_key, value in self.resources.debuffs.items():
            self.resources.debuffs[debuff_key][0] = value - \
                time_elapsed_millisecond

            if self.resources.debuffs[debuff_key][0] <= 0:
                self.resources.debuffs[debuff_key] = None

        self.current_time_millisecond += time_elapsed_millisecond
        mudra_timer_before = self.resources.mudra_timer

        self.resources.mudra_timer = max(
            0, self.resources.mudra_timer - time_elapsed_millisecond)

        if mudra_timer_before // 20000 != self.resources.mudra_timer // 20000:
            self.resources.stacks[NinjaStacks.MUDRA.value] += 1

    def _calculate_delay(self, action):

        delay = DEFAULT_DELAY_MILLISECOND

        if action == NinjaSkills.RAITON:

            delay += 1000

        elif action == NinjaSkills.SUITON:

            delay += 1500

        elif action == NinjaSkills.FUMA_SHURIKEN:

            delay += 500

        return delay

    def _has_requirements_for_skill(self, skill_id):

        if skill_id == NinjaSkills.BHAVACAKRA.value:

            return self.resources.stacks[NinjaStacks.NINKI.value] >= 50

        if skill_id == NinjaSkills.ZESHO_MEPPO.value:

            return (self.resources.stacks[NinjaStacks.NINKI.value] >= 50) and (self.resources.status[NinjaStatus.HIGI_STATUS.value])

        elif skill_id == NinjaSkills.RAITON.value or action == NinjaSkills.SUITON.value:

            return (self.resources.stacks[NinjaStacks.MUDRA.value] >= 1) or (self.resources.status[NinjaStatus.KASSATSU_STATUS.value] is not None)

        elif skill_id == NinjaSkills.TCJ_FUMA_SHURIKEN.value:

            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is not None

        elif skill_id == NinjaSkills.TCJ_RAITON.value:

            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is not None and self.resources.status[NinjaStacks.TCJ_FUMA.value] == 1

        elif skill_id == NinjaSkills.TCJ_SUITON.value:

            return self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value] is not None and self.resources.status[NinjaStacks.TCJ_FUMA.value] == 1 and self.resources.status[NinjaStacks.TCJ_RAITON.value] == 1

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

        return True

    def _calculate_potency(self, action):
        """Calculate potency = reward of the action chosen by the DQN.

        """

        potency = 0

        if action == NinjaSkills.AEOLIAN_EDGE.value:

            if self.resources.combo != 2:

                potency = 260

            else:

                potency = 440

            if self.resources.stacks[NinjaStacks.SHURIKEN.value] >= 1:

                potency += 100

            if self.resources.stacks[NinjaStatus.BUNSHIN_STATUS.value]:

                potency += 160

        elif action == NinjaSkills.ARMOR_CRUSH.value:

            if self.resources.combo != 2:

                potency = 280

            else:

                potency = 480

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

        elif action == NinjaSkills.FUMA_SHURIKEN.value or action == NinjaSkills.TCJ_FUMA_SHURIKEN.value:

            potency = 500

            if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:

                potency = potency * 1.3

        elif action == NinjaSkills.GUST_SLASH.value:

            if self.resources.combo != 1:

                potency = 240

            else:

                potency = 400

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

        elif action == NinjaSkills.TENRI_JINDO.value:

            potency = 1100

        if self.resources.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value]:

            potency *= 1.05

        elif self.resources.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value]:

            potency *= 1.1

        elif self.resources.status[NinjaStatus.MEDICATED_STATUS.value]:

            potency *= 1.08

        return potency

    def _update_state(self, action):
        """Update Markov State of the Ninja character.

        """

        if action == NinjaSkills.AEOLIAN_EDGE.value:

            if self.resources.combo == 2:

                self.resources.stacks[NinjaStacks.NINKI.value] = min(

                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 15)

            self.resources.stacks[NinjaStacks.SHURIKEN.value] = max(

                self.resources.stacks[NinjaStacks.SHURIKEN.value] - 1, 0)

            if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:

                assert self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][

                    1] >= 1, "bunshin status didn't disappear when stack is 0"

                self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] -= 1

                self.resources.stacks[NinjaStacks.NINKI.value] = min(

                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            self.resources.status[NinjaStatus.RAIJU_READY] = None

            self.resources.combo = 0

            self.resources.gcd_cooldown_millisecond = NINJA_SKILL_COOLDOWN_MILLISECONDS

        elif action == NinjaSkills.ARMOR_CRUSH.value:

            self.resources.stacks[NinjaStacks.SHURIKEN.value] = min(

                self.resources.stacks[NinjaStacks.SHURIKEN.value] + 2, 5)

            self.resources.stacks[NinjaStacks.NINKI.value] = min(

                100, self.resources.stacks[NinjaStacks.NINKI.value] + 15)

            if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:

                assert self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][

                    1] >= 1, "bunshin status didn't disappear when stack is 0"

                self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] -= 1

                self.resources.stacks[NinjaStacks.NINKI.value] = min(

                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            self.resources.status[NinjaStatus.RAIJU_READY] = None

            self.resources.combo = 0

            self.resources.gcd_cooldown_millisecond = NINJA_SKILL_COOLDOWN_MILLISECONDS

        elif action == NinjaSkills.BHAVACAKRA.value:

            assert self.resources.stacks[

                NinjaStacks.NINKI.value] >= 50, f'using bhavacakra @ _update_state, but ninki={self.resources.stacks[NinjaStacks.NINKI.value]} < 50'

            self.resources.stacks[NinjaStacks.NINKI.value] = self.resources.stacks[NinjaStacks.NINKI.value] - 50

            if self.resources.status[NinjaStatus.MEISUI_STATUS]:

                self.resources.status[NinjaStatus.MEISUI_STATUS][1] -= 1

        elif action == NinjaSkills.BUNSHIN.value:

            assert self.resources.cooldowns[NinjaSkills.BUNSHIN.value] == 0, 'bunshin used when Cooldown > 0'

            self.resources.cooldowns[NinjaSkills.BUNSHIN.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.BUNSHIN.value]

            self.resources.status[NinjaStatus.BUNSHIN_STATUS.value] = [

                30000, 5]

            self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value] = [

                45000, 1]

        elif action == NinjaSkills.DOKUMORI.value:

            # https://github.com/flyxiv/fflogs_ai_data_pipeline/issues/4#issuecomment-2692502549

            # Dokumori lasts 21 seconds

            assert self.resources.cooldowns[NinjaSkills.DOKUMORI.value] == 0, 'dokumori used when Cooldown > 0'

            self.resources.stacks[NinjaStacks.NINKI.value] = min(

                100, self.resources.stacks[NinjaStacks.NINKI.value] + 40)

            self.resources.cooldowns[NinjaSkills.DOKUMORI.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.DOKUMORI.value]

            self.resources.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value] = [

                21000, 1]

            self.resources.status[NinjaStatus.HIGI_STATUS.value] = [30000, 1]

        elif action == NinjaSkills.KUNAIS_BANE.value:

            # https://github.com/flyxiv/fflogs_ai_data_pipeline/issues/4#issuecomment-2692502549

            # Kunai's bane lasts 16.25 seconds

            assert self.resources.cooldowns[NinjaSkills.KUNAIS_BANE.value] == 0, "kunai's bane used when Cooldown > 0"

            self.resources.cooldowns[NinjaSkills.KUNAIS_BANE.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.KUNAIS_BANE.value]

            self.resources.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value] = [

                16250, 1]

        elif action == NinjaSkills.FLEETING_RAIJU.value:

            assert self.resources.status[NinjaStatus.RAIJU_READY.value], "don't have raiju ready when fleeting raiju is used"

            self.resources.status[NinjaStatus.RAIJU_READY.value][1] -= 1

            self.resources.gcd_cooldown_millisecond = NINJA_SKILL_COOLDOWN_MILLISECONDS

        elif action == NinjaSkills.FUMA_SHURIKEN.value or action == NinjaSkills.RAITON or action == NinjaSkills.SUITON.value:

            if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:

                self.resources.status[NinjaStatus.KASSATSU_STATUS.value][1] -= 1

            else:

                assert self.resources.stacks[NinjaStacks.MUDRA.value], "don't have mudra ready when using suiton/raiton/fuma"

                self.resources.stacks[NinjaStacks.MUDRA.value] -= 1

                self.resources.mudra_timer += 20000

                if self.resources.status[NinjaStatus.KASSATSU_STATUS.value]:

                    self.resources.status[NinjaStatus.KASSATSU_STATUS.value][1] -= 1

            self.resources.gcd_cooldown_millisecond = MUDRA_GCD_MILLISECOND

        elif action == NinjaSkills.TCJ_SUITON.value:

            assert self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value], "don't have TCJ when using TCJ_suiton"

            self.resources.status[NinjaStatus.TENCHIJIN_STATUS.value][1] -= 1

            self.resources.stacks[NinjaStacks.TCJ_FUMA.value] = 0

            self.resources.stacks[NinjaStacks.TCJ_RAITON.value] = 0

            self.resources.gcd_cooldown_millisecond = TCJ_GCD_MILLISECOND

        elif action == NinjaSkills.GUST_SLASH.value:

            self.resources.stacks[NinjaStacks.NINKI.value] = min(

                100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:

                assert self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][

                    1] >= 1, "bunshin status didn't disappear when stack is 0"

                self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] -= 1

                self.resources.stacks[NinjaStacks.NINKI.value] = min(

                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            self.resources.status[NinjaStatus.RAIJU_READY] = None

            self.resources.combo = 2

            self.resources.gcd_cooldown_millisecond = NINJA_SKILL_COOLDOWN_MILLISECONDS

        elif action == NinjaSkills.HYOSHO_RANRYU.value:

            assert self.resources.status[NinjaStatus.KASSATSU_STATUS.value], 'No kassatsu when using hyosho ranryu'

            self.resources.status[NinjaStatus.KASSATSU_STATUS.value][1] -= 1

            self.resources.gcd_cooldown_millisecond = MUDRA_GCD_MILLISECOND

        elif action == NinjaSkills.KASSATSU.value:

            self.resources.cooldowns[NinjaSkills.KASSATSU.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.KASSATSU.value]

            self.resources.status[NinjaStatus.KASSATSU_STATUS.value] = [

                15000, 1]

        elif action == NinjaSkills.MEDICATED.value:

            self.resources.cooldowns[NinjaSkills.MEDICATED.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.MEDICATED.value]

            self.resources.status[NinjaStatus.MEDICATED_STATUS.value] = [

                30000, 1]

        elif action == NinjaSkills.MEISUI.value:

            self.resources.cooldowns[NinjaSkills.MEISUI.value] = NINJA_SKILL_COOLDOWN_MILLISECONDS[NinjaSkills.MEISUI.value]

            self.resources.stacks[NinjaStacks.NINKI.value] = min(

                100, self.resources.stacks[NinjaStacks.NINKI.value] + 50)

            self.resources.status[NinjaStatus.MEISUI_STATUS.value] = [30000, 1]

        elif action == NinjaSkills.PHANTOM_KAMAITACHI.value:

            assert self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value], "using Phantom Kamaitachi, but doesn't have Phantom Kamaitachi Ready Status"

            self.resources.stacks[NinjaStacks.NINKI.value] = min(

                100, self.resources.stacks[NinjaStacks.NINKI.value] + 10)

            self.resources.status[NinjaStatus.PHANTOM_KAMAITACHI_READY.value][1] -= 1

            self.resources.gcd_cooldown_millisecond = NINJA_SKILL_COOLDOWN_MILLISECONDS

        elif action == NinjaSkills.SPINNING_EDGE.value:

            self.resources.stacks[NinjaStacks.NINKI.value] = min(

                100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            if self.resources.status[NinjaStatus.BUNSHIN_STATUS.value]:

                assert self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][

                    1] >= 1, "bunshin status didn't disappear when stack is 0"

                self.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] -= 1

                self.resources.stacks[NinjaStacks.NINKI.value] = min(

                    100, self.resources.stacks[NinjaStacks.NINKI.value] + 5)

            self.resources.gcd_cooldown_millisecond = NINJA_SKILL_COOLDOWN_MILLISECONDS

            self.resources.status[NinjaStatus.RAIJU_READY] = None

            self.resources.combo = 1

        elif action == NinjaSkills.TENCHIJIN.value:

            self.resources.cooldowns[action] = NINJA_SKILL_COOLDOWN_MILLISECONDS[action]

            self.resources.status[NinjaStatus.TENCHIJIN_STATUS] = [10000, 1]

        elif action == NinjaSkills.TCJ_FUMA_SHURIKEN.value:

            self.resources.stacks[NinjaStacks.TCJ_FUMA] += 1

            self.resources.gcd_cooldown_millisecond = TCJ_GCD_MILLISECOND

        elif action == NinjaSkills.TCJ_RAITON.value:

            self.resources.stacks[NinjaStacks.TCJ_RAITON] += 1

            self.resources.gcd_cooldown_millisecond = TCJ_GCD_MILLISECOND

        elif action == NinjaSkills.TENRI_JINDO.value:

            self.resources.status[NinjaStatus.TENRI_JINDO_READY.value] = [

                30000, 1]

        elif action == NinjaSkills.ZESHO_MEPPO.value:

            assert self.resources.status[NinjaStatus.HIGI_STATUS.value], "using zesho meppo but doesn't have Higi"

            self.resources.status[NinjaStatus.HIGI_STATUS.value][1] -= 1

            assert self.resources.stacks[

                NinjaStacks.NINKI.value] >= 50, f'using zesho meppo @ _update_state, but ninki={self.resources.stacks[NinjaStacks.NINKI.value]} < 50'

            self.resources.stacks[NinjaStacks.NINKI.value] = self.resources.stacks[NinjaStacks.NINKI.value] - 50

            if self.resources.status[NinjaStatus.MEISUI_STATUS]:

                self.resources.status[NinjaStatus.MEISUI_STATUS][1] -= 1

        for status_id, status in self.resources.status.items():

            if status[1] <= 0:

                self.resources[status_id] = None
