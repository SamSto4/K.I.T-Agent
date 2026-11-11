"""
Week 11 · Final project: Remember Me - an assistant that remembers you across sessions.

You reuse your Lab 1 memory (facts in memory.json) and your Lab 2 episodic memory (past sessions).
  TODO 1  start_session()    load the memory and greet the user
  TODO 2  handle_message()   remember new facts, recall a past session, answer
  TODO 3  handle_command()   privacy: /memory and /forget <key>
  TODO 4  end_session()      save a summary of this session as an episode

Run it in a normal terminal (it waits for you to type):  python remember_me.py
Test it:  python test_memory.py
Brief and rubric: PROJECT_BRIEF.md. Your AI mentor: https://jonathanpilnick.github.io/beginner_agentic_tutorial/week11/project
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "solutions" else HERE   # works from either folder
sys.path.insert(1, str(ROOT))                             # after this file's own folder
from llm import ask_claude                                 # noqa: E402
from lab1_memory import MEMORY_FILE, load_memory, save_memory, extract_facts, chat_with_memory  # noqa: E402
from lab2_planner import save_episode, recall_episodes   # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Make it yours: who is your assistant? (a study buddy, a gym coach, a travel helper...)
PERSONA = ("You are Remy, a friendly personal assistant who remembers the user. You know only what this "
           "conversation and your memory notes tell you about the user; ignore anything else. "
           "Use what you remember when it helps, without listing it. Answer in at most 3 sentences.")
SESSIONS = "sessions"        # ChromaDB collection for past-session summaries (episodic memory)
MIN_SCORE = 0.15             # only recall a past session if it is at least this similar (unrelated ones score about 0-0.1)


# ---------- TODO 1: start a session ----------------------------------------------
def start_session(path=MEMORY_FILE):
    """Load the long-term memory, greet the user, and return the memory dict."""
    # TODO 1: load the memory from `path` (Lab 1). If it has a "name", print a welcome-back greeting
    #   that uses it; otherwise print a first-time greeting. Return the memory dict.
    raise NotImplementedError("TODO 1 in remember_me.py")


# ---------- TODO 2: handle one message ------------------------------------------
def handle_message(message, memory, history, path=MEMORY_FILE, collection=SESSIONS):
    """Remember new facts, recall a relevant past session, answer, and update the chat history."""
    # TODO 2: 1) extract_facts(message); if there are any, add them to memory and save_memory(memory, path).
    #   2) recall_episodes(message, k=1, collection=collection); keep its text only if score >= MIN_SCORE.
    #   3) reply = chat_with_memory(message, memory, history, persona=PERSONA, past=<that text or "">).
    #   4) append the user message and the reply to history, then return the reply.
    raise NotImplementedError("TODO 2 in remember_me.py")


# ---------- TODO 3: privacy commands ----------------------------------------------
def handle_command(command, memory, path=MEMORY_FILE):
    """/memory shows every saved fact; /forget <key> deletes one fact and saves the file."""
    # TODO 3: "/memory" returns every fact, one "key: value" per line (or a message if it's empty).
    #   "/forget <key>" deletes that key from memory, saves the file, and confirms it
    #   (or says the key wasn't found). Anything else returns "Commands: /memory, /forget <key>, quit".
    raise NotImplementedError("TODO 3 in remember_me.py")


# ---------- TODO 4: end the session ------------------------------------------------
SUMMARY_SYSTEM = ("Summarise this conversation in 2 sentences for the assistant's future self: what the user "
                  "wanted, what was suggested, and anything to follow up. Don't include sensitive data.")


def end_session(history, collection=SESSIONS):
    """Save a short summary of this conversation as an episode, so a later session can recall it."""
    if not history:
        return None
    # TODO 4: join the history into a transcript ("user: ...", one line per message), ask Claude
    #   for a summary with system=SUMMARY_SYSTEM, save it with save_episode(summary, collection=collection)
    #   and return the summary.
    raise NotImplementedError("TODO 4 in remember_me.py")


# ---------- Given: the chat loop ------------------------------------------------------
def main():
    memory = start_session()
    history = []
    while True:
        try:
            message = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            message = "quit"
        if message.lower() in ("", "quit", "exit"):
            break
        if message.startswith("/"):
            print(handle_command(message, memory))
            continue
        print("Remy:", handle_message(message, memory, history))
    summary = end_session(history)
    if summary:
        print(f"\nSaved this session for next time: {summary}")
    print("Bye! Run me again later: I'll remember you.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as todo:
        print(f"\n>>> Next step: {todo}. Finish it, then run the file again.")
