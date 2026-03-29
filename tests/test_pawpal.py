"""
Unit tests for the PawPal+ system.

Tests validate core functionality of Task, Pet, Owner, and Scheduler classes.
"""

import unittest
from datetime import date, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import pawpal_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from pawpal_system import (
    Task,
    Priority,
    Category,
    Frequency,
    PetProfile,
    TaskRepository,
    OwnerProfile,
    Scheduler,
)


class TestTaskCompletion(unittest.TestCase):
    """Test cases for Task completion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task = Task(
            task_id="test_task_001",
            name="Test Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.WALKS,
            owner_id="owner_001",
            pet_id="pet_001",
            is_completed=False,
        )
    
    def test_task_mark_complete_changes_status(self):
        """Verify that mark_complete() changes task status to True."""
        # Arrange: Task starts as not completed
        self.assertFalse(self.task.is_completed, "Task should start as not completed")
        
        # Act: Mark task as complete
        self.task.mark_complete()
        
        # Assert: Task is now completed
        self.assertTrue(self.task.is_completed, "Task should be marked as completed")
    
    def test_task_mark_complete_idempotent(self):
        """Verify that mark_complete() can be called multiple times safely."""
        # Call mark_complete() multiple times
        self.task.mark_complete()
        self.assertTrue(self.task.is_completed)
        
        self.task.mark_complete()
        self.assertTrue(self.task.is_completed)
        
        # Should still be completed
        self.assertTrue(self.task.is_completed)


class TestTaskAddition(unittest.TestCase):
    """Test cases for adding tasks and tracking task counts."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo = TaskRepository()
        self.pet_id = "pet_001"
        
    def test_adding_task_increases_pet_task_count(self):
        """Verify that adding tasks to repository increases task count for that pet."""
        # Arrange: Create and add tasks for the pet
        task1 = Task(
            task_id="task_001",
            name="Morning Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.WALKS,
            pet_id=self.pet_id,
        )
        task2 = Task(
            task_id="task_002",
            name="Feeding",
            duration_minutes=10,
            priority=Priority.HIGH,
            category=Category.FEEDING,
            pet_id=self.pet_id,
        )
        
        # Act: Add tasks to repository
        self.repo.add_task(task1)
        initial_count = len(self.repo.get_tasks_for_pet(self.pet_id))
        
        self.repo.add_task(task2)
        final_count = len(self.repo.get_tasks_for_pet(self.pet_id))
        
        # Assert: Count increased by 1
        self.assertEqual(initial_count, 1, "Should have 1 task after first add")
        self.assertEqual(final_count, 2, "Should have 2 tasks after second add")
        self.assertEqual(final_count - initial_count, 1, "Count should increase by 1")
    
    def test_adding_multiple_tasks_for_same_pet(self):
        """Verify that multiple tasks can be added for the same pet."""
        # Arrange: Create multiple tasks for the same pet
        task_names = ["Walk", "Feeding", "Medication", "Playtime"]
        tasks = [
            Task(
                task_id=f"task_{i:03d}",
                name=name,
                duration_minutes=15 + (i * 5),
                priority=Priority.HIGH,
                category=Category.ENRICHMENT,
                pet_id=self.pet_id,
            )
            for i, name in enumerate(task_names)
        ]
        
        # Act: Add all tasks
        for task in tasks:
            self.repo.add_task(task)
        
        # Assert: All tasks are associated with the pet
        pet_tasks = self.repo.get_tasks_for_pet(self.pet_id)
        self.assertEqual(len(pet_tasks), 4, "Should have 4 tasks for this pet")
        self.assertEqual([t.name for t in pet_tasks], task_names)
    
    def test_adding_tasks_for_different_pets(self):
        """Verify that tasks for different pets are tracked separately."""
        # Arrange: Create tasks for two different pets
        pet1_id = "pet_001"
        pet2_id = "pet_002"
        
        task1_pet1 = Task(
            task_id="task_001",
            name="Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.WALKS,
            pet_id=pet1_id,
        )
        task1_pet2 = Task(
            task_id="task_002",
            name="Feeding",
            duration_minutes=10,
            priority=Priority.HIGH,
            category=Category.FEEDING,
            pet_id=pet2_id,
        )
        
        # Act: Add tasks to repository
        self.repo.add_task(task1_pet1)
        self.repo.add_task(task1_pet2)
        
        # Assert: Each pet's task list is correct
        self.assertEqual(
            len(self.repo.get_tasks_for_pet(pet1_id)),
            1,
            "Pet 1 should have 1 task"
        )
        self.assertEqual(
            len(self.repo.get_tasks_for_pet(pet2_id)),
            1,
            "Pet 2 should have 1 task"
        )


