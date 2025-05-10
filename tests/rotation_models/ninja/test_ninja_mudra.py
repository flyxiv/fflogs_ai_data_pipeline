import unittest
import math
from rotation_models.ninja.ninja_environment import NinjaEnvironment
from rotation_models.ninja.ninja_combat_data import NinjaSkills, NinjaStacks, NinjaStatus, NinjaDebuffs, MAX_COOLDOWN_MILLISECOND
from rotation_models.const import MAX_POTENCY, DEFAULT_DELAY_MILLISECOND

class NinjaMudraTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ninja_environment = NinjaEnvironment(100000)

    def test_ninja_suiton_kunais_bane_hyosho(self):
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.SUITON.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 580, f"potency should be 580, but it is {potency}"
        assert self.ninja_environment.resources.status[NinjaStatus.SUITON_STATUS.value][1] == 1, f"suiton stack should be 1, but it is {self.ninja_environment.resources.status[NinjaStatus.SUITON_STATUS.value][1]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.MUDRA.value] == 1, f"mudra should be 1, but it is {self.ninja_environment.resources.stacks[NinjaStacks.MUDRA.value]}"


        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.KUNAIS_BANE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 600, f"potency should be 600, but it is {potency}"
        assert self.ninja_environment.resources.status[NinjaStatus.SUITON_STATUS.value] == None
        assert self.ninja_environment.resources.stacks[NinjaStacks.MUDRA.value] == 1, f"mudra should be 1, but it is {self.ninja_environment.resources.stacks[NinjaStacks.MUDRA.value]}"
        assert self.ninja_environment.resources.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value] == [15550, 1], f"debuff should be [15550, 1], but it is {self.ninja_environment.resources.debuffs[NinjaDebuffs.KUNAIS_BANE_DEBUFF.value]}"


        # kunai's bane debuff is a 10% potency increase, so 300 * 1.1 = 330
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.DOKUMORI.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 330, f"potency should be 330, but it is {potency}"
        assert self.ninja_environment.resources.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value] == [20300, 1], f"debuff should be [20300, 1], but it is {self.ninja_environment.resources.debuffs[NinjaDebuffs.DOKUMORI_DEBUFF.value]}"


        # kunai's bane 10% buff and dokumori 5% buff, so 540 * 1.1 * 1.05 = 624
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.DREAM_WITHIN_A_DREAM.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 624, f"potency should be 624, but it is {potency}"
        
        self.ninja_environment.step(NinjaSkills.KASSATSU.value)
        assert self.ninja_environment.resources.status[NinjaStatus.KASSATSU_STATUS.value] == [14300, 1], f"kassatsu should be [14300, 1], but it is {self.ninja_environment.resources.status[NinjaStatus.KASSATSU_STATUS.value]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.MUDRA.value] == 1

        # kunai's bane 10% buff and dokumori 5% buff and kassatsu 30% buff, so 1300 * 1.1 * 1.05 * 1.3 = 1952 
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.HYOSHO_RANRYU.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 1952, f"potency should be 1952, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.MUDRA.value] == 1
        assert self.ninja_environment.resources.status[NinjaStatus.KASSATSU_STATUS.value] == None

if __name__ == '__main__':
    unittest.main()

