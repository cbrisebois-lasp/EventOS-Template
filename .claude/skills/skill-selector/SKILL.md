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
| `/use-container` | User wants to start, stop, or log into the Docker container, or run commands inside it |
| `/improve-container` | User wants to modify the Dockerfile, docker-compose, helper script, or container setup |
| `/version-control` | User wants to commit, branch, rebase, or is about to make changes that need version control |
| `/improve-build-system` | User wants to modify CMakeLists.txt, Makefiles, test discovery, coverage, or build configuration |
| `/use-build-system` | User wants to build the app, run tests, generate coverage, or clean build artifacts |
| `/run-tests` | User wants to run unit tests, check test results, or generate coverage |

## Selection guidelines

- If the task is purely about **using** something (building, testing, running), load the `use-*` skill.
- If the task is about **modifying** infrastructure (Dockerfile, compose, helper scripts), load the `improve-*` skill.
- If the task is about **modifying** the build system (CMake, Makefiles, test discovery), load `/improve-build-system`.
- If the task is about application code (`app/source/`), you may not need any of these skills — use your judgment.
- Do not load skills that are clearly irrelevant. Fewer is better.
