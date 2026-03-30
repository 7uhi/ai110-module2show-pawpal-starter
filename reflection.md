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
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
