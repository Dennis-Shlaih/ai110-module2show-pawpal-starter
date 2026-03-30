import streamlit as st
from datetime import date, time
from pawpal_system import (
    OwnerProfile,
    PetProfile,
    Task,
    Schedule,
    Scheduler,
    TaskRepository,
    Priority,
    Category,
    Frequency,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state init ────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = OwnerProfile(
        owner_id="owner_001",
        name="Jordan",
        email="jordan@example.com",
        available_time_per_day=180,
    )

if "pet" not in st.session_state:
    st.session_state.pet = PetProfile(
        pet_id="pet_001",
        name="Mochi",
        age=3,
        species="dog",
        breed="Shiba Inu",
        preferences=["walks", "enrichment"],
    )
    st.session_state.owner.pet = st.session_state.pet

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ── Owner & Pet Setup ─────────────────────────────────────────────────────────
st.subheader("Owner & Pet Setup")
col1, col2 = st.columns(2)
with col1:
    st.write("**Owner Info**")
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name, key="owner_name_input")
    if owner_name != st.session_state.owner.name:
        st.session_state.owner.update_profile(name=owner_name)

    available_time = st.number_input(
        "Available time per day (minutes)",
        value=st.session_state.owner.available_time_per_day,
        min_value=30, max_value=1440, key="available_time_input",
    )
    if available_time != st.session_state.owner.available_time_per_day:
        st.session_state.owner.update_profile(available_time_per_day=int(available_time))

with col2:
    st.write("**Pet Info**")
    pet_name = st.text_input("Pet name", value=st.session_state.pet.name, key="pet_name_input")
    if pet_name != st.session_state.pet.name:
        st.session_state.pet.update_profile(name=pet_name)

    species = st.selectbox(
        "Species", ["dog", "cat", "other"],
        index=0 if st.session_state.pet.species.lower() == "dog" else 1,
        key="species_input",
    )
    if species != st.session_state.pet.species.lower():
        st.session_state.pet.update_profile(species=species)

st.divider()

# ── Add Task Form ─────────────────────────────────────────────────────────────
st.subheader("Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning Walk", key="task_title_input")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="task_duration_input")
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], key="task_priority_input")
with col4:
    category = st.selectbox("Category", [c.value for c in Category], key="task_category_input")

col5, col6 = st.columns(2)
with col5:
    frequency = st.selectbox(
        "Frequency", [f.value for f in Frequency], key="task_frequency_input"
    )
with col6:
    set_start = st.checkbox("Set a scheduled start time", key="set_start_checkbox")
    scheduled_start = None
    if set_start:
        start_time = st.time_input("Start time", value=time(8, 0), key="task_start_input")
        scheduled_start = start_time.hour * 60 + start_time.minute

if st.button("➕ Add task"):
    task_id = f"task_{len(st.session_state.tasks) + 1:03d}"
    new_task = Task(
        task_id=task_id,
        name=task_title,
        duration_minutes=int(duration),
        priority=Priority[priority.upper()],
        category=Category[category.upper()],
        owner_id=st.session_state.owner.owner_id,
        pet_id=st.session_state.pet.pet_id,
        pet_name=st.session_state.pet.name,
        frequency=Frequency[frequency.upper()],
        scheduled_start=scheduled_start,
        is_completed=False,
    )
    st.session_state.tasks.append(new_task)
    st.success(f"Task '{task_title}' added!")

