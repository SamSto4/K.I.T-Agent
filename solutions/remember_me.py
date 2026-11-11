"""
Week 11 · Final project · SOLUTION: Remember Me - an assistant that remembers you across sessions.

Run it in a normal terminal (it waits for you to type):  python solutions/remember_me.py
Commands while chatting:  /memory   /forget <key>   quit
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
    memory = load_memory(path)
    name = memory.get("name")
    if name:
        print(f"Remy: Welcome back, {name}! I remember {len(memory)} things about you. (/memory shows them)")
    else:
        print("Remy: Hi! I'm Remy. Tell me about yourself and I'll remember it next time.")
    return memory


# ---------- TODO 2: handle one message ------------------------------------------
def handle_message(message, memory, history, path=MEMORY_FILE, collection=SESSIONS):
    """Remember new facts, recall a relevant past session, answer, and update the chat history."""
    facts = extract_facts(message)                     # 1. what's worth remembering?
    if facts:
        memory.update(facts)
        save_memory(memory, path)
    past = recall_episodes(message, k=1, collection=collection)   # 2. episodic memory
    past_text = past[0]["text"] if past and past[0]["score"] >= MIN_SCORE else ""
    reply = chat_with_memory(message, memory, history, persona=PERSONA, past=past_text)  # 3. answer
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return reply


# ---------- TODO 3: privacy commands ----------------------------------------------
def handle_command(command, memory, path=MEMORY_FILE):
    """/memory shows every saved fact; /forget <key> deletes one fact and saves the file."""
    if command == "/memory":
        if not memory:
            return "I don't remember anything about you yet."
        return "\n".join(f"  {k}: {v}" for k, v in memory.items())
    if command.startswith("/forget "):
        key = command.removeprefix("/forget ").strip()
        if key not in memory:
            return f"I don't have anything saved as '{key}'."
        del memory[key]
        save_memory(memory, path)
        return f"Forgotten: {key}."
    return "Commands: /memory, /forget <key>, quit"


# ---------- TODO 4: end the session ------------------------------------------------
SUMMARY_SYSTEM = ("Summarise this conversation in 2 sentences for the assistant's future self: what the user "
                  "wanted, what was suggested, and anything to follow up. Don't include sensitive data.")


def end_session(history, collection=SESSIONS):
    """Save a short summary of this conversation as an episode, so a later session can recall it."""
    if not history:
        return None
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    summary = ask_claude(transcript, system=SUMMARY_SYSTEM)
    save_episode(summary, collection=collection)
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
