"""
llm.py - call Claude from Python through your Claude Code subscription.

No API key and no extra purchase: this runs Claude Code's documented
non-interactive "print" mode (`claude -p`) and reads the answer back.

  ask_claude(prompt, system=...)               -> the reply as text
  ask_claude_json(prompt, schema, system=...)  -> a dict that matches your JSON Schema

  Docs: https://code.claude.com/docs/en/headless
        https://code.claude.com/docs/en/cli-reference

Notes
- Every call counts toward your Claude plan's usage limits (the same limits
  as Claude and Claude Code). Don't call it inside a big loop.
- Claude Code reports a "total_cost_usd" figure: an estimate of the equivalent
  API price. With a Claude subscription you are NOT billed per call.
- If ANTHROPIC_API_KEY is set, Claude Code would bill that API key instead of
  your subscription. This helper removes it for the child process.
- Never add --bare: bare mode ignores your subscription login and needs an API key.
  (The docs say bare mode may become the default for -p in a future release. If you
  then see an authentication error, check https://code.claude.com/docs/en/headless)
"""

import json
import os
import shutil
import subprocess
import tempfile

# "haiku" is fast and light on usage limits. Use "sonnet" for harder questions,
# or set COURSE_CLAUDE_MODEL="" to use your account's default model.
DEFAULT_MODEL = os.environ.get("COURSE_CLAUDE_MODEL", "haiku")


class ClaudeCodeError(RuntimeError):
    """Raised when the claude command is missing, not logged in, or fails."""


def _find_claude() -> str:
    path = shutil.which("claude")
    if not path:
        raise ClaudeCodeError(
            "Could not find the `claude` command.\n"
            "Open a NEW terminal and run:  claude --version\n"
            "If that fails, reinstall Claude Code: https://code.claude.com/docs/en/setup"
        )
    return path


def _run(prompt, system, model, timeout, extra_args=()):
    """Run one `claude -p` call and return Claude Code's JSON result as a dict."""
    # Write the system prompt to a temp file: avoids shell-quoting problems on Windows.
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as f:
        f.write(system)
        system_file = f.name

    def build_cmd(safe_mode: bool) -> list:
        cmd = [_find_claude(), "-p"]
        if safe_mode:
            cmd.append("--safe-mode")            # don't load CLAUDE.md, plugins, hooks...
        cmd += [
            "--system-prompt-file", system_file,  # replace Claude Code's coding prompt
            "--tools", "",                        # no built-in tools: just answer
            "--disallowedTools", "mcp__*",        # no MCP tools either
            "--no-session-persistence",           # don't save these runs as sessions
            "--output-format", "json",
            *extra_args,
        ]
        if model:
            cmd += ["--model", model]
        return cmd

    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)           # always use the subscription login

    try:
        for safe_mode in (True, False):
            proc = subprocess.run(
                build_cmd(safe_mode),
                input=prompt,                     # the prompt goes in through stdin
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout, env=env,
                cwd=tempfile.gettempdir(),        # run outside the kit, so the tutor's CLAUDE.md isn't loaded
            )
            # Older Claude Code versions don't know --safe-mode: retry without it.
            if "unknown option" in proc.stderr and "--safe-mode" in proc.stderr:
                continue
            break
    except subprocess.TimeoutExpired:
        raise ClaudeCodeError(f"Claude did not answer within {timeout} seconds.")
    finally:
        os.remove(system_file)

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise ClaudeCodeError(
            "Unexpected output from claude.\n"
            f"stdout: {proc.stdout[:500]}\nstderr: {proc.stderr[:500]}\n"
            "Try running `claude` once in a terminal to log in, then `claude update`."
        )
    if data.get("is_error"):
        raise ClaudeCodeError(
            f"Claude Code reported an error: {data.get('result')}\n"
            "Not logged in? Run `claude` once in a terminal. Usage limit? Wait and retry.")
    return data


def ask_claude(prompt: str,
               system: str = "You are a helpful assistant.",
               model: str = DEFAULT_MODEL,
               timeout: int = 180) -> str:
    """Send one prompt to Claude and return the text of the reply."""
    return (_run(prompt, system, model, timeout).get("result") or "").strip()


def ask_claude_json(prompt: str,
                    schema: dict,
                    system: str = "You are a helpful assistant.",
                    model: str = DEFAULT_MODEL,
                    timeout: int = 180) -> dict:
    """Send one prompt and get back a dict that matches `schema` (a JSON Schema).

    Uses Claude Code's --json-schema option: the validated answer arrives in the
    "structured_output" field of the JSON result.
    """
    data = _run(prompt, system, model, timeout,
                extra_args=("--json-schema", json.dumps(schema)))
    if "structured_output" not in data:            # e.g. Claude declined the request
        raise ClaudeCodeError(
            "Claude didn't return the JSON we asked for. Its reply was:\n"
            f"{(data.get('result') or '')[:500]}\n"
            "Old Claude Code? Run `claude update` (it needs the --json-schema option).")
    return data["structured_output"]


if __name__ == "__main__":
    print(ask_claude("Reply with exactly three words: memory lab ready"))
    print(ask_claude_json("Return status ready.", {"type": "object", "properties": {
        "status": {"type": "string"}}, "required": ["status"]}))
