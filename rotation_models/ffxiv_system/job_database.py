from typing import List
from copy import deepcopy
from .buff import Buff
from .debuff import Debuff

class JobDatabase:
    """Stores skills, buffs, debuffs and stacks for a job.
    """

    def __init__(self, buffs: List[Buff], debuffs: List[Debuff]):
        self.buffs = buffs
        self.debuffs = debuffs

    def create_buff(self, buff_id: int) -> Buff:
        return deepcopy(self.buffs[buff_id])


    def create_debuff(self, debuff_id: int) -> Debuff:
        return deepcopy(self.debuffs[debuff_id])