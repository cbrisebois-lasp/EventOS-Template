cmake_minimum_required(VERSION 3.20)
project(EventOSPosixPort C)

# ---------------------------------------------------------------------------
# EventOS POSIX platform port
# ---------------------------------------------------------------------------
# Provides hal_CriticalBegin/End and weak defaults for os_Fail,
# os_ActionBegin, os_ActionEnd. Used for host builds; replace with a
# target-specific HAL when cross-compiling for embedded hardware.

file(GLOB EVENTOS_POSIX_SOURCES "${EVENTOS_PATH}/examples/posix/source/*.c")

# OBJECT (not STATIC) so the port's .o files get inlined into the executable's
# link line. The kernel calls back into hal_CriticalBegin/End and the weak
# os_Fail/os_ActionBegin/End hooks live here, so a STATIC port plus a STATIC
# kernel produces a circular dependency that GNU ld cannot resolve in one pass.
add_library(eventos-posix OBJECT ${EVENTOS_POSIX_SOURCES})

target_include_directories(eventos-posix PUBLIC
    ${EVENTOS_PATH}/examples/posix/include
)

target_link_libraries(eventos-posix PUBLIC eventos)
