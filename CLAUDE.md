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

## Skill Catalog

| Skill | Purpose |
|-------|---------|
| `/use-container` | Interacting with the Docker container — MCP tools and fallback commands |
| `/improve-container` | Guidelines for modifying Dockerfile, compose, helper script, and container setup |
| `/version-control` | Branching, committing, and rebasing rules for this repo |
