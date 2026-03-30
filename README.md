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