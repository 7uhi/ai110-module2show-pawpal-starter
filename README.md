# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Task management
- **Priority levels** — each task is assigned a `HIGH`, `MEDIUM`, or `LOW` priority using an enum, ensuring consistent comparisons across the system.
- **Task recurrence** — marking a task complete automatically generates the next occurrence: daily tasks recur the next day, weekly tasks recur 7 days later, and as-needed tasks do not recur.
- **Completion tracking** — tasks carry an `is_completed` flag so pending and finished work can always be distinguished.

### Scheduling algorithms
- **Sort by priority** — `sort_tasks()` orders all tasks high → medium → low so the most critical care always appears first.
- **Sort by time** — `sort_by_time()` orders tasks by their scheduled time (earliest first), with unscheduled tasks placed at the end.
- **Filter by priority** — `get_tasks_by_priority()` returns only tasks matching a specific priority level, useful for focusing on urgent care.
- **Filter by status** — `get_incomplete_tasks()` and `get_tasks_by_pet_and_status()` let you query pending or completed tasks per pet.

### Conflict detection
- **Time-slot conflict warnings** — `detect_conflicts()` scans all incomplete tasks and flags any two that share the same scheduled time, reporting the exact time slot and the names of the conflicting tasks. Completed tasks are excluded so resolved work never triggers false alarms.

### AI schedule generation
- **Claude-powered daily plan** — `generate()` sends the owner's pets and tasks to the Claude API, which produces a prioritized daily schedule starting at 7 AM along with a plain-language explanation of the ordering decisions.

### Streamlit UI
- **Live metrics** — total task count, total duration in minutes, and pending task count update automatically as tasks are added.
- **Conflict banners** — scheduling conflicts surface as prominent error cards with per-conflict detail and a tip for resolving the overlap, so a pet owner immediately knows what to fix and how.
- **Status indicators** — the task table uses color-coded priority badges (🔴 High, 🟡 Medium, 🟢 Low) and status icons (✅ Done, ⏳ Pending) for fast visual scanning.

## 📸 Demo
<a href="pawpal_demo.png" target="_blank"><img src='/pawpal_demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

The tests cover:

- **Sorting** — `sort_by_time` returns tasks in chronological order (untimed tasks last); `sort_tasks` returns tasks in HIGH → MEDIUM → LOW priority order.
- **Recurrence logic** — completing a `daily` task generates a new task for the next day; `weekly` tasks recur 7 days out; `as-needed` tasks produce no next occurrence.
- **Conflict detection** — two incomplete tasks at the same scheduled time are flagged with a warning; completed tasks are excluded from conflict checks.
- **Edge cases** — a pet with no tasks returns empty lists and zero duration; an owner with no pets returns empty results from all scheduler methods.

## Reliability Confidence Level

**4 / 5 stars**

**What earns the 4 stars:**
- 13/13 tests pass, covering sorting, recurrence, conflict detection, and empty/null edge cases.
- Core scheduling logic is straightforward dataclass-based Python with no risky external dependencies.
- Conflict detection correctly excludes completed tasks from overlap checks.

**What holds back the 5th star:**
- Needs more kinds of tests, such as for the AI integration layer