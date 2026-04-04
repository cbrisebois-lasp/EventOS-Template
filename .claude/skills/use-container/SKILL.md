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

| Goal | MCP Tool |
|------|----------|
| Start the container | `container_start` |
| Stop the container | `container_stop` |
| Rebuild the Docker image | `container_build` |
| Remove container and volumes | `container_remove` |

### Build and test

| Goal | MCP Tool |
|------|----------|
| Build the application | `build_app` |
| Clean build artifacts | `build_clean` |
| Build and run all tests | `run_tests` |
| List available test targets | `list_tests` |
| Run tests with coverage report | `run_coverage` |

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
