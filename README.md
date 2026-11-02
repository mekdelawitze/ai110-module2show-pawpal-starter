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

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## ✨ Features

- **Owners, pets and tasks** modelled with Python dataclasses (`Owner`, `Pet`, `Task`) plus a `Scheduler` that reads every pet's tasks through `Owner.get_all_tasks()`.
- **Sorting by time**: tasks are ordered by due date, then `HH:MM`.
- **Filtering** by pet name and/or completion status.
- **Conflict warnings**: tasks at the same date and time (same or different pets) produce a warning message instead of an error.
- **Recurring tasks**: completing a daily or weekly task automatically creates the next occurrence.
- **Streamlit UI** with persistent session state, a sorted "Today's schedule" table and warnings.

## 🏗️ Implementation Summary

All logic lives in `pawpal_system.py`. An `Owner` has many `Pet`s, and a `Pet` has many `Task`s. The `Scheduler` is constructed with an `Owner` and never touches a single pet directly. It calls `Owner.get_all_tasks()` and then sorts, filters, checks conflicts and handles completion. `main.py` is a CLI demo, `app.py` is the Streamlit front end, and `tests/test_pawpal.py` holds the pytest suite. UML: `diagrams/uml.mmd` (initial draft) and `diagrams/uml_final.mmd` (final).

## 🖥️ Sample Output

Output of `python main.py`:

```
=== Today's Schedule for Jordan (2026-11-01) ===

Today's Schedule (sorted by time)
---------------------------------
  [ ] 2026-11-01  08:00  Mochi   Morning walk     (daily, 30 min, high)
  [ ] 2026-11-01  08:00  Luna    Breakfast        (daily, 10 min, medium)
  [ ] 2026-11-01  12:30  Luna    Flea medication  (weekly, 15 min, high)
  [ ] 2026-11-01  15:15  Mochi   Vet appointment  (once, 60 min, medium)
  [ ] 2026-11-01  18:00  Mochi   Evening walk     (daily, 30 min, high)

Warnings
--------
  ! Conflict on 2026-11-01 at 08:00: Morning walk (Mochi), Breakfast (Luna)

Completed 'Breakfast' -> next occurrence scheduled for 2026-11-02

Luna's tasks (filter by pet)
----------------------------
  [x] 2026-11-01  08:00  Luna    Breakfast        (daily, 10 min, medium)
  [ ] 2026-11-01  12:30  Luna    Flea medication  (weekly, 15 min, high)
  [ ] 2026-11-02  08:00  Luna    Breakfast        (daily, 10 min, medium)

Completed tasks (filter by status)
----------------------------------
  [x] 2026-11-01  08:00  Luna    Breakfast        (daily, 10 min, medium)
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The 14 tests cover: task completion and adding tasks to a pet; chronological sorting across pets (including time normalization such as `9:00` to `09:00`); daily, weekly and one-off recurrence; conflict detection (same pet, different pets, completed tasks ignored, different times); filtering by pet and status; empty owner and pet with no tasks; today's schedule excluding future and completed tasks; and input validation.

```
platform darwin -- Python 3.15.0, pytest-9.2.0, pluggy-1.7.0 -- /Users/mek/AI110/ai110-module2show-pawpal-starter/.venv/bin/python
tests/test_pawpal.py::test_mark_complete_changes_status PASSED
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED
tests/test_pawpal.py::test_sorting_is_chronological_across_pets PASSED
tests/test_pawpal.py::test_time_is_normalized_so_sorting_is_correct PASSED
tests/test_pawpal.py::test_daily_recurrence_creates_next_day_task PASSED
tests/test_pawpal.py::test_weekly_recurrence_adds_seven_days PASSED
tests/test_pawpal.py::test_one_off_task_does_not_recur PASSED
tests/test_pawpal.py::test_conflict_detected_for_same_time_different_pets PASSED
tests/test_pawpal.py::test_conflict_detected_for_same_pet PASSED
tests/test_pawpal.py::test_no_conflict_when_times_differ_or_task_completed PASSED
tests/test_pawpal.py::test_filtering_by_pet_and_status PASSED
tests/test_pawpal.py::test_pet_with_no_tasks_and_empty_owner PASSED
tests/test_pawpal.py::test_todays_schedule_excludes_future_and_completed PASSED
tests/test_pawpal.py::test_invalid_task_input_rejected PASSED
============================== 14 passed in 0.01s ==============================
```

**Confidence level:** ★★★★☆ (4/5). Core behaviours and edge cases pass. Overlapping durations and month/year rollover of weekly tasks are not tested beyond what `timedelta` guarantees.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | `sorted()` with a lambda key `(due_date, time)`; times are zero-padded `HH:MM` so string order is chronological |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Both filters are optional and combine; `get_todays_schedule()` returns pending tasks due today |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups pending tasks by exact (date, time) and returns warning strings; it never raises |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Daily adds `timedelta(days=1)`, weekly adds `timedelta(weeks=1)`; one-off tasks return `None` |

### How dates and times work

Each `Task` stores its date and time separately:

- `due_date` is a `datetime.date` and defaults to `date.today()`.
- `time` is a 24-hour `"HH:MM"` string (for example `"08:00"`). It is validated and zero-padded, so `"9:00"` becomes `"09:00"`.

```python
from datetime import date

Task("Morning walk", "08:00", "daily")                          # due today
Task("Vet visit", "15:15", "once", due_date=date(2026, 11, 5))  # due on a specific day
```

A conflict means two pending tasks have the exact same `(due_date, time)`. Overlapping durations are not checked.

## 📸 Demo Walkthrough

Run the app with `streamlit run app.py`.

1. **Add a pet**: enter a name and species in "Add a pet". The `Pet` is stored on the `Owner` in `st.session_state`, so it survives reruns.
2. **Schedule a task**: pick the pet, description, time, repeat frequency, duration and priority, then click "Add task".
3. **View today's schedule**: the "Today's schedule" table shows pending tasks sorted by time via `Scheduler.sort_by_time()`.
4. **See conflict warnings**: if two tasks share a time, a yellow `st.warning` names them and suggests moving one.
5. **Complete a task**: click its ✅ button. Daily and weekly tasks reappear on their next due date.
6. **Filter**: in "All tasks", filter by pet and by pending or completed.

Sample CLI output from `python main.py`:

```
=== Today's Schedule for Jordan (2026-11-01) ===

Today's Schedule (sorted by time)
---------------------------------
  [ ] 2026-11-01  08:00  Mochi   Morning walk     (daily, 30 min, high)
  [ ] 2026-11-01  08:00  Luna    Breakfast        (daily, 10 min, medium)
  [ ] 2026-11-01  12:30  Luna    Flea medication  (weekly, 15 min, high)
  [ ] 2026-11-01  15:15  Mochi   Vet appointment  (once, 60 min, medium)
  [ ] 2026-11-01  18:00  Mochi   Evening walk     (daily, 30 min, high)

Warnings
--------
  ! Conflict on 2026-11-01 at 08:00: Morning walk (Mochi), Breakfast (Luna)

Completed 'Breakfast' -> next occurrence scheduled for 2026-11-02

Luna's tasks (filter by pet)
----------------------------
  [x] 2026-11-01  08:00  Luna    Breakfast        (daily, 10 min, medium)
  [ ] 2026-11-01  12:30  Luna    Flea medication  (weekly, 15 min, high)
  [ ] 2026-11-02  08:00  Luna    Breakfast        (daily, 10 min, medium)

Completed tasks (filter by status)
----------------------------------
  [x] 2026-11-01  08:00  Luna    Breakfast        (daily, 10 min, medium)
```
