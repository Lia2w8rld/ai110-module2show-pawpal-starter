# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner keep track of care tasks across all of their pets. It sorts the day's tasks by time, and flags tasks that are booked for the same time. Behind the scenes, the backend also filters tasks and brings back daily and weekly tasks once they are completed (shown in the CLI demo and tests).

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

## ✨ Features

What is actually implemented and working right now:

- **Sorting by scheduled time.** `Scheduler.sort_by_time()` lists tasks from every pet earliest first. Tasks without a time go at the end.
- **Priority tie-breaking.** When two tasks have the same scheduled time, the higher priority task is listed first (high, then medium, then low).
- **Filtering by pet and completion status.** `Scheduler.filter_tasks()` returns only one pet's tasks, only completed or only unfinished tasks, or both filters combined. (This is shown in the CLI demo and tests. The Streamlit app doesn't have filter controls yet.)
- **Conflict warnings for the same exact time.** `Scheduler.detect_conflicts()` flags any time slot with more than one task, whether the tasks belong to the same pet or to different pets. It only compares start times, not durations, so overlapping tasks that start at different times aren't caught.
- **Daily and weekly recurring tasks.** Completing a task with `Pet.complete_task()` marks it done and adds a fresh copy: tomorrow for a daily task, 7 days later for a weekly one. A one-time task does not repeat. (This is backend logic shown in the CLI demo and tests. The Streamlit app doesn't have a mark-complete control yet.)
- **Multi-pet scheduling.** One owner can have any number of pets, each with its own task list. The `Scheduler` uses `Owner.tasks_with_pets()` to sort and check every pet's tasks together, so a dog's walk and a cat's feeding at the same time are caught as a conflict.
- **Streamlit schedule display.** In the app you can add an owner, pets, and tasks (title, duration, priority, scheduled time), then click **Generate schedule** to see one table of all tasks sorted by time. A warning appears for each conflict, or a success message if there are none.

Not implemented yet: the full `Scheduler.build_day()` planner that would fit tasks into the owner's free time windows. It's in the UML design, but `build_day()` and its helper methods still raise `NotImplementedError`, so the app and tests don't call it.

## Getting started

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running it

```bash
streamlit run app.py   # the interactive app
python3 main.py        # the terminal demo
python3 -m pytest      # the test suite
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧱 System Design

All of the logic lives in `pawpal_system.py`. The final UML class diagram is in **[`diagrams/uml_final.mmd`](diagrams/uml_final.mmd)**. (`diagrams/uml.mmd` is my original first draft, kept for comparison.)

The four main classes:

| Class | What it holds | Key methods |
|-------|---------------|-------------|
| `Owner` | `name`, a list of `pets`, `available_windows` | `add_pet()`, `all_items()`, `tasks_with_pets()` |
| `Pet` | `name`, `species`, a list of `tasks` (and `appointments`) | `add_task()`, `complete_task()`, `items()` |
| `CareTask` | `title`, `duration_minutes`, `priority`, `completed` (inherited from `CareItem`), plus `preferred_time`, `frequency`, `scheduled_time`, `due_date` | `mark_complete()`, `next_occurrence()` |
| `Scheduler` | the `owner` it plans for | `sort_by_time()`, `filter_tasks()`, `detect_conflicts()` |

How they connect: an `Owner` has many `Pet`s, and each `Pet` has many `CareTask`s. The `Scheduler` doesn't store tasks itself. It calls `Owner.tasks_with_pets()` to get every task paired with its pet, so it can work across all pets at once.

Supporting enums:

- `Priority` (`HIGH`, `MEDIUM`, `LOW`) with a `rank()` method so priorities can be sorted.
- `Frequency` (`ONCE`, `DAILY`, `WEEKLY`) controls whether a task repeats.
- `TimeOfDay` (`MORNING`, `AFTERNOON`, `EVENING`, `ANY`) is used by the CLI demo to group tasks.

The file also has `CareItem`, `Appointment`, `TimeWindow`, `ScheduledItem`, and `DailySchedule`, which were part of the original `build_day()` design. Most of their methods are still stubs, so the app and tests don't use them yet.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Earliest `scheduled_time` first, unscheduled last, ties broken by priority |
| Filtering | `Scheduler.filter_tasks()` | By `pet_name`, `completed`, or both |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks with the exact same start time |
| Recurring tasks | `CareTask.next_occurrence()`, `Pet.complete_task()` | Daily = +1 day, weekly = +7 days, once = no repeat |

### How each one works

**`Scheduler.sort_by_time(pairs=None)`**
Takes a list of `(pet, task)` pairs (or all of the owner's tasks if none are passed) and returns a new sorted list. The sort key is a tuple: `(has no time?, scheduled_time, priority rank)`. Since `False` sorts before `True`, timed tasks come first in clock order, unscheduled tasks fall to the bottom, and tasks at the same time are ordered high, medium, low. It uses Python's built-in `sorted()`, so it's O(n log n) and doesn't change the original list.

**`Scheduler.filter_tasks(pet_name=None, completed=None)`**
Returns only the pairs that match every filter given. Any filter left as `None` is skipped, so `filter_tasks(pet_name="Mochi")` gives all of Mochi's tasks and `filter_tasks(pet_name="Mochi", completed=False)` gives only her unfinished ones. The result can be passed straight into `sort_by_time()`.

**`Scheduler.detect_conflicts(pairs=None)`**
Groups every task that has a `scheduled_time` into a dictionary keyed by that time, then keeps only the times with more than one task. It returns `{time: [(pet, task), ...]}` sorted by time, or an empty dict if nothing clashes. It never raises an error. Unscheduled tasks are ignored.

Limitation: this only catches tasks with the **same exact start time**. It does not look at durations, so a 30 minute walk at 8:00 and a feeding at 8:15 are not flagged even though they overlap.

**Recurring tasks: `Pet.complete_task(task)` and `CareTask.next_occurrence(today)`**
`Pet.complete_task()` marks the task as done, then asks the task for its next occurrence. `next_occurrence()` uses `dataclasses.replace()` to copy the task with `completed=False` and a new `due_date` (today + 1 for daily, today + 7 for weekly). If a copy comes back, it gets added to the pet's task list. One-time tasks return `None`, so nothing is added. The finished task stays in the list as history.

## Demo Walkthrough

### Streamlit app

The app has four main parts, top to bottom: an **Owner** box, a **Pets** section, a **Tasks** section, and a **Build Schedule** section whose **Generate schedule** button shows the final plan.

1. **Launch the app** with `streamlit run app.py`. It opens in your browser (usually at `http://localhost:8501`).
2. **Create an owner.** Type a name into the "Owner name" box at the top (it starts as "Jordan"). The owner is stored in `st.session_state`, so pets and tasks don't disappear every time Streamlit reruns the page.
3. **Add multiple pets.** In the Pets section, enter a pet name, pick a species (dog, cat, or other), and click **Add pet**. Repeat for each pet. A table shows every pet and how many tasks it has. Blank names and duplicate names are rejected with an error.
4. **Add care tasks.** In the Tasks section, choose which pet the task is for from the "For pet" dropdown. Then fill in the four fields in a row:
   - **Task title** (for example "Morning walk")
   - **Duration (minutes)**, from 1 to 240
   - **Priority**: low, medium, or high (defaults to high)
   - **Scheduled time**, picked with a time selector (defaults to 08:00)

   Click **Add task**. Each pet's tasks show up in their own table underneath.
5. **Generate and view the schedule.** Click **Generate schedule**. This builds a `Scheduler` for the owner and shows one table with every task from every pet. Columns are time, pet, task, duration, priority, and completed.
6. **How tasks are sorted.** The table uses `sort_by_time()`: earliest scheduled time first. If two tasks have the same time, the higher priority one is listed first. Tasks with no time would be listed last as "unscheduled", but every task added in the app gets a time from the time picker.
7. **How conflict warnings appear.** Below the table, `detect_conflicts()` checks the same tasks. For each time slot with more than one task, a yellow warning shows the time and lists each pet and task booked then, like `⚠️ Conflict at 08:00 — Mochi: Fresh water, Biscuit: Morning walk`. If nothing clashes, a green "No scheduling conflicts found." message shows instead.
8. **How recurring tasks work.** Tasks added in the app use the default `DAILY` frequency. In the backend, completing a task through `Pet.complete_task()` marks it done and adds a new copy due tomorrow (daily) or in 7 days (weekly), while one-time tasks don't come back. The app doesn't have a "mark complete" button yet, so recurrence is shown in the CLI demo below and covered by the tests.

**Example workflow:** add a pet → add a task → choose a scheduled time → generate/view today's schedule.

For example: add Mochi (cat) and Biscuit (dog), give Biscuit a "Morning walk" at 07:00 and Mochi a "Puzzle feeder" at 13:00, then click **Generate schedule**. You'll see the walk listed first and a green "no conflicts" message.

**Trying out a conflict:** you can give two tasks the same scheduled time on purpose to see the conflict warning. For example, add "Fresh water" for Mochi at 08:00 with low priority and "Morning walk" for Biscuit at 08:00 with high priority, then generate the schedule. Both tasks show up at 08:00 (the high priority walk first) and a yellow warning lists them together. Since the time picker defaults to 08:00, adding several tasks without changing the time will also trigger this.

### CLI demo (`main.py`)

`main.py` sets up an owner (Lia) with two pets, Biscuit the dog and Mochi the cat, and prints four sections:

1. **Today's Schedule:** tasks grouped by preferred time of day (morning, afternoon, evening, any), highest priority first in each group, plus total care time.
2. **Sorting and filtering demo:** the tasks in the order they were added, then sorted by time (note the 08:00 tie where the high priority walk comes before the low priority water), then filtered by pet, by completed status, and both combined and sorted.
3. **Recurring tasks demo:** completes a daily, a weekly, and a one-time task for Biscuit and shows the new due dates and task counts.
4. **Conflict detection demo:** a separate setup with two tasks at 08:00 (different pets) and two at 18:00 (same pet), showing the warnings plus which tasks were not flagged.

Actual terminal output from running `python3 main.py`. This is the CLI demo, not the Streamlit app. The dates come from `date.today()`, so they'll be different on another day.

```text
$ python3 main.py
Today's Schedule for Lia -- Wednesday, October 07, 2026
==============================================

Morning
  - Morning walk (Biscuit, dog) -- 30 min [priority: high]
  - Fresh water (Mochi, cat) -- 5 min [priority: low]
  - Litter box scoop (Mochi, cat) -- 5 min [priority: low]

Afternoon
  - Puzzle feeder (Mochi, cat) -- 15 min [priority: medium]

Evening
  - Evening feeding (Biscuit, dog) -- 10 min [priority: high]

Any
  - Brush coat (Biscuit, dog) -- 15 min [priority: low]

Total care time today: 80 min across 2 pets

==============================================
Sorting and filtering demo
==============================================

As added (unsorted)
-------------------
  18:00  Evening feeding    Biscuit  [priority: high  ] [todo]
  --:--  Brush coat         Biscuit  [priority: low   ] [todo]
  08:00  Morning walk       Biscuit  [priority: high  ] [todo]
  13:00  Puzzle feeder      Mochi    [priority: medium] [todo]
  08:00  Fresh water        Mochi    [priority: low   ] [todo]
  07:30  Litter box scoop   Mochi    [priority: low   ] [todo]

Sorted by time
--------------
  07:30  Litter box scoop   Mochi    [priority: low   ] [todo]
  08:00  Morning walk       Biscuit  [priority: high  ] [todo]
  08:00  Fresh water        Mochi    [priority: low   ] [todo]
  13:00  Puzzle feeder      Mochi    [priority: medium] [todo]
  18:00  Evening feeding    Biscuit  [priority: high  ] [todo]
  --:--  Brush coat         Biscuit  [priority: low   ] [todo]

Filter: pet_name='Mochi'
------------------------
  13:00  Puzzle feeder      Mochi    [priority: medium] [todo]
  08:00  Fresh water        Mochi    [priority: low   ] [todo]
  07:30  Litter box scoop   Mochi    [priority: low   ] [todo]

Filter: completed=True
----------------------
  07:30  Litter box scoop   Mochi    [priority: low   ] [done]

Filter: completed=False
-----------------------
  18:00  Evening feeding    Biscuit  [priority: high  ] [todo]
  --:--  Brush coat         Biscuit  [priority: low   ] [todo]
  08:00  Morning walk       Biscuit  [priority: high  ] [todo]
  13:00  Puzzle feeder      Mochi    [priority: medium] [todo]
  08:00  Fresh water        Mochi    [priority: low   ] [todo]

Mochi's remaining tasks, sorted
-------------------------------
  08:00  Fresh water        Mochi    [priority: low   ] [todo]
  13:00  Puzzle feeder      Mochi    [priority: medium] [todo]

==============================================
Recurring tasks demo (today is Wed Oct 07)
==============================================

Completed 'Morning walk' (daily) -> completed=True
  New task: 'Morning walk' due Thu Oct 08 (+1 day), completed=False
  Biscuit's task count: 5 -> 6

Completed 'Bath' (weekly) -> completed=True
  New task: 'Bath' due Wed Oct 14 (+7 days), completed=False
  Biscuit's task count: 6 -> 7

Completed 'Vet nail trim' (once) -> completed=True
  No new task created (one-time task)
  Biscuit's task count: 7 -> 7

Biscuit's tasks now
-------------------
  18:00  Evening feeding    Biscuit  [priority: high  ] [todo]
  --:--  Brush coat         Biscuit  [priority: low   ] [todo]
  08:00  Morning walk       Biscuit  [priority: high  ] [done]
  --:--  Bath               Biscuit  [priority: medium] [done]
  --:--  Vet nail trim      Biscuit  [priority: medium] [done]
  08:00  Morning walk       Biscuit  [priority: high  ] [todo]
  --:--  Bath               Biscuit  [priority: medium] [todo]

==============================================
Conflict detection demo
==============================================

All tasks
---------
  18:00  Evening feeding    Biscuit  [priority: high  ] [todo]
  --:--  Brush coat         Biscuit  [priority: low   ] [todo]
  08:00  Morning walk       Biscuit  [priority: high  ] [todo]
  18:00  Give medication    Biscuit  [priority: medium] [todo]
  13:00  Puzzle feeder      Mochi    [priority: medium] [todo]
  08:00  Fresh water        Mochi    [priority: low   ] [todo]
  07:30  Litter box scoop   Mochi    [priority: low   ] [todo]

WARNING: 2 tasks at 08:00 (different pets):
  - Morning walk (Biscuit)
  - Fresh water (Mochi)
WARNING: 2 tasks at 18:00 (same pet):
  - Evening feeding (Biscuit)
  - Give medication (Biscuit)

Not conflicts (unique times): Puzzle feeder, Litter box scoop
Ignored (unscheduled): Brush coat
```

## Testing PawPal+

```bash
# Run the full test suite:
python3 -m pytest
```

There are **15 tests** in `tests/test_pawpal.py`, and all 15 currently pass. They cover:

- **Basics:** `mark_complete()` changes a task's status, and `add_task()` increases a pet's task count.
- **Sorting correctness:** `Scheduler.sort_by_time()` returns tasks in chronological order, puts unscheduled tasks last, and breaks ties by priority.
- **Recurring task logic:** completing a daily task adds a copy due the next day, a weekly task comes back 7 days later, a one-time task does not repeat, and the original task stays completed.
- **Conflict detection:** `Scheduler.detect_conflicts()` flags tasks with the same `scheduled_time` for the same pet or different pets, and ignores unscheduled tasks.
- **Edge cases:** a pet with no tasks, a day with no conflicts, and three tasks at the exact same time.

Sample test output:

```text
$ python3 -m pytest -q
...............                                                          [100%]
15 passed in 0.01s
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

The tests cover the main implemented behaviors and several edge cases. One star is held back because conflict detection only checks exact matching start times, not overlapping task durations (e.g. a 30 minute walk at 8:00 and a feeding at 8:15 are not flagged yet).
