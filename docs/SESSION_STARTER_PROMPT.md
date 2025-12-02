# Session Starter Prompt

**Copy and paste this at the start of each coding session:**

---

## START OF SESSION PROMPT

You are helping me with a biblical Hebrew figurative language analysis project. Before doing ANY work, you MUST:

### 1. READ THESE FILES FIRST (in order):
```
@docs/NEXT_SESSION_PROMPT.md    - Your specific tasks for this session
@docs/PROJECT_STATUS.md          - Current project state and blockers
```

### 2. FOLLOW THESE RULES:

**BEFORE CODING:**
- [ ] Read the task files above completely
- [ ] Confirm you understand the tasks by summarizing them back to me
- [ ] Ask clarifying questions if ANYTHING is unclear
- [ ] Do NOT start coding until I approve your understanding

**WHILE CODING:**
- [ ] Work on ONE task at a time
- [ ] Test each change before moving to the next task
- [ ] If something doesn't work as expected, STOP and tell me
- [ ] Do NOT modify files outside your assigned tasks
- [ ] Do NOT "clean up" or "improve" code that isn't part of your task

**AFTER EACH TASK:**
- [ ] Tell me what you changed and why
- [ ] Show me test results
- [ ] Wait for my approval before starting the next task

**AT END OF SESSION:**
- [ ] Update @docs/IMPLEMENTATION_LOG.md with a session entry
- [ ] Update @docs/PROJECT_STATUS.md with any completed items
- [ ] Update @docs/NEXT_SESSION_PROMPT.md for the next session
- [ ] List any issues discovered but not fixed

### 3. DOCUMENTATION REQUIREMENTS:

**For IMPLEMENTATION_LOG.md, include:**
- Session number and date
- Objective (what you were asked to do)
- What you actually did (files changed, lines modified)
- Test results (did it work? what did you verify?)
- Issues discovered (any problems found)
- Next steps (what's left to do)

**Keep documentation CONCISE:**
- Use bullet points, not paragraphs
- Include actual line numbers
- Copy/paste actual error messages
- Don't repeat information from other docs

### 4. RED FLAGS - STOP AND ASK ME IF:

- You're not sure which file to modify
- A test fails and you don't know why
- You want to change something not in your task list
- The code doesn't match what the documentation describes
- You've spent more than 15 minutes stuck on something

### 5. COST AWARENESS:

This project uses paid APIs (GPT-5.1). Before running ANY test:
- Tell me the expected cost
- Wait for my approval
- Report the actual cost after running

---

## NOW START BY:

1. Reading @docs/NEXT_SESSION_PROMPT.md
2. Reading @docs/PROJECT_STATUS.md
3. Summarizing your tasks back to me in 3-5 bullet points
4. Asking any clarifying questions
5. Waiting for my "GO" before starting

---

## QUICK REFERENCE

**Key files:**
- Main code: `private/interactive_parallel_processor.py`
- Validator: `private/src/hebrew_figurative_db/ai_analysis/metaphor_validator.py`
- Test script: `test_proverbs_3_11-18_batched_validated.py`

**Test command:**
```bash
python test_proverbs_3_11-18_batched_validated.py
```

**Expected test cost:** ~$0.10 after fixes (currently ~$0.40)

---

END OF SESSION STARTER PROMPT
