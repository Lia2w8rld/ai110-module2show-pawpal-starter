"""Tests for the core PawPal+ behaviors."""

from pawpal_system import CareTask, Pet, Priority, TimeOfDay


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
