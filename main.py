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
    # STEP 3: Create Tasks with Different Durations & Priorities
    # ─────────────────────────────────────────────────────────────────────────
    tasks = [
        Task(
            task_id="task_001",
            name="Morning Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.WALKS,
            owner_id="owner_001",
            pet_id="pet_001",
        ),
        Task(
            task_id="task_002",
            name="Breakfast",
            duration_minutes=10,
            priority=Priority.HIGH,
            category=Category.FEEDING,
            owner_id="owner_001",
            pet_id="pet_001",
        ),
        Task(
            task_id="task_003",
            name="Medication",
            duration_minutes=5,
            priority=Priority.HIGH,
            category=Category.MEDICATIONS,
            owner_id="owner_001",
            pet_id="pet_001",
        ),
        Task(
            task_id="task_004",
            name="Play Time & Enrichment",
            duration_minutes=45,
            priority=Priority.MEDIUM,
            category=Category.ENRICHMENT,
            owner_id="owner_001",
            pet_id="pet_001",
        ),
        Task(
            task_id="task_005",
            name="Afternoon Walk",
            duration_minutes=30,
            priority=Priority.MEDIUM,
            category=Category.WALKS,
            owner_id="owner_001",
            pet_id="pet_001",
        ),
        Task(
            task_id="task_006",
            name="Dinner",
            duration_minutes=10,
            priority=Priority.HIGH,
            category=Category.FEEDING,
            owner_id="owner_001",
            pet_id="pet_001",
        ),
        Task(
            task_id="task_007",
            name="Grooming",
            duration_minutes=20,
            priority=Priority.LOW,
            category=Category.GROOMING,
            owner_id="owner_001",
            pet_id="pet_001",
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

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 6: Demonstrate Task Operations
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 70)
    print("  📋 DEMONSTRATION: Task Operations")
    print("=" * 70)
    print()

    # Mark a task as complete
    if schedule.tasks:
        first_task = schedule.tasks[0]
        first_task.mark_complete()
        print(f"✓ Marked '{first_task.name}' as completed")
        print()

    # Query tasks by priority
    high_priority_tasks = repo.get_tasks_by_priority(Priority.HIGH)
    print(f"High Priority Tasks ({len(high_priority_tasks)}):")
    for task in high_priority_tasks:
        print(f"   • {task.name}")
    print()

    # Query tasks for this pet
    pet_tasks = repo.get_tasks_for_pet("pet_001")
    print(f"All Tasks for {dog.name} ({len(pet_tasks)}):")
    for task in pet_tasks:
        print(f"   • {task.name}")
    print()

    print("=" * 70)
    print("  ✅ Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
