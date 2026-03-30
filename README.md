# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

**Core**
- Create and manage owner and pet profiles with preferences and daily time budgets
- Add pet care tasks with name, duration, priority, category, frequency, and optional start time
- Generate a daily schedule that fits tasks within the owner's available time and explains its reasoning

**Sorting & Filtering**
- Sort tasks by priority (HIGH → MEDIUM → LOW), duration, or category
- Filter tasks by category, priority, completion status, or pet name
- All sorting and filtering is non-destructive — original task order is preserved

**Conflict Detection**
- Assign a start time to any task; the scheduler checks every pair for time-window overlaps
- Conflicts are surfaced as human-readable warnings in both the CLI and Streamlit UI — the program never crashes

**Recurring Tasks**
- Tasks can be marked as `ONCE`, `DAILY`, or `WEEKLY`
- Completing a recurring task automatically creates the next occurrence with an advanced due date
- One-time tasks complete normally with no follow-up created

**Algorithms Implemented**
- Greedy fit scheduling — tasks sorted by preference match then priority, added until the time budget is exhausted
- Pairwise overlap detection — O(n²) interval check using `start < other_end AND other_start < end`
- Composite tuple sort — preference boost combined with priority ordering in a single sort pass
- Automatic recurrence — due date advanced by a fixed `timedelta` (1 day or 7 days) on task completion

---

## Smarter Scheduling

The `Scheduler` class supports sorting tasks by duration, priority, or category, and filtering by category, priority, completion status, or pet name. `TaskRepository` provides matching query methods for persistent lookups.

Tasks can be assigned a `scheduled_start` (minutes from midnight); `Scheduler.detect_conflicts()` checks for time-window overlaps and returns plain warning strings without crashing the program.

Tasks support a `frequency` field (`ONCE`, `DAILY`, `WEEKLY`). Calling `TaskRepository.mark_task_complete()` on a recurring task automatically adds the next occurrence with an advanced due date.

---

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/
```
### Test Suite
38 tests cover task completion and idempotency, adding tasks to the repository, updating task attributes, scheduler sorting (duration, priority, category) and filtering (category, priority, status, pet name), recurring task recurrence logic (daily and weekly), and conflict detection for overlapping scheduled times.

### System Reliability
4 / 5 Stars: The core logic is well covered. All 38 tests pass consistently. One star is missing because right now, it misses edge case tests, such as a task that spans midnight or negative duration.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


