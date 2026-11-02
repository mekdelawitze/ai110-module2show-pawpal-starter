"""CLI demo for the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title, tasks):
    """Print a titled, aligned list of tasks."""
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (none)")
    for t in tasks:
        mark = "x" if t.completed else " "
        print(f"  [{mark}] {t.due_date}  {t.time}  {t.pet_name:<7} {t.description:<16} "
              f"({t.frequency}, {t.duration_minutes} min, {t.priority})")


def main():
    owner = Owner("Jordan")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of order; two share 08:00 to trigger a conflict.
    mochi.add_task(Task("Evening walk", "18:00", "daily", duration_minutes=30, priority="high"))
    mochi.add_task(Task("Morning walk", "08:00", "daily", duration_minutes=30, priority="high"))
    luna.add_task(Task("Breakfast", "08:00", "daily", duration_minutes=10))
    luna.add_task(Task("Flea medication", "12:30", "weekly", priority="high"))
    mochi.add_task(Task("Vet appointment", "15:15", "once", duration_minutes=60))

    scheduler = Scheduler(owner)

    print(f"=== Today's Schedule for {owner.name} ({date.today()}) ===")
    print_tasks("Today's Schedule (sorted by time)", scheduler.get_todays_schedule())

    print("\nWarnings")
    print("--------")
    for warning in scheduler.detect_conflicts() or ["(no conflicts)"]:
        print(f"  ! {warning}")

    breakfast = luna.tasks[0]
    new_task = scheduler.mark_task_complete(breakfast)
    print(f"\nCompleted '{breakfast.description}' -> next occurrence scheduled for {new_task.due_date}")

    print_tasks("Luna's tasks (filter by pet)", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")))
    print_tasks("Completed tasks (filter by status)", scheduler.filter_tasks(completed=True))


if __name__ == "__main__":
    main()
