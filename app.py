from datetime import time

import streamlit as st

from pawpal_system import CareTask, Owner, Pet, Priority, Scheduler


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

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Streamlit reruns this script on every interaction, so create the Owner once
# and keep it in session_state; later runs reuse the same object.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name

st.markdown("### Pets")

with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Give your pet a name first.")
        elif any(p.name == pet_name.strip() for p in owner.pets):
            st.error(f"You already have a pet named {pet_name.strip()}.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))

if owner.pets:
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    with st.form("add_task", clear_on_submit=True):
        chosen_name = st.selectbox("For pet", [p.name for p in owner.pets])
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            task_title = st.text_input("Task title", value="Morning walk")

        with col2:
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=240,
                value=20,
            )

        with col3:
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                index=2,
            )

        with col4:
            scheduled_time = st.time_input(
                "Scheduled time",
                value=time(8, 0),
            )

        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == chosen_name)
            pet.add_task(
                CareTask(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=Priority(priority),
                    scheduled_time=scheduled_time,
                )
            )

    for p in owner.pets:
        if p.tasks:
            st.write(f"**{p.name}**")
            st.table(
                [
                    {
                        "title": t.title,
                        "duration_minutes": t.duration_minutes,
                        "priority": t.priority.value,
                    }
                    for t in p.tasks
                ]
            )
    if not owner.all_items():
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before adding tasks.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner)
    pairs = owner.tasks_with_pets()

    if not pairs:
        st.info("No tasks to schedule yet.")
    else:
        # Earliest scheduled time first; tasks with no time go last.
        sorted_pairs = scheduler.sort_by_time(pairs)
        st.table(
            [
                {
                    "time": t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "unscheduled",
                    "pet": p.name,
                    "task": t.title,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority.value,
                    "completed": t.completed,
                }
                for p, t in sorted_pairs
            ]
        )

        # Tasks that share the exact same scheduled_time, grouped by that time.
        conflicts = scheduler.detect_conflicts(pairs)
        if conflicts:
            for slot, group in conflicts.items():
                details = ", ".join(f"{p.name}: {t.title}" for p, t in group)
                st.warning(f"⚠️ Conflict at {slot.strftime('%H:%M')} — {details}")
        else:
            st.success("No scheduling conflicts found.")
