# Week 11: Memory, State & Multi-Step Agents - student kit

In three lessons you give an assistant a memory, build a multi-step agent that plans, keeps its
state and remembers past runs, and finish with an assistant that remembers **you** across sessions:

| When | What you build | File |
|---|---|---|
| Lesson 1 · Lab 1 | **Give your assistant a memory**: chat history in the prompt, facts saved in `memory.json`, Claude decides what to remember | `lab1_memory.py` |
| Lesson 2 · Lab 2 | **Plan my evening**: a planner agent and a writer agent, tools, the agent's state, episodic memory in ChromaDB | `lab2_planner.py` |
| Lesson 3 · Project | **Remember Me**: an assistant that remembers your preferences across sessions, with `/memory` and `/forget` | `remember_me.py`, `PROJECT_BRIEF.md` |

Each step reuses the code you wrote in the one before it.

## Learn with your AI tutor (recommended)

Every lab has a page with a prompt you paste into **Claude Code**. Claude becomes your private tutor:
it explains what you'll build and why, teaches the ideas in short steps, and guides you while **you**
write the code.

- Lab pages: https://jonathanpilnick.github.io/beginner_agentic_tutorial/week11/index.html
- Or, inside this folder, run `claude` and type: `Be my tutor for Week 11 Lab 1. Read tutor/lab1_memory.md completely and follow it.`

## What runs where

Everything runs on your own computer with **free, open-source** packages.
The only account you need is your **Claude Code** login. No API keys, no purchases.

| Step | What runs it | Cost |
|---|---|---|
| Memory files | `memory.json` in this folder (plain JSON you can open and read) | free |
| Episodic memory and search | ChromaDB with the `all-MiniLM-L6-v2` model, on your laptop (the model download from Week 10 is reused) | free |
| The agents' thinking | Claude, through `claude -p` (Claude Code's non-interactive mode), see `llm.py` | your Claude plan's usage limits |

`memory.json` holds facts about you, so it is in `.gitignore`: it stays on your laptop.

## Setup (Lab 1, Part 0)

Your tutor walks you through this. To do it yourself:

1. Python **3.13** from python.org (on Windows, tick "Add python.exe to PATH").
   - Works on Python 3.11-3.13 everywhere, and on 3.14 except on Intel Macs and macOS 13. Not on 3.15 yet:
     onnxruntime, which ChromaDB needs, had no 3.15 build in November 2026. Macs need macOS 13 or newer.
   - Wrong version on Windows? `py install 3.13`, then use `py -3.13 -m venv .venv` in step 2.
2. Open a terminal **in this folder** (not inside OneDrive or another synced folder) and create a virtual environment:

   Windows (PowerShell):
   ```powershell
   py -3.13 -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
   In the old Command Prompt (cmd.exe), activate with `.venv\Scripts\activate.bat`.

   macOS / Linux (on a Mac, `python3` can be Apple's old 3.9, so name the version):
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Check Claude Code: `claude --version`, then `claude update` if it is old (the labs need the `--json-schema` option).
4. Run `python setup_check.py`. Every line should say `[ OK ]`.

## Files

| File | What it is |
|---|---|
| `lab1_memory.py` | Lab 1: 3 parts, 4 small TODOs |
| `lab2_planner.py` | Lab 2: 3 parts, 4 small TODOs (uses your Lab 1 `load_memory()`) |
| `remember_me.py` + `PROJECT_BRIEF.md` | Project: 4 TODOs, then test, write-up, peer review, demo |
| `test_memory.py` | Checks that your project remembers across two sessions (about 5 Claude calls) |
| `llm.py` | `ask_claude()` and `ask_claude_json()`: call Claude through your Claude Code login |
| `setup_check.py` | Checks Python, the packages, the embedding model and Claude Code |
| `data/` | **Fictional** places and weather for the Lemon Street neighbourhood, used in Lab 2 |
| `tutor/` | The tutor guides Claude Code reads |
| `solutions/` | Reference solutions. Try first! |

## Troubleshooting

- **`ModuleNotFoundError`:** your virtual environment isn't active. Activate it (step 2) and run again.
  Still failing? Run the environment's Python directly: `.venv\Scripts\python` (Windows) or `.venv/bin/python`.
- **Linux: "ensurepip is not available":** install the venv package (`sudo apt install python3-venv`), then repeat step 2.
- **`claude` is not recognized:** open a *new* terminal after installing Claude Code. See https://code.claude.com/docs/en/setup
- **"Claude didn't return the JSON we asked for":** run `claude update`; the labs use the `--json-schema` option.
- **`pip install` fails on onnxruntime:** no build for your Python or macOS (Python 3.15; 3.14 on an Intel Mac or macOS 13;
  macOS 12 or older). Install Python 3.13 and recreate `.venv`.
- **The embedding model download fails:** it comes once from `chroma-onnx-models.s3.amazonaws.com`. Retry on a stable connection.
- **Your Lab 1 code has a bug and Lab 2 needs it:** copy `solutions/lab1_memory.py` over `lab1_memory.py`.
- **`remember_me.py` seems to freeze inside Claude Code:** it waits for you to type. Run it in a normal terminal, not with `!`.
- **Start over with an empty memory:** delete `memory.json` (and the `chroma_db` folder for the episodes).
- **Windows on ARM laptops:** install the x64 ("AMD64") Python 3.13 from python.org; Windows 11 runs it under emulation.
- **You hit a usage limit:** wait for the reset. Run one part at a time, for example `python lab1_memory.py 3`.
