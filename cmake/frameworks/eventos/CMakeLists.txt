cmake_minimum_required(VERSION 3.20)
project(EventOS C)

# ---------------------------------------------------------------------------
# EventOS static library
# ---------------------------------------------------------------------------
# Builds the OS kernel from the mounted EventOS source tree.
# HAL and platform sources are project-specific and provided by the parent.

# Pick exactly one context allocator. EventOS ships ctxAllocMalloc and
# ctxAllocPool, both defining os_CtxAllocInit / os_CtxFree, so only one
# may be linked. Override with -DEVENTOS_CTX_ALLOC=ctxAllocPool.
set(EVENTOS_CTX_ALLOC "ctxAllocMalloc" CACHE STRING
    "EventOS context allocator (ctxAllocMalloc or ctxAllocPool)")

file(GLOB_RECURSE EVENTOS_SOURCES "${EVENTOS_PATH}/app/source/os/*.c")
file(GLOB EVENTOS_CTX_ALLOC_SOURCES "${EVENTOS_PATH}/app/source/os/mem/ctxAlloc*.c")
list(REMOVE_ITEM EVENTOS_SOURCES ${EVENTOS_CTX_ALLOC_SOURCES})
list(APPEND EVENTOS_SOURCES "${EVENTOS_PATH}/app/source/os/mem/${EVENTOS_CTX_ALLOC}.c")

add_library(eventos STATIC ${EVENTOS_SOURCES})

target_include_directories(eventos PUBLIC
    ${EVENTOS_PATH}/app/include
)

target_include_directories(eventos PRIVATE
    ${EVENTOS_PATH}/app/include/os
)

target_compile_features(eventos PUBLIC c_std_11)
