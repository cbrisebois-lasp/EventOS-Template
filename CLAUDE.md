# CLAUDE.md

## First Step

**Before starting any work, invoke `/skill-selector` to load the skills relevant to the user's request.**

## Project Overview

EventOS-Template is a template repository for bootstrapping new eventOS-based projects. Users clone this repo, then provide local clones of the EventOS and UnitTest frameworks via environment variables. A Docker Compose setup mounts the frameworks and builds the project inside a container.

## Architecture

### Framework Integration

EventOS and UnitTest are external dependencies, not vendored. They are mounted into the build container via docker-compose using `EVENTOS_PATH` and `UNITTEST_PATH` environment variables.

- **EventOS** provides a static library target (`eventos`) via `add_subdirectory()`
- **UnitTest** provides a header-only interface target (`unittest`) and a `unittest_add_tests()` CMake function for test auto-discovery

### Directory Layout

- `app/source/` — User-written application sources (auto-discovered by CMake)
- `app/include/` — User-written public headers
- `test/source/` — Test files mirroring `app/source/` (naming: `test_<source>.c`)
- `test/include/` — Test-specific headers and mock overrides
- `cmake/` — Toolchain files
- `docker/` — Dockerfile, docker-compose, and `.env` configuration

### Build System

- Top-level `CMakeLists.txt` builds the application, hooks EventOS via `add_subdirectory()`
- `test/CMakeLists.txt` uses `unittest_add_tests()` for test auto-discovery
- `Makefile` provides convenience wrappers (`make build`, `make test`, `make coverage`)
- Cross-compilation is configured via `CMAKE_TOOLCHAIN_FILE`

## Glossary

Key EventOS terms used throughout the codebase:

- **Service** — An application-level module organized as a directory under `app/source/<name>/` and `app/include/<name>/`. Services are not a formal EventOS type; they are a structural convention. Each service exposes a public header, a private header, and one `.c` file per function (command handler, tick, housekeeping, etc.).

- **Action** — The fundamental unit of work in EventOS. An action is a function pointer (`typedef void(*os_action_t)(os_context_t context)`) that runs to completion (non-preemptive, cooperative). Actions are executed by the OS dispatch loop (`os_Exec()`). The following functions operate on actions:
  - `os_Do(action, contextSize)` — Enqueue action with a newly allocated context. Returns the context pointer for the caller to populate.
  - `os_DoWith(action, context)` — Enqueue action reusing an existing context.
  - `os_DoAfter(action, contextSize, ticks)` — Schedule action with a new context after a delay (in ticks). Returns the context pointer.
  - `os_DoAfterWith(action, context, ticks)` — Schedule action with an existing context after a delay.

- **Context** — A block of OS-managed memory passed to an action as an opaque pointer (`typedef void *os_context_t`). Internally tracked with a reference count so the OS can share a single context across multiple subscribers and free it when the last consumer finishes. Applications must never hold context references long-term; the OS may relocate the data.

## Skill Catalog

| Skill | Purpose |
|-------|---------|
| `/use-container` | Interacting with the Docker container — MCP tools and fallback commands |
| `/improve-container` | Guidelines for modifying Dockerfile, compose, helper script, and container setup |
| `/version-control` | Branching, committing, and rebasing rules for this repo |
| `/improve-build-system` | Modifying CMake, Makefiles, test discovery, coverage, or build configuration |
| `/use-build-system` | Building the app, running tests, generating coverage, or cleaning build artifacts |
| `/run-tests` | Running unit tests, checking results, or generating coverage |
