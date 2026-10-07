"""PawPal+ core classes.

Skeleton generated from diagrams/uml.mmd. Attributes and method signatures
only -- the scheduling logic is implemented in later steps.
"""

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class Priority(Enum):
    """How important a care item is when time runs short."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def rank(self) -> int:
        """Sortable number for this priority (lower sorts first)."""
        return {"high": 0, "medium": 1, "low": 2}[self.value]


class TimeOfDay(Enum):
    """Preferred part of the day for a flexible task."""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANY = "any"


@dataclass
class TimeWindow:
    """A span of clock time the owner has free."""

    start: time
    end: time

    def minutes(self) -> int:
        """Length of this window in minutes."""
        raise NotImplementedError

    def overlaps(self, other: "TimeWindow") -> bool:
        """True if this window shares any minute with `other`."""
        raise NotImplementedError

    def contains(self, start: time, duration_minutes: int) -> bool:
        """True if a task of `duration_minutes` starting at `start` fits inside."""
        raise NotImplementedError


@dataclass
class CareItem:
    """Base class for anything that takes up time in the day."""

    title: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    completed: bool = False

    def mark_complete(self) -> None:
        """Record that this item has been taken care of today."""
        self.completed = True

    def is_fixed(self) -> bool:
        """True if the start time cannot be moved by the scheduler."""
        raise NotImplementedError

    def earliest_start(self) -> time | None:
        """Earliest time this item may start, or None if fully flexible."""
        raise NotImplementedError


@dataclass
class CareTask(CareItem):
    """A flexible task: walk, feeding, water, meds, enrichment."""

    preferred_time: TimeOfDay = TimeOfDay.ANY
    recurring_daily: bool = True

    def is_fixed(self) -> bool:
        """False -- the scheduler is free to move a care task around the day."""
        return False

    def fits_in(self, window: TimeWindow) -> bool:
        """True if this task could be placed somewhere in `window`."""
        raise NotImplementedError


@dataclass
class Appointment(CareItem):
    """A booked commitment with a locked start time: grooming, vet check-in."""

    start_time: time | None = None
    location: str = ""

    def is_fixed(self) -> bool:
        """True -- an appointment is booked, so its start time cannot move."""
        raise NotImplementedError

    def to_window(self) -> TimeWindow:
        """The window this appointment occupies, from start_time + duration."""
        raise NotImplementedError


@dataclass
class Pet:
    """One animal, with the care it needs."""

    name: str
    species: str
    tasks: list[CareTask] = field(default_factory=list)
    appointments: list[Appointment] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Attach a flexible care task to this pet."""
        self.tasks.append(task)

    def add_appointment(self, appointment: Appointment) -> None:
        """Attach a fixed-time appointment to this pet."""
        self.appointments.append(appointment)

    def items(self) -> list[CareItem]:
        """All tasks and appointments for this pet, in one list."""
        return [*self.tasks, *self.appointments]


@dataclass
class Owner:
    """The person doing the care, and the time they have to do it."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_windows: list[TimeWindow] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_items(self) -> list[CareItem]:
        """Every care item across every pet this owner has."""
        return [item for pet in self.pets for item in pet.items()]

    def total_available_minutes(self) -> int:
        """Sum of all available windows, the hard cap on what can be scheduled."""
        raise NotImplementedError


@dataclass
class ScheduledItem:
    """One care item placed at a concrete time, for one pet."""

    pet: Pet
    item: CareItem
    start: time
    end: time
    reason: str = ""

    def conflicts_with(self, other: "ScheduledItem") -> bool:
        """True if these two entries overlap in time (even across pets)."""
        raise NotImplementedError


@dataclass
class DailySchedule:
    """One day's plan for an owner, covering all of their pets."""

    day: date
    entries: list[ScheduledItem] = field(default_factory=list)
    skipped: list[CareItem] = field(default_factory=list)

    def add(self, entry: ScheduledItem) -> bool:
        """Add `entry` if it does not conflict. Returns whether it was added."""
        raise NotImplementedError

    def has_conflict(self, entry: ScheduledItem) -> bool:
        """True if `entry` overlaps anything already scheduled."""
        raise NotImplementedError

    def minutes_used(self) -> int:
        """Total scheduled minutes across all entries."""
        raise NotImplementedError

    def explain(self) -> str:
        """Human-readable account of what was scheduled, when, and why."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Builds a conflict-free daily plan from an owner's pets and free time."""

    owner: Owner
    windows: list[TimeWindow] = field(default_factory=list)

    def build_day(self, day: date) -> DailySchedule:
        """Produce the full plan for `day`: appointments first, then tasks."""
        raise NotImplementedError

    def place_appointments(self, schedule: DailySchedule) -> None:
        """Lock fixed-time appointments into `schedule` before anything else."""
        raise NotImplementedError

    def place_tasks(self, schedule: DailySchedule) -> None:
        """Fill remaining free time with flexible tasks, highest priority first."""
        raise NotImplementedError

    def sort_by_priority(self, items: list[CareItem]) -> list[CareItem]:
        """Order items so the most important ones are placed first."""
        raise NotImplementedError

    def next_free_slot(self, duration_minutes: int, window: TimeWindow) -> time | None:
        """Earliest unused start time in `window` that fits, or None."""
        raise NotImplementedError
