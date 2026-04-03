cmake_minimum_required(VERSION 3.20)
project(TestRunner C)

# ---------------------------------------------------------------------------
# Framework paths — inherited from environment or cache
# ---------------------------------------------------------------------------
if(DEFINED ENV{EVENTOS_PATH})
    set(EVENTOS_PATH "$ENV{EVENTOS_PATH}" CACHE PATH "Path to EventOS framework")
elseif(NOT DEFINED EVENTOS_PATH)
    message(FATAL_ERROR "EVENTOS_PATH is not set.")
endif()

if(DEFINED ENV{UNITTEST_PATH})
    set(UNITTEST_PATH "$ENV{UNITTEST_PATH}" CACHE PATH "Path to UnitTest framework")
elseif(NOT DEFINED UNITTEST_PATH)
    message(FATAL_ERROR "UNITTEST_PATH is not set.")
endif()

# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------
enable_testing()

option(VERBOSE_CUSTOM "Enable verbose status messages" OFF)
option(NO_REPORTS "Build without coverage instrumentation" OFF)

if(DEFINED MODULE_FILTER)
    message(STATUS "Filtering for module: ${MODULE_FILTER}")
endif()

set(BASE_WARN_FLAGS "-Wall -Wno-int-conversion -Wno-pointer-to-int-cast -Wno-unknown-pragmas -Wno-multistatement-macros")
set(CMAKE_C_STANDARD 11)

# Include paths: test overrides first, then app headers, then eventOS headers
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../app/include
    ${EVENTOS_PATH}/app/include
    ${UNITTEST_PATH}/framework
)

if(NO_REPORTS)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${BASE_WARN_FLAGS}")
else()
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${BASE_WARN_FLAGS} -fprofile-arcs -ftest-coverage")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --coverage")
endif()

# ---------------------------------------------------------------------------
# Auto-discover tests using UnitTest framework
# ---------------------------------------------------------------------------
include(${UNITTEST_PATH}/cmake/UnitTestDiscovery.cmake)

# List source files that are not expected to have tests
set(IGNORE_MISSING_TEST_FILES
    "main.c"
)

set(_ut_args
    APP_SOURCE_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/../app/source"
    TEST_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/source"
    IGNORE_FILES    ${IGNORE_MISSING_TEST_FILES}
)

if(DEFINED MODULE_FILTER AND NOT "${MODULE_FILTER}" STREQUAL "")
    list(APPEND _ut_args MODULE_FILTER "${MODULE_FILTER}")
endif()

if(VERBOSE_CUSTOM)
    list(APPEND _ut_args VERBOSE)
endif()

unittest_add_tests(${_ut_args})
