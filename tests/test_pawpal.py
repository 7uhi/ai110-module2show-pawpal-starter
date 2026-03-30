import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, Priority


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority=Priority.MEDIUM))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks should come back earliest scheduled_time first; untimed tasks last."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Evening walk",  duration_minutes=30, priority=Priority.LOW,    scheduled_time=1080))  # 18:00
    pet.add_task(Task(title="Morning walk",  duration_minutes=30, priority=Priority.HIGH,   scheduled_time=420))   # 07:00
    pet.add_task(Task(title="Midday feeding",duration_minutes=10, priority=Priority.MEDIUM, scheduled_time=720))   # 12:00
    pet.add_task(Task(title="Grooming",      duration_minutes=20, priority=Priority.LOW))                          # no time

    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))
    sorted_tasks = scheduler.sort_by_time()

    times = [t.scheduled_time for t in sorted_tasks]
    assert times == [420, 720, 1080, None], f"Expected [420, 720, 1080, None], got {times}"


def test_sort_tasks_returns_priority_order():
    """sort_tasks() should order HIGH → MEDIUM → LOW."""
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Litter box", duration_minutes=5,  priority=Priority.LOW))
    pet.add_task(Task(title="Feeding",    duration_minutes=10, priority=Priority.MEDIUM))
    pet.add_task(Task(title="Medication", duration_minutes=5,  priority=Priority.HIGH))

    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))
    sorted_tasks = scheduler.sort_tasks()

    priorities = [t.priority for t in sorted_tasks]
    assert priorities == [Priority.HIGH, Priority.MEDIUM, Priority.LOW]


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_recurs_next_day():
    """Completing a daily task should return a new task dated tomorrow."""
    today = date.today()
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
                frequency="daily", scheduled_date=today)

    next_task = task.mark_complete()

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.scheduled_date == today + timedelta(days=1)
    assert next_task.title == "Morning walk"
    assert next_task.is_completed is False


def test_weekly_task_recurs_next_week():
    """Completing a weekly task should return a new task dated 7 days out."""
    today = date.today()
    task = Task(title="Bath time", duration_minutes=45, priority=Priority.MEDIUM,
                frequency="weekly", scheduled_date=today)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.scheduled_date == today + timedelta(weeks=1)


def test_as_needed_task_does_not_recur():
    """as-needed tasks should return None from mark_complete (no next occurrence)."""
    task = Task(title="Vet visit", duration_minutes=60, priority=Priority.HIGH,
                frequency="as-needed")

    next_task = task.mark_complete()

    assert task.is_completed is True
    assert next_task is None


def test_complete_task_adds_recurrence_to_pet():
    """Scheduler.complete_task() should append the next occurrence to the pet's list."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
                      frequency="daily", scheduled_date=date.today()))

    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))
    next_task = scheduler.complete_task("Mochi", "Morning walk")

    assert next_task is not None
    # Original task + new recurrence = 2 tasks on the pet
    assert len(pet.tasks) == 2
    assert pet.tasks[1].scheduled_date == date.today() + timedelta(days=1)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_time_slot():
    """Two incomplete tasks at the same scheduled_time should produce a conflict warning."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH,   scheduled_time=420))
    pet.add_task(Task(title="Feeding",      duration_minutes=10, priority=Priority.MEDIUM, scheduled_time=420))

    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "07:00" in warnings[0]
    assert "Morning walk" in warnings[0]
    assert "Feeding" in warnings[0]


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task should not trigger a conflict, even if times overlap."""
    pet = Pet(name="Mochi", species="dog")
    completed = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, scheduled_time=420)
    completed.mark_complete()
    pet.add_task(completed)
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority=Priority.MEDIUM, scheduled_time=420))

    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))
    warnings = scheduler.detect_conflicts()

    assert warnings == []


def test_detect_conflicts_no_overlap_returns_empty():
    """Tasks at different times should not produce any conflict warnings."""
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Feeding",   duration_minutes=10, priority=Priority.MEDIUM, scheduled_time=420))
    pet.add_task(Task(title="Litter box",duration_minutes=5,  priority=Priority.LOW,    scheduled_time=480))

    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))
    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_returns_empty_and_zero_duration():
    pet = Pet(name="Ghost", species="fish")
    scheduler = Scheduler(owner=Owner(name="Alex", pets=[pet]))

    assert scheduler.get_all_tasks() == []
    assert scheduler.get_incomplete_tasks() == []
    assert scheduler.detect_conflicts() == []
    assert pet.total_duration() == 0


def test_owner_with_no_pets_returns_empty():
    scheduler = Scheduler(owner=Owner(name="Alex", pets=[]))
    assert scheduler.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.sort_tasks() == []
