from pawpal_system import Task, Pet, Owner, Scheduler, Priority

# --- Setup ---
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

# Tasks added OUT OF ORDER (mixed times and priorities)
mochi.add_task(Task(title="Evening play",      duration_minutes=20, priority=Priority.MEDIUM, frequency="daily",     scheduled_time=1080))  # 6:00 PM
mochi.add_task(Task(title="Morning walk",      duration_minutes=30, priority=Priority.HIGH,   frequency="daily",     scheduled_time=420))   # 7:00 AM
mochi.add_task(Task(title="Vet appointment",   duration_minutes=60, priority=Priority.HIGH,   frequency="as-needed", scheduled_time=600))   # 10:00 AM
mochi.add_task(Task(title="Breakfast feeding", duration_minutes=10, priority=Priority.HIGH,   frequency="daily",     scheduled_time=450))   # 7:30 AM

luna.add_task(Task(title="Brush grooming",      duration_minutes=15, priority=Priority.LOW,    frequency="weekly",    scheduled_time=900))   # 3:00 PM
luna.add_task(Task(title="Litter box cleaning", duration_minutes=10, priority=Priority.HIGH,   frequency="daily",     scheduled_time=480))   # 8:00 AM
luna.add_task(Task(title="Wet food feeding",    duration_minutes=5,  priority=Priority.MEDIUM, frequency="daily"))                          # no time set
# ── Intentional conflicts ──────────────────────────────────────────────────
# Same-pet conflict: Mochi has two tasks at 7:00 AM (420 min)
mochi.add_task(Task(title="Pill medication",    duration_minutes=5,  priority=Priority.HIGH,   frequency="daily",     scheduled_time=420))   # 7:00 AM — clashes with Morning walk
# Cross-pet conflict: both Mochi and Luna have a task at 3:00 PM (900 min)
mochi.add_task(Task(title="Afternoon nap",      duration_minutes=30, priority=Priority.LOW,    frequency="daily",     scheduled_time=900))   # 3:00 PM — clashes with Luna's Brush grooming

owner.add_pet(mochi)
owner.add_pet(luna)

# Mark one task complete to demonstrate status filtering
mochi.tasks[0].mark_complete()  # Evening play → done

scheduler = Scheduler(owner=owner)


def fmt_time(minutes: int | None) -> str:
    """Convert minutes-from-midnight to HH:MM string, or '--:--' if unset."""
    if minutes is None:
        return "--:--"
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


# ── 1. Sort by time ──────────────────────────────────────────────────────────
print("=" * 45)
print("  All tasks sorted by scheduled time")
print("=" * 45)
for task in scheduler.sort_by_time():
    status = "✓" if task.is_completed else "○"
    print(f"  {status} {fmt_time(task.scheduled_time)}  [{task.priority.name.lower():6}]  {task.title}")

# ── 2. Sort by priority ───────────────────────────────────────────────────────
print("\n" + "=" * 45)
print("  All tasks sorted by priority (high → low)")
print("=" * 45)
for task in scheduler.sort_tasks():
    status = "✓" if task.is_completed else "○"
    print(f"  {status} [{task.priority.name.lower():6}]  {task.title} ({fmt_time(task.scheduled_time)})")

# ── 3. Filter: incomplete tasks only ─────────────────────────────────────────
print("\n" + "=" * 45)
print("  Incomplete tasks (all pets)")
print("=" * 45)
for task in scheduler.get_incomplete_tasks():
    print(f"  ○ {fmt_time(task.scheduled_time)}  {task.title}")

# ── 4. Filter: tasks for a specific pet ──────────────────────────────────────
for pet_name in ["Mochi", "Luna"]:
    print(f"\n{'=' * 45}")
    print(f"  All tasks for {pet_name}")
    print("=" * 45)
    for task in scheduler.get_tasks_for_pet(pet_name):
        status = "✓" if task.is_completed else "○"
        print(f"  {status} {fmt_time(task.scheduled_time)}  {task.title}")

# ── 5. Filter: pet + completion status ───────────────────────────────────────
print("\n" + "=" * 45)
print("  Mochi — pending tasks only")
print("=" * 45)
for task in scheduler.get_tasks_by_pet_and_status("Mochi", completed=False):
    print(f"  ○ {fmt_time(task.scheduled_time)}  {task.title}")

print("\n" + "=" * 45)
print("  Mochi — completed tasks only")
print("=" * 45)
for task in scheduler.get_tasks_by_pet_and_status("Mochi", completed=True):
    print(f"  ✓ {fmt_time(task.scheduled_time)}  {task.title}")

# ── 6. Conflict detection ─────────────────────────────────────────────────────
print("\n" + "=" * 45)
print("  Conflict detection")
print("=" * 45)
warnings = scheduler.detect_conflicts()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")
