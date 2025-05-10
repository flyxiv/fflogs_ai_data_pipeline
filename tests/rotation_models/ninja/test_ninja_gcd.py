import unittest
import math
from rotation_models.ninja.ninja_environment import NinjaEnvironment
from rotation_models.ninja.ninja_combat_data import NinjaSkills, NinjaStacks, NinjaStatus, MAX_COOLDOWN_MILLISECOND
from rotation_models.const import MAX_POTENCY, DEFAULT_DELAY_MILLISECOND


class NinjaGCDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ninja_environment = NinjaEnvironment(100000)
    
    def test_ninja_at_combo0(self):
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.SPINNING_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 5
        assert self.ninja_environment.resources.combo == 1


        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert potency == 240, f"potency should be 240, but it is {potency}"
        assert self.ninja_environment.resources.combo == 0


        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 280, f"potency should be 280, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 0
        assert self.ninja_environment.resources.combo == 0


        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.ARMOR_CRUSH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert self.ninja_environment.resources.combo == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 0


        # if combo is 0 but has shuriken, aeolian edge should use the shuriken for 100 additional potency
        self.ninja_environment.reset()
        self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] = 1
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 380, f"potency should be 380, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value]}"


    def test_ninja_at_combo1(self):
        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 1
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.SPINNING_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 5
        assert self.ninja_environment.resources.combo == 1


        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 1
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 5
        assert potency == 400, f"potency should be 400, but it is {potency}"
        assert self.ninja_environment.resources.combo == 2


        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 1
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 280, f"potency should be 280, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 0
        assert self.ninja_environment.resources.combo == 0


        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 1
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.ARMOR_CRUSH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert self.ninja_environment.resources.combo == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 0


        # if combo is 1 but has shuriken, aeolian edge should use the shuriken for 100 additional potency
        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 1
        self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 380, f"potency should be 380, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 1


    def test_ninja_at_combo2(self):
        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.SPINNING_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 5
        assert self.ninja_environment.resources.combo == 1


        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 0
        assert potency == 240, f"potency should be 240, but it is {potency}"
        assert self.ninja_environment.resources.combo == 0


        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 460, f"potency should be 460, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 15
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 0
        assert self.ninja_environment.resources.combo == 0


        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.ARMOR_CRUSH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 500, f"potency should be 500, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 15
        assert self.ninja_environment.resources.combo == 0
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 2


        # if combo is 2 but has shuriken, aeolian edge should use the shuriken for 100 additional potency
        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 2
        self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 560, f"potency should be 560, but it is {potency}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 15
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 1

    def test_ninja_stack_overcap(self):
        # 1. Spinning Edge @ 100 Ninki, still 100
        self.ninja_environment.reset()
        self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] = 100
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.SPINNING_EDGE.value)

        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 100


        # 2. Armor Crush @ 100 Ninki and 4 shuriken, still 100 and only 5 shuriken
        self.ninja_environment.reset()
        self.ninja_environment.resources.combo = 2
        self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] = 100
        self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] = 4
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.ARMOR_CRUSH.value)

        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 100
        assert self.ninja_environment.resources.stacks[NinjaStacks.SHURIKEN.value] == 5
    
    def test_ninja_bunshin(self):
        self.ninja_environment.reset()
        self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] = 100
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.BUNSHIN.value)

        assert self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value] == [30000 - DEFAULT_DELAY_MILLISECOND, 5], f"status should be [{30000 - DEFAULT_DELAY_MILLISECOND}, 5], but it is {self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value]}"
        assert self.ninja_environment.resources.cooldowns[NinjaSkills.BUNSHIN.value] == 90000 - DEFAULT_DELAY_MILLISECOND, f"cooldown should be {90000 - DEFAULT_DELAY_MILLISECOND}, but it is {self.ninja_environment.resources.cooldowns[NinjaSkills.BUNSHIN.value]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 50, f"ninki should be 50, but it is {self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value]}"
        assert reward == 0, f"reward should be 0, but it is {reward}"

        self.ninja_environment.resources.combo = 2
        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 70 
        assert self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] == 4, f"bunshin should be 4, but it is {self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1]}"

        # 460 + bunshin potency 160 = 620
        assert potency == 620, f"potency should be 620, but it is {potency}"

        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.RAITON.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 740, f"potency should be 740, but it is {potency}"
        assert self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value] == [29000 - DEFAULT_DELAY_MILLISECOND, 1], f"status should be [{29000 - DEFAULT_DELAY_MILLISECOND}, 1], but it is {self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 70
        assert self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] == 4, f"bunshin should be 4, but it is {self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1]}"

        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.RAITON.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 740, f"potency should be 740, but it is {potency}"
        assert self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value][1] == 2, f"raiju stack must be 2, but it is {self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value][1]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 70
        assert self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] == 4, f"bunshin should be 4, but it is {self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1]}"

        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.FLEETING_RAIJU.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 860, f"potency should be 860, but it is {potency}"
        assert self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value][1] == 1, f"raiju stack must be 1, but it is {self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value][1]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 80, f"ninki should be 80, but it is {self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value]}"
        assert self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] == 3, f"bunshin should be 3, but it is {self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1]}"

        _, _, _, reward, _ = self.ninja_environment.step(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 400, f"potency should be 400, but it is {potency}"
        assert self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value] == None, f"raiju stack must be None, but it is {self.ninja_environment.resources.status[NinjaStatus.RAIJU_READY.value]}"
        assert self.ninja_environment.resources.stacks[NinjaStacks.NINKI.value] == 85
        assert self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1] == 2, f"bunshin should be 2, but it is {self.ninja_environment.resources.status[NinjaStatus.BUNSHIN_STATUS.value][1]}"


if __name__ == '__main__':
    unittest.main()

