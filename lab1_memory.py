"""
Week 11 · Lab 1 (Lesson 1): Give your assistant a memory.

An LLM forgets everything between calls. You fix that in 3 short parts:
  Part 1  build_prompt()                in-context memory: the recent chat history  (about 5 lines)
  Part 2  load_memory(), save_memory()  external memory: facts in memory.json       (about 4 lines)
  Part 3  extract_facts()               Claude decides what to remember             (2 lines)

Run:  python lab1_memory.py        runs every part you have finished
      python lab1_memory.py 3      runs only Part 3 (fewer Claude calls)

Your AI tutor: open https://jonathanpilnick.github.io/beginner_agentic_tutorial/week11/lab1
copy the prompt and paste it into Claude Code.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "solutions" else HERE   # works from either folder
sys.path.insert(1, str(ROOT))                             # after this file's own folder
from llm import ask_claude, ask_claude_json                # noqa: E402  (calls Claude through Claude Code)

# Print any character (Hebrew, emoji, arrows) even where the console isn't UTF-8 (Windows).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MEMORY_FILE = ROOT / "memory.json"        # your assistant's long-term memory (it stays on your laptop)
DEMO_FILE = ROOT / "demo_memory.json"     # used only by Part 2's restart demo

CHAT_SYSTEM = ("You are a friendly assistant. You know only what this conversation and your memory notes tell you "
               "about the user; ignore anything else. Answer the user's last message in at most 2 sentences.")


# ---------- Part 1: in-context memory ----------------------------------------
def build_prompt(history, user_message, max_messages=6):
    """Return the text Claude sees: the last `max_messages` messages of `history`,
    one per line as 'User: ...' or 'Assistant: ...', then 'User: <user_message>'.
    history is a list like [{"role": "user", "content": "Hi"}, {"role": "assistant", ...}]."""
    # TODO 1: make an empty list of lines. For each message in the LAST max_messages of
    #   history (hint: history[-max_messages:]), add "User: <content>" or "Assistant: <content>".
    #   Then add "User: <user_message>" and return the lines joined with "\n".
    raise NotImplementedError("TODO 1 in lab1_memory.py")


# ---------- Part 2: external memory in a file --------------------------------
def load_memory(path=MEMORY_FILE):
    """Return the saved facts as a dict, or {} if there is no memory file yet."""
    path = Path(path)
    # TODO 2a: if the file doesn't exist yet (path.exists()), return {}.
    #   Otherwise read its text (encoding="utf-8") and turn it into a dict with json.loads().
    raise NotImplementedError("TODO 2a in lab1_memory.py")


def save_memory(memory, path=MEMORY_FILE):
    """Write the facts to a JSON file that a person can read (UTF-8, indented)."""
    # TODO 2b: the opposite of load_memory(): turn the dict into JSON text with json.dumps()
    #   (indent=2 makes it readable, ensure_ascii=False keeps Hebrew readable) and write it to
    #   the file at `path` as UTF-8 text.
    raise NotImplementedError("TODO 2b in lab1_memory.py")


# ---------- Part 3: Claude decides what to remember ---------------------------
FACTS_SCHEMA = {
    "type": "object",
    "properties": {"facts": {"type": "object", "additionalProperties": {"type": "string"}}},
    "required": ["facts"],
}
EXTRACT_SYSTEM = (
    "You manage a user's long-term memory. From the user's message, pick out stable facts and preferences "
    "worth remembering in future conversations: name, diet, likes, dislikes, goals, budget, constraints. "
    "Use short snake_case keys and values of 1-5 words. If there is nothing worth remembering, return an empty object. "
    "Never store passwords, ID or card numbers, health details or other sensitive data."
)


def extract_facts(message):
    """Ask Claude which facts in `message` are worth remembering.
    Returns a dict such as {"name": "Noa", "diet": "vegetarian"}."""
    # TODO 3: ask Claude for JSON that follows FACTS_SCHEMA (ask_claude_json() in llm.py), with
    #   EXTRACT_SYSTEM as the system prompt. Return only the facts dict from the result.
    raise NotImplementedError("TODO 3 in lab1_memory.py")


def chat_with_memory(user_message, memory, history, persona=CHAT_SYSTEM, past=""):
    """Answer using the saved facts (external memory) and the recent chat (in-context memory)."""
    facts = "\n".join(f"- {k}: {v}" for k, v in memory.items()) or "- (nothing yet)"
    system = persona + "\n\nWhat you remember about the user from earlier sessions:\n" + facts
    if past:
        system += "\n\nA past conversation that may be relevant:\n" + past
    return ask_claude(build_prompt(history, user_message), system=system)


# ---------- the demo: run the parts you have finished --------------------------
CHAT = [
    {"role": "user", "content": "Hi! I'm Noa, and I'm learning Python this year."},
    {"role": "assistant", "content": "Nice to meet you, Noa! Python is a great first language."},
    {"role": "user", "content": "Can you suggest a first project?"},
    {"role": "assistant", "content": "Try a small to-do list app that saves to a file."},
]
QUESTION = "Which programming language am I learning?"


def part1():
    print("=== Part 1 · In-context memory ===")
    print("What Claude sees with a window of only 2 messages (the first message has dropped out):")
    print(build_prompt(CHAT, QUESTION, max_messages=2), "\n")
    print("Q:", QUESTION)
    print("  no history  :", ask_claude(QUESTION, system=CHAT_SYSTEM))
    print("  with history:", ask_claude(build_prompt(CHAT, QUESTION), system=CHAT_SYSTEM))
    print()


def part2():
    print("=== Part 2 · External memory: a file that survives a restart ===")
    demo = load_memory(DEMO_FILE)
    demo["runs"] = demo.get("runs", 0) + 1
    save_memory(demo, DEMO_FILE)
    print(f"This is run #{demo['runs']}. It is saved in {DEMO_FILE.name}: {DEMO_FILE.read_text(encoding='utf-8')}")
    print("Run the file again: the number goes up, because the file outlives the program.\n")


def part3():
    print("=== Part 3 · Claude decides what to remember ===")
    message = "Hi, I'm Noa. I'm vegetarian, I love live jazz, and I'm on a student budget."
    facts = extract_facts(message)
    print("User said:", message)
    print("Facts to remember:", facts)
    memory = load_memory()
    memory.update(facts)
    save_memory(memory)
    print(f"memory.json now holds {len(memory)} facts.\n")
    question = "Any ideas for dinner and something to do tonight?"
    print("New session, empty chat history. Q:", question)
    print("A:", chat_with_memory(question, load_memory(), history=[]))


if __name__ == "__main__":
    # python lab1_memory.py      runs every part you have finished
    # python lab1_memory.py 3    runs only Part 3 (saves Claude calls once Parts 1-2 work)
    chosen = sys.argv[1:] or ["1", "2", "3"]
    try:
        for number, part in (("1", part1), ("2", part2), ("3", part3)):
            if number in chosen:
                part()
        if len(chosen) == 3:
            print("\nAll 3 parts work. Look inside memory.json: that is your assistant's long-term memory.")
    except NotImplementedError as todo:
        print(f"\n>>> Next step: {todo}. Finish it, then run the file again.")
