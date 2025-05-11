from abc import abstractmethod
from .combat_status import CombatStatus

class Cost:
    def __init__(self, buff_id: int, stacks: int):
        self.buff_id = buff_id
        self.stacks = stacks

    @abstractmethod
    def use(self, combat_status: CombatStatus):
        pass

    @abstractmethod
    def has_cost(self, combat_status: CombatStatus):
        pass

class CheckBuff(Cost):
    def __init__(self, buff_id: int):
        self.buff_id = buff_id

    def has_cost(self, combat_status: CombatStatus):
        return combat_status.buffs[self.buff_id] 
    
    def use(self, combat_status: CombatStatus):
        pass


class UseResource(Cost):
    def __init__(self, resource_id: int, amount: int):
        self.resource_id = resource_id
        self.amount = amount

    def has_cost(self, combat_status: CombatStatus):
        return combat_status.resources[self.resource_id].current_stacks >= self.amount

    def use(self, combat_status: CombatStatus):
        combat_status.resources[self.resource_id].current_stacks -= max(0, self.amount)


class UseBuff(Cost):
    def __init__(self, buff_id: int):
        self.buff_id = buff_id

    def has_cost(self, combat_status: CombatStatus):
        return combat_status.buffs[self.buff_id] and combat_status.buffs[self.buff_id].current_stacks >= 1 

    def use(self, combat_status: CombatStatus):
        if combat_status.buffs[self.buff_id]:
            combat_status.buffs[self.buff_id].current_stacks -= 1

            if combat_status.buffs[self.buff_id].current_stacks == 0:
                combat_status.buffs[self.buff_id] = None

    
class UseDebuff(Cost):
    def __init__(self, debuff_id: int):
        self.debuff_id = debuff_id
        
    def has_cost(self, combat_status: CombatStatus):
        return combat_status.debuffs[self.debuff_id] and combat_status.debuffs[self.debuff_id].current_stacks >= 1 

    def use(self, combat_status: CombatStatus):
        if combat_status.debuffs[self.debuff_id]:
            combat_status.debuffs[self.debuff_id].current_stacks -= 1

            if combat_status.debuffs[self.debuff_id].current_stacks == 0:
                combat_status.debuffs[self.debuff_id] = None


class UseAllBuff(Cost):
    def __init__(self, buff_id: int):
        self.buff_id = buff_id

    def has_cost(self, combat_status: CombatStatus):
        return True 

    def use(self, combat_status: CombatStatus):
        combat_status.buffs[self.buff_id] = None


class UseAllDebuff(Cost):
    def __init__(self, debuff_id: int):
        self.debuff_id = debuff_id

    def has_cost(self, combat_status: CombatStatus):
        return True 

    def use(self, combat_status: CombatStatus):
        combat_status.debuffs[self.debuff_id] = None

class DoesNotHaveBuff(Cost):
    def __init__(self, buff_id: int):
        self.buff_id = buff_id

    def has_cost(self, combat_status: CombatStatus):
        return not combat_status.buffs[self.buff_id]
    
    def use(self, combat_status: CombatStatus):
        pass

