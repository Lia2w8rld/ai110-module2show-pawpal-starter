# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    So the owner can own multiple pets, for each pet it'd have a schedule, and walking time/ feeding time/ meds
    each pet would have appointments so grooming/ check ins 
    there cant be cross over between an owener pet schedyles. 
    certain tasks priority like feeding and water and walking in the mroning and night . 

- What classes did you include, and what responsibilities did you assign to each?
    Classes 
    Class	Responsibility
Owner	Knows who the person is, which pets they have, and how much free time they've got. The only class that sees across all pets.
Pet	Holds one animal's identity and the care it needs: its tasks and its appointments. Doesn't know about time or other pets.
CareItem	Base class. Defines what every schedulable thing has: a title, a duration, a priority.
CareTask	A flexible item (walk, feeding, water, meds). Knows its preferred time of day and whether it repeats, but not its actual start time. The scheduler decides that.
Appointment	A fixed item (grooming, vet check-in). Owns a locked start_time, so it constrains the plan instead of bending to it.
TimeWindow	A span of clock time, and the overlap math: overlaps() and contains(). Every conflict check bottoms out here.
Enums: fixed vocabularies rather than free text, so typos can't silently create a fourth priority level:

Priority (HIGH/MEDIUM/LOW): decides whether something gets scheduled when time runs short.
TimeOfDay (MORNING/AFTERNOON/EVENING/ANY): decides where in the day it lands.
Plan classes: these are the output:

Class	Responsibility
ScheduledItem	One care item pinned to a concrete start/end for one pet, plus the reason it landed there. Carries the pet reference, which is what makes cross-pet conflict detection possible.
DailySchedule	The day's plan. Guards its own integrity (add() refuses anything that conflicts) and tracks what got skipped. Also produces the explanation.
Logic class:

