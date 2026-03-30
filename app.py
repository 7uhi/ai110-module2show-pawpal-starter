import streamlit as st
from pawpal_system import Priority, Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.owner.add_pet(st.session_state.pet)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
    st.session_state.pet.add_task(new_task)

PRIORITY_LABEL = {Priority.HIGH: "🔴 High", Priority.MEDIUM: "🟡 Medium", Priority.LOW: "🟢 Low"}
STATUS_LABEL   = {True: "✅ Done", False: "⏳ Pending"}

if st.session_state.pet.tasks:
    scheduler = Scheduler(owner=st.session_state.owner)
    sorted_tasks = scheduler.sort_tasks()

    # Summary metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total tasks", len(sorted_tasks))
    m2.metric("Total duration", f"{st.session_state.pet.total_duration()} min")
    m3.metric("Pending", len(scheduler.get_incomplete_tasks()))

    # Sorted task table
    st.caption("Tasks ordered high → medium → low priority")
    st.dataframe(
        [
            {
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": PRIORITY_LABEL[t.priority],
                "Frequency": t.frequency,
                "Status": STATUS_LABEL[t.is_completed],
            }
            for t in sorted_tasks
        ],
        use_container_width=True,
        hide_index=True,
    )

    # Conflict feedback
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.error(
            f"**{len(conflicts)} scheduling conflict(s) found.** "
            "Two or more tasks are assigned to the same time slot. "
            "Resolve these before generating your schedule."
        )
        for warning in conflicts:
            with st.container(border=True):
                st.warning(warning)
                st.caption("Tip: change one task's scheduled time to remove this overlap.")
    else:
        st.success("No scheduling conflicts — all tasks are ready to schedule!")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a prioritized daily care plan for your pet using AI.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=st.session_state.owner)

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.error(
            f"**{len(conflicts)} conflict(s) detected.** "
            "Your schedule may have overlapping tasks."
        )
        for warning in conflicts:
            with st.container(border=True):
                st.warning(warning)

    with st.spinner("Building your pet care schedule..."):
        result = scheduler.generate()

    if result.startswith("Error"):
        st.error(result)
    else:
        st.success("Schedule ready!")
        st.markdown(result)
