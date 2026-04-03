---
name: audit-tool-server
description: How to audit the MCP server for structural improvements — duplicate helpers, dispatch patterns, and helper call chains
user-invocable: true
---

# Auditing the MCP Tool Server

Use this skill when a user asks you to audit, review, or improve the structure of the MCP server. The server evolves as tools are added, and its internal patterns (helpers, dispatch, call chains) should be periodically reviewed.

## Server location

| File | Role |
|------|------|
| `.claude/mcp/eventos-template.py` | MCP server — tool definitions, helpers, handlers, JSON-RPC transport |
| `.claude/helpers/tool-grapher/generate_tool_graph.py` | Generates a DOT graph of the tool-to-helper call hierarchy |

## Audit process

### 1. Generate the call graph

Run the grapher to get the current tool hierarchy:

```bash
python3 .claude/helpers/tool-grapher/generate_tool_graph.py
```

This outputs DOT source showing:
- **Tool -> Helper edges** with numbered labels for serial call order
- **Helper -> Helper edges** (dashed) showing internal chains
- **Simple tools** resolved from the `SIMPLE_TOOLS` config dict

Render to SVG for visual inspection if Graphviz is available:

```bash
python3 .claude/helpers/tool-grapher/generate_tool_graph.py -o graph.svg
```

### 2. Read the server and identify patterns

Read the full server file and categorize every tool handler into one of:

| Category | Description | Current example |
|----------|-------------|-----------------|
| **Simple (config-driven)** | Single helper call + output formatting. Defined in `SIMPLE_TOOLS` dict, dispatched by `handle_simple_tool()`. | `build_app`, `container_start` |
| **Custom handler** | Unique logic that can't be expressed as config (branching, parameter extraction, fallback chains). Defined as a standalone `handle_*()` function. | `run_tests`, `container_status` |

### 3. Check for issues

Look for the following problems, in priority order:

#### Duplicate helper logic

Multiple helpers doing the same thing with different code paths. Signs:
- Raw `subprocess.run()` calls outside of `run_compose()` or `exec_in_container()`
- Multiple functions checking container status independently
- Copy-pasted error handling or output formatting

**Resolution**: Converge into a single helper. Callers should use the helper, not reimplement it.

#### Missing helper serialization

A tool handler manually calling a precondition check before calling another helper, when the helper itself should enforce the precondition. Signs:
- Multiple handlers with identical guard patterns (e.g., `if not container_is_running(): return ...`)
- A helper that assumes state without verifying it

**Resolution**: Move the precondition into the helper so callers don't need to repeat it.

#### Handlers that should be config-driven

A handler function whose body is just "call one helper, format the output." Signs:
- Handler body is 3-5 lines
- No branching on input parameters
- Output formatting matches an existing pattern (OK/FAILED or success/failure message)

**Resolution**: Add an entry to `SIMPLE_TOOLS` and delete the handler function.

#### Handlers that outgrew their config entry

A `SIMPLE_TOOLS` entry that now needs conditional logic, parameter extraction, or multiple helper calls. Signs:
- The tool's requirements changed and a simple config entry can no longer express them

**Resolution**: Promote to a custom handler function.

### 4. Check the grapher itself

If the server's dispatch patterns changed (e.g., new config dict, new helper, renamed function), verify the grapher still produces an accurate graph:

- **`KNOWN_HELPERS`** in the grapher must list all helper functions
- **`HELPER_FIELD_MAP`** must map `SIMPLE_TOOLS` `"helper"` field values to function names
- **`parse_simple_tools()`** must match the structure of the `SIMPLE_TOOLS` dict

Run the grapher after any server changes and compare the output to the actual code.

## Current server architecture

### Helpers (call chain)

```
run_compose(args, timeout)          # Runs any docker compose command
  ^
  |
container_is_running()              # Bool check via run_compose(["ps", "-q", ...])
  ^
  |
exec_in_container(cmd, workdir, timeout)  # Checks container_is_running(), then runs compose exec
```

All container interaction flows through `run_compose()` at the bottom of the chain. `exec_in_container()` enforces the running precondition internally — callers do not need to check.

### Dispatch pattern

```
SIMPLE_TOOLS dict  -->  handle_simple_tool()  -->  run_compose / exec_in_container
Custom handlers    -->  handle_*() functions   -->  run_compose / exec_in_container / container_is_running
```

The `HANDLERS` dict merges both: simple tools generate lambda entries, custom handlers are referenced directly.

### Design principles

- **One code path per concern**: Container status checking, command execution, and compose invocation each live in exactly one helper.
- **Helpers enforce their own preconditions**: `exec_in_container` checks `container_is_running` internally. Callers trust the helper.
- **Config over code for simple tools**: If a tool is just "call helper, format output," it belongs in `SIMPLE_TOOLS`, not a function.
- **Custom handlers for branching logic**: If a tool needs conditionals, parameter extraction, or multi-step flows, it gets its own function.

## Output

Present audit findings as a checklist:

```
## Tool server audit

- [x] No duplicate helper logic
- [ ] Missing serialization: `handle_foo` checks `container_is_running()` before `exec_in_container()`
- [x] All simple handlers are config-driven
- [x] No custom handlers that should be config entries
- [x] Grapher matches server structure

### Recommendations
1. Move the running check from `handle_foo` into `exec_in_container`
2. ...
```
