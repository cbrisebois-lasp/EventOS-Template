---
name: audit-tool-server
description: How to audit the MCP tool server for overlaps that should become shared helpers or lib entries
user-invocable: true
---

# Auditing the MCP Tool Server

Use this skill when the user asks you to audit the tool server. The goal is to find overlaps across helpers that should be consolidated into shared helpers or promoted to lib.

## What you are looking for

As tools are added independently, similar patterns emerge across helpers. An audit identifies these overlaps and recommends where to extract shared code.

| Overlap type | What it looks like | What to do |
| ------------ | ------------------ | ---------- |
| **Helper overlap** | Two or more helpers perform the same operation (same subprocess call, same command pattern) | Extract a shared helper that both handlers can call |
| **Lib candidate** | Two or more helpers duplicate the same low-level utility (e.g. building compose commands, parsing output) | Extract to a shared lib function |

## Server package location

```
.claude/mcp/
    eventos_template/
        lib/          # Shared utilities — subprocess wrapper, paths, result types
        helpers/      # Operations — own their logic, call run_subprocess directly
        handlers/     # Tool entry points — one file per tool, call helpers
        tools.py      # Tool schemas
        server.py     # JSON-RPC transport
```

## Key architectural rule

Helpers own their operations directly — they build commands and call `run_subprocess` from lib. Lib only contains utilities that are genuinely shared across multiple helpers. If only one helper uses something, it belongs in the helper, not lib.

## Audit process

### Step 1: Read all helpers

Read every file in `helpers/`. For each helper function, note:

- **Name** and **file**
- **What it does** — the subprocess command it builds and runs
- **Arguments** it accepts
- **What it logs** (step names and details)
- **What lib imports** it uses (paths, subprocess, result)

### Step 2: Read all handlers

Read every file in `handlers/` (one per tool). For each handler, note:

- **Which helpers** it calls and in what order
- **Parameter extraction** logic (what it pulls from `args`)
- **Any inline logic** that isn't delegated to a helper (this is a smell — handlers should only call helpers)

### Step 3: Identify overlaps

Compare your notes and look for the following patterns:

#### Duplicate operations across helpers

Two or more helpers that build the same kind of subprocess command with similar arguments. This means a shared helper should be extracted.

**Example:** If two helpers both build `COMPOSE_CMD + ["exec", "-T", "-u", CONTAINER_USER, ...]` with slightly different commands, a shared `execute_in_container` helper should handle this.

#### Repeated utility patterns

A low-level pattern that appears in multiple helpers but isn't captured in lib. This is a candidate for a new lib function.

**Example:** If several helpers all parse JSON output from compose commands with the same error handling, extract a `parse_compose_json()` lib function.

#### Handlers with inline logic

A handler that contains logic beyond parameter extraction, helper calls, and failure formatting. Any conditional logic, string building, or data transformation in a handler should move into a helper.

#### Helpers that could be parameterized

Two helpers that do the same thing with different arguments. If the structure is identical except for a parameter, one parameterized helper could replace both.

**Example:** If `build_app()` runs `make build` and `clean_build()` runs `make clean` with identical structure, a shared `run_make(target)` helper could serve both.

#### Unused lib functions

A lib function that no helper imports. Either remove it, or check if helpers are reimplementing its logic inline.

### Step 4: Assess each overlap

Not every overlap is worth fixing. For each one, consider:

- **How many places** share the pattern? (2 is borderline, 3+ is clear)
- **Is the shared code stable** or likely to diverge? (If the two uses will evolve differently, don't merge them)
- **Does extracting it simplify the callers?** (If the shared function needs many parameters to handle all cases, it may be worse than the duplication)

### Step 5: Present findings

Present the audit as a report:

#### Overlap inventory

For each overlap found, describe:

- **What**: The duplicated pattern
- **Where**: Which files and functions contain it
- **Recommendation**: Extract to shared helper, extract to lib, or leave as-is (with reasoning)

#### Summary checklist

```
## Tool server audit

### Helper overlaps
- [ ] <description> — <files involved> — <recommendation>

### Lib candidates
- [ ] <description> — <files involved> — <recommendation>

### Handler inline logic
- [ ] <description> — <handler> — <recommendation>

### Unused lib functions
- [ ] <function name> — <recommendation>

### No issues found
- [x] All helpers perform distinct operations
- [x] No handlers contain inline logic
- [x] All lib functions are used by multiple helpers
```

Mark items as `[x]` if no issues were found in that category.

## What NOT to do during an audit

- **Do not make changes** — the audit produces a report, not code modifications
- **Do not reorganize file structure** — the audit is about code overlaps within the existing structure
- **Do not evaluate tool schemas or descriptions** — that is a separate concern
- **Do not assess the transport layer** (`server.py`) — it is not part of the tool architecture
