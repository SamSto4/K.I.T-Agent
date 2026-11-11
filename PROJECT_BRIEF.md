# Week 11 project: Remember Me

Build an assistant that **remembers you across sessions**. Close it, open it tomorrow, and it still
knows your name, your preferences and what you talked about last time. You also control what it keeps.

It is the syllabus hands-on for this week ("an agent that remembers user preferences across sessions"),
built from your Lab 1 memory and your Lab 2 episodic memory. It's also a portfolio piece: in Week 12
you give it a web interface, and it can grow into your capstone.

**When:** Lesson 3. About 2 hours of building and testing, 15 minutes of peer review, then demos.
**Your AI mentor:** https://jonathanpilnick.github.io/beginner_agentic_tutorial/week11/project

## 1. Make it yours

Edit `PERSONA` in `remember_me.py`: a study buddy, a gym coach, a recipe helper, a travel planner...
Its memory should matter for its job (a gym coach remembers your goal and injuries to avoid; a recipe
helper remembers your diet).

**Privacy rule:** test it with made-up or harmless facts. No passwords, ID numbers, health records or
other people's details. Everything you say is sent to Claude, and facts are saved in `memory.json`.

## 2. Build it: `remember_me.py` (4 TODOs)

1. **`start_session()`**: load the memory (Lab 1) and greet the user, by name if you know it.
2. **`handle_message()`**: remember new facts (`extract_facts`), recall a similar past session
   (`recall_episodes`), answer with `chat_with_memory`, and update the chat history.
3. **`handle_command()`**: privacy controls. `/memory` shows every saved fact; `/forget <key>` deletes one.
   (The session summaries in `chroma_db` can still mention it: deleting those too is a stretch goal.)
4. **`end_session()`**: summarise the conversation and save it as an episode (`save_episode`).

Run it in a normal terminal (it waits for you to type): `python remember_me.py`, and type `quit` to end a session.

## 3. Test it

1. Run `python test_memory.py`. It plays two sessions with your functions and should print `6/6 checks passed`.
2. Write 3 test conversations of your own in `PROJECT_README.md`. For each one: what you told it in
   session 1, what you asked in session 2 after a restart, and whether the answer used the memory.
3. Find one failure (it forgot something, remembered something wrong, or saved something it shouldn't)
   and explain why. Try one fix (the extraction prompt, `MIN_SCORE` (default 0.15), the persona) and test again.

## 4. Write `PROJECT_README.md`

A new file in `week11_memory` (keep the kit's `README.md`):

```markdown
# Remember Me: <your assistant's name and job>
What it does: one or two sentences.
What it remembers: the kinds of facts, where they are stored, and how /forget works.
How to run: the commands.
Test results: test_memory.py result, and my 3 test conversations.
One failure: what went wrong, why, and what I changed.
```

## 5. Peer review (15 minutes, in pairs)

Swap laptops with a partner. Use their assistant and fill in this checklist for them:

- [ ] I told it 2 facts about me (made up), typed `quit`, started it again, and it greeted me by name.
- [ ] I asked something where my facts matter, and the answer used them.
- [ ] `/memory` showed my facts, and `/forget <key>` removed one (I checked `/memory` again).
- [ ] I asked about the same topic as my first session, and it used something from that session.
- [ ] Their code: one thing that is clear, one suggestion to make it better.

## 6. Demo (3 minutes)

Show: session 1 (tell it something), a restart, session 2 (it remembers), `/memory` and `/forget`,
and the failure you found with what you learned from it.

## Grading (100 points)

| Part | Points |
|---|---|
| Remembers preferences after a restart (facts in `memory.json`) | 20 |
| Uses what it remembers in its answers | 15 |
| Recalls a past session (episodic memory) | 15 |
| Privacy controls: `/memory` and `/forget` work | 10 |
| Testing: `test_memory.py` passes and 3 test conversations written up | 10 |
| `PROJECT_README.md` with one failure explained | 10 |
| Peer review: a filled-in checklist for your partner | 10 |
| Demo | 10 |

You may use Claude Code as a pair programmer, but you must be able to explain every line you hand in.

## Stretch goals (optional, pick one)

- **A critic agent (evaluator-optimizer):** before printing a reply, a second Claude call checks it against
  the memory ("Does this answer respect the user's diet and goals?") and asks for a rewrite if not.
- **Importance scores:** ask Claude to rate each fact or episode from 1 to 10 and recall the important ones first,
  like the Generative Agents paper.
- **A router:** if a message asks for an evening plan, hand it to your Lab 2 planner (`plan_my_evening`) instead.
- **Forget everywhere:** make `/forget` also delete or rewrite the session summaries that mention the fact.
