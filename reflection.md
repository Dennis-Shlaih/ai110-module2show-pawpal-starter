# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Core user actions the PawPal+ system enables:
1. **Manage Pet & Owner Profile** – A user can enter and store basic information about themselves and their pet (name, age, preferences, available time per day).
2. **Create and Manage Care Tasks** – A user can add, edit, and organize pet care tasks with attributes including task name, duration, priority level, and category (walks, feeding, medications, enrichment, grooming, etc.).
3. **Generate and View Daily Schedule** – A user can request the system to generate a daily schedule that organizes tasks within available time, respects priority constraints, and explains the reasoning behind the schedule order.

Classes and responsibilities:
- **OwnerProfile**: Stores owner information (name, email, available time per day). Maintains a reference to the associated pet and a collection of schedules. Responsible for owner profile updates and retrieving available time.
- **PetProfile**: Stores pet information (name, age, species, breed, preferences). Handles pet profile updates and preference queries.
- **Task**: Represents a single care task with duration (in minutes), priority (HIGH/MEDIUM/LOW), and category (walks, feeding, medications, enrichment, grooming). Can be marked complete and updated.
- **Schedule**: Represents a daily schedule for a specific date. Contains an ordered list of tasks, tracks total duration, and generates explanations for the scheduling decisions.
- **Priority & Category**: Enumerations defining task priority levels and task types respectively.

**b. Design changes**

**Issue identified**: The current design has a logic bottleneck in the Schedule class. All scheduling logic (sorting tasks by priority, fitting them into available time slots, respecting owner preferences) will be implemented in `Schedule.generate_schedule()`, which could make this method complex and difficult to test independently.

**Recommended change**: Introduce a separate **Scheduler** class responsible for the scheduling algorithm. The Scheduler would take tasks, constraints (available time, priorities, preferences), and produce an ordered list of tasks. This separates the scheduling algorithm from the schedule data representation, making the code more testable and maintainable. Schedule would then use Scheduler to generate its plan.

**Secondary consideration**: Tasks currently have no direct reference to their owner or pet. This means finding all tasks for a specific pet requires iterating through all of that owner's schedules. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: available time per day (hard cap in minutes), task priority (HIGH, MEDIUM, LOW), and pet preferences (preferred categories like "walks" or "enrichment"). Tasks matching pet preferences are grouped first, then sorted by priority within each group; tasks are then added until the time budget is exhausted.

Time was treated as the hardest constraint because no schedule can exceed an owner's actual availability. Priority came second since pet care has non-negotiable tasks (medications, feeding) that must be addressed before optional ones. Preferences were applied as a boost on top of priority to personalize the schedule without overriding safety-critical tasks.

**b. Tradeoffs**

The scheduler uses a greedy fit strategy: it works through tasks in priority/preference order and adds each one if it fits in the remaining time, skipping it permanently if it does not. This means a single long HIGH priority task could consume enough time to crowd out several shorter MEDIUM tasks that would have collectively fit.

This tradeoff is reasonable for pet care because correctness matters more than time efficiency — a medication task must be scheduled even if it leaves less room for enrichment. A more optimal bin-packing approach would add significant complexity with little practical benefit at the scale of one pet's daily routine.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I primarily used Claude AI after I came up with my initial design plan. I used it to create a UML diagram that matched the system design, write the boilerplate code, and help with much of the debugging while implementing functionality.

The most helpful prompts were the ones that were specific, yet concise. If I asked Claude to do something with multiple steps in great detail, it tends to miss the big picture. When I started to break the problem into smaller steps, each being a part of a separate message, Claude did a much better job solving the problem and implementing my solution.

**b. Judgment and verification**

One instance where I did not accept an AI suggestion was when Claude wanted to replace the schedule_tasks() algorithm with a more pythonic single sorted() method. While both have similar efficiencies of O(nlogn), I decided to go with the slightly longer (10 lines vs 6 lines) algorithm even though more space is allocated (2 extra lists). At this stage, there wouldn't be any noticeable difference in performance, and the single sorted() approach would be less readable for someone not as familiar with Python.

Throughout the project, I verified what the AI suggested by reading the code line-by-line and making sure it made sense. If it passed this scan, I would then make sure the solution matched my design expectations. Finally, I would evaluate the solution by testing it in either main.py or the demo, and recommend changes if necessary.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers five main areas: task completion (marking complete, idempotency), task management (adding to the repository, updating attributes, preventing task ID changes), scheduler sorting (duration ascending/descending, priority order, category clustering), scheduler filtering (by category, priority, completion status, and pet name including case-insensitivity), recurring task logic (daily and weekly due date advancement, attribute inheritance, no next occurrence for once tasks), and conflict detection (overlapping windows flagged, back-to-back windows not flagged, tasks without a start time safely ignored).

These tests were important because the scheduler's correctness is not obvious from reading the code alone, a greedy fit algorithm can silently produce wrong output if the sort order or time comparison is off by one. Testing boundary cases like exact back-to-back tasks (no overlap) and completing a recurring task with no due date gave confidence that edge inputs wouldn't break the system.

**b. Confidence**

I would say I'm mostly confident. The core logic is well covered, and all 38 tests in the test suite pass consistently. However, it doesn't cover all edge cases. For example, a task with a negative or zero duration, or a task that spans midnight.

---

## 5. Reflection

**a. What went well**

The parts of the project I'm most satisfied with are the system architecture and sorting algorithms.

**b. What you would improve**

If I had another attempt at this project, I believe that I would've spent more time testing edge cases in the program. Also, I likely would've included more functionality to it such, as the ability to delete tasks.

**c. Key takeaway**

One important thing I learned about working with AI is that you must give it thoughtful prompts, or it will not work optimally. It is crucial to spend a decent amount of time designing the system architecture even before thinking about using AI to implement your idea, and even when you've gotten to the state where AI is making suggestions, you must still verify it and make changes if necessary.
