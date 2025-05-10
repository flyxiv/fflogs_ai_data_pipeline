"""Stores basic skills and statuses needed for ninja rotation models
"""

import logging
from enum import Enum

class NinjaSkills(Enum):
    AEOLIAN_EDGE = 1
    ARMOR_CRUSH = 2
    BHAVACAKRA = 3
    BUNSHIN = 4
    DOKUMORI = 5
    DREAM_WITHIN_A_DREAM = 6
    FLEETING_RAIJU = 7
    TCJ_FUMA_SHURIKEN = 8
    GUST_SLASH = 9
    HYOSHO_RANRYU = 10
    KASSATSU = 11
    KUNAIS_BANE = 12
    MEDICATED = 13
    MEISUI = 14
    PHANTOM_KAMAITACHI = 15
    RAITON = 16
    TCJ_RAITON = 17
    SPINNING_EDGE = 18
    TCJ_SUITON = 19
    SUITON = 20
    TENCHIJIN = 21
    TENRI_JINDO = 22
    ZESHO_MEPPO = 23
    FUMA_SHURIKEN = 24

    @staticmethod
    def get_gcd_skills():
        return set([NinjaSkills.TCJ_FUMA_SHURIKEN.value, NinjaSkills.TCJ_RAITON.value, NinjaSkills.TCJ_SUITON.value, NinjaSkills.SUITON.value, NinjaSkills.RAITON.value, NinjaSkills.SPINNING_EDGE.value, NinjaSkills.ARMOR_CRUSH.value, NinjaSkills.AEOLIAN_EDGE.value, NinjaSkills.HYOSHO_RANRYU.value, NinjaSkills.FLEETING_RAIJU.value, NinjaSkills.GUST_SLASH.value, NinjaSkills.PHANTOM_KAMAITACHI.value, NinjaSkills.FUMA_SHURIKEN.value]) 


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
    SUITON_STATUS = 9


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
            NinjaStatus.SUITON_STATUS.value: None,
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

    def debug_print(self):
        logging.info(f"mudra_timer: {self.mudra_timer}")
        logging.info(f"combo: {self.combo}")
        logging.info(f"combo_timer: {self.combo_timer}")
        logging.info(
            f"gcd_cooldown_millisecond: {self.gcd_cooldown_millisecond}")

        logging.info(f"stacks: =======================")
        for stack in self.stacks.keys():
            logging.info(f"{NinjaStacks(stack).name}: {self.stacks[stack]}")
        logging.info(f"=======================")

        logging.info(f"status: =======================")
        for status in self.status.keys():
            logging.info(f"{NinjaStatus(status).name}: {self.status[status]}")
        logging.info(f"=======================")

        logging.info(f"debuffs: =======================")
        for debuff in self.debuffs.keys():
            logging.info(
                f"{NinjaDebuffs(debuff).name}: {self.debuffs[debuff]}")
        logging.info(f"=======================")

        logging.info(f"cooldowns: =======================")
        for cooldown in self.cooldowns.keys():
            logging.info(
                f"{NinjaSkills(cooldown).name}: {self.cooldowns[cooldown]}")
        logging.info(f"=======================")


MAX_COOLDOWN_MILLISECOND = 120000
MAX_STATUS_DURATION_MILLISECOND = 45000
MAX_STACKS = 5

DEFAULT_GCD_MILLISECOND = 2120
MUDRA_GCD_MILLISECOND = 1500
TCJ_GCD_MILLISECOND = 1000