class TestTaskUpdate(unittest.TestCase):
    """Test cases for updating task attributes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task = Task(
            task_id="task_001",
            name="Walk",
            duration_minutes=30,
            priority=Priority.MEDIUM,
            category=Category.WALKS,
        )
    
    def test_update_task_duration(self):
        """Verify that task duration can be updated."""
        # Act: Update duration
        self.task.update_task(duration_minutes=45)
        
        # Assert: Duration changed
        self.assertEqual(self.task.duration_minutes, 45)
    
    def test_update_task_priority(self):
        """Verify that task priority can be updated."""
        # Act: Update priority
        self.task.update_task(priority=Priority.HIGH)
        
        # Assert: Priority changed
        self.assertEqual(self.task.priority, Priority.HIGH)
    
    def test_update_task_prevents_id_change(self):
        """Verify that task_id cannot be changed via update_task()."""
        original_id = self.task.task_id
        
        # Act: Attempt to update task_id
        self.task.update_task(task_id="new_id")
        
        # Assert: task_id remains unchanged
        self.assertEqual(self.task.task_id, original_id)


class TestSchedulerSorting(unittest.TestCase):
    """Test cases for Scheduler sorting methods."""
    
    def setUp(self):
        """Set up test fixtures with multiple tasks."""
        self.scheduler = Scheduler()
        self.tasks = [
            Task(
                task_id="task_001",
                name="Long Walk",
                duration_minutes=45,
                priority=Priority.MEDIUM,
                category=Category.WALKS,
            ),
            Task(
                task_id="task_002",
                name="Quick Feeding",
                duration_minutes=10,
                priority=Priority.HIGH,
                category=Category.FEEDING,
            ),
            Task(
                task_id="task_003",
                name="Grooming",
                duration_minutes=30,
                priority=Priority.LOW,
                category=Category.GROOMING,
            ),
            Task(
                task_id="task_004",
                name="Medication",
                duration_minutes=5,
                priority=Priority.HIGH,
                category=Category.MEDICATIONS,
            ),
        ]
    
    def test_sort_by_duration_ascending(self):
        """Verify tasks are sorted by duration in ascending order (shortest first)."""
        # Act: Sort by duration ascending
        sorted_tasks = self.scheduler.sort_by_duration(self.tasks, order="asc")
        
        # Assert: Tasks ordered by duration (5, 10, 30, 45)
        durations = [t.duration_minutes for t in sorted_tasks]
        self.assertEqual(durations, [5, 10, 30, 45])
    
    def test_sort_by_duration_descending(self):
        """Verify tasks are sorted by duration in descending order (longest first)."""
        # Act: Sort by duration descending
        sorted_tasks = self.scheduler.sort_by_duration(self.tasks, order="desc")
        
        # Assert: Tasks ordered by duration (45, 30, 10, 5)
        durations = [t.duration_minutes for t in sorted_tasks]
        self.assertEqual(durations, [45, 30, 10, 5])
    
    def test_sort_by_priority(self):
        """Verify tasks are sorted by priority (HIGH > MEDIUM > LOW)."""
        # Act: Sort by priority
        sorted_tasks = self.scheduler.sort_by_priority(self.tasks)
        
        # Assert: HIGH tasks first, then MEDIUM, then LOW
        priorities = [t.priority for t in sorted_tasks]
        self.assertEqual(
            priorities,
            [Priority.HIGH, Priority.HIGH, Priority.MEDIUM, Priority.LOW]
        )
    
    def test_sort_by_category(self):
        """Verify tasks are sorted by category to cluster similar tasks."""
        # Act: Sort by category
        sorted_tasks = self.scheduler.sort_by_category(self.tasks)
        
        # Assert: Tasks grouped by category (alphabetical order)
        categories = [t.category.value for t in sorted_tasks]
        self.assertEqual(
            categories,
            ["feeding", "grooming", "medications", "walks"]
        )


class TestSchedulerFiltering(unittest.TestCase):
    """Test cases for Scheduler filtering methods."""
    
    def setUp(self):
        """Set up test fixtures with multiple tasks."""
        self.scheduler = Scheduler()
        self.tasks = [
            Task(
                task_id="task_001",
                name="Walk",
                duration_minutes=30,
                priority=Priority.HIGH,
                category=Category.WALKS,
                is_completed=True,
            ),
            Task(
                task_id="task_002",
                name="Feeding",
                duration_minutes=15,
                priority=Priority.HIGH,
                category=Category.FEEDING,
                is_completed=False,
            ),
            Task(
                task_id="task_003",
                name="Enrichment",
                duration_minutes=45,
                priority=Priority.MEDIUM,
                category=Category.ENRICHMENT,
                is_completed=False,
            ),
            Task(
                task_id="task_004",
                name="Grooming",
                duration_minutes=20,
                priority=Priority.LOW,
                category=Category.GROOMING,
                is_completed=False,
            ),
        ]
    
    def test_filter_by_category(self):
        """Verify filtering tasks by category returns only matching tasks."""
        # Act: Filter for WALKS category
        walks = self.scheduler.filter_by_category(self.tasks, Category.WALKS)
        
        # Assert: Only walk task returned
        self.assertEqual(len(walks), 1)
        self.assertEqual(walks[0].name, "Walk")
    
    def test_filter_by_priority(self):
        """Verify filtering tasks by priority returns only matching tasks."""
        # Act: Filter for HIGH priority
        high_priority = self.scheduler.filter_by_priority(self.tasks, Priority.HIGH)
        
        # Assert: Two HIGH priority tasks returned
        self.assertEqual(len(high_priority), 2)
        names = [t.name for t in high_priority]
        self.assertIn("Walk", names)
        self.assertIn("Feeding", names)
    
    def test_filter_completed(self):
        """Verify filtering for completed tasks returns only completed ones."""
        # Act: Filter for completed tasks
        completed = self.scheduler.filter_completed(self.tasks, completed=True)
        
        # Assert: Only one completed task (Walk)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].name, "Walk")
        self.assertTrue(completed[0].is_completed)
    
    def test_filter_pending(self):
        """Verify filtering for pending tasks returns only incomplete ones."""
        # Act: Filter for pending (not completed) tasks
        pending = self.scheduler.filter_completed(self.tasks, completed=False)
        
        # Assert: Three pending tasks
        self.assertEqual(len(pending), 3)
        for task in pending:
            self.assertFalse(task.is_completed)
    
    def test_filter_by_pet_name(self):
        """Verify filtering tasks by pet name returns only tasks for that pet."""
        # Arrange: Update tasks with pet names
        self.tasks[0].pet_name = "Max"
        self.tasks[1].pet_name = "Bella"
        self.tasks[2].pet_name = "Max"
        self.tasks[3].pet_name = "Charlie"
        
        # Act: Filter for Max's tasks
        max_tasks = self.scheduler.filter_by_pet_name(self.tasks, "Max")
        
        # Assert: Two tasks for Max
        self.assertEqual(len(max_tasks), 2)
        for task in max_tasks:
            self.assertEqual(task.pet_name.lower(), "max")
    
    def test_filter_by_pet_name_case_insensitive(self):
        """Verify pet name filtering is case-insensitive."""
        # Arrange: Set pet names with mixed case
        self.tasks[0].pet_name = "Max"
        self.tasks[1].pet_name = "max"
        self.tasks[2].pet_name = "MAX"
        self.tasks[3].pet_name = "Charlie"
        
        # Act: Filter with different case variations
        max_tasks_lower = self.scheduler.filter_by_pet_name(self.tasks, "max")
        max_tasks_upper = self.scheduler.filter_by_pet_name(self.tasks, "MAX")
        
        # Assert: All variations return 3 tasks
        self.assertEqual(len(max_tasks_lower), 3)
        self.assertEqual(len(max_tasks_upper), 3)


class TestTaskRepositoryFiltering(unittest.TestCase):
    """Test cases for TaskRepository filtering methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo = TaskRepository()
        self.tasks = [
            Task(
                task_id="task_001",
                name="Walk 1",
                duration_minutes=30,
                priority=Priority.HIGH,
                category=Category.WALKS,
                is_completed=True,
                pet_id="pet_001",
            ),
            Task(
                task_id="task_002",
                name="Walk 2",
                duration_minutes=30,
                priority=Priority.HIGH,
                category=Category.WALKS,
                is_completed=False,
                pet_id="pet_001",
            ),
            Task(
                task_id="task_003",
                name="Feeding",
                duration_minutes=15,
                priority=Priority.MEDIUM,
                category=Category.FEEDING,
                is_completed=False,
                pet_id="pet_001",
            ),
        ]
        for task in self.tasks:
            self.repo.add_task(task)
    
    def test_get_tasks_by_category(self):
        """Verify repository returns only tasks in specified category."""
        # Act: Get all walk tasks
        walks = self.repo.get_tasks_by_category(Category.WALKS)
        
        # Assert: Two walk tasks returned
        self.assertEqual(len(walks), 2)
        for task in walks:
            self.assertEqual(task.category, Category.WALKS)
    
    def test_get_completed_tasks(self):
        """Verify repository returns only completed tasks."""
        # Act: Get completed tasks
        completed = self.repo.get_completed_tasks()
        
        # Assert: Only one completed task
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].name, "Walk 1")
        self.assertTrue(completed[0].is_completed)
    
    def test_get_pending_tasks(self):
        """Verify repository returns only pending (incomplete) tasks."""
        # Act: Get pending tasks
        pending = self.repo.get_pending_tasks()
        
        # Assert: Two pending tasks
        self.assertEqual(len(pending), 2)
        for task in pending:
            self.assertFalse(task.is_completed)
    
    def test_get_tasks_by_pet_name(self):
        """Verify repository returns only tasks for the specified pet name."""
        # Arrange: Set pet names for tasks
        self.tasks[0].pet_name = "Max"
        self.tasks[1].pet_name = "Bella"
        self.tasks[2].pet_name = "Max"
        # Re-add tasks with updated pet names
        self.repo = TaskRepository()
        for task in self.tasks:
            self.repo.add_task(task)
        
        # Act: Get tasks for Max
        max_tasks = self.repo.get_tasks_by_pet_name("Max")
        
        # Assert: Two tasks for Max
        self.assertEqual(len(max_tasks), 2)
        for task in max_tasks:
            self.assertEqual(task.pet_name.lower(), "max")
    
    def test_get_tasks_by_pet_name_case_insensitive(self):
        """Verify repository pet name queries are case-insensitive."""
        # Arrange: Set pet names with different cases
        self.tasks[0].pet_name = "Max"
        self.tasks[1].pet_name = "max"
        self.tasks[2].pet_name = "MAX"
        # Re-add tasks
        self.repo = TaskRepository()
        for task in self.tasks:
            self.repo.add_task(task)
        
        # Act: Query with different case variations
        max_lower = self.repo.get_tasks_by_pet_name("max")
        max_upper = self.repo.get_tasks_by_pet_name("MAX")
        max_mixed = self.repo.get_tasks_by_pet_name("MaX")
        
        # Assert: All case variations return 3 tasks
        self.assertEqual(len(max_lower), 3)
        self.assertEqual(len(max_upper), 3)
        self.assertEqual(len(max_mixed), 3)


