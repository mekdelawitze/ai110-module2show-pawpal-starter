from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def setup():
    owner = Owner("Jordan")
    mochi, luna = Pet("Mochi"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner, mochi, luna, Scheduler(owner)


def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi")
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Feed", "09:00"))
    assert len(pet.tasks) == 2
    assert pet.tasks[0].pet_name == "Mochi"


def test_sorting_is_chronological_across_pets(setup):
    _, mochi, luna, scheduler = setup
    mochi.add_task(Task("Evening", "18:00"))
    luna.add_task(Task("Morning", "07:30"))
    mochi.add_task(Task("Noon", "12:00"))
    assert [t.time for t in scheduler.sort_by_time()] == ["07:30", "12:00", "18:00"]


def test_time_is_normalized_so_sorting_is_correct(setup):
    _, mochi, _, scheduler = setup
    mochi.add_task(Task("Late", "10:00"))
    mochi.add_task(Task("Early", "9:00"))
    assert [t.description for t in scheduler.sort_by_time()] == ["Early", "Late"]


def test_daily_recurrence_creates_next_day_task(setup):
    _, mochi, _, scheduler = setup
    task = Task("Walk", "08:00", "daily")
    mochi.add_task(task)
    new = scheduler.mark_task_complete(task)
    assert task.completed
    assert new.due_date == date.today() + timedelta(days=1)
    assert new.completed is False and new in mochi.tasks and len(mochi.tasks) == 2


def test_weekly_recurrence_adds_seven_days(setup):
    _, mochi, _, scheduler = setup
    task = Task("Meds", "08:00", "weekly")
    mochi.add_task(task)
    assert scheduler.mark_task_complete(task).due_date == date.today() + timedelta(days=7)


def test_one_off_task_does_not_recur(setup):
    _, mochi, _, scheduler = setup
    task = Task("Vet", "08:00", "once")
    mochi.add_task(task)
    assert scheduler.mark_task_complete(task) is None
    assert len(mochi.tasks) == 1


def test_conflict_detected_for_same_time_different_pets(setup):
    _, mochi, luna, scheduler = setup
    mochi.add_task(Task("Walk", "08:00"))
    luna.add_task(Task("Feed", "08:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1 and "08:00" in warnings[0]


def test_conflict_detected_for_same_pet(setup):
    _, mochi, _, scheduler = setup
    mochi.add_task(Task("Walk", "08:00"))
    mochi.add_task(Task("Feed", "08:00"))
    assert len(scheduler.detect_conflicts()) == 1


def test_no_conflict_when_times_differ_or_task_completed(setup):
    _, mochi, _, scheduler = setup
    mochi.add_task(Task("Walk", "08:00"))
    done = Task("Feed", "08:00")
    mochi.add_task(done)
    done.mark_complete()
    mochi.add_task(Task("Play", "09:00"))
    assert scheduler.detect_conflicts() == []


def test_filtering_by_pet_and_status(setup):
    _, mochi, luna, scheduler = setup
    walk = Task("Walk", "08:00")
    mochi.add_task(walk)
    luna.add_task(Task("Feed", "09:00"))
    walk.mark_complete()
    assert [t.description for t in scheduler.filter_tasks(pet_name="luna")] == ["Feed"]
    assert scheduler.filter_tasks(completed=True) == [walk]
    assert scheduler.filter_tasks(pet_name="Mochi", completed=False) == []


def test_pet_with_no_tasks_and_empty_owner():
    scheduler = Scheduler(Owner("Empty"))
    assert scheduler.get_todays_schedule() == []
    assert scheduler.detect_conflicts() == []
    owner = Owner("O")
    owner.add_pet(Pet("Solo"))
    assert Scheduler(owner).sort_by_time() == []


def test_todays_schedule_excludes_future_and_completed(setup):
    _, mochi, _, scheduler = setup
    mochi.add_task(Task("Today", "08:00"))
    mochi.add_task(Task("Tomorrow", "07:00", due_date=date.today() + timedelta(days=1)))
    mochi.tasks[-1].mark_complete()
    assert [t.description for t in scheduler.get_todays_schedule()] == ["Today"]


def test_invalid_task_input_rejected():
    with pytest.raises(ValueError):
        Task("Bad", "25:00")
    with pytest.raises(ValueError):
        Task("Bad", "08:00", frequency="hourly")
