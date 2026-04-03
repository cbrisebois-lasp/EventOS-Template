---
name: use-build-system
description: How to build, test, and generate coverage using the available MCP tools and fallback commands
user-invocable: true
---

# Using the Build System

All build and test commands run inside the Docker container. Use the MCP tools below to interact with the build system. If MCP tools are not connected, fall back to `container_exec` or the helper script.

## Prerequisites

The container must be running. Check with `container_status` and start with `container_start` if needed.

## MCP tools

### Application build

| Goal | MCP Tool | Notes |
|------|----------|-------|
| Build the application | `build_app` | Runs `make build` at the project root |
| Clean all build artifacts | `build_clean` | Removes both `build/` and `test/build/` |

### Test build and execution

| Goal | MCP Tool | Parameters |
|------|----------|------------|
| Build and run all tests | `run_tests` | No parameters |
| Run tests for one module | `run_tests` | `module` (e.g. `"sample"`) |
| Run a single test target | `run_tests` | `target` (e.g. `"sample_Init_c_exe"`) |
| List available test targets | `list_tests` | |
| Run tests with coverage report | `run_coverage` | `module` (optional) |

### Test target naming

Test targets follow the pattern `<module>_<SourceFile>_c_exe`. For example:
- `app/source/sample/Init.c` → `sample_Init_c_exe`
- `app/source/sample/Transform.c` → `sample_Transform_c_exe`

Use `list_tests` to see all available targets.

## Fallback: container_exec

If the dedicated build tools are not available, use `container_exec` with the equivalent commands:

```
container_exec command="make build"                          # build app
container_exec command="make clean"                          # clean all
container_exec command="make test"                           # run all tests
container_exec command="cd test && make test"                # run tests directly
container_exec command="cd test && MODULE_FILTER=sample make test"  # filter by module
container_exec command="cd test && make coverage"            # coverage report
```

## Fallback: helper script + manual commands

```bash
./docker/docker_env.sh login     # open shell in container
make build                       # build app
make test                        # run all tests
make coverage                    # run tests with coverage
make clean                       # clean all build dirs
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
1. `run_tests` with the relevant `module` or `target`
2. Fix any failures, repeat

**Before committing:**
1. `run_tests` (all tests) to verify nothing is broken
2. Optionally `run_coverage` to check coverage

**After modifying test infrastructure (CMakeLists.txt, Makefiles):**
1. `build_clean` to clear cached build state
2. `run_tests` to verify discovery and execution still work
