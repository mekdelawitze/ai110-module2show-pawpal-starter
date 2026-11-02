from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Streamlit reruns this script on every click, so keep the Owner in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(pet_name):
            st.error(f"You already have a pet named {pet_name}.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name.strip()}!")

st.subheader("Schedule a task")
if not owner.pets:
    st.info("Add a pet first, then you can schedule tasks.")
else:
    with st.form("add_task"):
        c1, c2 = st.columns(2)
        target = c1.selectbox("Pet", [p.name for p in owner.pets])
        description = c2.text_input("Task", value="Morning walk")
        c3, c4, c5, c6 = st.columns(4)
        time_value = c3.time_input("Time")
        frequency = c4.selectbox("Repeats", ["once", "daily", "weekly"])
        duration = c5.number_input("Minutes", min_value=1, max_value=240, value=20)
        priority = c6.selectbox("Priority", ["high", "medium", "low"], index=1)
        if st.form_submit_button("Add task"):
            if not description.strip():
                st.error("Please enter a task description.")
            else:
                task = Task(description.strip(), time_value.strftime("%H:%M"), frequency,
                            date.today(), int(duration), priority)
                owner.get_pet(target).add_task(task)
                st.success(f"Scheduled '{task.description}' for {target} at {task.time}.")

st.divider()
st.subheader("Today's schedule")

for warning in scheduler.detect_conflicts():
    st.warning(f"⚠️ {warning}. Consider moving one of these tasks.")

todays = scheduler.get_todays_schedule()
if todays:
    st.table([{"Time": t.time, "Pet": t.pet_name, "Task": t.description,
               "Repeats": t.frequency, "Minutes": t.duration_minutes,
               "Priority": t.priority} for t in todays])
    st.markdown("**Mark a task done**")
    for t in todays:
        if st.button(f"✅ {t.time} {t.pet_name}: {t.description}", key=f"done_{id(t)}"):
            follow_up = scheduler.mark_task_complete(t)
            if follow_up:
                st.session_state.flash = f"Done! Next '{t.description}' is scheduled for {follow_up.due_date}."
            else:
                st.session_state.flash = f"Done! '{t.description}' completed."
            st.rerun()
else:
    st.info("Nothing scheduled for today.")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

st.subheader("All tasks")
c1, c2 = st.columns(2)
pet_filter = c1.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
status_filter = c2.selectbox("Filter by status", ["All", "Pending", "Completed"])
filtered = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "Pending": False, "Completed": True}[status_filter],
)
filtered = scheduler.sort_by_time(filtered)
if filtered:
    st.table([{"Date": str(t.due_date), "Time": t.time, "Pet": t.pet_name, "Task": t.description,
               "Done": "✅" if t.completed else ""} for t in filtered])
else:
    st.caption("No tasks match.")
