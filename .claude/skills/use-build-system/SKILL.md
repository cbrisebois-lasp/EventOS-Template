---
name: use-build-system
description: How to build, test, and generate coverage using the available MCP tools and fallback commands
user-invocable: true
---

# Using the Build System

All build and test commands run inside the Docker container. Use the MCP tools below to interact with the build system.

## Prerequisites

The container must be running. Start with `container_start` if needed.

## MCP tools

### Application build

| Goal | MCP Tool |
|------|----------|
| Build the application | `build_app` |
| Clean all build artifacts | `build_clean` |

### Test build and execution

| Goal | MCP Tool |
|------|----------|
| Build and run all tests | `run_tests` |
| List available test targets | `list_tests` |
| Run tests with coverage report | `run_coverage` |

### Test target naming

Test targets follow the pattern `<module>_<SourceFile>_c_exe`. For example:
- `app/source/sample/Init.c` → `sample_Init_c_exe`
- `app/source/sample/Transform.c` → `sample_Transform_c_exe`

Use `list_tests` to see all available targets.

## Fallback: helper script + manual commands

If MCP tools are not connected, use the helper script to open a shell and run commands directly:

```bash
./docker/docker_env.sh login     # open shell in container
make build                       # build app
make test                        # run all tests
make clean                       # clean all build dirs
cd test && make coverage         # run tests with coverage
cd test && MODULE_FILTER=sample make test  # filter by module
```

## Build outputs

| Output | Location |
|--------|----------|
| Application binary | `build/EventOS-App.elf` |
| Test executables | `test/build/<target_name>` |
| Coverage HTML report | `test/build/coverage_report/index.html` |

## Common workflows

**After modifying application source code:**
1. `build_app` to verify it compiles

**After modifying application source code that has tests:**
1. `run_tests` to verify tests pass
2. Fix any failures, repeat

**Before committing:**
1. `run_tests` to verify nothing is broken
2. Optionally `run_coverage` to check coverage

**After modifying test infrastructure (CMakeLists.txt, Makefiles):**
1. `build_clean` to clear cached build state
2. `run_tests` to verify discovery and execution still work
