"""Stores basic skills and statuses needed for ninja rotation models"""

from rotation_models.ffxiv_system.skill import Skill
from rotation_models.ffxiv_system.cost import (
    UseAllBuff,
    UseAllDebuff,
    UseBuff,
    UseDebuff,
    UseResource,
    DoesNotHaveBuff,
    CheckBuff,
)
from rotation_models.ffxiv_system.resource import Resource
from rotation_models.ffxiv_system.status_event import (
    ApplyBuffEvent,
    ApplyDebuffEvent,
    AddResourceEvent,
)
from rotation_models.ffxiv_system.buff import Buff
from rotation_models.ffxiv_system.debuff import Debuff
from rotation_models.ffxiv_system.job_database import JobDatabase
from rotation_models.ffxiv_system.combat_status import CombatStatus

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
        return set(
            [
                NinjaSkills.TCJ_FUMA_SHURIKEN.value,
                NinjaSkills.TCJ_RAITON.value,
                NinjaSkills.TCJ_SUITON.value,
                NinjaSkills.SUITON.value,
                NinjaSkills.RAITON.value,
                NinjaSkills.SPINNING_EDGE.value,
                NinjaSkills.ARMOR_CRUSH.value,
                NinjaSkills.AEOLIAN_EDGE.value,
                NinjaSkills.HYOSHO_RANRYU.value,
                NinjaSkills.FLEETING_RAIJU.value,
                NinjaSkills.GUST_SLASH.value,
                NinjaSkills.PHANTOM_KAMAITACHI.value,
                NinjaSkills.FUMA_SHURIKEN.value,
            ]
        )


class NinjaBuffs(Enum):
    BUNSHIN_BUFF = 0
    HIGI_BUFF = 1
    KASSATSU_BUFF = 2
    MEISUI_BUFF = 3
    MEDICATED_BUFF = 4
    PHANTOM_KAMAITACHI_READY = 5
    RAIJU_READY = 6
    TENCHIJIN_BUFF = 7
    TENRI_JINDO_READY = 8
    SUITON_BUFF = 9
    TCJ_FUMA_BUFF = 10
    TCJ_RAITON_BUFF = 11
    TCJ_SUITON_BUFF = 12


class NinjaDebuffs(Enum):
    DOKUMORI_DEBUFF = 0
    KUNAIS_BANE_DEBUFF = 1


class NinjaResources(Enum):
    NINKI = 0
    SHURIKEN = 1


DEFAULT_GCD_MILLISECOND = 2120
MUDRA_GCD_MILLISECOND = 1500
TCJ_GCD_MILLISECOND = 1000


AEOLIAN_EDGE = Skill(
    skill_id=NinjaSkills.AEOLIAN_EDGE.value,
    name="AEOLIAN EDGE",
    potency=280,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=DEFAULT_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[AddResourceEvent(NinjaResources.NINKI.value, 15, 2)],
    cancel_events=[UseAllBuff(NinjaBuffs.RAIJU_READY.value)],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=460,
    next_combo=0,
    required_combo=2,
    bonus_potency_if_resource=[NinjaResources.SHURIKEN.value, 100],
    is_combo=True,
    proc_events=None,
)

ARMOR_CRUSH = Skill(
    skill_id=NinjaSkills.ARMOR_CRUSH.value,
    name="ARMOR CRUSH",
    potency=300,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=DEFAULT_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[
        AddResourceEvent(NinjaResources.NINKI.value, 15, 2),
        AddResourceEvent(NinjaResources.SHURIKEN.value, 2, 2),
    ],
    cancel_events=[UseAllBuff(NinjaBuffs.RAIJU_READY.value)],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=500,
    next_combo=0,
    required_combo=2,
    bonus_potency_if_resource=None,
    is_combo=True,
    proc_events=None,
)

