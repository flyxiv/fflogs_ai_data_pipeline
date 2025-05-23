import math
import logging
from .cost import Cost
from .status_event import StatusEvent
from rotation_models.const import DEFAULT_DELAY_MILLISECOND
from dataclasses import dataclass


class ComboData:
    def __init__(self, *, combo_potency: int, next_combo: int, required_combo):
        self.combo_potency = combo_potency
        self.next_combo = next_combo
        self.required_combo = required_combo


@dataclass
class DelayData:
    gcd_cooldown_millisecond: int
    delay_millisecond: int
    charge_time_millisecond: int
    cast_time_millisecond: int


class Skill:
    """Implements skill characteristics for FFXIV Combat Class

    charge_time_millisecond: time it takes to charge the skill - skills like raiton need time to cast mudras. We abstract them out as charge time and add delay time before applying the skill.
    gcd_cooldown_millisecond: cooldown time for skills that are GCD skills
    cast_time_millisecond: time it takes to cast the skill. Used for casting spells 
    delay_millisecond: FFXIV has a default 0.7ms delay after using each skill. However some skills have shorter/longer delays. We automatically advance time by this delay after using the skill, since the character can't do anything during the delay.
    """

    def __init__(
        self,
        *,
        skill_id: int,
        name: str,
        potency: int,
        max_stacks: int,
        gcd_cooldown_millisecond: int,
        cooldown_millisecond: int,
        cast_time_millisecond: int,
        charge_time_millisecond: int,
        delay_millisecond: int,
        cost: list[Cost],
        events: list[StatusEvent],
        cancel_events: list[StatusEvent],
        cooldown_skill_id: int,
        is_gcd: bool,
        combo_potency,
        next_combo,
        required_combo,
        is_combo=False,
        bonus_potency_if_resource=None,
        proc_events=None,
    ):
        self.skill_id = skill_id
        self.name = name
        self.potency = potency
        self.max_stacks = max_stacks
        self.stacks = max_stacks

        self.delay_data = DelayData(
            gcd_cooldown_millisecond=gcd_cooldown_millisecond,
            delay_millisecond=(
                DEFAULT_DELAY_MILLISECOND
                if delay_millisecond is None
                else delay_millisecond
            ),
            cast_time_millisecond=cast_time_millisecond,
            charge_time_millisecond=charge_time_millisecond,
        )

        self.current_cooldown_millisecond = 0
        self.cooldown_millisecond = cooldown_millisecond

        self.cost = cost
        self.events = events
        self.cancel_events = cancel_events

        self.cooldown_skill_id = cooldown_skill_id
        self.is_gcd = is_gcd
        self.bonus_potency_if_resource = bonus_potency_if_resource

        self.combo_data = None
        if is_combo:
            self.combo_data = ComboData(
                combo_potency=combo_potency,
                next_combo=next_combo,
                required_combo=required_combo,
            )

    def start_cooldown(self):
        assert (
            self.stacks > 0
        ), f"start_cooldown called when stack == 0, {self.name}, {self.skill_id}"
        self.stacks -= 1
        self.current_cooldown_millisecond += self.cooldown_millisecond

    def is_valid_action(self, combat_status):
        if self.is_gcd and combat_status.gcd_cooldown_millisecond > 0:
            return False

        if self.cooldown_skill_id:
            cooldown_ready = combat_status.skills[self.cooldown_skill_id - 1].stacks > 0
        else:
            cooldown_ready = self.stacks > 0

        if not cooldown_ready:
            return False

        for cost in self.cost:
            if not cost.has_cost(combat_status):
                return False

        return True

    def _calculate_total_damage_increase(self, combat_status):
        total_damage_increase = 1

        for buff in combat_status.buffs:
            if buff:
                total_damage_increase *= buff.get_damage_increase()

        for debuff in combat_status.debuffs:
            if debuff:
                total_damage_increase *= debuff.get_damage_increase()

        return total_damage_increase

    def _simulate_skill_status_changes(self, combat_status):
        for cost in self.cost:
            cost.use(combat_status)

        for event in self.events:
            event.handle_event(combat_status)

        for cancel_event in self.cancel_events:
            cancel_event.use(combat_status)

    def _calculate_potency_and_combo_update(self, combat_status):
        potency = self.potency

        if self.combo_data:
            if self.combo_data.required_combo:
                if self.combo_data.required_combo == combat_status.combo:
                    potency = self.combo_data.combo_potency
                    combat_status.update_combo(self.combo_data.next_combo)
                else:
                    combat_status.update_combo(0)
            else:
                combat_status.update_combo(self.combo_data.next_combo)

        return potency

    def use_skill(self, combat_status):
        """Simulate all events and triggers and status changes that happen when the skill is used.

        1) Start skill cooldown
        2) Activated trigger buffs
        3) Apply buffs and debuffs damage buff
        4) Advance time if there is charge time
        5) Update status changes
        """
        logging.debug(f"Using {self.name} on {combat_status.combat_time_millisecond}")

        if self.cooldown_skill_id:
            combat_status.skills[self.cooldown_skill_id - 1].start_cooldown()
        else:
            self.start_cooldown()

        combat_status.advance_time(self.delay_data.charge_time_millisecond)

        total_damage_increase = self._calculate_total_damage_increase(combat_status)
        self._simulate_skill_status_changes(combat_status)
        potency = self._calculate_potency_and_combo_update(combat_status)

        for buff in combat_status.buffs:
            if buff:
                triggered = buff.apply_trigger(combat_status.buffs, self.skill_id)

                if triggered:
                    additional_potency, resource_events = triggered
                    potency += additional_potency

                    for resource_event in resource_events:
                        resource_event.handle_event(combat_status)

        if self.bonus_potency_if_resource:
            [resource_id, bonus_potency] = self.bonus_potency_if_resource
            if combat_status.resources[resource_id].current_stacks >= 1:
                potency += bonus_potency
                combat_status.resources[resource_id].current_stacks -= 1

        return potency * total_damage_increase, self.delay_data

    def advance_time(self, delta_time_millisecond: int):
        if self.cooldown_millisecond == 0:
            self.stacks = self.max_stacks
            return

        prev_stack = int(
            math.ceil(self.current_cooldown_millisecond / self.cooldown_millisecond)
        )

        self.current_cooldown_millisecond = max(
            0, self.current_cooldown_millisecond - delta_time_millisecond
        )

        current_stack = int(
            math.ceil(self.current_cooldown_millisecond / self.cooldown_millisecond)
        )

        if prev_stack != current_stack:
            self.stacks += 1

    def get_state(self):
        if self.cooldown_skill_id:
            return list()
        else:
            return [
                self.current_cooldown_millisecond / max(1, self.cooldown_millisecond),
                self.stacks / max(1, self.max_stacks),
            ]
