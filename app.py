import streamlit as st
from datetime import date
from pawpal_system import (
    OwnerProfile,
    PetProfile,
    Task,
    Schedule,
    Scheduler,
    TaskRepository,
    Priority,
    Category,
)

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

# ── Initialize session state for Owner and Pet ────────────────────────────────
# Check if Owner exists in session_state; if not, create it
if "owner" not in st.session_state:
    st.session_state.owner = OwnerProfile(
        owner_id="owner_001",
        name="Jordan",
        email="jordan@example.com",
        available_time_per_day=180,  # 3 hours
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
    st.session_state.owner.pet = st.session_state.pet  # Associate pet with owner

# ── UI for editing Owner and Pet info ─────────────────────────────────────────
st.subheader("Owner & Pet Setup")

col1, col2 = st.columns(2)
with col1:
    st.write("**Owner Info**")
    owner_name = st.text_input(
        "Owner name",
        value=st.session_state.owner.name,
        key="owner_name_input"
    )
    if owner_name != st.session_state.owner.name:
        st.session_state.owner.update_profile(name=owner_name)
    
    available_time = st.number_input(
        "Available time per day (minutes)",
        value=st.session_state.owner.available_time_per_day,
        min_value=30,
        max_value=1440,
        key="available_time_input"
    )
    if available_time != st.session_state.owner.available_time_per_day:
        st.session_state.owner.update_profile(available_time_per_day=int(available_time))

with col2:
    st.write("**Pet Info**")
    pet_name = st.text_input(
        "Pet name",
        value=st.session_state.pet.name,
        key="pet_name_input"
    )
    if pet_name != st.session_state.pet.name:
        st.session_state.pet.update_profile(name=pet_name)
    
    species = st.selectbox(
        "Species",
        ["dog", "cat", "other"],
        index=0 if st.session_state.pet.species.lower() == "dog" else 1,
        key="species_input"
    )
    if species != st.session_state.pet.species.lower():
        st.session_state.pet.update_profile(species=species)

st.divider()

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="task_duration_input")
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], key="task_priority_input")
with col4:
    category = st.selectbox(
        "Category",
        [c.value for c in Category],
        key="task_category_input"
    )

if st.button("➕ Add task"):
    # Create an actual Task object using Phase 2 methods
    task_id = f"task_{len(st.session_state.tasks) + 1:03d}"
    priority_enum = Priority[priority.upper()]
    category_enum = Category[category.upper()]
    
    new_task = Task(
        task_id=task_id,
        name=task_title,
        duration_minutes=int(duration),
        priority=priority_enum,
        category=category_enum,
        owner_id=st.session_state.owner.owner_id,
        pet_id=st.session_state.pet.pet_id,
        is_completed=False,
    )
    
    st.session_state.tasks.append(new_task)
    st.success(f"✓ Task '{task_title}' added!")

if st.session_state.tasks:
    st.write(f"**📋 Current Tasks** ({len(st.session_state.tasks)})")
    
    # Display tasks with their properties
    task_display = []
    for task in st.session_state.tasks:
        task_display.append({
            "Task": task.name,
            "Duration": f"{task.duration_minutes} min",
            "Priority": task.priority.value,
            "Category": task.category.value,
            "Status": "✓ Done" if task.is_completed else "○ Pending",
        })
    st.table(task_display)
else:
    st.info("📝 No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

# Display current session state info
with st.expander("📊 Session State (Developer Info)", expanded=False):
    st.markdown("""
    **How Session State Works in Streamlit:**
    - Every time you interact with the app (click a button, type in a field), Streamlit reruns the entire script
    - Without `st.session_state`, any objects you create at the top level would be recreated (and "empty") on every rerun
    - `st.session_state` is a persistent "vault" that survives reruns
    
    **Pattern used here:**
    ```python
    if "owner" not in st.session_state:
        st.session_state.owner = OwnerProfile(...)
    ```
    - Check if object exists → only create once
    - Retrieve it on subsequent reruns
    - Mutations (like `.update_profile()`) are preserved across reruns
    """)
    
    st.write("**Current Session State:**")
    st.json({
        "owner": f"{st.session_state.owner.name} (available: {st.session_state.owner.available_time_per_day} min)",
        "pet": f"{st.session_state.pet.name} ({st.session_state.pet.species})",
        "tasks_count": len(st.session_state.tasks),
    })

if st.button("🎯 Generate schedule"):
    if not st.session_state.tasks:
        st.warning("⚠️ Add at least one task before generating a schedule.")
    else:
        # ── Call Phase 2 methods to generate the schedule ────────────────────────
        scheduler = Scheduler()
        schedule = Schedule(
            schedule_id="schedule_001",
            date=date.today(),
            owner=st.session_state.owner,
            scheduler=scheduler,
        )
        
        # Generate the schedule using Phase 2 logic
        schedule.generate_schedule(st.session_state.tasks)
        
        # Display the generated schedule
        st.success("✅ Schedule generated successfully!")
        
        st.subheader(f"📅 Today's Schedule for {st.session_state.owner.name}")
        
        col_pet, col_time = st.columns(2)
        with col_pet:
            st.metric("Pet", f"{st.session_state.pet.name} ({st.session_state.pet.species})")
        with col_time:
            st.metric(
                "Time Used",
                f"{schedule.total_duration_minutes} / {st.session_state.owner.get_available_time()} min"
            )
        
        st.divider()
        
        # Display scheduled tasks
        if schedule.tasks:
            st.markdown("### 🎯 Scheduled Tasks")
            for i, task in enumerate(schedule.tasks, 1):
                with st.container():
                    col_num, col_info = st.columns([0.5, 6])
                    with col_num:
                        st.header(str(i))
                    with col_info:
                        st.markdown(f"**{task.name}**")
                        st.caption(
                            f"⏱️ {task.duration_minutes} min | "
                            f"📌 {task.priority.value.upper()} | "
                            f"🏷️ {task.category.value}"
                        )
        else:
            st.info("ℹ️ No tasks could fit in the available time.")
        
        st.divider()
        
        # Display scheduling reasoning
        st.markdown("### 💡 Scheduling Reasoning")
        st.info(schedule.explain_reasoning())