BHAVACAKRA = Skill(
    skill_id=NinjaSkills.BHAVACAKRA.value,
    name="BHAVACAKRA",
    potency=400,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseResource(NinjaResources.NINKI.value, 50),
        DoesNotHaveBuff(NinjaBuffs.HIGI_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

BUNSHIN = Skill(
    skill_id=NinjaSkills.BUNSHIN.value,
    name="BUNSHIN",
    potency=0,
    max_stacks=1,
    cooldown_millisecond=90000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseResource(NinjaResources.NINKI.value, 50),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[
        ApplyBuffEvent(NinjaBuffs.BUNSHIN_BUFF.value, 30000, 5, True),
        ApplyBuffEvent(NinjaBuffs.PHANTOM_KAMAITACHI_READY.value, 45000, 1, True),
    ],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)


DOKUMORI = Skill(
    skill_id=NinjaSkills.DOKUMORI.value,
    name="DOKUMORI",
    potency=300,
    max_stacks=1,
    cooldown_millisecond=120000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[
        ApplyDebuffEvent(NinjaDebuffs.DOKUMORI_DEBUFF.value, 21000, 1, True),
        AddResourceEvent(NinjaResources.NINKI.value, 40, None),
        ApplyBuffEvent(NinjaBuffs.HIGI_BUFF.value, 30000, 1, True),
    ],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

DREAM_WITHIN_A_DREAM = Skill(
    skill_id=NinjaSkills.DREAM_WITHIN_A_DREAM.value,
    name="DREAM WITHIN A DREAM",
    potency=540,
    max_stacks=1,
    cooldown_millisecond=60000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

FLEETING_RAIJU = Skill(
    skill_id=NinjaSkills.FLEETING_RAIJU.value,
    name="FLEETING RAIJU",
    potency=700,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=DEFAULT_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.RAIJU_READY.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[AddResourceEvent(NinjaResources.NINKI.value, 5, None)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

TCJ_FUMA_SHURIKEN = Skill(
    skill_id=NinjaSkills.TCJ_FUMA_SHURIKEN.value,
    name="TCJ FUMA SHURIKEN",
    potency=500,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=TCJ_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        CheckBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value),
        UseBuff(NinjaBuffs.TCJ_FUMA_BUFF.value),
    ],
    events=[ApplyBuffEvent(NinjaBuffs.TCJ_RAITON_BUFF.value, 6000, 1, True)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

GUST_SLASH = Skill(
    skill_id=NinjaSkills.GUST_SLASH.value,
    name="GUST SLASH",
    potency=240,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=DEFAULT_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[AddResourceEvent(NinjaResources.NINKI.value, 5, 1)],
    cancel_events=[UseAllBuff(NinjaBuffs.RAIJU_READY.value)],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=400,
    next_combo=2,
    required_combo=1,
    bonus_potency_if_resource=None,
    is_combo=True,
    proc_events=None,
)

HYOSHO_RANRYU = Skill(
    skill_id=NinjaSkills.HYOSHO_RANRYU.value,
    name="HYOSHO RANRYU",
    potency=1690,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=MUDRA_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=1000,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.KASSATSU_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)


KASSATSU = Skill(
    skill_id=NinjaSkills.KASSATSU.value,
    name="KASSATSU",
    potency=0,
    max_stacks=1,
    cooldown_millisecond=60000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[ApplyBuffEvent(NinjaBuffs.KASSATSU_BUFF.value, 15000, 1, True)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

KUNAIS_BANE = Skill(
    skill_id=NinjaSkills.KUNAIS_BANE.value,
    name="KUNAIS BANE",
    potency=600,
    max_stacks=1,
    cooldown_millisecond=60000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.SUITON_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[ApplyDebuffEvent(NinjaDebuffs.KUNAIS_BANE_DEBUFF.value, 16250, 1, True)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

MEDICATED = Skill(
    skill_id=NinjaSkills.MEDICATED.value,
    name="MEDICATED",
    potency=0,
    max_stacks=1,
    cooldown_millisecond=270000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[ApplyBuffEvent(NinjaBuffs.MEDICATED_BUFF.value, 30000, 1, True)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

MEISUI = Skill(
    skill_id=NinjaSkills.MEISUI.value,
    name="MEISUI",
    potency=0,
    max_stacks=1,
    cooldown_millisecond=120000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.SUITON_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[ApplyBuffEvent(NinjaBuffs.MEISUI_BUFF.value, 20000, 1, True), AddResourceEvent(NinjaResources.NINKI.value, 50, None)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

PHANTOM_KAMAITACHI = Skill(
    skill_id=NinjaSkills.PHANTOM_KAMAITACHI.value,
    name="PHANTOM KAMAITACHI",
    potency=600,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=DEFAULT_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.PHANTOM_KAMAITACHI_READY.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[AddResourceEvent(NinjaResources.NINKI.value, 10, None)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

RAITON = Skill(
    skill_id=NinjaSkills.RAITON.value,
    name="RAITON",
    potency=740,
    max_stacks=2,
    cooldown_millisecond=20000,
    gcd_cooldown_millisecond=MUDRA_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=1000,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[ApplyBuffEvent(NinjaBuffs.RAIJU_READY.value, 30000, 1, True)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)


TCJ_RAITON = Skill(
    skill_id=NinjaSkills.TCJ_RAITON.value,
    name="TCJ RAITON",
    potency=740,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=TCJ_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        CheckBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
        UseBuff(NinjaBuffs.TCJ_RAITON_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value),
    ],
    events=[
        ApplyBuffEvent(NinjaBuffs.TCJ_SUITON_BUFF.value, 6000, 1, True),
        ApplyBuffEvent(NinjaBuffs.RAIJU_READY.value, 30000, 1, True),
    ],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

SPINNING_EDGE = Skill(
    skill_id=NinjaSkills.SPINNING_EDGE.value,
    name="SPINNING EDGE",
    potency=300,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=DEFAULT_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value)],
    events=[AddResourceEvent(NinjaResources.NINKI.value, 5, None)],
    cancel_events=[UseAllBuff(NinjaBuffs.RAIJU_READY.value)],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=1,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=True,
    proc_events=None,
)

TCJ_SUITON = Skill(
    skill_id=NinjaSkills.TCJ_SUITON.value,
    name="TCJ SUITON",
    potency=580,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=TCJ_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
        UseBuff(NinjaBuffs.TCJ_SUITON_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value),
    ],
    events=[ApplyBuffEvent(NinjaBuffs.SUITON_BUFF.value, 20000, 1, True)],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

SUITON = Skill(
    skill_id=NinjaSkills.SUITON.value,
    name="SUITON",
    potency=580,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=MUDRA_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=1500,
    delay_millisecond=None,
    cost=[
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value),
    ],
    events=[ApplyBuffEvent(NinjaBuffs.SUITON_BUFF.value, 20000, 1, True)],
    cancel_events=[],
    cooldown_skill_id=NinjaSkills.RAITON.value,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

TENCHIJIN = Skill(
    skill_id=NinjaSkills.TENCHIJIN.value,
    name="TENCHIJIN",
    potency=0,
    max_stacks=1,
    cooldown_millisecond=120000,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value)],
    events=[
        ApplyBuffEvent(NinjaBuffs.TENCHIJIN_BUFF.value, 6000, 1, True),
        ApplyBuffEvent(NinjaBuffs.TCJ_FUMA_BUFF.value, 6000, 1, True),
        ApplyBuffEvent(NinjaBuffs.TENRI_JINDO_READY.value, 30000, 1, True),
    ],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)


TENRI_JINDO = Skill(
    skill_id=NinjaSkills.TENRI_JINDO.value,
    name="TENRI JINDO",
    potency=1100,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value),
        UseBuff(NinjaBuffs.TENRI_JINDO_READY.value),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

ZESHO_MEPPO = Skill(
    skill_id=NinjaSkills.ZESHO_MEPPO.value,
    name="ZESHO MEPPO",
    potency=700,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=0,
    cast_time_millisecond=0,
    charge_time_millisecond=0,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.HIGI_BUFF.value),
        UseResource(NinjaResources.NINKI.value, 50),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
    ],
    events=[],
    cancel_events=[],
    cooldown_skill_id=None,
    is_gcd=False,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)

FUMA_SHURIKEN = Skill(
    skill_id=NinjaSkills.FUMA_SHURIKEN.value,
    name="FUMA SHURIKEN",
    potency=500,
    max_stacks=1,
    cooldown_millisecond=0,
    gcd_cooldown_millisecond=MUDRA_GCD_MILLISECOND,
    cast_time_millisecond=0,
    charge_time_millisecond=500,
    delay_millisecond=None,
    cost=[
        UseBuff(NinjaBuffs.HIGI_BUFF.value),
        UseResource(NinjaResources.NINKI.value, 50),
        DoesNotHaveBuff(NinjaBuffs.TENCHIJIN_BUFF.value),
        DoesNotHaveBuff(NinjaBuffs.KASSATSU_BUFF.value),
    ],
    events=[],
    cancel_events=[],
    cooldown_skill_id=NinjaSkills.RAITON.value,
    is_gcd=True,
    combo_potency=None,
    next_combo=None,
    required_combo=None,
    bonus_potency_if_resource=None,
    is_combo=False,
    proc_events=None,
)


BUNSHIN_BUFF = Buff(
    id=NinjaBuffs.BUNSHIN_BUFF.value,
    name="BUNSHIN BUFF",
    max_duration_millisecond=30000,
    max_stacks=5,
    damage_buff_percent=0,
    activate_skill_ids=[
        NinjaSkills.AEOLIAN_EDGE.value,
        NinjaSkills.ARMOR_CRUSH.value,
        NinjaSkills.SPINNING_EDGE.value,
        NinjaSkills.GUST_SLASH.value,
        NinjaSkills.FLEETING_RAIJU.value,
    ],
    trigger_potency=160,
    trigger_resource_id=NinjaResources.NINKI.value,
    trigger_resource_amount=5,
)

HIGI_BUFF = Buff(
    id=NinjaBuffs.HIGI_BUFF.value,
    name="HIGI BUFF",
    max_duration_millisecond=30000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)


KASSATSU_BUFF = Buff(
    id=NinjaBuffs.KASSATSU_BUFF.value,
    name="KASSATSU BUFF",
    max_duration_millisecond=15000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

MEISUI_BUFF = Buff(
    id=NinjaBuffs.MEISUI_BUFF.value,
    name="MEISUI BUFF",
    max_duration_millisecond=20000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=[NinjaSkills.BHAVACAKRA.value, NinjaSkills.ZESHO_MEPPO.value],
    trigger_potency=150,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

MEDICATED_BUFF = Buff(
    id=NinjaBuffs.MEDICATED_BUFF.value,
    name="MEDICATED BUFF",
    max_duration_millisecond=30000,
    max_stacks=1,
    damage_buff_percent=8,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

PHANTOM_KAMAITACHI_READY = Buff(
    id=NinjaBuffs.PHANTOM_KAMAITACHI_READY.value,
    name="PHANTOM KAMAITACHI READY",
    max_duration_millisecond=45000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

RAIJU_READY = Buff(
    id=NinjaBuffs.RAIJU_READY.value,
    name="RAIJU READY",
    max_duration_millisecond=30000,
    max_stacks=5,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

TENCHIJIN_BUFF = Buff(
    id=NinjaBuffs.TENCHIJIN_BUFF.value,
    name="TENCHIJIN BUFF",
    max_duration_millisecond=6000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

TENRI_JINDO_READY = Buff(
    id=NinjaBuffs.TENRI_JINDO_READY.value,
    name="TENRI JINDO READY",
    max_duration_millisecond=30000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

SUITON_BUFF = Buff(
    id=NinjaBuffs.SUITON_BUFF.value,
    name="SUITON BUFF",
    max_duration_millisecond=20000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

TCJ_FUMA_BUFF = Buff(
    id=NinjaBuffs.TCJ_FUMA_BUFF.value,
    name="TCJ FUMA BUFF",
    max_duration_millisecond=6000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

TCJ_RAITON_BUFF = Buff(
    id=NinjaBuffs.TCJ_RAITON_BUFF.value,
    name="TCJ RAITON BUFF",
    max_duration_millisecond=6000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)

TCJ_SUITON_BUFF = Buff(
    id=NinjaBuffs.TCJ_SUITON_BUFF.value,
    name="TCJ SUITON BUFF",
    max_duration_millisecond=6000,
    max_stacks=1,
    damage_buff_percent=0,
    activate_skill_ids=None,
    trigger_potency=None,
    trigger_resource_id=None,
    trigger_resource_amount=None,
)


DOKUMORI_DEBUFF = Debuff(
    id=NinjaDebuffs.DOKUMORI_DEBUFF.value,
    name="DOKUMORI DEBUFF",
    max_duration_millisecond=21000,
    max_stacks=1,
    damage_buff_percent=5,
)

KUNAIS_BANE_DEBUFF = Debuff(
    id=NinjaDebuffs.KUNAIS_BANE_DEBUFF.value,
    name="KUNAIS BANE DEBUFF",
    max_duration_millisecond=16250,
    damage_buff_percent=10,
    max_stacks=1,
)

NINKI = Resource(
    id=NinjaResources.NINKI.value,
    name="NINKI",
    max_stacks=100,
)

SHURIKEN = Resource(
    id=NinjaResources.SHURIKEN.value,
    name="SHURIKEN",
    max_stacks=5,
)


def create_ninja_environment(target_time_millisecond, start_time_millisecond):
    skills = [
        AEOLIAN_EDGE,
        ARMOR_CRUSH,
        BHAVACAKRA,
        BUNSHIN,
        DOKUMORI,
        DREAM_WITHIN_A_DREAM,
        FLEETING_RAIJU,
        TCJ_FUMA_SHURIKEN,
        GUST_SLASH,
        HYOSHO_RANRYU,
        KASSATSU,
        KUNAIS_BANE,
        MEDICATED,
        MEISUI,
        PHANTOM_KAMAITACHI,
        RAITON,
        TCJ_RAITON,
        SPINNING_EDGE,
        TCJ_SUITON,
        SUITON,
        TENCHIJIN,
        TENRI_JINDO,
        ZESHO_MEPPO,
        FUMA_SHURIKEN,
    ]

    assert len(skills) == len(
        NinjaSkills
    ), f"Skills and NinjaSkills mismatch: {len(skills)} != {len(NinjaSkills)}"

    for idx, skill in enumerate(skills):
        assert (
            skill.skill_id == idx + 1
        ), f"Skill ID mismatch: {skill.skill_id} != {idx + 1}, {skill.name}"

    buffs = [
        BUNSHIN_BUFF,
        HIGI_BUFF,
        KASSATSU_BUFF,
        MEISUI_BUFF,
        MEDICATED_BUFF,
        PHANTOM_KAMAITACHI_READY,
        RAIJU_READY,
        TENCHIJIN_BUFF,
        TENRI_JINDO_READY,
        SUITON_BUFF,
        TCJ_FUMA_BUFF,
        TCJ_RAITON_BUFF,
        TCJ_SUITON_BUFF,
    ]

    assert len(buffs) == len(
        NinjaBuffs
    ), f"Buffs and NinjaBuffs mismatch: {len(buffs)} != {len(NinjaBuffs)}"

    for idx, buff in enumerate(buffs):
        assert buff.id == idx, f"Buff ID mismatch: {buff.id} != {idx}, {buff.name}"

    debuffs = [DOKUMORI_DEBUFF, KUNAIS_BANE_DEBUFF]

    resources = [NINKI, SHURIKEN]

    job_database = JobDatabase(
        buffs=buffs,
        debuffs=debuffs,
    )

    combat_status = CombatStatus(
        job_database=job_database,
        skills=skills,
        resources=resources,
        target_time_millisecond=target_time_millisecond,
        start_time_millisecond=start_time_millisecond,
    )

    return combat_status
