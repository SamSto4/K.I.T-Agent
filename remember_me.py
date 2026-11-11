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
PERSONA = ("You are Clicker, Sam's personal AI agent inside his Mac agent platform. "
           "In this chat you can't use the computer yet: you talk with Sam and remember what you learn about him. "
           "You're casual, friendly and helpful, with no fluff, and you keep replies short (1-3 lines). "
           "If you don't know something or can't do it, say so honestly; never pretend a task is done. "
           "You know only what this conversation and your memory notes tell you about Sam; ignore anything else. "
           "Use what you remember when it helps, without listing it.")
SESSIONS = "sessions"        # ChromaDB collection for past-session summaries (episodic memory)
MIN_SCORE = 0.15             # only recall a past session if it is at least this similar (unrelated ones score about 0-0.1)


# ---------- TODO 1: start a session ----------------------------------------------
def start_session(path=MEMORY_FILE):
    """Load the long-term memory, greet the user, and return the memory dict."""
    # TODO 1: load the memory from `path` (Lab 1). If it has a "name", print a welcome-back greeting
    #   that uses it; otherwise print a first-time greeting. Return the memory dict.
    memory = load_memory(path)
    name = memory.get("name")
    if name:
        print(f"Clicker: Welcome back, {name}! I remember {len(memory)} things about you.")
    else:
        print("Clicker: Hey, I'm Clicker! What's your name?")
    return memory


# ---------- TODO 2: handle one message ------------------------------------------
def handle_message(message, memory, history, path=MEMORY_FILE, collection=SESSIONS):
    """Remember new facts, recall a relevant past session, answer, and update the chat history."""
    # TODO 2: 1) extract_facts(message); if there are any, add them to memory and save_memory(memory, path).
    #   2) recall_episodes(message, k=1, collection=collection); keep its text only if score >= MIN_SCORE.
    #   3) reply = chat_with_memory(message, memory, history, persona=PERSONA, past=<that text or "">).
    #   4) append the user message and the reply to history, then return the reply.
    # 1. Learn: pull facts out of Sam's message and save them
    facts = extract_facts(message)
    if facts:
        memory.update(facts)
        save_memory(memory, path)

    # 2. Recall: find the most similar past session, keep it only if it's similar enough
    past = ""
    found = recall_episodes(message, k=1, collection=collection)
    if found and found[0]["score"] >= MIN_SCORE:
        past = found[0]["text"]

    # 3. Answer: reply using the saved facts, the chat so far and the past session
    reply = chat_with_memory(message, memory, history, persona=PERSONA, past=past)

    # 4. Remember the chat: add both messages to the history
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return reply


# ---------- TODO 3: privacy commands ----------------------------------------------
def handle_command(command, memory, path=MEMORY_FILE):
    """/memory shows every saved fact; /forget <key> deletes one fact and saves the file."""
    # TODO 3: "/memory" returns every fact, one "key: value" per line (or a message if it's empty).
    #   "/forget <key>" deletes that key from memory, saves the file, and confirms it
    #   (or says the key wasn't found). Anything else returns "Commands: /memory, /forget <key>, quit".
    # /memory: show every saved fact, one "key: value" per line
    if command == "/memory":
        if not memory:
            return "I don't remember anything about you yet."
        return "\n".join(f"{key}: {value}" for key, value in memory.items())

    # /forget <key>: delete one fact and save the file
    if command.startswith("/forget "):
        key = command.removeprefix("/forget ").strip()
        if key in memory:
            del memory[key]
            save_memory(memory, path)
            return f"Forgotten: {key}"
        return f"I don't have anything saved under '{key}'."

    # anything else: show the help line
    return "Commands: /memory, /forget <key>, quit"


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
    # 1. Turn the chat history into a transcript, one "role: content" line per message
    transcript = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)

    # 2. Ask Claude for a short summary of the whole conversation
    summary = ask_claude(transcript, system=SUMMARY_SYSTEM)

    # 3. Save the summary in ChromaDB so a later session can recall it
    save_episode(summary, collection=collection)

    # 4. Give the summary back
    return summary


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
        print("Clicker:", handle_message(message, memory, history))
    summary = end_session(history)
    if summary:
        print(f"\nSaved this session for next time: {summary}")
    print("Bye! Run me again later: I'll remember you.")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as todo:
        print(f"\n>>> Next step: {todo}. Finish it, then run the file again.")
