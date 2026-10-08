"""Tests for the core PawPal+ behaviors."""

from datetime import date, time

from pawpal_system import (
    CareTask,
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    TimeOfDay,
)

TODAY = date(2026, 1, 1)


def make_scheduler(*pets):
    """A Scheduler for a test owner who has the given pets."""
    owner = Owner(name="Test Owner")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


def test_mark_complete_changes_task_status():
    """Calling mark_complete() flips a task from not-done to done."""
    task = CareTask(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        preferred_time=TimeOfDay.MORNING,
    )

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet grows that pet's task list by one."""
    pet = Pet(name="Biscuit", species="dog")

    assert len(pet.tasks) == 0

    pet.add_task(CareTask(title="Evening feeding", duration_minutes=10))

    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Evening feeding"


# --- Sorting correctness ---


def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order come back earliest first."""
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(CareTask(title="Dinner", duration_minutes=10, scheduled_time=time(18, 0)))
    pet.add_task(CareTask(title="Breakfast", duration_minutes=10, scheduled_time=time(8, 0)))
    pet.add_task(CareTask(title="Lunch walk", duration_minutes=20, scheduled_time=time(12, 30)))

    result = make_scheduler(pet).sort_by_time()

    assert [task.title for _, task in result] == ["Breakfast", "Lunch walk", "Dinner"]


def test_sort_by_time_puts_unscheduled_tasks_last():
    """A task with no scheduled_time goes after every timed task."""
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(CareTask(title="Brushing", duration_minutes=15))
    pet.add_task(CareTask(title="Morning walk", duration_minutes=30, scheduled_time=time(7, 0)))

    result = make_scheduler(pet).sort_by_time()

    assert [task.title for _, task in result] == ["Morning walk", "Brushing"]


def test_sort_by_time_breaks_ties_by_priority():
    """At the same time, the higher-priority task comes first."""
    pet = Pet(name="Biscuit", species="dog")
    # LOW is added first so the test only passes if priority decides the order.
    pet.add_task(
        CareTask(title="Play", duration_minutes=15, priority=Priority.LOW, scheduled_time=time(9, 0))
    )
    pet.add_task(
        CareTask(title="Meds", duration_minutes=5, priority=Priority.HIGH, scheduled_time=time(9, 0))
    )

    result = make_scheduler(pet).sort_by_time()

    assert [task.title for _, task in result] == ["Meds", "Play"]


# --- Recurrence logic ---


def test_completing_daily_task_creates_next_day_task():
    """Finishing a daily task adds a fresh copy due tomorrow."""
    pet = Pet(name="Biscuit", species="dog")
    task = CareTask(title="Feeding", duration_minutes=10, frequency=Frequency.DAILY)
    pet.add_task(task)

    next_task = pet.complete_task(task, today=TODAY)

    assert next_task is not None
    assert next_task.due_date == date(2026, 1, 2)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_completed_original_task_stays_completed():
    """Creating the next occurrence does not undo the original's completion."""
    pet = Pet(name="Biscuit", species="dog")
    task = CareTask(title="Feeding", duration_minutes=10, frequency=Frequency.DAILY)
    pet.add_task(task)

    next_task = pet.complete_task(task, today=TODAY)

    assert task.completed is True
    assert next_task is not task


def test_completing_weekly_task_creates_task_seven_days_later():
    """A weekly task comes back exactly 7 days later."""
    pet = Pet(name="Biscuit", species="dog")
    task = CareTask(title="Bath", duration_minutes=30, frequency=Frequency.WEEKLY)
    pet.add_task(task)

    next_task = pet.complete_task(task, today=TODAY)

    assert next_task is not None
    assert next_task.due_date == date(2026, 1, 8)


def test_completing_once_task_does_not_create_new_task():
    """A one-time task is marked done and nothing new is added."""
    pet = Pet(name="Biscuit", species="dog")
    task = CareTask(title="Vet visit", duration_minutes=60, frequency=Frequency.ONCE)
    pet.add_task(task)

    next_task = pet.complete_task(task, today=TODAY)

    assert next_task is None
    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


# --- Conflict detection ---


def test_detect_conflicts_flags_same_time_same_pet():
    """Two tasks for one pet at the same time are a conflict."""
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(CareTask(title="Walk", duration_minutes=30, scheduled_time=time(8, 0)))
    pet.add_task(CareTask(title="Bath", duration_minutes=20, scheduled_time=time(8, 0)))

    conflicts = make_scheduler(pet).detect_conflicts()

    assert list(conflicts) == [time(8, 0)]
    assert [task.title for _, task in conflicts[time(8, 0)]] == ["Walk", "Bath"]


def test_detect_conflicts_flags_same_time_different_pets():
    """Tasks for different pets at the same time still clash for the owner."""
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Mochi", species="cat")
    dog.add_task(CareTask(title="Walk", duration_minutes=30, scheduled_time=time(8, 0)))
    cat.add_task(CareTask(title="Feeding", duration_minutes=10, scheduled_time=time(8, 0)))

    conflicts = make_scheduler(dog, cat).detect_conflicts()

    assert list(conflicts) == [time(8, 0)]
    assert {pet.name for pet, _ in conflicts[time(8, 0)]} == {"Biscuit", "Mochi"}


def test_detect_conflicts_ignores_unscheduled_tasks():
    """Tasks with no scheduled_time never count as conflicts."""
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(CareTask(title="Brushing", duration_minutes=15))
    pet.add_task(CareTask(title="Nail trim", duration_minutes=10))
    pet.add_task(CareTask(title="Walk", duration_minutes=30, scheduled_time=time(8, 0)))

    assert make_scheduler(pet).detect_conflicts() == {}


# --- Edge cases ---


def test_pet_with_no_tasks_sorts_and_checks_cleanly():
    """A pet with no tasks gives empty results instead of an error."""
    scheduler = make_scheduler(Pet(name="Biscuit", species="dog"))

    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == {}


def test_detect_conflicts_returns_empty_when_no_overlap():
    """Tasks at different times produce no conflicts."""
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(CareTask(title="Breakfast", duration_minutes=10, scheduled_time=time(8, 0)))
    pet.add_task(CareTask(title="Walk", duration_minutes=30, scheduled_time=time(12, 0)))
    pet.add_task(CareTask(title="Dinner", duration_minutes=10, scheduled_time=time(18, 0)))

    assert make_scheduler(pet).detect_conflicts() == {}


def test_detect_conflicts_groups_three_tasks_at_same_time():
    """Three tasks at one time form a single group of three."""
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Mochi", species="cat")
    dog.add_task(CareTask(title="Walk", duration_minutes=30, scheduled_time=time(9, 0)))
    dog.add_task(CareTask(title="Meds", duration_minutes=5, scheduled_time=time(9, 0)))
    cat.add_task(CareTask(title="Feeding", duration_minutes=10, scheduled_time=time(9, 0)))

    conflicts = make_scheduler(dog, cat).detect_conflicts()

    assert list(conflicts) == [time(9, 0)]
    assert len(conflicts[time(9, 0)]) == 3
