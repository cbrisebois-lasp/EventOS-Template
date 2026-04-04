---
name: add-new-tool
description: Step-by-step guide for adding a new MCP tool to the EventOS-Template server
user-invocable: true
---

# Adding a New Tool to the MCP Server

Use this skill when adding a new tool to the EventOS-Template MCP server. Follow each step in order.

## Server package layout

```
.claude/mcp/
    eventos-template.py              # Entry point (thin launcher)
    eventos_template/
        server.py                    # JSON-RPC transport
        tools.py                     # Tool schema definitions
        handlers/
            __init__.py              # HANDLERS dict (tool name -> handler function)
            formatting.py            # format_failure() utility
            run_tests.py             # One file per tool, named after the tool
            ...
        helpers/
            __init__.py
            container.py             # is_container_running
            exec.py                  # execute_in_container
            ...
        lib/
            result.py                # HelperResult, StepLog dataclasses
            paths.py                 # Path and environment constants
            subprocess.py            # run_subprocess() wrapper
```

## Step 1: Define the tool schema

Add an entry to the `TOOLS` list in `eventos_template/tools.py`.

Every tool schema has three fields:

| Field | Description |
| ----- | ----------- |
| `name` | Unique tool name, snake_case (e.g. `container_logs`) |
| `description` | One sentence describing what the tool does — this is what the agent reads to decide whether to call it |
| `inputSchema` | JSON Schema object defining the tool's parameters |

Example — tool with no parameters:

```python
{
    "name": "container_logs",
    "description": "Retrieve the last 100 lines of container logs.",
    "inputSchema": {"type": "object", "properties": {}}
}
```

Example — tool with parameters:

```python
{
    "name": "container_logs",
    "description": "Retrieve container logs. Optionally specify the number of lines.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "lines": {
                "type": "integer",
                "description": "Number of log lines to retrieve (default: 100)."
            }
        }
    }
}
```

Use `"required": ["param_name"]` in the schema if a parameter is mandatory.

## Step 2: Identify helpers needed

Check what already exists in `helpers/` before creating anything new. Helpers are shared across handlers — reuse them when the operation is the same.

| Helper module | What it provides |
| ------------- | ---------------- |
| `helpers/container.py` | `is_container_running()` — checks if the container is up |
| `helpers/exec.py` | `execute_in_container(cmd, workdir, timeout)` — runs a command inside the container |

**If your tool runs a command inside the container**, your handler will chain `is_container_running` → `execute_in_container`.

**If your tool needs a new operation**, create a new helper. Every helper must:

1. Create a `HelperResult(success=False)`
2. Log steps via `result.add_step(step, detail)` describing what it is doing
3. Perform the operation directly (using `run_subprocess` from lib and constants from `lib/paths.py`)
4. Set `result.success` and `result.result` based on the outcome
5. Return the `HelperResult`

```python
from ..lib.paths import COMPOSE_CMD, CONTAINER_SERVICE
from ..lib.result import HelperResult
from ..lib.subprocess import run_subprocess


def get_container_logs(lines=100):
    r = HelperResult(success=False)
    r.add_step("exec", f"Retrieving last {lines} lines of container logs")
    cmd = COMPOSE_CMD + ["logs", "--tail", str(lines), CONTAINER_SERVICE]
    output, rc = run_subprocess(cmd, timeout=30)
    r.success = rc == 0
    r.result = output
    r.add_step("result", f"exit code {rc}")
    return r
```

**Helper rules:**
- Accept explicit arguments — no reaching into `args` dicts
- Return `HelperResult` — never raw strings or tuples
- Do not call other helpers
- Own the operation directly — build commands and call `run_subprocess`, don't delegate through intermediate lib functions
- Log enough detail that an agent can diagnose failures from the log alone

## Step 3: Create the handler

Create a new file in `handlers/` named after the tool (e.g. `handlers/container_logs.py`).

Every handler must:

1. Extract parameters from the `args` dict
2. Call helper(s) sequentially
3. Short-circuit on first helper failure, returning `format_failure()`
4. On success, return only the result data (discard logs)

```python
from ..helpers.container import get_container_logs
from .formatting import format_failure


def handle_container_logs(args):
    lines = args.get("lines", 100)

    result = get_container_logs(lines=lines)
    if not result.success:
        return format_failure("container_logs", result)
    return result.result
```

**Handler rules:**
- Signature: `def handle_<tool_name>(args: dict) -> str`
- One file per handler, named after the tool
- Call helpers — never lib functions directly
- Short-circuit on first failure — do not continue after a helper fails
- On success, return `result.result` (a string) — logs are discarded

**If the handler calls multiple helpers:**

```python
def handle_some_tool(args):
    step1 = first_helper()
    if not step1.success:
        return format_failure("some_tool", step1)

    step2 = second_helper(step1.result)
    if not step2.success:
        return format_failure("some_tool", step1, step2)

    return step2.result
```

Pass all helper results (including successful ones) to `format_failure()` so the diagnostic shows the full chain.

## Step 4: Register the handler

Add the handler to the `HANDLERS` dict in `handlers/__init__.py`:

```python
from .container_logs import handle_container_logs

HANDLERS = {
    # ... existing entries ...
    "container_logs": handle_container_logs,
}
```

The key must match the tool's `name` field in `tools.py` exactly.

## Step 5: Add the tool permission

Add the tool to the `allow` list in `.claude/settings.json`:

```json
"mcp__eventos-template__container_logs"
```

The format is `mcp__<server-name>__<tool-name>`.

## Step 6: Verify

1. Restart the MCP server (or restart Claude Code) so the new tool is picked up
2. Call the tool via Claude Code and confirm it works
3. Test the failure path — e.g. stop the container and call the tool to verify the diagnostic log is readable

## Checklist

- [ ] Tool schema added to `tools.py`
- [ ] Helpers identified (reuse existing or create new)
- [ ] Handler created in `handlers/<tool_name>.py` — calls helpers, short-circuits on failure
- [ ] Handler registered in `handlers/__init__.py`
- [ ] Permission added to `.claude/settings.json`
- [ ] Tool verified end-to-end (success and failure paths)
