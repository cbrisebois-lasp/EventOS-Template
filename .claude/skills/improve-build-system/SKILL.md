---
name: improve-build-system
description: Guidelines and constraints for modifying the CMake and Make build system — application build, test discovery, coverage, and framework integration
user-invocable: true
---

# Improving the Build System

Follow these guidelines when making changes to the build infrastructure.

## Files and their responsibilities

| File | Role | Change carefully |
|------|------|-----------------|
| `CMakeLists.txt` | Top-level application build: hooks EventOS, glob-discovers app sources, links against `eventos` library | Yes — affects all builds |
| `test/CMakeLists.txt` | Test build: framework paths, include paths, compiler flags, test auto-discovery via UnitTest | Yes — affects all test runs |
| `Makefile` | Top-level convenience wrappers: `make build`, `make test`, `make coverage` | Low risk |
| `test/Makefile` | Test convenience wrappers: `make build`, `make test`, `make coverage` | Low risk |

## Two separate build systems

The project has two independent CMake projects with separate build directories:

1. **Application build** (`CMakeLists.txt`, builds into `build/`) — cross-compiles the `.elf` binary, links against EventOS
2. **Test build** (`test/CMakeLists.txt`, builds into `test/build/`) — compiles tests with the host compiler, runs via CTest

These are not nested — `test/CMakeLists.txt` is a standalone project, not a subdirectory of the top-level CMake. Each has its own `Makefile` wrapper.

## Application build (`CMakeLists.txt`)

- Sources are glob-discovered: `file(GLOB_RECURSE ... "app/source/*.c")` and `"app/source/*.S"`
- EventOS is hooked via `add_subdirectory()` and provides the `eventos` library target
- Include path: `app/include/`
- Optional cross-compilation via `-DCMAKE_TOOLCHAIN_FILE`
- Optional linker script via `-DLINKER_SCRIPT`

## Test build (`test/CMakeLists.txt`)

### Framework dependencies

Two external frameworks are required via environment variables:

- `EVENTOS_PATH` — EventOS framework (headers only, for include paths)
- `UNITTEST_PATH` — UnitTest framework (headers + CMake test discovery module)

### Include path order (matters for mock overrides)

```
1. test/include/          — test-specific headers and mock overrides (takes priority)
2. app/include/           — application public headers
3. ${EVENTOS_PATH}/app/include  — EventOS framework headers
4. ${UNITTEST_PATH}/framework   — UnitTest.h
```

Test headers intentionally shadow app/EventOS headers to enable mocking. Do not reorder.

### Test auto-discovery

Tests are discovered by `unittest_add_tests()` from the UnitTest framework (`${UNITTEST_PATH}/cmake/UnitTestDiscovery.cmake`). It:

1. Globs all `.c` files under `app/source/`
2. For each source file `<module>/<Name>.c`, looks for `test/source/<module>/test_<Name>.c`
3. Creates one executable per source/test pair, linking only those two files (plus any `EXTRA_SOURCES`)
4. Registers each executable with CTest via `add_test()`

Source files without a matching test file produce a warning, unless listed in `IGNORE_MISSING_TEST_FILES`.

### `unittest_add_tests()` parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| `APP_SOURCE_DIR` | Required | Absolute path to application source root |
| `TEST_SOURCE_DIR` | Required | Absolute path to test source root |
| `IGNORE_FILES` | Optional list | Relative paths from `APP_SOURCE_DIR` to skip (e.g. `"main.c"`) |
| `MODULE_FILTER` | Optional string | Only process sources whose module path contains this string |
| `EXTRA_SOURCES` | Optional list | Additional source files linked into every test executable |
| `VERBOSE` | Optional flag | Print status messages for each test added |

### Passing options safely

`MODULE_FILTER` and `VERBOSE` must only be passed when they have meaningful values. Passing an empty `MODULE_FILTER` or a boolean like `OFF` as a positional argument causes the CMake argument parser to misinterpret subsequent arguments. The current code builds the argument list conditionally:

```cmake
set(_ut_args
    APP_SOURCE_DIR  "..."
    TEST_SOURCE_DIR "..."
    IGNORE_FILES    ${IGNORE_MISSING_TEST_FILES}
)

if(DEFINED MODULE_FILTER AND NOT "${MODULE_FILTER}" STREQUAL "")
    list(APPEND _ut_args MODULE_FILTER "${MODULE_FILTER}")
endif()

if(VERBOSE_CUSTOM)
    list(APPEND _ut_args VERBOSE)
endif()

unittest_add_tests(${_ut_args})
```

Do not inline these options back into the `unittest_add_tests()` call.

### CMake options

| Option | Default | Purpose |
|--------|---------|---------|
| `NO_REPORTS` | `OFF` | When `ON`, disables coverage instrumentation (`-fprofile-arcs -ftest-coverage`) |
| `VERBOSE_CUSTOM` | `OFF` | When `ON`, passes `VERBOSE` flag to `unittest_add_tests()` |
| `MODULE_FILTER` | unset | When set via `-DMODULE_FILTER=<string>`, limits test discovery to matching modules |

### Coverage instrumentation

When `NO_REPORTS` is `OFF` (the default), the test build adds `-fprofile-arcs -ftest-coverage` to `CMAKE_C_FLAGS` and `--coverage` to linker flags. The `test/Makefile` `coverage` target then runs `lcov` and `genhtml` to produce an HTML report at `test/build/coverage_report/index.html`. Test files (`test_*`) are excluded from the coverage report.

## Makefile wrappers

### Top-level `Makefile`

| Target | Action |
|--------|--------|
| `build` | Configure and build the application |
| `test` | Delegates to `test/Makefile` (`make -C test all`) |
| `coverage` | Delegates to `test/Makefile` (`make -C test coverage`) |
| `clean` | Removes both `build/` and `test/build/` |

### Test `Makefile` (`test/Makefile`)

| Target | Action |
|--------|--------|
| `build` | CMake configure + Ninja build |
| `test` | Build then `ctest --output-on-failure` |
| `coverage` | Build with coverage, run tests, generate HTML report via lcov/genhtml |
| `clean` | Removes `test/build/` |

The test Makefile defaults `NO_REPORTS=1` (coverage off). The `coverage` target overrides this with `NO_REPORTS=0`.

## Adding a new source file

No build system changes needed. Both the application build (`GLOB_RECURSE`) and test discovery (`unittest_add_tests`) auto-discover new `.c` files.

If the new file should not have a test, add it to `IGNORE_MISSING_TEST_FILES` in `test/CMakeLists.txt`.

## Adding extra sources to specific test executables

If a test needs additional source files beyond its one app source (e.g. auto-generated config tables), use `EXTRA_SOURCES` in the `unittest_add_tests()` call. These files are linked into every test executable, so use sparingly. For module-specific extras, the `unittest_add_tests()` function would need extension — this is a UnitTest framework change, not a template change.

## Constraints

- **Generator**: Ninja. Both Makefiles hardcode `-G Ninja`.
- **C standard**: C11 (`CMAKE_C_STANDARD 11` in test build, inherits from EventOS in app build).
- **Compiler warnings**: `-Wall` with several `-Wno-*` suppressions. Do not remove existing suppressions without verifying they don't break the EventOS or UnitTest headers.
- **Build directories**: `build/` for application, `test/build/` for tests. Both are gitignored.
- **Framework paths**: Must come from environment variables. Do not hardcode paths.
- **UnitTest is external**: The test discovery CMake module and `UnitTest.h` header live in the UnitTest repo, not this project. Changes to test discovery behavior require modifying the UnitTest framework.
