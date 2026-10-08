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

## 🖥️ Sample Output

Terminal output from running `python main.py`:

```
$ python main.py
Today's Schedule for Lia -- Wednesday, October 07, 2026
==============================================

Morning
  - Morning walk (Biscuit, dog) -- 30 min [priority: high]
  - Litter box scoop (Mochi, cat) -- 5 min [priority: low]

Afternoon
  - Puzzle feeder (Mochi, cat) -- 15 min [priority: medium]

Evening
  - Evening feeding (Biscuit, dog) -- 10 min [priority: high]

Total care time today: 60 min across 2 pets
```

Tasks are grouped by preferred time of day, and sorted highest priority first
within each group. Concrete clock times arrive once `Scheduler.build_day` places
tasks into the owner's available windows.

## Testing PawPal+

```bash
# Run the full test suite:
python3 -m pytest
```

The tests in `tests/test_pawpal.py` cover:

- **Sorting correctness** -- `Scheduler.sort_by_time()` returns tasks in
  chronological order, puts unscheduled tasks last, and breaks ties by priority.
- **Recurring task logic** -- completing a daily task adds a copy due the next
  day, a weekly task comes back 7 days later, a one-time task does not repeat,
  and the original task stays completed.
- **Conflict detection** -- `Scheduler.detect_conflicts()` flags tasks with the
  same `scheduled_time` for the same pet or different pets, and ignores
  unscheduled tasks.
- **Edge cases** -- a pet with no tasks, a day with no conflicts, and three
  tasks at the exact same time.

Sample test output:

```
$ python3 -m pytest -q
...............                                                          [100%]
15 passed in 0.03s
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

The tests cover the main implemented behaviors and several edge cases. One
star is held back because conflict detection only checks exact matching start
times, not overlapping task durations (e.g. a 30-minute walk at 8:00 and a
feeding at 8:15 are not flagged yet).

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
