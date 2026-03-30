from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low", "medium", "high"
    is_completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Owner:
    name: str


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def total_duration(self) -> int:
        pass


@dataclass
class Schedule:
    owner: Owner
    pet: Pet
    plan_text: str = ""
    generated: bool = False

    def generate(self) -> str:
        pass
