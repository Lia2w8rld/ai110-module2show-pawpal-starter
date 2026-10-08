"""Demo script for PawPal+.

Builds one owner with two pets and a handful of care tasks, then prints
today's schedule to the terminal, followed by the sorting and filtering demos.

Run with: python main.py
"""

from datetime import date, time

from pawpal_system import CareTask, Frequency, Owner, Pet, Priority, Scheduler, TimeOfDay

# Order the parts of the day run in, so tasks print in the order they happen.
TIME_ORDER = [TimeOfDay.MORNING, TimeOfDay.AFTERNOON, TimeOfDay.EVENING, TimeOfDay.ANY]


def build_owner() -> Owner:
    """Set up the sample owner, pets, and care tasks.

    Tasks are added deliberately out of clock order so sort_by_time() has
    real work to do.
    """
    biscuit = Pet(name="Biscuit", species="dog")
    biscuit.add_task(
        CareTask(
            title="Evening feeding",
            duration_minutes=10,
            priority=Priority.HIGH,
            preferred_time=TimeOfDay.EVENING,
            scheduled_time=time(18, 0),
        )
    )
    # No scheduled_time, so this one should sort last.
    biscuit.add_task(
        CareTask(
            title="Brush coat",
            duration_minutes=15,
            priority=Priority.LOW,
        )
    )
    biscuit.add_task(
        CareTask(
            title="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            preferred_time=TimeOfDay.MORNING,
            scheduled_time=time(8, 0),
        )
    )

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(
        CareTask(
            title="Puzzle feeder",
            duration_minutes=15,
            priority=Priority.MEDIUM,
            preferred_time=TimeOfDay.AFTERNOON,
            scheduled_time=time(13, 0),
        )
    )
    # Same time as Biscuit's walk but lower priority, to show the tie-break.
    mochi.add_task(
        CareTask(
            title="Fresh water",
            duration_minutes=5,
            priority=Priority.LOW,
            preferred_time=TimeOfDay.MORNING,
            scheduled_time=time(8, 0),
        )
    )
    mochi.add_task(
        CareTask(
            title="Litter box scoop",
            duration_minutes=5,
            priority=Priority.LOW,
            preferred_time=TimeOfDay.MORNING,
            scheduled_time=time(7, 30),
        )
    )

    owner = Owner(name="Lia")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    return owner


def print_schedule(owner: Owner, day: date) -> None:
    """Print every pet's tasks for `day`, grouped by part of the day."""
    print(f"Today's Schedule for {owner.name} -- {day:%A, %B %d, %Y}")
    print("=" * 46)

    for slot in TIME_ORDER:
        # Pair each task with its pet so the printout can name the pet.
        rows = [
            (pet, task)
            for pet in owner.pets
            for task in pet.tasks
            if task.preferred_time is slot
        ]
        if not rows:
            continue

        # Most important tasks first inside each part of the day.
        rows.sort(key=lambda row: row[1].priority.rank())

        print(f"\n{slot.value.title()}")
        for pet, task in rows:
            print(
                f"  - {task.title} ({pet.name}, {pet.species})"
                f" -- {task.duration_minutes} min [priority: {task.priority.value}]"
            )

    total = sum(task.duration_minutes for pet in owner.pets for task in pet.tasks)
    print(f"\nTotal care time today: {total} min across {len(owner.pets)} pets")


def print_pairs(heading: str, pairs: list[tuple[Pet, CareTask]]) -> None:
    """Print a list of (pet, task) pairs under a heading, one per line."""
    print(f"\n{heading}")
    print("-" * len(heading))
    if not pairs:
        print("  (none)")
    for pet, task in pairs:
        when = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "--:--"
        status = "done" if task.completed else "todo"
        print(
            f"  {when}  {task.title:<18} {pet.name:<8}"
            f" [priority: {task.priority.value:<6}] [{status}]"
        )


