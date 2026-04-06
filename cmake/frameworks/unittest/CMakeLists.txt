cmake_minimum_required(VERSION 3.20)
project(UnitTest C)

# ---------------------------------------------------------------------------
# UnitTest interface library (header-only)
# ---------------------------------------------------------------------------
# Exposes the UnitTest framework headers from the mounted source tree.

add_library(unittest INTERFACE)

target_include_directories(unittest INTERFACE
    ${UNITTEST_PATH}/framework
)

# ---------------------------------------------------------------------------
# Test auto-discovery function
# ---------------------------------------------------------------------------
# Makes unittest_add_tests() available to the parent project.

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/UnitTestDiscovery.cmake)
