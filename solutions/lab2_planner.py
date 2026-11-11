"""
Week 11 · Lab 2 (Lesson 2) · SOLUTION: Plan my evening - a multi-step agent with state and episodic memory.

Run:  python solutions/lab2_planner.py
      python solutions/lab2_planner.py "Plan a cheap Thursday evening with street food"
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "solutions" else HERE   # works from either folder
sys.path.insert(1, str(ROOT))                             # after this file's own folder
from llm import ask_claude, ask_claude_json                # noqa: E402  (calls Claude through Claude Code)
from lab1_memory import load_memory                        # noqa: E402  (your Lab 1 code)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = ROOT / "data"
client = chromadb.PersistentClient(path=str(ROOT / "chroma_db"))


# ---------- Given: two tools the agent can use ----------------------------------
PLACES = json.loads((DATA / "places.json").read_text(encoding="utf-8"))["places"]
WEATHER = json.loads((DATA / "weather.json").read_text(encoding="utf-8"))


def describe(place):
    return (f"{place['name']} ({place['type']}): {place['description']} Tags: {', '.join(place['tags'])}. "
            f"{place['price_nis']} NIS per person. Open {', '.join(place['days'])}, {place['hours']}.")


def build_places_index():
    """Store every place in ChromaDB so search_places() can find them by meaning (like Week 10)."""
    try:
        client.delete_collection("places")
    except NotFoundError:
        pass
    col = client.create_collection("places", configuration={"hnsw": {"space": "cosine"}})
    col.add(ids=[p["name"] for p in PLACES], documents=[describe(p) for p in PLACES])
    return col


places = build_places_index()


def search_places(query):
    """Tool: the 5 places that best match `query`, one per line."""
    res = places.query(query_texts=[query], n_results=5)
    return "\n".join(res["documents"][0])


def get_weather(day):
    """Tool: the (fictional) forecast for Thu, Fri or Sat."""
    key = day.strip()[:3].title()
    return WEATHER.get(key, f"No forecast for {day!r}. Known days: Thu, Fri, Sat.")


TOOLS = {"search_places": search_places, "get_weather": get_weather}


# ---------- Part 1: the planner agent breaks the goal into steps ----------------
PLAN_SCHEMA = {
    "type": "object",
    "properties": {"steps": {"type": "array", "minItems": 1, "maxItems": 5, "items": {
        "type": "object",
        "properties": {"tool": {"type": "string", "enum": list(TOOLS)},
                       "input": {"type": "string"},
                       "why": {"type": "string"}},
        "required": ["tool", "input", "why"]}}},
    "required": ["steps"],
}
PLANNER_SYSTEM = (
    "You are the PLANNER in a two-agent system. Break the user's goal into 2-5 steps. Each step uses one tool:\n"
    "- search_places: input = ONE short thing to find (2-6 words), e.g. 'cheap vegetarian dinner'\n"
    "- get_weather: input = a day: Thu, Fri or Sat\n"
    "All places are in the (fictional) Lemon Street neighbourhood. Use the user's preferences. "
    "Plan only: don't answer the goal yourself."
)


def facts_text(memory):
    return "\n".join(f"- {k}: {v}" for k, v in memory.items()) or "- (nothing saved yet)"


def make_plan(goal, memory, past=""):
    """Ask the planner agent for a list of steps: [{"tool": ..., "input": ..., "why": ...}, ...]."""
    prompt = (f"Goal: {goal}\n\nUser preferences (from memory.json):\n{facts_text(memory)}\n\n"
              f"A similar past episode (use it if it helps):\n{past or '(none)'}")
    return ask_claude_json(prompt, schema=PLAN_SCHEMA, system=PLANNER_SYSTEM)["steps"]


# ---------- Part 2: run the plan, keep the agent's state, let the writer answer --
def run_plan(goal, steps):
    """Run each step with its tool. The state dict records where the agent is and what it found."""
    state = {"goal": goal, "steps": steps, "results": [], "status": "running"}
    for i, step in enumerate(steps, 1):
        tool = TOOLS.get(step["tool"])
        output = tool(step["input"]) if tool else f"ERROR: unknown tool {step['tool']!r}"
        state["results"].append({"step": i, "tool": step["tool"], "input": step["input"], "output": output})
        print(f"  step {i}/{len(steps)} done: {step['tool']}({step['input']!r})")
    state["status"] = "done"
    return state


WRITER_SYSTEM = (
    "You are the WRITER in a two-agent system. Using ONLY the tool results you are given, write the user a short "
    "evening plan: where to go, when, the total cost per person, and why it fits their preferences. Skip anything "
    "that doesn't fit (diet, opening days, weather, budget). At most 120 words."
)


def write_answer(state, memory):
    """The second agent turns the state (goal + tool results) into the final answer."""
    results = "\n\n".join(f"Step {r['step']} · {r['tool']}({r['input']}):\n{r['output']}" for r in state["results"])
    prompt = f"Goal: {state['goal']}\n\nUser preferences:\n{facts_text(memory)}\n\nTool results:\n{results}"
    return ask_claude(prompt, system=WRITER_SYSTEM)


# ---------- Part 3: episodic memory (what happened in past runs) ----------------
def describe_episode(goal, steps, answer):
    plan = "; ".join(f"{s['tool']}({s['input']})" for s in steps)
    return f"Goal: {goal}\nPlan: {plan}\nOutcome: {answer[:400]}"


def episodes_collection(name):
    return client.get_or_create_collection(name, configuration={"hnsw": {"space": "cosine"}})


def save_episode(text, collection="episodes"):
    """Store one episode (a short text about something that happened) with the time it happened."""
    col = episodes_collection(collection)
    col.add(ids=[f"episode-{time.time_ns()}"], documents=[text],
            metadatas=[{"time": datetime.now().isoformat(timespec="seconds")}])
    return col.count()


def recall_episodes(query, k=1, collection="episodes"):
    """Return up to k past episodes most similar to `query`: [{"text", "time", "score"}, ...]."""
    col = episodes_collection(collection)
    if col.count() == 0:
        return []
    res = col.query(query_texts=[query], n_results=min(k, col.count()))
    return [{"text": doc, "time": meta["time"], "score": round(1 - dist, 2)}
            for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])]


# ---------- the agent ------------------------------------------------------------
def plan_my_evening(goal):
    memory = load_memory()                                   # Lab 1: semantic memory (facts)
    print(f"Goal: {goal}")
    print(f"Memory: {len(memory)} facts from memory.json")
    try:
        past = recall_episodes(goal)                         # Part 3: episodic memory
    except NotImplementedError:
        past = []                                            # (Part 3 isn't finished yet)
    if past:
        print(f"Recalled a similar past episode (score {past[0]['score']}, {past[0]['time']}):")
        print("  " + past[0]["text"].splitlines()[0])
    past_text = past[0]["text"] if past else ""

    print("\n[planner agent]")
    steps = make_plan(goal, memory, past_text)               # Part 1
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s['tool']}({s['input']!r})  - {s['why']}")

    print("\n[tools]")
    state = run_plan(goal, steps)                            # Part 2
    print(f"  state: status={state['status']!r}, {len(state['results'])} results")

    print("\n[writer agent]")
    answer = write_answer(state, memory)
    print(answer)

    count = save_episode(describe_episode(goal, steps, answer))   # Part 3
    print(f"\nSaved this run as episode #{count} in chroma_db (collection 'episodes').")
    best = recall_episodes(goal)[0]                                # Part 3 check
    print(f"Recall check: the closest episode to this goal scores {best['score']} ({best['time']}).")
    return answer


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or "Plan my Friday evening: dinner and live music, under 150 NIS."
    print(f"Indexed {places.count()} places for the search_places tool.\n")
    try:
        plan_my_evening(goal)
        print("\nAll 3 parts work. Run it again with a similar goal and watch it recall this episode.")
    except NotImplementedError as todo:
        print(f"\n>>> Next step: {todo}. Finish it, then run the file again.")
