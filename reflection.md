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
Pet	Holds one animal's identity and the care it needs — its tasks and its appointments. Doesn't know about time or other pets.
CareItem	Base class. Defines what every schedulable thing has: a title, a duration, a priority.
CareTask	A flexible item (walk, feeding, water, meds). Knows its preferred time of day and whether it repeats, but not its actual start time — the scheduler decides that.
Appointment	A fixed item (grooming, vet check-in). Owns a locked start_time, so it constrains the plan instead of bending to it.
TimeWindow	A span of clock time, and the overlap math — overlaps() and contains(). Every conflict check bottoms out here.
Enums — fixed vocabularies rather than free text, so typos can't silently create a fourth priority level:

Priority (HIGH/MEDIUM/LOW) — decides whether something gets scheduled when time runs short.
TimeOfDay (MORNING/AFTERNOON/EVENING/ANY) — decides where in the day it lands.
Plan classes — these are the output:

Class	Responsibility
ScheduledItem	One care item pinned to a concrete start/end for one pet, plus the reason it landed there. Carries the pet reference, which is what makes cross-pet conflict detection possible.
DailySchedule	The day's plan. Guards its own integrity — add() refuses anything that conflicts — and tracks what got skipped. Also produces the explanation.
Logic class:

Class	Responsibility
Scheduler	The only class that makes decisions. Places appointments first (they can't move), sorts remaining tasks by priority, fits them into free slots, and drops what doesn't fit.




**b. Design changes**

- Did your design change during implementation?
- Yes it did. 
- If yes, describe at least one change and why you made it.
- AI gave me potential logic breaks and which classes should go underneath each other to prevent bugs and errors. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    It has a 5 contraints time budget, no overlapping, fixed commitment, time of day preference, and priority. 
- How did you decide which constraints mattered most?
    - The first 3 matter the most so hard constrait because breaking one of those plans is invalid. The last two are soft contraints they can bent if needed. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
    One tradeoff my scheduler makes is that place_tasks() walks through tasks in priority order and puts each task in the first slot that fits. This means preference can yield to priority. For example, a lower-priority task might have a preferred time, but if a higher-priority task needs that time, the higher-priority task gets placed first.

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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
