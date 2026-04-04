---
name: run-tests
description: How to run unit tests — all tests or with coverage
user-invocable: true
---

# Running Tests

All tests run inside the Docker container. The container must be running — start with `container_start` if needed.

## MCP tools

| Goal | MCP Tool |
|------|----------|
| Build and run all tests | `run_tests` |
| List available test targets | `list_tests` |
| Run tests with coverage report | `run_coverage` |

## Test target naming

Targets follow the pattern `<module>_<SourceFile>_c_exe`:

| Source file | Test file | Target name |
|-------------|-----------|-------------|
| `app/source/sample/Init.c` | `test/source/sample/test_Init.c` | `sample_Init_c_exe` |
| `app/source/sample/Transform.c` | `test/source/sample/test_Transform.c` | `sample_Transform_c_exe` |

Use `list_tests` to see all available targets when unsure.

## When to run tests

- After modifying any source file under `app/source/` that has a matching test
- After modifying any test file under `test/source/`
- Before committing — run all tests to verify nothing is broken

## Interpreting results

Each test target is a single executable containing multiple assertions. CTest reports pass/fail per executable. If a test fails, the output shows which assertions failed and their location.

- **100% passed** — all good
- **FAILED** — read the output for the failing assertion, fix the source or test, re-run

## Advanced usage

For operations beyond what the MCP tools provide (e.g. running a single target, filtering by module), use the build system directly inside the container via the helper script or docker compose exec:

```bash
# Run tests filtered by module
cd test && MODULE_FILTER=sample make test

# Run a single test target
cd test && make build && cd build && ctest -R sample_Init_c_exe --output-on-failure
```
