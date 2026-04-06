cmake_minimum_required(VERSION 3.20)
project(EventOS C)

# ---------------------------------------------------------------------------
# EventOS static library
# ---------------------------------------------------------------------------
# Builds the OS kernel from the mounted EventOS source tree.
# HAL and platform sources are project-specific and provided by the parent.

file(GLOB_RECURSE EVENTOS_SOURCES "${EVENTOS_PATH}/app/source/os/*.c")

add_library(eventos STATIC ${EVENTOS_SOURCES})

target_include_directories(eventos PUBLIC
    ${EVENTOS_PATH}/app/include
)

target_include_directories(eventos PRIVATE
    ${EVENTOS_PATH}/app/include/os
)

target_compile_features(eventos PUBLIC c_std_11)
