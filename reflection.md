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
    my scheduler makes  trades off with place_tasks() it walks task in priority order and drop each in the first slot that fits. and preference yields to priority. 
- Why is that tradeoff reasonable for this scenario?
    it's reasonable because it allows you to prioritize a handful of pet tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
