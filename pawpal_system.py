from dataclasses import dataclass, field
from enum import Enum
from typing import List
import os

import anthropic


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    frequency: str = "daily"   # "daily", "weekly", "as-needed"
    is_completed: bool = False

    def __post_init__(self) -> None:
        """Coerce a raw string priority value into a Priority enum on creation."""
        if not isinstance(self.priority, Priority):
            self.priority = Priority(self.priority.lower())

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


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
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(self.get_all_tasks(), key=lambda t: order[t.priority])

    def _build_prompt(self) -> str:
        """Construct the Claude prompt from owner, pets, and tasks."""
        task_lines = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                task_lines.append(
                    f"- {task.title} ({task.duration_minutes} min, "
                    f"priority: {task.priority.value}, frequency: {task.frequency}) "
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
