# MCP Server Re-Architecture Plan

## Context

The MCP server at `.claude/mcp/eventos-template.py` is a 409-line monolith mixing transport, dispatch, helpers, and handlers. The user wants a complete rewrite into a multi-file package with clean separation into three layers: **server lib** (primitives), **helpers** (operations), and **handlers** (tool entry points). The new design introduces structured logging in helpers so that on failure, the agent receives a diagnostic log showing exactly which step failed and why.

## Architecture

### Three layers

| Layer | Role | Returns |
|-------|------|---------|
| **Server lib** | Low-level primitives (subprocess, compose, container checks) | `(output, returncode)` tuples |
| **Helpers** | Orchestrate lib calls for one discrete operation | `HelperResult(success, log, result)` |
| **Handlers** | One per tool. Call helpers sequentially, short-circuit on first failure | `str` (response text) |

### Key design rules

- Handlers short-circuit on first helper failure and return the helper's structured log as a diagnostic
- On success, handlers return only the result data — logs are discarded
- Helpers log structured entries (`{"step": ..., "detail": ...}`) about their operations
- Server lib functions are reusable primitives shared across helpers
- No SIMPLE_TOOLS config pattern — every tool gets an explicit handler function

## Package layout

```
.claude/mcp/
    eventos-template.py              # Thin launcher (keeps .mcp.json working)
    eventos_template/                # Package
        __init__.py
        server.py                    # JSON-RPC transport + main loop
        tools.py                     # TOOLS list (11 tool schemas, unchanged)
        handlers/
            __init__.py              # Exports HANDLERS dict
            formatting.py            # format_failure() utility
            container.py             # 6 handlers: start, stop, status, build, remove, exec
            build.py                 # 2 handlers: build_app, build_clean
            tests.py                 # 3 handlers: run_tests, list_tests, run_coverage
        helpers/
            __init__.py
            container.py             # start, stop, status, build_image, remove, exec_command
            build.py                 # build_app, clean_build
            tests.py                 # build_tests, execute_tests, list_tests, run_coverage
        lib/
            __init__.py
            result.py                # HelperResult + StepLog dataclasses
            paths.py                 # Constants: PROJECT_ROOT, COMPOSE_FILE, COMPOSE_CMD, etc.
            subprocess.py            # run_subprocess() — universal subprocess wrapper
            compose.py               # run_compose() — docker compose command runner
            container.py             # container_is_running(), exec_in_container()
```

## Module details

### `lib/result.py` — Helper result type

```python
@dataclass
class StepLog:
    step: str
    detail: str

@dataclass
class HelperResult:
    success: bool
    log: list[StepLog] = field(default_factory=list)
    result: Any = None

    def add_step(self, step: str, detail: str) -> "HelperResult":
        self.log.append(StepLog(step=step, detail=detail))
        return self
```

### `lib/paths.py` — Centralized constants

All path/env constants currently at the top of the monolith: `SCRIPT_DIR`, `PROJECT_ROOT`, `COMPOSE_FILE`, `COMPOSE_CMD`, `CONTAINER_SERVICE`, `CONTAINER_USER`, `PROJECT_DIR`, `COMPOSE_ENV`, `CONTAINER_WORKDIR`.

### `lib/subprocess.py` — Universal subprocess wrapper

Single `run_subprocess(cmd, timeout, env)` function. Handles capture, timeout, `FileNotFoundError`. Returns `(output: str, returncode: int)`. All subprocess calls in the server funnel through this.

### `lib/compose.py` — Docker compose runner

`run_compose(args, timeout)` — builds full compose command and delegates to `run_subprocess()`.

### `lib/container.py` — Container primitives

- `container_is_running()` — bool check via `run_compose(["ps", "-q", ...])` (unchanged logic)
- `exec_in_container(cmd, workdir, timeout)` — checks `container_is_running()`, then runs compose exec via `run_subprocess()`. Returns `(output, returncode)`. Stays in lib because multiple helpers need it as a primitive.

### `helpers/*.py` — Operation layer

Each helper:
1. Creates a `HelperResult(success=False)`
2. Logs steps as it goes via `result.add_step()`
3. Calls lib functions
4. Sets `success` and `result` based on outcome
5. Returns the `HelperResult`

Example — `helpers/build.py::build_app()`:
```python
def build_app():
    r = HelperResult(success=False)
    r.add_step("exec", "Running make build")
    output, rc = exec_in_container("make build", timeout=300)
    r.success = rc == 0
    r.result = output
    r.add_step("result", f"exit code {rc}")
    return r
```

### `handlers/*.py` — Tool entry points

Each handler:
1. Extracts parameters from `args` dict
2. Calls helpers sequentially
3. Short-circuits on first failure, returning `format_failure()`
4. On success, returns result string

### `handlers/formatting.py` — Failure log formatter

`format_failure(tool_name, *helper_results)` composes helper logs into a readable diagnostic:
```
run_tests failed at helper 2/2

--- Helper 1: build_tests (ok) ---
  [build] compiling test targets
  [result] exit code 0

--- Helper 2: execute_tests (FAILED) ---
  [run] all tests
  [result] exit code 1
  <test output>
```

