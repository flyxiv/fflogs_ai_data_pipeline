from .status_event import AddResourceEvent

class Buff:
    def __init__(self, id: int, name: str, max_duration_millisecond: int, max_stacks: int, damage_buff_percent, activate_skill_ids: list[int], trigger_potency: int, trigger_resource_id=None, trigger_resource_amount=None):
        self.id = id
        self.name = name
        self.max_duration_millisecond = max_duration_millisecond
        self.max_stacks = max_stacks
        self.current_duration_millisecond = 0
        self.current_stacks = 0
        self.damage_buff_percent = damage_buff_percent
        self.activate_skill_ids = activate_skill_ids
        self.trigger_potency = trigger_potency
        self.trigger_resource_id = trigger_resource_id
        self.trigger_resource_amount = trigger_resource_amount
    
    def apply_trigger(self, buff_table, skill_id: int):
        if self.activate_skill_ids and skill_id in self.activate_skill_ids:
            self.use_stack(buff_table, 1)

            if self.trigger_resource_id is not None:
                return self.trigger_potency, [AddResourceEvent(self.trigger_resource_id, self.trigger_resource_amount, None)]
            else:
                return self.trigger_potency, []

    def get_damage_increase(self):
        if self.damage_buff_percent:
            return 1 + self.damage_buff_percent / 100
        else:
            return 1

    def add_stack(self, stack: int, refresh_duration: bool = False):
        self.current_stacks = min(self.max_stacks, self.current_stacks + stack)
        if self.current_stacks > self.max_stacks:
            self.current_stacks = self.max_stacks

    
    def use_stack(self, buff_table, stack: int):
        self.current_stacks = max(0, self.current_stacks - stack)

        if self.current_stacks == 0:
            buff_table[self.id] = None


    def advance_time(self, buff_table, delta_time_millisecond: int):
        self.current_duration_millisecond = max(0, self.current_duration_millisecond - delta_time_millisecond)

        if self.current_duration_millisecond == 0:
            buff_table[self.id] = None


    def get_state(self):
        return [self.current_duration_millisecond / self.max_duration_millisecond, self.current_stacks / self.max_stacks]

    def __str__(self):
        return f"Buff({self.name}, {self.current_duration_millisecond}, {self.current_stacks})"

    def __repr__(self):
        return self.__str__()