Class	Responsibility
Scheduler	The only class that makes decisions. Places appointments first (they can't move), sorts remaining tasks by priority, fits them into free slots, and drops what doesn't fit.




**b. Design changes**

- Did your design change during implementation?
- Yes it did. 
- If yes, describe at least one change and why you made it.
- AI gave me potential logic breaks and which classes should go underneath each other to prevent bugs and errors. 

    The final version is simpler than my first UML in some ways. The main pieces that actually run are Owner, Pet, CareTask, and Scheduler, and I kept them separate on purpose. Owner just holds the pets. Pet holds its own tasks. CareTask is the info about one task (title, duration, priority, time, how often it repeats). Scheduler is the only one that does the "thinking" like sorting and finding conflicts. That way if I wanted to change how sorting works I only have to touch Scheduler and not every class.

    One change I made was adding scheduled_time and due_date to CareTask. My original plan was that a task wouldn't know its start time and the scheduler would pick it, but to do sorting and conflict checks I needed tasks to actually have a time.

    Another change was how tasks remember which pet they belong to. A CareTask doesn't store its pet, so I added Owner.tasks_with_pets() which gives back (Pet, CareTask) pairs. The Scheduler works with those pairs, so when it shows a schedule or a conflict it can still say "Mochi: Fresh water" and not just "Fresh water". It also means the scheduler can look across all the pets at once, which is how it catches a dog task and a cat task at the same time.

    For recurring tasks I put complete_task() on Pet. It marks the task done, then asks the task for its next_occurrence(), which makes a copy with completed=False and a new due date (tomorrow for daily, 7 days for weekly). The old task stays in the list as history instead of getting deleted or reset, so you can still see it was done.

    To be honest, not everything from my first UML got built. build_day(), place_appointments(), place_tasks(), next_free_slot(), and the TimeWindow / DailySchedule / ScheduledItem / Appointment methods are still there but they just raise NotImplementedError. I left them in so the code still matches the UML, but the app and tests don't use them.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    It has a 5 contraints time budget, no overlapping, fixed commitment, time of day preference, and priority. 
- How did you decide which constraints mattered most?
    - The first 3 matter the most so hard constrait because breaking one of those plans is invalid. The last two are soft contraints they can bent if needed. 

    Note: that's what I designed for build_day(), which isn't finished. What the scheduler actually checks right now is scheduled time and priority. It sorts by time first, and if two tasks have the same time the higher priority one goes first. I put the sorting in Scheduler instead of in Pet or Owner because it needs to look at every pet's tasks together, and the Scheduler is the class that is supposed to make those decisions.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
    One tradeoff my scheduler is designed to make (this part is planned, place_tasks() isn't implemented yet) is that place_tasks() walks through tasks in priority order and puts each task in the first slot that fits. This means preference can yield to priority. For example, a lower-priority task might have a preferred time, but if a higher-priority task needs that time, the higher-priority task gets placed first.

    This is reasonable for PawPal+ because some pet care tasks are more important than others. Feeding, medication, and other high-priority tasks should be scheduled before lower-priority tasks when time is limited.

    Another tradeoff I made with conflict detection is that it only checks for tasks with the exact same scheduled time. For example, if two tasks are both scheduled for 8:00, the scheduler flags them as a conflict. However, if one task starts at 8:00 and lasts 30 minutes while another starts at 8:15, it will not detect that they overlap. Detecting duration overlaps would be more realistic, but it would also make the algorithm more complicated. For this version of PawPal+, I chose the simpler exact-time check because it catches obvious double-bookings while keeping the code easier to understand.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

    I used AI throughout the project for design brainstorming, debugging, and thinking through the scheduling logic before implementing it. I also used AI to help me break the project into smaller steps and identify where certain logic should live in the classes. For example, I used AI to think through how Owner, Pet, CareTask, and Scheduler should work together and how sorting, filtering, recurring tasks, and conflict detection could be added without changing the whole system.

    The most helpful prompts were the ones where I gave AI the assignment requirements and asked it to explain the logic before changing my code. Asking it to focus on one step at a time helped me understand what each method was supposed to do instead of just having AI write everything at once.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

    One moment where I did not accept an AI suggestion as-is was when I asked AI to review my detect_conflicts() algorithm and suggest ways to make it simpler. It suggested alternatives such as using an explicit if statement, or groupby. After comparing them, I decided to keep my original setdefault() approach because it was already efficient and clear enough for the size of this project.

    I verified the suggestions by looking at how each version would actually work with my task data and by running my tests and demos. This helped me realize that shorter code is not automatically better code. I wanted my implementation to be something I could explain and debug myself, not just something that looked more advanced.

**c. AI Strategy**

- Which AI coding assistant features were most effective for building the scheduler?

    The most useful thing was having AI look at my existing code before changing anything. It would read pawpal_system.py and the UML first, so its suggestions fit what I already had instead of starting over. Design review was helpful too, especially early on when I was figuring out which classes should own what.

    Doing it step by step also helped a lot. I added sorting, then filtering, then recurring tasks, then conflict detection, and ran main.py after each one to see if it worked. AI also helped write and review the tests, and I checked that they matched what the methods were actually supposed to do. One small thing that helped was when I hooked up the UI. When I added the scheduled time input to app.py, AI checked that CareTask already had a scheduled_time field and passed it through, otherwise the time picker would have shown up but not actually saved anything.

- Give one example of an AI suggestion you rejected or modified to keep the system design clean.

    The detect_conflicts() one I talked about above. AI suggested rewriting it with groupby or a more explicit if statement. I kept my setdefault() version because it was already simple, it doesn't need the list sorted first like groupby does, and I could explain every line of it.

- How did using separate chat sessions for different phases help you stay organized?

    I used different chats for the UML and core classes, the algorithms, testing, the UI, and the docs. It kept each chat focused on one thing, so when I was working on tests the AI wasn't also trying to change the UI or rewrite my classes. It also made it easier to check each phase before moving on. I could run the tests or main.py at the end of a phase and know that whatever changed came from that phase, and I committed after each one.

- What did you learn about being the "lead architect" when collaborating with powerful AI tools?

    AI can write and change code really fast, but it doesn't know what my project actually needs. I still had to decide what features belonged in PawPal+, which suggestions actually matched the rubric, and what to reject or change. I also had to decide how the classes relate to each other, like keeping the pet link through (Pet, CareTask) pairs. And I had to check that things were actually right by running the tests and the demo, not just trusting it. A big one for me was knowing when not to add more. It's easy to keep adding features with AI, but I wanted to finish what the assignment asked for and keep the code something I understand.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

    There are 15 tests in tests/test_pawpal.py. They test that mark_complete() changes a task's status and add_task() adds to the pet's task count. They test that sort_by_time() puts tasks in time order, puts tasks with no time last, and uses priority when times are tied. For recurring tasks they check that a daily task comes back the next day, a weekly task comes back in 7 days, a one-time task doesn't come back, and the original stays completed. For conflicts they check same pet and different pets at the same time, that unscheduled tasks are ignored, that it returns nothing when there's no conflict, and three tasks at the same time. There's also one for a pet with no tasks.

    These were important because sorting, recurrence, and conflicts are the main things the app does, and they are easy to break without noticing if you only look at the UI.

    Final check: I ran python3 -m pytest and got 15 passed. I also ran python3 main.py and checked that the output showed the sorting (including the 08:00 tie), filtering by pet and by completed, the recurring daily/weekly/once tasks, and the conflict warnings all working.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

    I'd say 4 out of 5. The parts that are implemented are tested and they work. I'm not giving it a 5 because conflict detection only checks exact same start times, so a 30 minute walk at 8:00 and something at 8:15 won't get flagged. Next I'd test overlapping durations (after adding that), tasks that go past midnight, completing the same recurring task more than once, and two pets with the same name.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    I'm happiest with how the Scheduler works across all the pets at once. Using the (Pet, CareTask) pairs made sorting and conflicts work for every pet without having to change the Pet class, and the conflict warnings in the app actually tell you which pet each task is for.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    I'd finish build_day() so it actually fits tasks into the owner's free time, and I'd change conflict detection to check overlapping durations instead of only exact times. I'd also add a "mark complete" button in the app so you can see recurring tasks work in the UI and not just in main.py, and maybe filter options in the app too.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    Doing the design first made everything after it easier, even though not all of it got built. AI was really helpful but I had to stay in charge of what got added and check that it worked. Going one step at a time and testing as I went is what made it work.