def demo_sort_and_filter(owner: Owner) -> None:
    """Show sort_by_time() and filter_tasks() on the sample data."""
    scheduler = Scheduler(owner=owner)

    print("\n" + "=" * 46)
    print("Sorting and filtering demo")
    print("=" * 46)

    print_pairs("As added (unsorted)", owner.tasks_with_pets())
    print_pairs("Sorted by time", scheduler.sort_by_time())

    print_pairs("Filter: pet_name='Mochi'", scheduler.filter_tasks(pet_name="Mochi"))

    # Finish one task so the completion filters have something to split on.
    owner.pets[1].tasks[2].mark_complete()  # Mochi's litter box scoop
    print_pairs("Filter: completed=True", scheduler.filter_tasks(completed=True))
    print_pairs("Filter: completed=False", scheduler.filter_tasks(completed=False))

    # Filters combine, and the result can be fed straight into the sorter.
    print_pairs(
        "Mochi's remaining tasks, sorted",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)),
    )


def demo_recurring(owner: Owner) -> None:
    """Complete a daily, a weekly, and a one-time task and show what comes next."""
    biscuit = owner.pets[0]
    today = date.today()
    print("\n" + "=" * 46)
    print(f"Recurring tasks demo (today is {today:%a %b %d})")
    print("=" * 46)

    walk = biscuit.tasks[2]  # Morning walk, daily by default
    bath = CareTask(title="Bath", duration_minutes=20, frequency=Frequency.WEEKLY)
    vet = CareTask(title="Vet nail trim", duration_minutes=15, frequency=Frequency.ONCE)
    biscuit.add_task(bath)
    biscuit.add_task(vet)

    for task in (walk, bath, vet):
        before = len(biscuit.tasks)
        next_task = biscuit.complete_task(task)
        print(f"\nCompleted '{task.title}' ({task.frequency.value}) -> completed={task.completed}")
        if next_task is None:
            print("  No new task created (one-time task)")
        else:
            gap = (next_task.due_date - today).days
            print(
                f"  New task: '{next_task.title}' due {next_task.due_date:%a %b %d}"
                f" (+{gap} day{'s' if gap != 1 else ''}), completed={next_task.completed}"
            )
        print(f"  Biscuit's task count: {before} -> {len(biscuit.tasks)}")

    print_pairs("Biscuit's tasks now", Scheduler(owner=owner).filter_tasks(pet_name="Biscuit"))


def demo_conflicts() -> None:
    """Show detect_conflicts() finding same-time tasks across and within pets."""
    # Fresh owner, so tasks added by the recurring demo don't muddy the result.
    owner = build_owner()
    biscuit = owner.pets[0]
    # Same pet, same time as Biscuit's 18:00 evening feeding.
    biscuit.add_task(
        CareTask(title="Give medication", duration_minutes=5, scheduled_time=time(18, 0))
    )
    # Already in build_owner(): Morning walk (Biscuit) and Fresh water (Mochi)
    # both at 08:00 -- a cross-pet clash. Litter box 07:30 and Puzzle feeder
    # 13:00 are alone at their times; Brush coat has no time at all.

    print("\n" + "=" * 46)
    print("Conflict detection demo")
    print("=" * 46)
    print_pairs("All tasks", owner.tasks_with_pets())

    conflicts = Scheduler(owner=owner).detect_conflicts()
    print()
    if not conflicts:
        print("No conflicts found.")
    for slot, group in conflicts.items():
        pet_names = {pet.name for pet, _ in group}
        kind = "same pet" if len(pet_names) == 1 else "different pets"
        print(f"WARNING: {len(group)} tasks at {slot:%H:%M} ({kind}):")
        for pet, task in group:
            print(f"  - {task.title} ({pet.name})")

    flagged = {id(task) for group in conflicts.values() for _, task in group}
    clear = [t.title for _, t in owner.tasks_with_pets() if t.scheduled_time and id(t) not in flagged]
    ignored = [t.title for _, t in owner.tasks_with_pets() if t.scheduled_time is None]
    print(f"\nNot conflicts (unique times): {', '.join(clear)}")
    print(f"Ignored (unscheduled): {', '.join(ignored)}")


def main() -> None:
    owner = build_owner()
    print_schedule(owner, date.today())
    demo_sort_and_filter(owner)
    demo_recurring(owner)
    demo_conflicts()


if __name__ == "__main__":
    main()
