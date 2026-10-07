"""Demo script for PawPal+.

Builds one owner with two pets and a handful of care tasks, then prints
today's schedule to the terminal.

Run with: python main.py
"""

from datetime import date

from pawpal_system import CareTask, Owner, Pet, Priority, TimeOfDay

# Order the parts of the day run in, so tasks print in the order they happen.
TIME_ORDER = [TimeOfDay.MORNING, TimeOfDay.AFTERNOON, TimeOfDay.EVENING, TimeOfDay.ANY]


def build_owner() -> Owner:
    """Set up the sample owner, pets, and care tasks."""
    biscuit = Pet(name="Biscuit", species="dog")
    biscuit.add_task(
        CareTask(
            title="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            preferred_time=TimeOfDay.MORNING,
        )
    )
    biscuit.add_task(
        CareTask(
            title="Evening feeding",
            duration_minutes=10,
            priority=Priority.HIGH,
            preferred_time=TimeOfDay.EVENING,
        )
    )

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(
        CareTask(
            title="Puzzle feeder",
            duration_minutes=15,
            priority=Priority.MEDIUM,
            preferred_time=TimeOfDay.AFTERNOON,
        )
    )
    mochi.add_task(
        CareTask(
            title="Litter box scoop",
            duration_minutes=5,
            priority=Priority.LOW,
            preferred_time=TimeOfDay.MORNING,
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


def main() -> None:
    owner = build_owner()
    print_schedule(owner, date.today())


if __name__ == "__main__":
    main()
