"""
test_memory.py - does your Remember Me assistant really remember you across sessions?

It plays two short sessions with your functions from remember_me.py and checks the results.
It uses its own test memory file and test collection, so your real memory.json is not touched.
About 5 short Claude calls.

Run:  python test_memory.py
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from chromadb.errors import NotFoundError      # noqa: E402
import remember_me as R                        # noqa: E402  (your project code)
from lab2_planner import client, recall_episodes  # noqa: E402

TEST_FILE = HERE / "test_memory.json"
TEST_COLLECTION = "test_sessions"
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"   ({detail})" if detail else ""))


def saved_facts():
    return json.loads(TEST_FILE.read_text(encoding="utf-8")) if TEST_FILE.exists() else {}


def clean():
    TEST_FILE.unlink(missing_ok=True)
    try:
        client.delete_collection(TEST_COLLECTION)
    except NotFoundError:
        pass


def main():
    clean()
    print("--- Session 1 ---")
    memory = R.start_session(TEST_FILE)
    check("1. a new user starts with an empty memory", memory == {})
    history = []
    reply = R.handle_message("Hi, I'm Noa. I'm vegetarian and I love live jazz.", memory, history,
                             path=TEST_FILE, collection=TEST_COLLECTION)
    print("Remy:", reply)
    facts = saved_facts()
    check("2. the new facts are saved in the memory file",
          any("vegetarian" in str(v).lower() for v in facts.values()), facts)
    memory["test_key"] = "delete me"
    R.save_memory(memory, TEST_FILE)
    print(R.handle_command("/forget test_key", memory, TEST_FILE))
    check("3. /forget deletes a fact from the file", "test_key" not in saved_facts())
    summary = R.end_session(history, collection=TEST_COLLECTION)
    check("4. the session is saved as an episode", bool(summary), summary)

    print("\n--- Session 2 (a fresh start, like reopening the program) ---")
    memory2 = R.start_session(TEST_FILE)
    check("5. the facts survive a restart", len(memory2) >= 1, f"{len(memory2)} facts")
    question = "What should I cook tonight?"
    past = recall_episodes(question, collection=TEST_COLLECTION)
    check(f"6. session 1 is recalled (score >= {R.MIN_SCORE})", past and past[0]["score"] >= R.MIN_SCORE,
          f"score {past[0]['score']}" if past else "nothing found")
    print("You:", question)
    print("Remy:", R.handle_message(question, memory2, [], path=TEST_FILE, collection=TEST_COLLECTION))

    print(f"\n{sum(results)}/{len(results)} checks passed.")
    print("Now read Remy's last answer yourself: does it use what it remembered (vegetarian)?")
    clean()


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as todo:
        print(f"\n>>> Not finished yet: {todo}.")
