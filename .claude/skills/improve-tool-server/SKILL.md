---
name: improve-tool-server
description: Architecture and guidelines for modifying, improving, or extending the MCP tool server
user-invocable: true
---

# Improving the MCP Tool Server

Use this skill when modifying, extending, or improving the MCP server's architecture, adding new tools, or changing how existing tools work.

## Server location

| Path | Role |
| ---- | ---- |
| `.claude/mcp/eventos-template.py` | Entry point — thin launcher |
| `.claude/mcp/eventos_template/` | Server package |
| `.mcp.json` | MCP server configuration (entry point path) |
| `.claude/settings.json` | Tool permission whitelist |

## Architecture

The server is a multi-file Python package with three layers. Each layer has a clear role, return type, and dependency direction: handlers depend on helpers, helpers depend on lib.

### Layer 1: Lib (`lib/`)

Shared utilities used by multiple helpers. Lib only contains things that would otherwise be duplicated across helpers.

| Module | Contents |
| ------ | -------- |
| `lib/result.py` | `HelperResult` and `StepLog` dataclasses — the structured return type for all helpers |
| `lib/paths.py` | Centralized constants: `PROJECT_ROOT`, `COMPOSE_FILE`, `COMPOSE_CMD`, `CONTAINER_SERVICE`, `CONTAINER_USER`, `CONTAINER_WORKDIR`, etc. |
| `lib/subprocess.py` | `run_subprocess(cmd, timeout, env)` — universal subprocess wrapper. Returns `(output: str, returncode: int)` |

**Rules:**
- Lib is for shared utilities only — if only one helper needs it, it belongs in the helper
- Lib functions do not log steps — that is the helper's job

### Layer 2: Helpers (`helpers/`)

Each helper performs one discrete operation. Helpers are the unit of reuse across handlers. They own their logic directly — building commands, calling `run_subprocess`, parsing output — rather than delegating to intermediate lib functions.

**Rules:**
- Every helper returns a `HelperResult(success, log, result)`
- Helpers log structured entries via `result.add_step(step, detail)` to describe what they are doing
- Helpers do not call other helpers
- Helpers accept explicit arguments — no implicit global state
- Helpers import shared utilities from `lib/` (paths, subprocess, result types)
- One helper file per logical operation (e.g. `container.py`, `exec.py`)

### Layer 3: Handlers (`handlers/`)

One handler per tool, one file per handler (named after the tool).

**Rules:**
- Each handler has the signature `def handle_<tool_name>(args: dict) -> str`
- Handlers call helpers sequentially — each call depends on the prior succeeding
- On first helper failure, the handler short-circuits and returns `format_failure()` with all helper results collected so far
- On success, the handler returns only the result data — helper logs are discarded
- Handlers never call lib functions directly — always go through helpers

### Transport and dispatch

| Module | Contents |
| ------ | -------- |
| `server.py` | JSON-RPC over stdio: `send()`, `handle_request()`, `main()`. Imports `TOOLS` from `tools.py` and `HANDLERS` from `handlers/` |
| `tools.py` | `TOOLS` list — all tool schema definitions (name, description, inputSchema) |
| `eventos-template.py` | Thin launcher that adds the package to `sys.path` and calls `server.main()` |

### Dependency graph

```
eventos-template.py (launcher)
    └── server.py (transport)
            ├── tools.py (schemas)
            └── handlers/ (dispatch)
                    └── helpers/ (operations)
                            └── lib/ (shared utilities)
```

## How to add a new tool

See the `/add-new-tool` skill for a detailed step-by-step guide.

## How to modify an existing tool

1. Identify which layer the change belongs to:
   - **Schema change** (new parameter, updated description) — edit `tools.py`
   - **Behavioral change** (different command, different logic) — edit the helper in `helpers/`
   - **New shared utility needed** — add to `lib/`, then use from the helper
   - **Output format change** — edit the handler in `handlers/`
2. Changes should not cross layer boundaries unnecessarily

## HelperResult structure

```python
@dataclass
class StepLog:
    step: str       # Short label for the operation (e.g. "exec", "check", "parse")
    detail: str     # Human-readable description of what happened

@dataclass
class HelperResult:
    success: bool
    log: list[StepLog]   # Ordered list of steps the helper performed
    result: Any          # Payload for the handler on success (usually str)
```

## Failure diagnostic format

When a handler short-circuits on failure, `format_failure()` composes the helper logs into a diagnostic that an agent or user can parse to determine what went wrong:

```
<tool_name> failed at helper <N>/<total>

--- Helper 1: <helper_name> (ok) ---
  [step] detail
  [step] detail

--- Helper 2: <helper_name> (FAILED) ---
  [step] detail
  [step] detail
```

## Design principles

- **One handler per tool** — no config-driven dispatch or lambda wrappers
- **One file per handler** — named after the tool (e.g. `handlers/run_tests.py`)
- **Helpers are the unit of reuse** — if two handlers need the same operation, they share a helper
- **Helpers own their operations** — they build commands and call `run_subprocess` directly, not through intermediate lib functions
- **Lib is for shared utilities only** — paths, subprocess wrapper, result types
- **Fail fast** — handlers stop on first failure, helpers return structured diagnostics
- **Zero external dependencies** — stdlib only
