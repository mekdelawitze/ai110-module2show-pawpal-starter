"""PawPal+ logic layer: Owner, Pet, Task and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

FREQUENCIES = ("once", "daily", "weekly")
PRIORITIES = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM", 24-hour
    frequency: str = "once"  # once | daily | weekly
    due_date: date = field(default_factory=date.today)
    duration_minutes: int = 15
    priority: str = "medium"
    completed: bool = False
    pet_name: str = ""

    def __post_init__(self) -> None:
        """Validate frequency, priority and the HH:MM time format."""
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {FREQUENCIES}")
        if self.priority not in PRIORITIES:
            raise ValueError(f"priority must be one of {tuple(PRIORITIES)}")
        hours, _, minutes = self.time.partition(":")
        if not (hours.isdigit() and minutes.isdigit() and len(minutes) == 2
                and int(hours) < 24 and int(minutes) < 60):
            raise ValueError(f"time must be HH:MM, got {self.time!r}")
        self.time = f"{int(hours):02d}:{minutes}"

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh task for the next daily/weekly occurrence, or None for one-off tasks."""
        step = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}.get(self.frequency)
        if step is None:
            return None
        return Task(self.description, self.time, self.frequency, self.due_date + step,
                    self.duration_minutes, self.priority, False, self.pet_name)


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive), or None."""
        return next((p for p in self.pets if p.name.lower() == name.lower()), None)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain': organizes, filters and checks tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that reads tasks from the given owner."""
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks for every pet via the owner."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks chronologically by due date, then HH:MM time (zero-padded, so string order works)."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Filter tasks by pet name and/or completion status; None means 'don't filter on this'."""
        result = self.get_all_tasks()
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def get_todays_schedule(self, day: Optional[date] = None) -> List[Task]:
        """Return pending tasks due on the given day (default today), sorted by time."""
        day = day or date.today()
        due = [t for t in self.get_all_tasks() if t.due_date == day and not t.completed]
        return self.sort_by_time(due)

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warning messages for pending tasks sharing the same date and time (never raises)."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        slots = {}
        for task in tasks:
            if not task.completed:
                slots.setdefault((task.due_date, task.time), []).append(task)
        warnings = []
        for (day, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in group)
                warnings.append(f"Conflict on {day} at {time}: {names}")
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; for daily/weekly tasks add the next occurrence to the same pet and return it."""
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(follow_up)
        return follow_up
