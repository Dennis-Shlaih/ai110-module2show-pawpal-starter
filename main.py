"""
PawPal+ Demo Script

Demonstrates the core functionality of the PawPal+ system:
- Creating an owner with multiple pets
- Adding tasks to pets with varying priorities
- Generating an optimized daily schedule
- Displaying the schedule with reasoning
"""

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
    Frequency,
)


def main():
    print("=" * 70)
    print("  🐾 PAWPAL+ - Pet Care Scheduling System Demo")
    print("=" * 70)
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Create an Owner
    # ─────────────────────────────────────────────────────────────────────────
    owner = OwnerProfile(
        owner_id="owner_001",
        name="Sarah",
        email="sarah@email.com",
        available_time_per_day=180,  # 3 hours = 180 minutes
    )
    print(f"📋 Owner Created: {owner.name}")
    print(f"   Available time per day: {owner.available_time_per_day} minutes")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Create Pets with Preferences
    # ─────────────────────────────────────────────────────────────────────────
    dog = PetProfile(
        pet_id="pet_001",
        name="Max",
        age=3,
        species="Dog",
        breed="Golden Retriever",
        preferences=["walks", "enrichment"],  # Dog likes walks and playtime
    )
    owner.pet = dog  # Assign dog to owner
    
    print(f"🐕 Pet Created: {dog.name} (3-yr-old {dog.breed})")
    print(f"   Preferences: {', '.join(dog.preferences)}")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Create Tasks with Different Durations & Priorities (OUT OF ORDER)
    # ─────────────────────────────────────────────────────────────────────────
    # Note: Tasks added in random order to demonstrate sorting & filtering
    tasks = [
        Task(
            task_id="task_005",
            name="Afternoon Walk",
            duration_minutes=30,
            priority=Priority.MEDIUM,
            category=Category.WALKS,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
        ),
        Task(
            task_id="task_001",
            name="Morning Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.WALKS,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
            scheduled_start=480,   # 8:00 AM
        ),
        Task(
            task_id="task_007",
            name="Grooming",
            duration_minutes=20,
            priority=Priority.LOW,
            category=Category.GROOMING,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
        ),
        Task(
            task_id="task_003",
            name="Medication",
            duration_minutes=5,
            priority=Priority.HIGH,
            category=Category.MEDICATIONS,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
            scheduled_start=495,   # 8:15 AM — overlaps with Morning Walk (8:00–8:30)
        ),
        Task(
            task_id="task_004",
            name="Play Time & Enrichment",
            duration_minutes=45,
            priority=Priority.MEDIUM,
            category=Category.ENRICHMENT,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
        ),
        Task(
            task_id="task_006",
            name="Dinner",
            duration_minutes=10,
            priority=Priority.HIGH,
            category=Category.FEEDING,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
        ),
        Task(
            task_id="task_002",
            name="Breakfast",
            duration_minutes=10,
            priority=Priority.HIGH,
            category=Category.FEEDING,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
        ),
    ]

    print("📝 Tasks Created:")
    for task in tasks:
        print(
            f"   • {task.name}: {task.duration_minutes} min | "
            f"Priority: {task.priority.value} | "
            f"Category: {task.category.value}"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Create Task Repository and Store Tasks
    # ─────────────────────────────────────────────────────────────────────────
    repo = TaskRepository()
    for task in tasks:
        repo.add_task(task)

    print(f"📚 Task Repository: {len(repo.tasks)} tasks stored")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Generate Today's Schedule
    # ─────────────────────────────────────────────────────────────────────────
    scheduler = Scheduler()
    schedule = Schedule(
        schedule_id="schedule_001",
        date=date.today(),
        owner=owner,
        scheduler=scheduler,
    )

    # Generate the schedule for today
    schedule.generate_schedule(tasks)

    print()
    print("=" * 70)
    print(f"  📅 TODAY'S SCHEDULE for {owner.name} & {dog.name}")
    print(f"  Date: {schedule.date}")
    print(f"  Total Available Time: {owner.get_available_time()} minutes")
    print(f"  Total Scheduled Time: {schedule.total_duration_minutes} minutes")
    print("=" * 70)
    print()

    # Display scheduled tasks
    print("🎯 SCHEDULED TASKS:")
    cumulative_time = 0
    for i, task in enumerate(schedule.tasks, 1):
        print(
            f"   {i}. {task.name}"
            f"\n      ├─ Duration: {task.duration_minutes} min"
            f"\n      ├─ Priority: {task.priority.value.upper()}"
            f"\n      ├─ Category: {task.category.value}"
            f"\n      └─ Status: {'✓ Completed' if task.is_completed else '○ Pending'}"
        )
        cumulative_time += task.duration_minutes
        print()

    print("=" * 70)
    print("💡 SCHEDULING REASONING:")
    print("=" * 70)
    print(schedule.explain_reasoning())
    print()

    print("=" * 70)
    print("  🔍 DEMONSTRATION: Sorting & Filtering Methods")
    print("=" * 70)
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Show Tasks as Created (Out of Order)
    # ─────────────────────────────────────────────────────────────────────────
    print("📋 Tasks as Created (OUT OF ORDER):")
    for i, task in enumerate(tasks, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Duration: {task.duration_minutes:2}min | "
            f"Priority: {task.priority.value:6} | "
            f"Category: {task.category.value:12}"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Sort by Duration (Ascending)
    # ─────────────────────────────────────────────────────────────────────────
    sorted_by_duration = scheduler.sort_by_duration(tasks, order="asc")
    print("📊 Sorted by Duration (ASCENDING - Shortest First):")
    for i, task in enumerate(sorted_by_duration, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Duration: {task.duration_minutes:2}min"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Sort by Duration (Descending)
    # ─────────────────────────────────────────────────────────────────────────
    sorted_by_duration_desc = scheduler.sort_by_duration(tasks, order="desc")
    print("📊 Sorted by Duration (DESCENDING - Longest First):")
    for i, task in enumerate(sorted_by_duration_desc, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Duration: {task.duration_minutes:2}min"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Sort by Priority
    # ─────────────────────────────────────────────────────────────────────────
    sorted_by_priority = scheduler.sort_by_priority(tasks)
    print("🎯 Sorted by Priority (HIGH → MEDIUM → LOW):")
    for i, task in enumerate(sorted_by_priority, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Priority: {task.priority.value:6}"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Sort by Category (Cluster Similar Tasks)
    # ─────────────────────────────────────────────────────────────────────────
    sorted_by_category = scheduler.sort_by_category(tasks)
    print("📂 Sorted by Category (Clustered Similar Tasks):")
    current_category = None
    for i, task in enumerate(sorted_by_category, 1):
        if task.category != current_category:
            print(f"\n   {task.category.value}:")
            current_category = task.category
        print(
            f"      {i}. {task.name:23} | Duration: {task.duration_minutes:2}min"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Filter by Category (Walks Only)
    # ─────────────────────────────────────────────────────────────────────────
    walk_tasks = scheduler.filter_by_category(tasks, Category.WALKS)
    print(f"🚶 Filter by Category (WALKS ONLY - {len(walk_tasks)} tasks):")
    for i, task in enumerate(walk_tasks, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Duration: {task.duration_minutes:2}min | "
            f"Priority: {task.priority.value:6}"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Filter by Category (Feeding Only)
    # ─────────────────────────────────────────────────────────────────────────
    feeding_tasks = scheduler.filter_by_category(tasks, Category.FEEDING)
    print(f"🍽️  Filter by Category (FEEDING ONLY - {len(feeding_tasks)} tasks):")
    for i, task in enumerate(feeding_tasks, 1):
        print(f"   {i}. {task.name}")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Filter by Priority (HIGH Priority Only)
    # ─────────────────────────────────────────────────────────────────────────
    high_priority = scheduler.filter_by_priority(tasks, Priority.HIGH)
    print(f"⚡ Filter by Priority (HIGH PRIORITY ONLY - {len(high_priority)} tasks):")
    for i, task in enumerate(high_priority, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Duration: {task.duration_minutes:2}min"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Filter by Pet Name
    # ─────────────────────────────────────────────────────────────────────────
    max_tasks = scheduler.filter_by_pet_name(tasks, "Max")
    print(f"🐕 Filter by Pet Name (Max - {len(max_tasks)} tasks):")
    for i, task in enumerate(max_tasks, 1):
        print(
            f"   {i}. {task.name:25} | "
            f"Pet: {task.pet_name:15} | "
            f"Duration: {task.duration_minutes:2}min"
        )
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Repository Queries
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 70)
    print("  📚 Repository Queries")
    print("=" * 70)
    print()

    # Get tasks by pet name from repository
    repo_max_tasks = repo.get_tasks_by_pet_name("Max")
    print(f"Repository Query: Tasks for pet 'Max' ({len(repo_max_tasks)} tasks):")
    for i, task in enumerate(repo_max_tasks, 1):
        print(f"   {i}. {task.name}")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # Conflict Detection
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 70)
    print("  ⚠️  CONFLICT DETECTION")
    print("=" * 70)
    print()
    conflicts = scheduler.detect_conflicts(tasks)
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No scheduling conflicts detected.")
    print()

    print("=" * 70)
    print("  ✅ Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
