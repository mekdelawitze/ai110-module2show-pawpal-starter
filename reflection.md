# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started by identifying three core actions a user should be able to perform: add a pet, schedule a task for a pet, and see today's schedule. For the initial UML I chose four classes, and I tried to give each one a single clear responsibility.

- `Task` represents one activity. It holds the description, time, frequency, and whether it is completed, and it can mark itself complete.
- `Pet` holds the pet's name and species along with its own list of tasks.
- `Owner` holds many pets and has a `get_all_tasks()` method so that every pet's tasks can be seen together.
- `Scheduler` is the "brain" of the app. It is given an `Owner` and organizes tasks across all of the pets, instead of looking at a single pet.

**b. Design changes**

Yes, my design changed once I started thinking about how the pieces would actually work together. I realized my first `Task` was missing some things.

- I added `due_date` because recurrence can't work without one. A daily task needs a "today + 1 day" to move to.
- I added `pet_name` because once the Scheduler flattens everyone's tasks with `get_all_tasks()`, it can't tell which pet a task belongs to. `Pet.add_task()` now sets it automatically.
- I added `Task.next_occurrence()` and `Scheduler.mark_task_complete()` so that a recurring task creates its next copy on the correct pet.
- I also added `duration_minutes` and `priority`, since the scenario mentions them.
- Times are now validated and zero-padded when a task is created, so sorting them as strings is safe.

My final diagram is in `diagrams/uml_final.mmd`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler mainly considers the date and time of a task, and then whether it is completed. Completed tasks are left out of today's schedule and ignored when checking for conflicts. Priority and duration are stored and shown in the app, but I would say they don't change the ordering yet. I decided that time mattered most because an owner's day is driven by when things need to happen, like a walk in the morning or medication at noon.

**b. Tradeoffs**

One tradeoff my scheduler makes is that it only flags conflicts when two tasks have the exact same date and time. It does not catch overlaps, so a 30-minute walk at 08:00 and a feeding at 08:15 would not be flagged, even though tasks have durations. I think this is reasonable for this project because exact matching is simple, easy to explain, and easy to test. Checking for overlapping time ranges would be the next step. I also made conflicts return a warning message instead of raising an error, so the owner can keep both tasks and decide for themselves what to move.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code throughout the project for brainstorming the UML, generating the class skeleton, implementing the algorithms, drafting tests, and writing up the README. I treated the different phases (design, core implementation, algorithms, testing, and the UI) as separate pieces of work. The prompts that helped most were the specific ones. For example, I told it that the Scheduler must read from `Owner.get_all_tasks()` and not from a single pet, and I asked for particular things like a `sorted()` lambda key for `HH:MM` strings and `timedelta` for recurrence.

**b. Judgment and verification**

One moment I did not just accept a more complicated approach was sorting. Instead of parsing every time into a `datetime` object, I kept the times as `HH:MM` strings and made sure they are zero-padded when a task is created. That way a simple `(due_date, time)` key sorts correctly, and `sort_by_time()` stays easy to read. I made a similar choice with conflict detection, keeping it as simple grouping instead of a more clever interval algorithm that would be harder to follow.

To verify the results, I ran `python main.py` and the pytest suite, which has 14 passing tests including edge cases like a pet with no tasks and a time entered as `"9:00"`. I also tested the Streamlit app by adding a pet, adding two tasks at the same time, checking that the conflict warning appeared, and marking a task complete.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, adding tasks to a pet, sorting across multiple pets, daily, weekly, and one-time recurrence, conflict detection, filtering by pet and status, empty owners and pets with no tasks, today's schedule leaving out future and completed tasks, and invalid input. These were important because they are the behaviors the UI depends on.

**b. Confidence**

I would say I am about 4 out of 5 confident that the scheduler works correctly. The core behaviors and edge cases I tested pass, but I can't say it has been fully covered. If I had more time, I would test overlapping durations, weekly recurrence across month and year boundaries, duplicate pet names, and completing tasks out of order.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the CLI-first workflow. Because I verified `pawpal_system.py` with `main.py` and pytest before touching the UI, connecting Streamlit was mostly just session state and display code, and I could trust the logic underneath it.

**b. What you would improve**

If I had another iteration, I would use priority and duration to build a real daily plan that explains why it chose that order, and I would detect overlapping time ranges. I would also let users edit and delete tasks in the app and save their data so it doesn't disappear when the session ends.

**c. Key takeaway**

I learned that being the lead architect means making the design decisions and checking the AI's work against them. The decisions were things like the Scheduler reading through the Owner, tasks knowing which pet they belong to, and conflicts warning instead of crashing. AI can produce code very quickly, but I think the judgment about what the system should do, and the verification that it actually does it, still has to come from the human.
