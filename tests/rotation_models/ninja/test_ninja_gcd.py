import unittest
import math
from rotation_models.ninja.ninja_combat_data import NinjaSkills, NinjaResources, NinjaBuffs, create_ninja_environment
from rotation_models.const import MAX_POTENCY, DEFAULT_DELAY_MILLISECOND


class NinjaGCDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ninja_environment = create_ninja_environment(100000)
    
    def test_ninja_at_combo0(self):
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.SPINNING_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 5, f"ninki should be 5, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.combo == 1, f"combo should be 1, but it is {self.ninja_environment.combo}"


        # Gush Slash should give weak potency when combo is 0
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0
        assert potency == 240, f"potency should be 240, but it is {potency}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Aeolian Edge should give weak potency when combo is 0
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 280, f"potency should be 280, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Armor Crush should give weak potency when combo is 0
        self.ninja_environment.reset()
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.ARMOR_CRUSH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Bonus Test:
        # if combo is 0 but ninja has a shuriken stack, aeolian edge should use the shuriken for 100 additional potency
        self.ninja_environment.reset()
        self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks = 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 380, f"potency should be 380, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"


    def test_ninja_at_combo1(self):
        self.ninja_environment.reset()
        self.ninja_environment.combo = 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.SPINNING_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 5
        assert self.ninja_environment.combo == 1


        # Gush Slash should give full potency and generate ninki when combo is 1
        self.ninja_environment.reset()
        self.ninja_environment.combo = 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 5, f"ninki should be 5, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert potency == 400, f"potency should be 400, but it is {potency}"
        assert self.ninja_environment.combo == 2, f"combo should be 2, but it is {self.ninja_environment.combo}"


        # Aeolian Edge should give weak potency when combo is 1
        self.ninja_environment.reset()
        self.ninja_environment.combo = 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 280, f"potency should be 280, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Armor Crush should give weak potency when combo is 1
        self.ninja_environment.reset()
        self.ninja_environment.combo = 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.ARMOR_CRUSH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Bonus Test:
        # if combo is 1 but ninja has a shuriken stack, aeolian edge should use the shuriken for 100 additional potency
        self.ninja_environment.reset()
        self.ninja_environment.combo = 1
        self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 380, f"potency should be 380, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 1, f"shuriken should be 1, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"


    def test_ninja_at_combo2(self):
        self.ninja_environment.reset()
        self.ninja_environment.combo = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.SPINNING_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 300, f"potency should be 300, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 5, f"ninki should be 5, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.combo == 1, f"combo should be 1, but it is {self.ninja_environment.combo}"


        # Gush Slash should give weak potency when combo is 2
        self.ninja_environment.reset()
        self.ninja_environment.combo = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 240, f"potency should be 240, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 0, f"ninki should be 0, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Aeolian Edge should give full potency and generate ninki when combo is 2
        self.ninja_environment.reset()
        self.ninja_environment.combo = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 460, f"potency should be 460, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 15, f"ninki should be 15, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 0, f"shuriken should be 0, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"


        # Armor Crush should give full potency and generate ninki when combo is 2 
        self.ninja_environment.reset()
        self.ninja_environment.combo = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.ARMOR_CRUSH.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 500, f"potency should be 500, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 15, f"ninki should be 15, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.combo == 0, f"combo should be 0, but it is {self.ninja_environment.combo}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 2, f"shuriken should be 2, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"


        # if combo is 2 and ninja has shuriken, aeolian edge should use the shuriken for 100 additional potency
        self.ninja_environment.reset()
        self.ninja_environment.combo = 2
        self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        assert potency == 560, f"potency should be 560, but it is {potency}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 15, f"ninki should be 15, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 1, f"shuriken should be 1, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"

    def test_ninja_stack_overcap(self):
        # 1. Spinning Edge @ 100 Ninki, still 100
        self.ninja_environment.reset()
        self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks = 100
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.SPINNING_EDGE.value)

        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 100, f"ninki should be 100, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"


        # 2. Armor Crush @ 100 Ninki and 4 shuriken, ninki is 100 and only 5 shuriken
        self.ninja_environment.reset()
        self.ninja_environment.combo = 2
        self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks = 100
        self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks = 4
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.ARMOR_CRUSH.value)

        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 100, f"ninki should be 100, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks == 5, f"shuriken should be 5, but it is {self.ninja_environment.resources[NinjaResources.SHURIKEN.value].current_stacks}"
    
    def test_ninja_bunshin(self):

        # start with 100 ninki and use bunshin: 50 ninki, 5 bunshin stacks
        self.ninja_environment.reset()
        self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks = 100
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.BUNSHIN.value)

        bunshin_status = self.ninja_environment.buffs[NinjaBuffs.BUNSHIN_BUFF.value]
        bunshin_state = [bunshin_status.current_duration_millisecond, bunshin_status.current_stacks]
        bunshin_cooldown = self.ninja_environment.skills[NinjaSkills.BUNSHIN.value - 1].current_cooldown_millisecond
        assert bunshin_state == [30000 - DEFAULT_DELAY_MILLISECOND, 5], f"status should be [{30000 - DEFAULT_DELAY_MILLISECOND}, 5], but it is {bunshin_state}"
        assert bunshin_cooldown == 90000 - DEFAULT_DELAY_MILLISECOND, f"cooldown should be {90000 - DEFAULT_DELAY_MILLISECOND}, but it is {bunshin_cooldown}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 50, f"ninki should be 50, but it is {self.ninja_environment.resources[NinjaStacks.NINKI.value].current_stacks}"
        assert reward == 0, f"reward should be 0, but it is {reward}"

        # use aeolian edge: generates 15 + 5 = 20 ninki (50 + 20 = 70 total), 4 bunshin stacks
        self.ninja_environment.combo = 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.AEOLIAN_EDGE.value)
        potency = int(round(reward * MAX_POTENCY))

        bunshin_status = self.ninja_environment.buffs[NinjaBuffs.BUNSHIN_BUFF.value]
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 70, f"ninki should be 70, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert bunshin_status.current_stacks == 4, f"bunshin should be 4, but it is {bunshin_state.current_stacks}"

        # 460 + bunshin potency 160 = 620
        assert potency == 620, f"potency should be 620, but it is {potency}"


        # Use Raiton: still 70 ninki, 4 bunshin stacks, raiju_ready must be stacked to 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.RAITON.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 740, f"potency should be 740, but it is {potency}"

        raiju_status = self.ninja_environment.buffs[NinjaBuffs.RAIJU_READY.value]
        raiju_state = [raiju_status.current_duration_millisecond, raiju_status.current_stacks]
        bunshin_status = self.ninja_environment.buffs[NinjaBuffs.BUNSHIN_BUFF.value]
        assert raiju_state == [30000 - DEFAULT_DELAY_MILLISECOND, 1], f"status should be [{30000 - DEFAULT_DELAY_MILLISECOND}, 1], but it is {raiju_state}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 70, f"ninki should be 70, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert bunshin_status.current_stacks == 4, f"bunshin should be 4, but it is {bunshin_status.current_stacks}"

        # Use Raiton: still 70 ninki, 4 bunshin stacks, raiju_ready must be stacked to 2
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.RAITON.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 740, f"potency should be 740, but it is {potency}"

        raiju_status = self.ninja_environment.buffs[NinjaBuffs.RAIJU_READY.value]
        bunshin_status = self.ninja_environment.buffs[NinjaBuffs.BUNSHIN_BUFF.value]
        assert raiju_status.current_stacks == 2, f"raiju stack must be 2, but it is {raiju_state.current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 70, f"ninki should be 70, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert bunshin_status.current_stacks == 4, f"bunshin should be 4, but it is {bunshin_status.current_stacks}"

        # Use Fleeting Raiju: generate 5 + 5 = 10 ninki(80 ninki total), 3 bunshin stacks, raiju_ready must be stacked to 1
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.FLEETING_RAIJU.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 860, f"potency should be 860, but it is {potency}"

        raiju_status = self.ninja_environment.buffs[NinjaBuffs.RAIJU_READY.value]
        bunshin_status = self.ninja_environment.buffs[NinjaBuffs.BUNSHIN_BUFF.value]
        assert raiju_status.current_stacks == 1, f"raiju stack must be 1, but it is {raiju_status.current_stacks}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 80, f"ninki should be 80, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert bunshin_status.current_stacks == 3, f"bunshin should be 3, but it is {bunshin_status.current_stacks}"


        # Using gust slash while raiju_ready is 1 should destroy the raiju_ready buff
        # generate 5 ninki (total 85), 2 bunshin stacks
        _, _, _, reward, _ = self.ninja_environment.use_skill(NinjaSkills.GUST_SLASH.value)
        potency = int(round(reward * MAX_POTENCY))
        assert potency == 400, f"potency should be 400, but it is {potency}"

        raiju_status = self.ninja_environment.buffs[NinjaBuffs.RAIJU_READY.value]
        bunshin_status = self.ninja_environment.buffs[NinjaBuffs.BUNSHIN_BUFF.value]
        assert raiju_status is None, f"raiju stack must be None, but it is {raiju_status}"
        assert self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks == 85, f"ninki should be 85, but it is {self.ninja_environment.resources[NinjaResources.NINKI.value].current_stacks}"
        assert bunshin_status.current_stacks == 2, f"bunshin should be 2, but it is {bunshin_status.current_stacks}"


if __name__ == '__main__':
    unittest.main()