### `tools.py` — Tool schemas

The `TOOLS` list copied verbatim from the current server. All 11 tool names and schemas unchanged.

### `server.py` — JSON-RPC transport

`send()`, `handle_request()`, `main()` — identical protocol logic to today. Imports `TOOLS` from `tools.py` and `HANDLERS` from `handlers/`.

### `eventos-template.py` — Thin launcher

```python
#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eventos_template.server import main
main()
```

## Current code mapping

| Current code | New location |
|---|---|
| `SCRIPT_DIR`, `PROJECT_ROOT`, path constants (lines 16-25) | `lib/paths.py` |
| `TOOLS` list (lines 30-126) | `tools.py` |
| `run_compose()` (lines 132-144) | `lib/compose.py` |
| `exec_in_container()` (lines 147-166) | `lib/container.py` |
| `container_is_running()` (lines 169-172) | `lib/container.py` |
| `SIMPLE_TOOLS` dict (lines 179-211) | Eliminated — each becomes an explicit handler |
| `handle_simple_tool()` (lines 214-225) | Eliminated |
| `handle_container_stop()` (lines 232-238) | `handlers/container.py` |
| `handle_container_status()` (lines 241-262) | `handlers/container.py` |
| `handle_container_exec()` (lines 265-275) | `handlers/container.py` |
| `handle_run_tests()` (lines 278-291) | `handlers/tests.py` |
| `handle_list_tests()` (lines 294-299) | `handlers/tests.py` |
| `handle_run_coverage()` (lines 302-311) | `handlers/tests.py` |
| `HANDLERS` dict (lines 318-326) | `handlers/__init__.py` |
| `send()`, `handle_request()`, `main()` (lines 333-408) | `server.py` |

## Implementation order

### Phase 1: Scaffolding and wiring

Set up the package structure, shared types, and transport layer so the server runs but has no tools yet.

1. Create directory structure (`eventos_template/`, `lib/`, `helpers/`, `handlers/`)
2. Create `lib/result.py` — `HelperResult` and `StepLog` dataclasses
3. Create `lib/paths.py` — centralized constants
4. Create `lib/subprocess.py` — universal subprocess wrapper
5. Create `handlers/__init__.py` — empty `HANDLERS` dict
6. Create `handlers/formatting.py` — `format_failure()` utility
7. Create `tools.py` — empty `TOOLS` list (tools added one at a time below)
8. Create `server.py` — JSON-RPC transport
9. Rewrite `eventos-template.py` as thin launcher
10. Verify the server starts and responds to `initialize` and `tools/list`

### Phase 2: Migrate tools one at a time

Add each tool iteratively. For each tool:

1. Add its schema to `tools.py`
2. Identify what lib functions it needs — create new ones or reuse existing
3. Identify what helper(s) it needs — create new ones or reuse existing
4. Write its handler
5. Register the handler in `handlers/__init__.py`
6. Verify the tool works

As overlaps emerge between tools, they naturally reveal what belongs in lib vs helpers. The migration order is chosen so that foundational lib functions (compose, container checks) are introduced by the first tools and reused by later ones.

#### Tool migration order

| Step | Tool | Why this order |
| ---- | ---- | -------------- |
| 2a | `container_status` | Introduces `lib/compose.py` and `run_compose()` — no container-running precondition needed |
| 2b | `container_start` | Reuses `run_compose()`, simple compose call |
| 2c | `container_stop` | Reuses `run_compose()`, introduces `lib/container.py::container_is_running()` |
| 2d | `container_build` | Reuses `run_compose()`, simple compose call |
| 2e | `container_remove` | Reuses `run_compose()`, simple compose call |
| 2f | `container_exec` | Introduces `lib/container.py::exec_in_container()` (reuses `container_is_running()` + `run_compose()`) |
| 2g | `build_app` | Reuses `exec_in_container()`, first tool using it via helper layer |
| 2h | `build_clean` | Reuses `exec_in_container()`, same pattern as `build_app` |
| 2i | `list_tests` | Reuses `exec_in_container()` |
| 2j | `run_tests` | Reuses `exec_in_container()`, has branching logic (target/module/all) |
| 2k | `run_coverage` | Reuses `exec_in_container()`, has branching logic (module filter) |

### Phase 3: Cleanup

1. Remove the old monolith code (original `eventos-template.py` contents replaced by launcher)
2. Verify all 11 tools work end-to-end

## Files that don't change

- `.mcp.json` — entry point path unchanged
- `.claude/settings.json` — tool names unchanged

## Files that will need updating (separate effort)

- `.claude/helpers/tool-grapher/generate_tool_graph.py` — deferred; user has ideas for this
- `.claude/skills/improve-tool-server/SKILL.md` — update to reflect final architecture once migration is complete

## Verification

After each tool migration:

1. Start the server: `python3 .claude/mcp/eventos-template.py` (should accept JSON-RPC on stdin)
2. Verify the newly added tool works via Claude Code
3. Verify previously added tools still work (no regressions)

Final verification:

1. All 11 tools respond correctly
2. Test failure path: stop the container, then call `build_app` — should return structured diagnostic log
3. Confirm `.mcp.json` entry point still works (no path changes)
