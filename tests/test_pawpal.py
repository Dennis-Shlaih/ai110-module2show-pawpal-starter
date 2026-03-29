"""
Unit tests for the PawPal+ system.

Tests validate core functionality of Task, Pet, Owner, and Scheduler classes.
"""

import unittest
from datetime import date
import sys
from pathlib import Path

# Add parent directory to path to import pawpal_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from pawpal_system import (
    Task,
    Priority,
    Category,
    PetProfile,
    TaskRepository,
    OwnerProfile,
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


if __name__ == "__main__":
    unittest.main()
