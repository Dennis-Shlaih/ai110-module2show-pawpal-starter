from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import Optional


# ── Enumerations ──────────────────────────────────────────────────────────────

class Priority(Enum):
    """Enumeration of task priority levels: HIGH, MEDIUM, LOW."""
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"


class Category(Enum):
    """Enumeration of pet care task categories: WALKS, FEEDING, MEDICATIONS, ENRICHMENT, GROOMING."""
    WALKS       = "walks"
    FEEDING     = "feeding"
    MEDICATIONS = "medications"
    ENRICHMENT  = "enrichment"
    GROOMING    = "grooming"


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class PetProfile:
    """Represents a pet with profile information including name, species, breed, and care preferences."""
    pet_id:      str
    name:        str
    age:         int
    species:     str
    breed:       str
    preferences: list[str] = field(default_factory=list)

    def update_profile(self, **kwargs) -> None:
        """Update pet profile attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_preferences(self) -> list[str]:
        """Retrieve pet preferences."""
        return self.preferences


@dataclass
class Task:
    """Represents a single pet care task with duration, priority, category, and completion status."""
    task_id:          str
    name:             str
    duration_minutes: int
    priority:         Priority
    category:         Category
    owner_id:         Optional[str] = None    # Reference to owner for easier lookups
    pet_id:           Optional[str] = None    # Reference to pet for easier lookups
    is_completed:     bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def update_task(self, **kwargs) -> None:
        """Update task attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'task_id':  # Prevent changing task_id
                setattr(self, key, value)


# ── Classes ───────────────────────────────────────────────────────────────────

class OwnerProfile:
    """Manages owner information, pets, and associated schedules."""
    def __init__(
        self,
        owner_id:               str,
        name:                   str,
        email:                  str,
        available_time_per_day: int,       # minutes
    ) -> None:
        self.owner_id               = owner_id
        self.name                   = name
        self.email                  = email
        self.available_time_per_day = available_time_per_day
        self.pet:       Optional[PetProfile] = None
        self.schedules: list["Schedule"]     = []

    def update_profile(self, **kwargs) -> None:
        """Update owner profile attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'owner_id':  # Prevent changing owner_id
                setattr(self, key, value)

    def get_available_time(self) -> int:
        """Return the owner's available time per day in minutes."""
        return self.available_time_per_day


class Scheduler:
    """Encapsulates scheduling algorithm logic.
    
    Responsible for sorting tasks, respecting constraints, and fitting them
    into available time slots. Separates algorithm from data representation.
    """
    
    def __init__(self):
        """Initialize the Scheduler."""
        pass
    
    def schedule_tasks(
        self,
        tasks:               list[Task],
        available_time:      int,
        pet_preferences:     list[str],
    ) -> tuple[list[Task], str]:
        """Generate an ordered schedule of tasks by priority and pet preferences, returning scheduled tasks and reasoning."""
        if not tasks:
            return [], "No tasks to schedule."
        
        # Priority order mapping
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        
        # Separate tasks into preference-matched and others
        preference_tasks = []
        other_tasks = []
        
        for task in tasks:
            if task.category.value in pet_preferences:
                preference_tasks.append(task)
            else:
                other_tasks.append(task)
        
        # Sort each group by priority
        preference_tasks.sort(key=lambda t: priority_order[t.priority])
        other_tasks.sort(key=lambda t: priority_order[t.priority])
        
        # Combine: preferences first, then others
        sorted_tasks = preference_tasks + other_tasks
        
        # Fit tasks into available time
        scheduled = []
        total_time = 0
        skipped = []
        
        for task in sorted_tasks:
            if total_time + task.duration_minutes <= available_time:
                scheduled.append(task)
                total_time += task.duration_minutes
            else:
                skipped.append(task.name)
        
        # Build reasoning
        reasoning = f"Scheduled {len(scheduled)} of {len(tasks)} tasks in {total_time} minutes. "
        reasoning += f"Prioritized tasks matching pet preferences: {', '.join([t.category.value for t in preference_tasks[:3]])}. "
        if skipped:
            reasoning += f"Could not fit: {', '.join(skipped)}."
        
        return scheduled, reasoning


class Schedule:
    """Represents a daily schedule containing ordered tasks and scheduling reasoning for a specific owner."""
    def __init__(
        self,
        schedule_id: str,
        date:        date,
        owner:       OwnerProfile,
        scheduler:   Optional[Scheduler] = None,
    ) -> None:
        """Initialize a daily schedule for an owner with optional custom scheduler."""
        self.schedule_id            = schedule_id
        self.date                   = date
        self.owner                  = owner
        self.scheduler              = scheduler or Scheduler()
        self.tasks:                   list[Task] = []
        self.total_duration_minutes:  int        = 0
        self.reasoning:               str        = ""

    def generate_schedule(self, available_tasks: list[Task]) -> None:
        """Generate the daily schedule using the Scheduler based on available tasks."""
        if not self.owner.pet:
            self.reasoning = "Error: No pet associated with owner."
            return
        
        pet_prefs = self.owner.pet.get_preferences()
        scheduled_tasks, reasoning = self.scheduler.schedule_tasks(
            available_tasks,
            self.owner.get_available_time(),
            pet_prefs,
        )
        
        self.tasks = scheduled_tasks
        self.reasoning = reasoning
        self.total_duration_minutes = sum(t.duration_minutes for t in self.tasks)

    def add_task(self, task: Task) -> bool:
        """Add a task to the schedule if it fits within available time, returning success status."""
        available_time = self.owner.get_available_time()
        if self.total_duration_minutes + task.duration_minutes <= available_time:
            self.tasks.append(task)
            self.total_duration_minutes += task.duration_minutes
            return True
        return False

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the schedule by task_id, returning success status."""
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                self.total_duration_minutes -= task.duration_minutes
                self.tasks.pop(i)
                return True
        return False

    def explain_reasoning(self) -> str:
        """Return the scheduling reasoning explanation."""
        return self.reasoning


class TaskRepository:
    """Centralized task management and queries.
    
    Provides convenient methods for finding tasks by owner, pet, priority, etc.
    """
    
    def __init__(self):
        """Initialize an empty task repository."""
        self.tasks: list[Task] = []
    
    def add_task(self, task: Task) -> None:
        """Add a new task to the repository."""
        self.tasks.append(task)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the repository by task_id, returning success status."""
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                self.tasks.pop(i)
                return True
        return False
    
    def get_tasks_for_owner(self, owner_id: str) -> list[Task]:
        """Retrieve all tasks for a specific owner."""
        return [task for task in self.tasks if task.owner_id == owner_id]
    
    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Retrieve all tasks for a specific pet."""
        return [task for task in self.tasks if task.pet_id == pet_id]
    
    def get_tasks_by_priority(self, priority: Priority) -> list[Task]:
        """Retrieve all tasks with a specific priority level."""
        return [task for task in self.tasks if task.priority == priority]
