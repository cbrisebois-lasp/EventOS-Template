---
name: improve-container
description: Guidelines and constraints for modifying the EventOS-Template Docker container setup — Dockerfile, compose, helper script, and MCP server
user-invocable: true
---

# Improving the EventOS-Template Container

Follow these guidelines when making changes to the container infrastructure.

## Files and their responsibilities

| File | Role | Change carefully |
|------|------|-----------------|
| `docker/Dockerfile` | Image definition: Ubuntu 24.04 base, installed packages, user setup | Yes — affects all developers |
| `docker/docker-compose.yaml` | Container orchestration: volumes, environment variables, image build | Yes — affects runtime behavior |
| `docker/docker_env.sh` | Helper script: start, stop, login, build, remove | Low risk |
| `docker/.env.example` | Template for developer-overridable variables | Low risk |
| `docker/.gitignore` | Excludes `docker/.env` from version control | Low risk |

## Constraints

- **Base image**: Ubuntu 24.04. Package installs use `apt-get`.
- **User**: `user` created via `useradd -m`. Has passwordless sudo. Home directory is `/home/user`. Do not change this — the volume mounts and working directory depend on it.
- **WORKDIR**: `/home/user/${PROJECT_DIR}` — `PROJECT_DIR` is a build arg defaulting to `project`. The helper script auto-sets it to the repo root directory name (e.g. `EventOS-Template`). The compose file passes it as a build arg and uses it in the volume mount.
- **Container runs `sleep infinity`**: Set as the Dockerfile `ENTRYPOINT`. Keep this — it keeps the container alive for interactive use. Do not change it to a build command.
- **Docker and Podman**: `docker_env.sh` supports both via auto-detection. Test changes against Docker at minimum; avoid Docker-only features that break Podman compatibility.
- **Container name**: `eventos-app` — set in `docker-compose.yaml` and referenced by the MCP server.

## Variable resolution flow

`PROJECT_DIR` flows through three layers:

1. **`docker_env.sh`** — exports `PROJECT_DIR` as the repo root basename (e.g. `EventOS-Template`) unless already set
2. **`docker-compose.yaml`** — passes `PROJECT_DIR` as a build arg and uses it in the volume mount path, with `project` as a static fallback
3. **`Dockerfile`** — receives `PROJECT_DIR` as an `ARG` (default `project`) and uses it in `WORKDIR`

When using the helper script, the repo name propagates automatically. When running `docker compose` directly without the helper script, `PROJECT_DIR` falls back to `project` unless set in the environment or `docker/.env`.

## Volume mounts (defined in docker-compose.yaml)

| Host path | Container path | Purpose |
|-----------|---------------|---------|
| `..` (repo root, relative to compose file) | `/home/user/${PROJECT_DIR}` | Application code |
| `${EVENTOS_PATH}` (default: `../../EventOS`) | `/home/user/EventOS` | EventOS framework |
| `${UNITTEST_PATH}` (default: `../../UnitTest`) | `/home/user/UnitTest` | UnitTest framework |

Framework paths default to sibling directories next to the repo root. Developers can override them in `docker/.env`.

## Environment variables inside the container

The compose file sets these so CMake can locate the frameworks at their mount points:

- `EVENTOS_PATH=/home/user/EventOS`
- `UNITTEST_PATH=/home/user/UnitTest`

These are the container-side paths, not the host paths. They must stay in sync with the volume mount targets above.

## When adding packages to the Dockerfile

- Add to the existing `apt-get install` block to keep a single layer.
- `rm -rf /var/lib/apt/lists/*` runs at the end of the install — keep it there.
- Document why the package is needed if it is not obvious.

## When modifying the helper script

- Preserve the `case` structure for commands.
- The `remove` command has a confirmation prompt — keep this safety check.
- `remove force` bypasses the prompt — this is intentional for CI use.
- The script auto-detects Docker vs Podman — new commands should use the `execute` helper function and `${DOCKER_COMPOSE_COMMAND}` variable.
- The script resolves `DOCKER_COMPOSE_CONFIG` to its own directory — commands work regardless of the caller's working directory.
- `PROJECT_DIR` is derived at the top of the script from the repo root basename — keep this before any compose commands.

## When modifying docker-compose.yaml

- The bind mount `source` uses `..` (relative to the compose file location, i.e. the repo root).
- Commented-out mounts exist for an optional cross-compiler toolchain — preserve these.
- Do not add port mappings without coordinating with the team — they affect the host network.

## Required packages (do not remove)

gcc, g++, gdb, cmake, ninja-build, make, lcov, gawk, python3, git — all needed for building and testing the project.
