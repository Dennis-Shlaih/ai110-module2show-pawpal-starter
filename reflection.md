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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
