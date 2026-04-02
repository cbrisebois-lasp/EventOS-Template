---
name: use-container
description: How to interact with the EventOS-Template Docker container — which MCP tools to use and fallback commands
user-invocable: true
---

# Using the EventOS-Template Container

The development environment runs inside a Docker container (Ubuntu 24.04). All build and test commands should be run inside the container.

## Prerequisites

Before starting the container, optionally create `docker/.env` to override defaults:

```bash
cp docker/.env.example docker/.env
```

Framework paths default to sibling directories next to the repo (`../EventOS`, `../UnitTest`). Only create `.env` if your paths differ.

## MCP tools (preferred)

Use these MCP tools for all container interactions. They handle error reporting and are the recommended interface.

### Container lifecycle

| Goal | MCP Tool | Notes |
|------|----------|-------|
| Start the container | `container_start` | Builds the image if needed |
| Stop the container | `container_stop` | |
| Check if container is running | `container_status` | Returns: running, stopped, or not created |
| Rebuild the Docker image | `container_build` | Use after Dockerfile changes |
| Remove container and volumes | `container_remove` | Destructive — removes all container data |

### Running commands inside the container

| Goal | MCP Tool | Parameters |
|------|----------|------------|
| Run a shell command | `container_exec` | `command` (required), `workdir`, `timeout` |
| Build and run tests | `run_tests` | `module`, `target` (both optional) |
| List available test targets | `list_tests` | |
| Run tests with coverage report | `run_coverage` | `module` (optional) |

Use `container_exec` for any command that needs to run inside the container (e.g. `make build`, `cmake` invocations, installing packages).

## Fallback: helper script

If MCP tools are not connected, use the helper script:

```bash
./docker/docker_env.sh start    # Start the container
./docker/docker_env.sh stop     # Stop the container
./docker/docker_env.sh login    # Open a shell inside the container
./docker/docker_env.sh build    # Rebuild the Docker image
./docker/docker_env.sh remove   # Remove container and volumes (prompts for confirmation)
```

## Fallback: docker compose directly

```bash
docker compose -f docker/docker-compose.yaml exec -u user eventos-app <command>
```

## What is mounted where

| Host | Container | Description |
|------|-----------|-------------|
| Project root | `/home/user/${PROJECT_DIR}` | Application code (defaults to repo name) |
| `$EVENTOS_PATH` | `/home/user/EventOS` | EventOS framework |
| `$UNITTEST_PATH` | `/home/user/UnitTest` | UnitTest framework |

Changes on either side are immediately reflected.

## Container details

- **Container name**: `eventos-app`
- **User**: `user` (has passwordless sudo)
- **Installed tools**: gcc, g++, gdb, cmake, ninja-build, make, lcov, gawk, python3, git
