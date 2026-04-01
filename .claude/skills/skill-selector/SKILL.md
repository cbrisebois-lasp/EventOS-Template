---
name: skill-selector
description: Evaluate the user's prompt and load the most relevant skills before beginning work
user-invocable: true
---

# Skill Selector

Before doing any work on the user's request, reason about which skills will be needed and load them.

## Process

1. Read the user's prompt carefully.
2. Review the skill catalog below.
3. Select 1-3 skills that are most relevant to the task.
4. Invoke each selected skill to load its context.
5. Only then begin working on the user's request.

## Skill Catalog

| Skill | When to load |
|-------|-------------|
| `/use-build-system` | User wants to build the project or configure the toolchain |
| `/improve-build-system` | User wants to modify CMakeLists, Makefiles, linker script, or test infrastructure |
| `/run-tests` | User wants to run tests, filter by module, run a single test, or generate coverage |
| `/use-container` | User wants to start, stop, or log into the Docker container |
| `/improve-container` | User wants to modify the Dockerfile, docker-compose, or helper script |
| `/improve-route` | User wants to modify or understand the route service (packet routing, routing tables, commands, HK, code generation) |
| `/use-hal-comip` | User wants to write code that sends or receives packets via ComIp (PacNet interfaces) |
| `/version-control` | User wants to commit, branch, rebase, or is about to make changes that need version control |

## Selection guidelines

- If the task is purely about **using** something (building, testing, running), load the `use-*` skill.
- If the task involves **changing** infrastructure (build system, container), load the `improve-*` skill AND the corresponding `use-*` skill (to understand current behavior before modifying it).
- If the task is about application code (`app/source/`), you may not need any of these skills — use your judgment.
- Do not load skills that are clearly irrelevant. Fewer is better.
