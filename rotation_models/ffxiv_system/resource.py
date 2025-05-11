from dataclasses import dataclass

class Resource:
    """Abstraction for stacks needed for skills in jobs, such as Ninki and Shuriken.
    """

    def __init__(self, id: int, name: str, max_stacks: int, start_with_full_stacks: bool = False, regen_time_millisecond: int = None):
        self.id = id
        self.name = name
        self.max_stacks = max_stacks

        if start_with_full_stacks:
            self.current_stacks = self.max_stacks
        else:
            self.current_stacks = 0

        self.regen_time_millisecond = regen_time_millisecond
        self.current_regen_time_millisecond = 0

    def add_resource(self, amount: int):
        self.current_stacks = min(self.max_stacks, self.current_stacks + amount)

    def use_resource(self, amount: int):
        self.current_stacks = max(0, self.current_stacks - amount)

    def advance_time(self, delta_time_millisecond: int):
        if self.regen_time_millisecond:
            self.current_regen_time_millisecond -= delta_time_millisecond

            if self.current_regen_time_millisecond <= 0:
                self.current_stacks = min(self.max_stacks, self.current_stacks + 1)
                self.current_regen_time_millisecond += self.regen_time_millisecond

    def get_state(self):
        stacks_state = [self.current_stacks / self.max_stacks]
        if self.regen_time_millisecond:
            stacks_state.append(self.current_regen_time_millisecond / self.regen_time_millisecond)

        return stacks_state

