"""
setup_check.py - run this first (Week 11 Lab 1, Part 0):   python setup_check.py

Checks Python, the Python packages, the free local embedding model,
and that Python can talk to Claude through your Claude Code login.
"""

import json
import os
import platform
import shutil
import subprocess
import sys

OK, WARN, FAIL = "[ OK ]", "[WARN]", "[FAIL]"
problems = 0

# 1. Python version: the kit supports 3.11-3.14. onnxruntime (used by Chroma's embedder)
#    had no Python 3.15 build when this kit was made (November 2026), and on a Mac it
#    needs macOS 13+, with no Python 3.14 build for Intel Macs or macOS 13.
v = sys.version_info
mac = platform.mac_ver()[0] if sys.platform == "darwin" else ""
mac_major = int(mac.split(".")[0]) if mac else 0
if not (3, 11) <= v < (3, 15):
    problems += 1
    print(FAIL, f"Python {v.major}.{v.minor} found. Install Python 3.13 from python.org")
elif mac and mac_major < 13:
    problems += 1
    print(FAIL, f"macOS {mac}: ChromaDB's model runtime needs macOS 13 or newer. Pair with a neighbour.")
elif mac and v >= (3, 14) and (platform.machine() == "x86_64" or mac_major < 14):
    problems += 1
    print(FAIL, f"Python {v.major}.{v.minor} on this Mac: install Python 3.13 from python.org and recreate .venv")
else:
    print(OK, f"Python {v.major}.{v.minor}.{v.micro}")

# 2. Packages
for name in ("chromadb", "numpy"):
    try:
        mod = __import__(name)
        print(OK, f"{name} {getattr(mod, '__version__', '')}")
    except ImportError:
        problems += 1
        print(FAIL, f"{name} missing. Run:  pip install -r requirements.txt")

# 3. Embedding model (downloads under 100 MB the first time, then works offline)
try:
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    vec = DefaultEmbeddingFunction()(["hello world"])[0]
    print(OK, f"Embedding model works: 'hello world' -> {len(vec)} numbers")
except Exception as e:  # noqa: BLE001 - show any error to the student
    problems += 1
    print(FAIL, f"Embedding model failed: {e}")

# 4. Claude Code
claude = shutil.which("claude")
if not claude:
    problems += 1
    print(FAIL, "`claude` not found. Open a new terminal; see https://code.claude.com/docs/en/setup")
else:
    out = subprocess.run([claude, "--version"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    print(OK, f"Claude Code {out.stdout.strip()}")
    status = subprocess.run([claude, "auth", "status"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    try:
        info = json.loads(status.stdout)
        if info.get("loggedIn"):
            print(OK, f"Logged in (auth method: {info.get('authMethod')})")
        else:
            problems += 1
            print(FAIL, "Not logged in. Run `claude` once in a terminal and log in.")
    except json.JSONDecodeError:
        print(WARN, "Could not read `claude auth status`. Run `claude update`.")

if os.environ.get("ANTHROPIC_API_KEY"):
    print(WARN, "ANTHROPIC_API_KEY is set. llm.py ignores it, but Claude Code itself (your tutor chat) "
                "may bill that API key instead of your plan. Remove it from your environment.")

# 5. End-to-end call
if claude and problems == 0:
    try:
        from llm import ask_claude_json
        reply = ask_claude_json("Reply with status 'memory lab ready'.",
                                {"type": "object", "properties": {"status": {"type": "string"}}, "required": ["status"]})
        print(OK, f"Claude replied with JSON: {reply}")
    except Exception as e:  # noqa: BLE001
        problems += 1
        print(FAIL, f"Calling Claude failed: {e}")

print("\nAll good - you're ready for Week 11!" if problems == 0
      else f"\n{problems} problem(s) found - fix the [FAIL] lines above.")
