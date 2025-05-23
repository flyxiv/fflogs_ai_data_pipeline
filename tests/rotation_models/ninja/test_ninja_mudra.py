import unittest
import math
from rotation_models.ninja.ninja_combat_data import NinjaSkills, NinjaResources, NinjaBuffs, NinjaDebuffs, create_ninja_environment
from rotation_models.const import MAX_POTENCY, DEFAULT_DELAY_MILLISECOND

class NinjaMudraTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ninja_environment = create_ninja_environment(100000)

    def test_ninja_suiton_kunais_bane_hyosho(self):
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.SUITON.value)
        potency = int(round(reward * MAX_POTENCY))

        raiton_stacks = self.ninja_environment.skills[NinjaSkills.RAITON.value].stacks
        assert potency == 580, f"potency should be 580, but it is {potency}"
        assert self.ninja_environment.buffs[NinjaBuffs.SUITON_BUFF.value].current_stacks == 1, f"suiton stack should be 1, but it is {self.ninja_environment.buffs[NinjaBuffs.SUITON_BUFF.value].current_stacks}"
        assert raiton_stacks == 1, f"raiton should be 1, but it is {raiton_stacks}"


        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.KUNAIS_BANE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 600, f"potency should be 600, but it is {potency}"

        kunais_bane_debuff = self.ninja_environment.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value]
        kunais_bane_state = [kunais_bane_debuff.current_duration_millisecond, kunais_bane_debuff.current_stacks]
        assert self.ninja_environment.buffs[NinjaBuffs.SUITON_BUFF.value] is None
        assert self.ninja_environment.skills[NinjaSkills.RAITON.value].stacks == 1, f"raiton should be 1, but it is {self.ninja_environment.skills[NinjaSkills.RAITON.value].stacks}"
        assert kunais_bane_state == [15550, 1], f"debuff should be [15550, 1], but it is {kunais_bane_state}"


        # kunai's bane debuff is a 10% potency increase, so 300 * 1.1 = 330
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.DOKUMORI.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 330, f"potency should be 330, but it is {potency}"

        dokumori_debuff = self.ninja_environment.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value]
        dokumori_state = [dokumori_debuff.current_duration_millisecond, dokumori_debuff.current_stacks]
        assert dokumori_state == [20300, 1], f"debuff should be [20300, 1], but it is {dokumori_state}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 40, f"ninki should be 40, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"


        # kunai's bane 10% buff and dokumori 5% buff, so 540 * 1.1 * 1.05 = 624
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.DREAM_WITHIN_A_DREAM.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 624, f"potency should be 624, but it is {potency}"
        

        # use kassatsu
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.KASSATSU.value)
        kassatsu_buff = self.ninja_environment.buffs[NinjaBuffs.KASSATSU_BUFF.value]
        kassatsu_state = [kassatsu_buff.current_duration_millisecond, kassatsu_buff.current_stacks]
        raiton_stacks = self.ninja_environment.skills[NinjaSkills.RAITON.value].stacks
        assert kassatsu_state == [14300, 1], f"kassatsu should be [14300, 1], but it is {kassatsu_state}"
        assert raiton_stacks == 1, f"raiton should be 1, but it is {raiton_stacks}"


        # kunai's bane 10% buff and dokumori 5% buff and kassatsu 30% buff, so 1300 * 1.1 * 1.05 * 1.3 = 1952 
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.HYOSHO_RANRYU.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 1952, f"potency should be 1952, but it is {potency}"

        raiton_stacks = self.ninja_environment.skills[NinjaSkills.RAITON.value].stacks
        assert raiton_stacks == 1, f"raiton should be 1, but it is {raiton_stacks}"
        assert self.ninja_environment.buffs[NinjaBuffs.KASSATSU_BUFF.value] is None

if __name__ == '__main__':
    unittest.main()

