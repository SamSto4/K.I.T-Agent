# Remember Me: Clicker, my personal agent's memory brain

## What it does
Clicker is the memory "brain" for my Mac AI agent platform. It chats with me, learns facts about me
from normal conversation without me asking it to, and remembers them after a restart. It also
remembers short summaries of past conversations and uses them when I ask about something related.

## What it remembers
Clicker uses three kinds of memory:

| Memory type | What it holds | Where it is stored |
|---|---|---|
| In-context | This conversation | The `history` list. It is gone when I type `quit`. |
| Semantic (facts) | Facts about me, like `name`, `hobby` and `favorite_color` | `memory.json` |
| Episodic | A 2-sentence summary of each past conversation | ChromaDB (`chroma_db/`, the `sessions` collection) |

**Privacy controls:**
- `/memory` shows every saved fact, one `key: value` per line.
- `/forget <key>` deletes that fact from `memory.json` and saves the file, so it stays deleted after a restart.
- Limit: `/forget` does not delete old session summaries in ChromaDB, so a summary could still mention a forgotten fact.
- Clicker is told not to keep sensitive data, and `memory.json` is in `.gitignore`, so my facts never go to GitHub.

## How to run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python remember_me.py      # chat with Clicker, type quit to end a session
python test_memory.py      # automatic two-session test
```

## Test results
**`test_memory.py`:** `6/6 checks passed.`

### Test conversation 1: preferences after a restart
- **Session 1:** I told Clicker my name, that I like playing guitar, and that my favorite color is blue. Then I typed `quit`.
- **Session 2 (after a restart):** Clicker greeted me by name. I asked it to suggest a weekend project.
- **Did it use the memory?** Yes. The project it suggested was based on what it knew about me (guitar and blue).

### Test conversation 2: correcting a fact
- **Session 1:** ✏️ (Sam: fill in, e.g. "I said my favorite color is now green.")
- **Session 2:** ✏️ (Sam: what did `/memory` show? Was blue replaced, or were there two keys?)
- **Did it use the memory?** ✏️

### Test conversation 3: forgetting a fact
- **Session 1:** ✏️ (Sam: which key did you `/forget`?)
- **Session 2:** ✏️ (Sam: after a restart, did `/memory` still show it?)
- **Did it use the memory?** ✏️

## One failure
- **What went wrong:** ✏️ (Sam: e.g. a duplicate key, a fact it forgot, or something it saved that it shouldn't have)
- **Why it happened:** ✏️
- **What I changed, and did it help:** ✏️

## What's next
- **Stretch goal:** memory tools, so Clicker itself can decide to call `save_fact` or `forget_fact`.
- **Later:** connect this memory brain to my Clicker Mac agent platform, so the platform's system prompt
  gets my saved facts in its "memory slots" section.
