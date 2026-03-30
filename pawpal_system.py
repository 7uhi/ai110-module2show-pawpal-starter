from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional
import os

import anthropic


class Priority(Enum):
    LOW    = 0
    MEDIUM = 1
    HIGH   = 2


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    frequency: str = "daily"   # "daily", "weekly", "as-needed"
    is_completed: bool = False
    scheduled_time: Optional[int] = None  # minutes from midnight, e.g. 420 = 7:00 AM
    scheduled_date: Optional[date] = None  # which day this instance belongs to

    def __post_init__(self) -> None:
        """Coerce a raw string priority value into a Priority enum on creation."""
        if not isinstance(self.priority, Priority):
            self.priority = Priority[self.priority.upper()]

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and return the next occurrence.

        Returns a new Task for the next day (daily) or next week (weekly),
        or None for as-needed tasks which do not recur automatically.
        """
        self.is_completed = True

        if self.frequency == "as-needed":
            return None

        base = self.scheduled_date or date.today()
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            scheduled_time=self.scheduled_time,
            scheduled_date=base + delta,
        )


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, index: int) -> None:
        """Remove the task at the given index, if the index is valid."""
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)

    def total_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        return sum(task.duration_minutes for task in self.tasks)


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def all_tasks(self) -> List[Task]:
        """Return every task across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


@dataclass
class Scheduler:
    owner: Owner
    plan_text: str = ""
    generated: bool = False

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks across every pet owned by this owner."""
        return self.owner.all_tasks()

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Filter all tasks to only those matching the given priority."""
        return [t for t in self.get_all_tasks() if t.priority == priority]

    def sort_tasks(self) -> List[Task]:
        """Return all tasks sorted high → medium → low priority."""
        return sorted(self.get_all_tasks(), key=lambda t: t.priority.value, reverse=True)

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted by scheduled_time, earliest first.

        Uses a two-element tuple sort key so that tasks with no scheduled_time
        are always placed after tasks that have one:
          - First element (bool): False (0) for timed tasks, True (1) for untimed,
            so timed tasks sort before untimed ones.
          - Second element (int): the actual minute offset, used to order timed
            tasks among themselves; falls back to 0 for untimed tasks (the bool
            already pushed them to the end, so the value doesn't matter).
        """
        tasks = self.get_all_tasks()
        return sorted(tasks, key=lambda t: (t.scheduled_time is None, t.scheduled_time or 0))

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the named pet.

        The name comparison is case-insensitive, so "mochi" and "Mochi" match
        the same pet.  Returns a shallow copy of the pet's task list so the
        caller cannot accidentally mutate the pet's internal state.
        Returns an empty list if no pet with that name is found.
        """
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    def get_incomplete_tasks(self) -> List[Task]:
        """Return all tasks that have not yet been completed."""
        return [t for t in self.get_all_tasks() if not t.is_completed]

    def get_tasks_by_pet_and_status(self, pet_name: str, completed: bool) -> List[Task]:
        """Return tasks for a specific pet filtered by completion status.

        Combines get_tasks_for_pet and an is_completed check in one call:
          - completed=False  →  tasks still pending for that pet
          - completed=True   →  tasks already marked done for that pet

        Returns an empty list if the pet is not found or has no tasks matching
        the requested status.
        """
        return [t for t in self.get_tasks_for_pet(pet_name) if t.is_completed == completed]

    def detect_conflicts(self) -> List[str]:
        """Check for scheduling conflicts and return a list of warning strings.

        A conflict exists when two or more incomplete tasks share the same
        scheduled_time (same pet or different pets).  Tasks with no
        scheduled_time are skipped — they cannot conflict on a specific slot.
        Returns an empty list when no conflicts are found.
        """
        from collections import defaultdict

        slot_map: dict = defaultdict(list)  # {scheduled_time: [(pet_name, task)]}
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.is_completed or task.scheduled_time is None:
                    continue
                slot_map[task.scheduled_time].append((pet.name, task))

        warnings = []
        for time_slot, entries in sorted(slot_map.items()):
            if len(entries) < 2:
                continue
            h, m = divmod(time_slot, 60)
            time_str = f"{h:02d}:{m:02d}"
            conflict_desc = ", ".join(
                f'"{task.title}" ({pet_name})' for pet_name, task in entries
            )
            warnings.append(f"⚠ Conflict at {time_str} — {conflict_desc}")

        return warnings

    def complete_task(self, pet_name: str, task_title: str) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add the next occurrence to the pet.

        Finds the first incomplete task matching pet_name and task_title,
        marks it done, and appends the returned next-occurrence Task to that
        pet's list (daily → tomorrow, weekly → next week, as-needed → nothing).

        Returns the newly created next-occurrence Task, or None.
        """
        for pet in self.owner.pets:
            if pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if task.title.lower() == task_title.lower() and not task.is_completed:
                    next_task = task.mark_complete()
                    if next_task is not None:
                        pet.add_task(next_task)
                    return next_task
        return None

    def _build_prompt(self) -> str:
        """Construct the Claude prompt from owner, pets, and tasks."""
        task_lines = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                task_lines.append(
                    f"- {task.title} ({task.duration_minutes} min, "
                    f"priority: {task.priority.name.lower()}, frequency: {task.frequency}) "
                    f"for {pet.name} the {pet.species}"
                )
        tasks_text = "\n".join(task_lines) if task_lines else "No tasks added."
        pets_summary = ", ".join(f"{p.name} ({p.species})" for p in self.owner.pets)

        return f"""You are a helpful pet care scheduling assistant.

Owner: {self.owner.name}
Pets: {pets_summary}

Tasks to schedule today:
{tasks_text}

Please create a practical daily schedule starting at 7:00 AM.
Order tasks by priority (high first) and logical time of day.
After the schedule, explain briefly why you ordered things this way.

Format your response exactly as:
SCHEDULE:
[time] - [task name] ([duration] min)
...

REASONING:
[your explanation]"""

    def generate(self) -> str:
        """Call the Claude API and store the resulting schedule in plan_text."""
        try:
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": self._build_prompt()}],
            )
            self.plan_text = message.content[0].text
            self.generated = True
        except Exception as e:
            self.plan_text = f"Error generating schedule: {e}"
        return self.plan_text