class TestRecurringTasks(unittest.TestCase):
    """Test cases for recurring task auto-scheduling behavior."""

    def _make_task(self, task_id, frequency, due_date=None):
        return Task(
            task_id=task_id,
            name="Morning Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.WALKS,
            owner_id="owner_001",
            pet_id="pet_001",
            pet_name="Max",
            frequency=frequency,
            due_date=due_date,
        )

    # ── create_next_occurrence ────────────────────────────────────────────────

    def test_once_task_returns_none(self):
        """Non-recurring tasks should not generate a next occurrence."""
        task = self._make_task("t1", Frequency.ONCE, date(2026, 3, 29))
        task.mark_complete()
        self.assertIsNone(task.create_next_occurrence())

    def test_daily_task_advances_due_date_by_one_day(self):
        """Daily task's next occurrence should be due one day later."""
        task = self._make_task("t2", Frequency.DAILY, date(2026, 3, 29))
        task.mark_complete()
        next_task = task.create_next_occurrence()
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.due_date, date(2026, 3, 30))

    def test_weekly_task_advances_due_date_by_seven_days(self):
        """Weekly task's next occurrence should be due seven days later."""
        task = self._make_task("t3", Frequency.WEEKLY, date(2026, 3, 29))
        task.mark_complete()
        next_task = task.create_next_occurrence()
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.due_date, date(2026, 4, 5))

    def test_next_occurrence_is_not_completed(self):
        """Next occurrence should start as not completed."""
        task = self._make_task("t4", Frequency.DAILY, date(2026, 3, 29))
        task.mark_complete()
        next_task = task.create_next_occurrence()
        self.assertFalse(next_task.is_completed)

    def test_next_occurrence_inherits_attributes(self):
        """Next occurrence should carry over name, priority, category, etc."""
        task = self._make_task("t5", Frequency.DAILY, date(2026, 3, 29))
        task.mark_complete()
        next_task = task.create_next_occurrence()
        self.assertEqual(next_task.name, task.name)
        self.assertEqual(next_task.priority, task.priority)
        self.assertEqual(next_task.category, task.category)
        self.assertEqual(next_task.frequency, task.frequency)
        self.assertEqual(next_task.owner_id, task.owner_id)
        self.assertEqual(next_task.pet_id, task.pet_id)
        self.assertNotEqual(next_task.task_id, task.task_id)

    def test_next_occurrence_without_due_date_defaults_to_tomorrow_or_next_week(self):
        """If no due_date set, next occurrence uses today + delta."""
        daily_task = self._make_task("t6", Frequency.DAILY, None)
        daily_task.mark_complete()
        next_daily = daily_task.create_next_occurrence()
        self.assertEqual(next_daily.due_date, date.today() + timedelta(days=1))

        weekly_task = self._make_task("t7", Frequency.WEEKLY, None)
        weekly_task.mark_complete()
        next_weekly = weekly_task.create_next_occurrence()
        self.assertEqual(next_weekly.due_date, date.today() + timedelta(weeks=1))

    # ── TaskRepository.mark_task_complete ─────────────────────────────────────

    def test_repo_mark_complete_adds_next_daily_task(self):
        """mark_task_complete on a daily task should add its next occurrence to the repo."""
        repo = TaskRepository()
        task = self._make_task("t8", Frequency.DAILY, date(2026, 3, 29))
        repo.add_task(task)

        repo.mark_task_complete("t8")

        self.assertTrue(task.is_completed)
        self.assertEqual(len(repo.tasks), 2)
        next_task = repo.tasks[1]
        self.assertFalse(next_task.is_completed)
        self.assertEqual(next_task.due_date, date(2026, 3, 30))

    def test_repo_mark_complete_adds_next_weekly_task(self):
        """mark_task_complete on a weekly task should add its next occurrence to the repo."""
        repo = TaskRepository()
        task = self._make_task("t9", Frequency.WEEKLY, date(2026, 3, 29))
        repo.add_task(task)

        repo.mark_task_complete("t9")

        self.assertEqual(len(repo.tasks), 2)
        self.assertEqual(repo.tasks[1].due_date, date(2026, 4, 5))

    def test_repo_mark_complete_once_task_does_not_add_new_task(self):
        """mark_task_complete on a once task should not add any new task."""
        repo = TaskRepository()
        task = self._make_task("t10", Frequency.ONCE, date(2026, 3, 29))
        repo.add_task(task)

        result = repo.mark_task_complete("t10")

        self.assertIsNone(result)
        self.assertEqual(len(repo.tasks), 1)
        self.assertTrue(task.is_completed)

    def test_repo_mark_complete_returns_none_for_unknown_task_id(self):
        """mark_task_complete should return None if task_id not found."""
        repo = TaskRepository()
        result = repo.mark_task_complete("nonexistent")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