# ── Task Display with Sorting ─────────────────────────────────────────────────
if st.session_state.tasks:
    scheduler = Scheduler()

    sort_by = st.radio(
        "Sort tasks by:",
        ["Added order", "Priority", "Duration", "Category"],
        horizontal=True,
        key="sort_radio",
    )

    if sort_by == "Priority":
        display_tasks = scheduler.sort_by_priority(st.session_state.tasks)
    elif sort_by == "Duration":
        display_tasks = scheduler.sort_by_duration(st.session_state.tasks, order="asc")
    elif sort_by == "Category":
        display_tasks = scheduler.sort_by_category(st.session_state.tasks)
    else:
        display_tasks = st.session_state.tasks

    st.write(f"**Current Tasks** ({len(display_tasks)})")
    task_rows = []
    for task in display_tasks:
        start_label = ""
        if task.scheduled_start is not None:
            h, m = divmod(task.scheduled_start, 60)
            start_label = f"{h:02d}:{m:02d}"
        task_rows.append({
            "Task": task.name,
            "Duration": f"{task.duration_minutes} min",
            "Priority": task.priority.value,
            "Category": task.category.value,
            "Frequency": task.frequency.value,
            "Start": start_label or "—",
            "Status": "✓ Done" if task.is_completed else "○ Pending",
        })
    st.table(task_rows)

    # ── Edit Task ─────────────────────────────────────────────────────────────
    with st.expander("✏️ Edit a task"):
        task_names = [t.name for t in st.session_state.tasks]
        selected_name = st.selectbox("Select task to edit", task_names, key="edit_select")
        task_to_edit = next(t for t in st.session_state.tasks if t.name == selected_name)

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            new_name = st.text_input("Name", value=task_to_edit.name, key="edit_name")
        with col_b:
            new_duration = st.number_input("Duration (min)", min_value=1, max_value=240,
                                           value=task_to_edit.duration_minutes, key="edit_duration")
        with col_c:
            priority_options = [p.value for p in Priority]
            new_priority = st.selectbox("Priority", priority_options,
                                        index=priority_options.index(task_to_edit.priority.value),
                                        key="edit_priority")
        with col_d:
            category_options = [c.value for c in Category]
            new_category = st.selectbox("Category", category_options,
                                        index=category_options.index(task_to_edit.category.value),
                                        key="edit_category")

        col_e, col_f = st.columns(2)
        with col_e:
            freq_options = [f.value for f in Frequency]
            new_frequency = st.selectbox("Frequency", freq_options,
                                         index=freq_options.index(task_to_edit.frequency.value),
                                         key="edit_frequency")
        with col_f:
            current_start = None
            if task_to_edit.scheduled_start is not None:
                h, m = divmod(task_to_edit.scheduled_start, 60)
                current_start = time(h, m)
            edit_set_start = st.checkbox("Set start time", value=task_to_edit.scheduled_start is not None,
                                         key="edit_set_start")
            new_scheduled_start = task_to_edit.scheduled_start
            if edit_set_start:
                edit_start_time = st.time_input("Start time", value=current_start or time(8, 0),
                                                key="edit_start_time")
                new_scheduled_start = edit_start_time.hour * 60 + edit_start_time.minute
            else:
                new_scheduled_start = None

        if st.button("💾 Save changes"):
            task_to_edit.update_task(
                name=new_name,
                duration_minutes=int(new_duration),
                priority=Priority[new_priority.upper()],
                category=Category[new_category.upper()],
                frequency=Frequency[new_frequency.upper()],
                scheduled_start=new_scheduled_start,
            )
            st.success(f"Task updated to '{new_name}'!")
            st.rerun()

else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Generate Schedule ─────────────────────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("🎯 Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler()
        schedule = Schedule(
            schedule_id="schedule_001",
            date=date.today(),
            owner=st.session_state.owner,
            scheduler=scheduler,
        )
        schedule.generate_schedule(st.session_state.tasks)

        # ── Conflict Detection ────────────────────────────────────────────────
        conflicts = scheduler.detect_conflicts(st.session_state.tasks)
        if conflicts:
            st.error("Scheduling conflicts detected — review before finalizing your plan:")
            for warning in conflicts:
                # Extract just the descriptive part after "WARNING: "
                message = warning.replace("WARNING: Scheduling conflict — ", "")
                st.warning(f"⚠️ Conflict: {message}")
        else:
            st.success("No scheduling conflicts detected.")

        st.subheader(f"Today's Schedule for {st.session_state.owner.name} & {st.session_state.pet.name}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Pet", f"{st.session_state.pet.name} ({st.session_state.pet.species})")
        with col_b:
            st.metric(
                "Time Used",
                f"{schedule.total_duration_minutes} / {st.session_state.owner.get_available_time()} min",
            )

        st.divider()

        if schedule.tasks:
            st.markdown("### Scheduled Tasks")
            for i, task in enumerate(schedule.tasks, 1):
                start_label = ""
                if task.scheduled_start is not None:
                    h, m = divmod(task.scheduled_start, 60)
                    start_label = f" · 🕐 {h:02d}:{m:02d}"
                with st.container():
                    col_num, col_info = st.columns([0.5, 6])
                    with col_num:
                        st.header(str(i))
                    with col_info:
                        st.markdown(f"**{task.name}**{start_label}")
                        st.caption(
                            f"⏱️ {task.duration_minutes} min · "
                            f"📌 {task.priority.value.upper()} · "
                            f"🏷️ {task.category.value} · "
                            f"🔁 {task.frequency.value}"
                        )
        else:
            st.info("No tasks could fit in the available time.")

        st.divider()
        st.markdown("### Scheduling Reasoning")
        st.info(schedule.explain_reasoning())

# ── Developer Info ────────────────────────────────────────────────────────────
with st.expander("Session State (Developer Info)", expanded=False):
    st.json({
        "owner": f"{st.session_state.owner.name} ({st.session_state.owner.available_time_per_day} min/day)",
        "pet": f"{st.session_state.pet.name} ({st.session_state.pet.species})",
        "tasks_count": len(st.session_state.tasks),
    })
