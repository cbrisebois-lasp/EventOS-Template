cmake_minimum_required(VERSION 3.20)
project(EventOS-App C ASM)

# ---------------------------------------------------------------------------
# Framework paths — set via environment variables or CMake cache
# ---------------------------------------------------------------------------
if(DEFINED ENV{EVENTOS_PATH})
    set(EVENTOS_PATH "$ENV{EVENTOS_PATH}" CACHE PATH "Path to EventOS framework")
elseif(NOT DEFINED EVENTOS_PATH)
    message(FATAL_ERROR
        "EVENTOS_PATH is not set. Point it at your local EventOS clone:\n"
        "  export EVENTOS_PATH=/path/to/EventOS\n"
        "  — or —\n"
        "  cmake -DEVENTOS_PATH=/path/to/EventOS ..")
endif()

if(DEFINED ENV{UNITTEST_PATH})
    set(UNITTEST_PATH "$ENV{UNITTEST_PATH}" CACHE PATH "Path to UnitTest framework")
elseif(NOT DEFINED UNITTEST_PATH)
    message(FATAL_ERROR
        "UNITTEST_PATH is not set. Point it at your local UnitTest clone:\n"
        "  export UNITTEST_PATH=/path/to/UnitTest\n"
        "  — or —\n"
        "  cmake -DUNITTEST_PATH=/path/to/UnitTest ..")
endif()

# ---------------------------------------------------------------------------
# Hook the frameworks
# ---------------------------------------------------------------------------
add_subdirectory(${EVENTOS_PATH} ${CMAKE_BINARY_DIR}/eventos)

# ---------------------------------------------------------------------------
# Application target
# ---------------------------------------------------------------------------
file(GLOB_RECURSE APP_C_SOURCES "${CMAKE_SOURCE_DIR}/app/source/*.c")
file(GLOB_RECURSE APP_ASM_SOURCES "${CMAKE_SOURCE_DIR}/app/source/*.S")

add_executable(${PROJECT_NAME}.elf
    ${APP_C_SOURCES}
    ${APP_ASM_SOURCES}
)

target_include_directories(${PROJECT_NAME}.elf PRIVATE
    ${CMAKE_SOURCE_DIR}/app/include
)

# Link against the eventOS library — this also pulls in eventOS public headers
target_link_libraries(${PROJECT_NAME}.elf PRIVATE eventos)

# ---------------------------------------------------------------------------
# Toolchain file (optional, for cross-compilation)
# ---------------------------------------------------------------------------
# Pass -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-example.cmake (or your own)
# when invoking CMake for cross-compilation. When no toolchain file is given,
# the system compiler is used (useful for host-based testing/simulation).

# ---------------------------------------------------------------------------
# Linker script (optional, set by user for their target platform)
# ---------------------------------------------------------------------------
if(DEFINED LINKER_SCRIPT)
    target_link_options(${PROJECT_NAME}.elf PRIVATE -T ${LINKER_SCRIPT})
endif()

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
