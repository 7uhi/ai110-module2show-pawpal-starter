from pawpal_system import Task, Pet, Owner, Scheduler, Priority

# --- Setup ---
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

# Tasks for Mochi (dog)
mochi.add_task(Task(title="Morning walk",     duration_minutes=30, priority=Priority.HIGH,   frequency="daily"))
mochi.add_task(Task(title="Breakfast feeding", duration_minutes=10, priority=Priority.HIGH,   frequency="daily"))
mochi.add_task(Task(title="Evening play",     duration_minutes=20, priority=Priority.MEDIUM, frequency="daily"))

# Tasks for Luna (cat)
luna.add_task(Task(title="Litter box cleaning", duration_minutes=10, priority=Priority.HIGH,   frequency="daily"))
luna.add_task(Task(title="Wet food feeding",    duration_minutes=5,  priority=Priority.MEDIUM, frequency="daily"))
luna.add_task(Task(title="Brush grooming",      duration_minutes=15, priority=Priority.LOW,    frequency="weekly"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Schedule ---
scheduler = Scheduler(owner=owner)
sorted_tasks = scheduler.sort_tasks()

print("=" * 40)
print("       Today's Schedule")
print("=" * 40)

for pet in owner.pets:
    print(f"\n{pet.name} ({pet.species})  —  {pet.total_duration()} min total")
    print("-" * 30)
    for task in pet.tasks:
        status = "✓" if task.is_completed else "○"
        print(f"  {status} [{task.priority.value:6}]  {task.title} ({task.duration_minutes} min, {task.frequency})")

print("\n" + "=" * 40)
print("  All tasks by priority (high → low)")
print("=" * 40)
for task in sorted_tasks:
    print(f"  [{task.priority.value:6}]  {task.title}")
