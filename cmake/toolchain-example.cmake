# Example CMake toolchain file for cross-compilation.
#
# Copy this file, fill in the values for your target, and pass it to CMake:
#   cmake -DCMAKE_TOOLCHAIN_FILE=cmake/my-toolchain.cmake ..
#
# For more information see:
#   https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html

set(CMAKE_SYSTEM_NAME Generic)    # Bare-metal (no OS)
set(CMAKE_SYSTEM_PROCESSOR riscv) # Replace with your target arch

# Toolchain prefix and path
set(TOOLCHAIN_PREFIX "riscv32-unknown-elf")

# If TOOLCHAIN_PATH is set in the environment, use it; otherwise assume PATH
if(DEFINED ENV{TOOLCHAIN_PATH})
    set(TOOLCHAIN_DIR "$ENV{TOOLCHAIN_PATH}/bin/")
else()
    set(TOOLCHAIN_DIR "")
endif()

set(CMAKE_C_COMPILER   "${TOOLCHAIN_DIR}${TOOLCHAIN_PREFIX}-gcc")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_DIR}${TOOLCHAIN_PREFIX}-gcc")

# Compiler flags — customize for your target
set(CMAKE_C_FLAGS_INIT "-std=gnu11 --specs=nano.specs")
