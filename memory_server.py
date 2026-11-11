"""
memory_server.py - Clicker's memory brain as a small web service that only this Mac can reach.

The Clicker Mac app (Swift) can't call Python functions directly, so it talks to this server over
HTTP on localhost instead. The server reuses the functions from remember_me.py and the labs:
  facts about Sam   -> memory.json  (Lab 1: load_memory, save_memory, extract_facts)
  past sessions     -> chroma_db    (Lab 2: save_episode, recall_episodes)

Endpoints (all answers are JSON):
  GET  /health        is the server running?
  GET  /memory        every saved fact                              (like /memory)
  POST /context       {"message": "..."}  -> text to add to Clicker's system prompt
  POST /learn         {"message": "..."}  -> save new facts from what Sam said
  POST /forget        {"key": "..."}      -> delete one fact          (like /forget <key>)
  POST /end_session   {"history": [{"role": "user", "content": "..."}, ...]}  -> save a summary

Run it (with .venv active):  python memory_server.py
Try it in a second terminal:  curl http://127.0.0.1:8765/memory
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import remember_me as brain
from lab1_memory import load_memory, save_memory, extract_facts
from lab2_planner import recall_episodes

HOST = "127.0.0.1"           # localhost: only programs on this Mac can connect, nobody on the network
PORT = 8765
MAX_BODY = 1_000_000          # refuse requests bigger than about 1 MB
memory_lock = threading.Lock()  # two requests at once must not both write memory.json


def facts_text(memory):
    """The saved facts as a bullet list, like chat_with_memory() builds in Lab 1."""
    return "\n".join(f"- {key}: {value}" for key, value in memory.items()) or "- (nothing yet)"


def get_context(message):
    """Everything Clicker should know before it answers: the facts plus a similar past session."""
    memory = load_memory()
    past = ""
    if message:
        found = recall_episodes(message, k=1, collection=brain.SESSIONS)
        if found and found[0]["score"] >= brain.MIN_SCORE:
            past = found[0]["text"]
    prompt = "What you remember about Sam from earlier sessions:\n" + facts_text(memory)
    if past:
        prompt += "\n\nA past conversation that may be relevant:\n" + past
    return {"facts": memory, "past": past, "prompt": prompt}


def learn(message):
    """Save the facts in what Sam said. Only Sam's own words come here, never screenshots or web pages."""
    facts = extract_facts(message)          # the slow part (a Claude call), done outside the lock
    if facts:
        with memory_lock:
            memory = load_memory()          # reload, in case something changed meanwhile
            memory.update(facts)
            save_memory(memory)
    return {"learned": facts}


def forget(key):
    with memory_lock:
        memory = load_memory()
        return {"result": brain.handle_command(f"/forget {key}", memory)}


def end_session(history):
    summary = brain.end_session(history, collection=brain.SESSIONS)
    return {"summary": summary}


class MemoryHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            # The app stopped waiting (for example, Clicker saving a summary while it quits).
            # The work is already done, so there is nobody left to answer: that's fine.
            pass

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ValueError("request too big")
        data = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(data, dict):
            raise ValueError("send a JSON object")
        return data

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"ok": True})
        elif self.path == "/memory":
            self.send_json(200, {"facts": load_memory()})
        else:
            self.send_json(404, {"error": "unknown path"})

    def do_POST(self):
        try:
            data = self.read_json()
            if self.path == "/context":
                result = get_context(str(data.get("message", "")))
            elif self.path == "/learn":
                result = learn(str(data.get("message", "")))
            elif self.path == "/forget":
                result = forget(str(data.get("key", "")).strip())
            elif self.path == "/end_session":
                history = data.get("history") or []
                if not isinstance(history, list):
                    raise ValueError("history must be a list")
                result = end_session(history)
            else:
                return self.send_json(404, {"error": "unknown path"})
            self.send_json(200, result)
        except ValueError as error:          # bad input from the caller (json errors are ValueErrors too)
            self.send_json(400, {"error": str(error)})
        except Exception as error:           # something broke here: report it, keep the server running
            self.send_json(500, {"error": f"{type(error).__name__}: {error}"})

    def log_message(self, format, *args):    # one short line per request instead of the default log
        print(f"[memory] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), MemoryHandler)
    print(f"Clicker memory server running on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
