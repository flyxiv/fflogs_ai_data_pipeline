class Debuff:
    """Debuff applied to the target

    Currently the environment only considers single player and single target, so the debuff will be saved on the player.
    Later when we add buff jobs we need to add snapshotting to the debuff, so it is considered a different entity than buff.
    """

    def __init__(
        self,
        id: int,
        name: str,
        max_duration_millisecond: int,
        max_stacks: int,
        damage_buff_percent: int,
    ):
        # metadata
        self.id = id
        self.name = name

        # state max values
        self.max_duration_millisecond = max_duration_millisecond
        self.max_stacks = max_stacks

        # actual state values
        self.current_duration_millisecond = 0
        self.current_stacks = 0

        # damage buff
        self.damage_buff_percent = damage_buff_percent

    def get_damage_increase(self):
        if self.damage_buff_percent:
            return 1 + self.damage_buff_percent / 100
        else:
            return 1

    def add_stack(self, stack: int, refresh_duration: bool = False):
        self.current_stacks = min(self.max_stacks, self.current_stacks + stack)
        if self.current_stacks > self.max_stacks:
            self.current_stacks = self.max_stacks

    def use_stack(self, debuff_table, stack: int):
        self.current_stacks = max(0, self.current_stacks - stack)

        if self.current_stacks == 0:
            debuff_table[self.id] = None

    def advance_time(self, debuff_table, delta_time_millisecond: int):
        self.current_duration_millisecond = max(
            0, self.current_duration_millisecond - delta_time_millisecond
        )

        if self.current_duration_millisecond == 0:
            debuff_table[self.id] = None

    def get_state(self):
        return [
            self.current_duration_millisecond / self.max_duration_millisecond,
            self.current_stacks / self.max_stacks,
        ]

    def __str__(self):
        return f"Debuff({self.name}, {self.current_duration_millisecond}, {self.current_stacks})"

    def __repr__(self):
        return self.__str__()
