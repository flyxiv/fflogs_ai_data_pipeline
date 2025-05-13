from enum import Enum
from abc import abstractmethod


class StatusEvent:
    """Implements interface for status change events that happen from skill usage

    Some events consist of: 
    1) Add more resource of a specific resource
    2) Apply a buff to the player
    3) Apply a debuff to the target

    StatusEvents handle "acquirements" that happen from skill usage. The reduction of resources usually
    acts as a "constraint" condition of whether the skill is usable, so those events are handled by the "cost" entities.
    """

    @abstractmethod
    def handle_event(self, combat_status):
        pass


class AddResourceEvent(StatusEvent):
    """Only add combos when the current combo matches the conditional combo id
    
    ex) Aeolian Edge doesn't generate ninki when combo != 2 
    """
    def __init__(self, resource_id: int, amount: int, combo):
        self.resource_id = resource_id
        self.amount = amount
        self.combo = combo

    def handle_event(self, combat_status):
        if self.combo:
            if combat_status.combo == self.combo:
                combat_status.resources[self.resource_id].add_resource(self.amount)
        else:
            combat_status.resources[self.resource_id].add_resource(self.amount)


class ApplyBuffEvent(StatusEvent):
    def __init__(
        self,
        buff_id: int,
        duration_millisecond: int,
        stacks=1,
        refresh_duration: bool = False,
    ):
        self.buff_id = buff_id
        self.stacks = stacks
        self.duration_millisecond = duration_millisecond
        self.refresh_duration = refresh_duration

    def handle_event(self, combat_status):
        if combat_status.buffs[self.buff_id]:
            if self.refresh_duration:
                combat_status.buffs[self.buff_id].duration_millisecond = (
                    self.duration_millisecond
                )

            combat_status.buffs[self.buff_id].add_stack(self.stacks)
        else:
            buff = combat_status.job_database.create_buff(self.buff_id)
            buff.current_stacks = self.stacks
            buff.current_duration_millisecond = self.duration_millisecond
            combat_status.buffs[self.buff_id] = buff


class ApplyDebuffEvent(StatusEvent):
    def __init__(
        self,
        debuff_id: int,
        duration_millisecond: int,
        stacks=1,
        refresh_duration: bool = False,
    ):
        self.debuff_id = debuff_id
        self.stacks = stacks
        self.duration_millisecond = duration_millisecond
        self.refresh_duration = refresh_duration

    def handle_event(self, combat_status):
        if combat_status.debuffs[self.debuff_id]:
            if self.refresh_duration:
                combat_status.debuffs[self.debuff_id].duration_millisecond = (
                    self.duration_millisecond
                )

            combat_status.debuffs[self.debuff_id].add_stack(self.stacks)
        else:
            debuff = combat_status.job_database.create_debuff(self.debuff_id)
            debuff.current_stacks = self.stacks
            debuff.current_duration_millisecond = self.duration_millisecond
            combat_status.debuffs[self.debuff_id] = debuff
