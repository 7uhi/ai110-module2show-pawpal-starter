# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- Three core actions a user should be able to perform
  1. Enter owner & pet info
  2. Add care tasks
  3. Generate & view a daily schedule
- Briefly describe your initial UML design.
Owner  ──has──>  Pet  ──has many──>  Task
Schedule  ──uses──>  Owner
Schedule  ──uses──>  Pet
Schedule.generate()  ──calls──>  Claude API
- What classes did you include, and what responsibilities did you assign to each?
Task: title, duration, priority, is_completed, mark_complete()
Owner: name, mainly a data holder. Can add add_pet() if supporting multiple pets.
Pet: name, species, tasks, add_task()
Schedule: owner, pet, plan
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Missing Relationships
Owner has no link to Pet
The UML shows Owner owns Pet, but there's no pets list on Owner and no way to navigate from an owner to their pet(s). Schedule holds both separately, so the relationship only exists implicitly inside Schedule. This is fine for a single-pet app, but if you ever support multiple pets, you'd need Owner.pets: List[Pet].

Schedule has no link back to individual Task results
plan_text is a raw string from Claude. Once generated, you can't query "which tasks are scheduled?" or "what time is task X?" programmatically. The schedule output is opaque — fine for display, but a bottleneck if you want to mark tasks complete or filter the plan.

Potential Logic Bottlenecks
generate() does everything in one call
Building the prompt, calling the API, parsing the response, and storing results are all in one method. If the API call fails mid-way, you lose context on what was sent. Consider separating _build_prompt() as a helper — makes it testable without hitting the API.

priority is an unvalidated string
Nothing prevents Task(priority="urgent") or Task(priority="HIGH"). When Claude's prompt lists tasks by priority, inconsistent casing or values could confuse the output. An Enum or validation in __post_init__ would close this gap.

total_duration() returns None right now (stub returns pass)
Any code that calls pet.total_duration() before implementation will silently get None instead of an int. Low risk now, but worth flagging for when you wire it into the prompt.

No way to remove or edit tasks
Pet only has add_task. If a user adds a task by mistake in the UI, there's no remove_task(index) or clear_tasks(). This will surface as a UX issue once connected to Streamlit.

Implemented all of these changes for the reasons listed above.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
Priority, scheduled time, completion status, recurrence frequency, time conflicts
- How did you decide which constraints mattered most?
Priority ranked first because some tasks are non-negotiable on safety grounds — a medication dose or vet appointment can't be bumped, whereas an afternoon nap or grooming session can. Time slotting ranked second because priority alone doesn't produce an actionable schedule. Two HIGH tasks still need to know which comes first in the day. sort_by_time() answers "when," while sort_tasks() answers "what matters most" — they're complementary rather than competing.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Right now Priority.value is a human-readable string ("high", "medium", "low"). Changing it to an integer (0, 1, 2) means the enum's stored value no longer describes itself — you lose that freebie display string.
- Why is that tradeoff reasonable for this scenario?
The string values were a convenience that leaked into the sort logic, forcing sort_tasks() to maintain a separate translation dict to make them sortable. Integers are what the sort actually needs — so the enum's value should just be that directly.

In a larger system where Priority.value was serialized to a database, sent over an API, or matched against user input in many places, the cost of changing it would be much higher. Here the surface area is small (two display lines, one coercion line), so the one-time fix is cheap and the long-term design is cleaner.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude for design brainstorming, generating UML diagrams, creating methods, implementing the methods, connecting different files together, debugging, and refactoring.
- What kinds of prompts or questions were most helpful?
The ones which were based off of things that were more thought out, such as UML diagrams or a prompt using plan mode.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When I asked to evaluate an algorithm to make it more simple.
- How did you evaluate or verify what the AI suggested?
I evaluated what the AI suggested by asking for its justification on the change, and seeing if it was readable and not just purely "pythonic".
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

  - **Sorting by priority** — verified that `sort_tasks()` always returns tasks in HIGH → MEDIUM → LOW order, regardless of the order they were added.
  - **Sorting by time** — verified that `sort_by_time()` returns tasks in chronological order (earliest `scheduled_time` first) and places tasks with no scheduled time at the end of the list.
  - **Daily recurrence** — verified that completing a `daily` task produces a new task dated exactly one day later with `is_completed = False` and the same title and duration.
  - **Weekly recurrence** — verified that completing a `weekly` task produces a new task dated 7 days later.
  - **As-needed non-recurrence** — verified that completing an `as-needed` task returns `None` — no next occurrence is created.
  - **Scheduler recurrence integration** — verified that `Scheduler.complete_task()` not only marks the task done but also appends the next occurrence to the pet's task list, so the pet always has an up-to-date schedule.
  - **Conflict detection — same time slot** — verified that two incomplete tasks sharing a `scheduled_time` produce exactly one warning containing the correct time string and both task names.
  - **Conflict detection — completed tasks excluded** — verified that a completed task at the same time as an active task does not trigger a conflict warning.
  - **Conflict detection — no overlap** — verified that tasks at distinct times return an empty warnings list.
  - **Edge case: pet with no tasks** — verified that all scheduler query methods return empty lists and `total_duration()` returns 0, so nothing crashes on a fresh pet.
  - **Edge case: owner with no pets** — verified that `get_all_tasks()`, `sort_tasks()`, and `sort_by_time()` all return empty lists when the owner has no pets registered.

- Why were these tests important?

  Sorting correctness matters because the entire schedule depends on it — if priority order is wrong, a pet could miss a high-urgency task like medication while a low-priority grooming session runs first. Testing both sort methods separately confirmed that priority ordering and time ordering work independently.

  Recurrence logic tests are critical because a missed recurrence means a care task silently disappears from the schedule after one completion. Each frequency type (daily, weekly, as-needed) has a different code path, so all three needed explicit coverage. The `complete_task()` integration test was especially important because it verified that the scheduler correctly wires `mark_complete()` output back into the pet's task list — a step that could easily be missed.

  Conflict detection tests protect the pet owner from accidentally double-booking time slots. The "completed tasks excluded" test is specifically important because without it, finishing a task could leave a phantom conflict warning that confuses the owner even though the situation is already resolved.

  The edge case tests guard against crashes on a fresh or empty app state — the most common state a new user will encounter. Without them, a `None` return or an index error on an empty list could break the UI silently.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am very confident that my scheduler works correctly, but more features would definitely help and there are definitely edge cases that I have not thought of yet.
- What edge cases would you test next if you had more time?
get_tasks_by_pet_and_status() has no tests at all.

This method combines two filters — pet name and completion status — but neither path has ever been exercised.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with how the overall process went in terms of planning, implementing, testing, debugging, and refactoring. It felt smooth and also I felt more confident when interacting with the AI.
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would try to improve the UI, to make it more visually appealing and easy to use.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned that it is important to plan a lot with your AI, as well as ask it to justify what it is doing.