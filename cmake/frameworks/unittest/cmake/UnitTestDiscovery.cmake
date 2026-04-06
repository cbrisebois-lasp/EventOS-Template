# UnitTestDiscovery.cmake
#
# Provides unittest_add_tests() — a reusable CMake function that auto-discovers
# test files and creates one executable per source/test pair.

# unittest_add_tests()
#
# Required arguments:
#   APP_SOURCE_DIR  — absolute path to the application source root
#   TEST_SOURCE_DIR — absolute path to the test source root
#
# Optional arguments:
#   IGNORE_FILES    — list of relative paths (from APP_SOURCE_DIR) to skip
#   MODULE_FILTER   — if set, only process sources whose module path contains this string
#   EXTRA_SOURCES   — list of additional source files to link into every test executable
#   VERBOSE         — if ON, print status messages for each test added
#
function(unittest_add_tests)
    # Parse arguments
    set(options VERBOSE)
    set(oneValueArgs APP_SOURCE_DIR TEST_SOURCE_DIR MODULE_FILTER)
    set(multiValueArgs IGNORE_FILES EXTRA_SOURCES)
    cmake_parse_arguments(UT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    # Validate required arguments
    if(NOT DEFINED UT_APP_SOURCE_DIR)
        message(FATAL_ERROR "unittest_add_tests: APP_SOURCE_DIR is required")
    endif()
    if(NOT DEFINED UT_TEST_SOURCE_DIR)
        message(FATAL_ERROR "unittest_add_tests: TEST_SOURCE_DIR is required")
    endif()

    # Discover all app source files
    file(GLOB_RECURSE _app_sources "${UT_APP_SOURCE_DIR}/*.c")

    set(_skipped_files "")

    foreach(_app_file ${_app_sources})
        get_filename_component(_src_filename ${_app_file} NAME)
        get_filename_component(_src_dir ${_app_file} PATH)

        # Get relative module path from source root
        file(RELATIVE_PATH _module_path "${UT_APP_SOURCE_DIR}" "${_src_dir}")

        # Apply module filter if set
        if(DEFINED UT_MODULE_FILTER AND NOT "${UT_MODULE_FILTER}" STREQUAL "")
            string(FIND "${_module_path}" "${UT_MODULE_FILTER}" _module_match)
            if(_module_match EQUAL -1)
                continue()
            endif()
        endif()

        # Construct expected test file path
        set(_test_file "${UT_TEST_SOURCE_DIR}/${_module_path}/test_${_src_filename}")

        if(EXISTS ${_test_file})
            # Build a safe target name
            if("${_module_path}" STREQUAL "")
                set(_module_id "top")
            else()
                string(REPLACE "/" "_" _module_id ${_module_path})
                string(REPLACE "-" "_" _module_id ${_module_id})
            endif()

            string(REPLACE "." "_" _src_id ${_src_filename})
            string(REPLACE "-" "_" _src_id ${_src_id})

            set(_target_name "${_module_id}_${_src_id}_exe")

            # Create executable: app source + test source + any extra sources
            add_executable(${_target_name}
                ${_app_file}
                ${_test_file}
                ${UT_EXTRA_SOURCES}
            )

            # Register with CTest
            add_test(NAME ${_target_name}
                     COMMAND "${CMAKE_BINARY_DIR}/${_target_name}")

            if(UT_VERBOSE)
                message(STATUS "Adding test: ${_target_name}")
            endif()
        else()
            # Check if this file is in the ignore list
            file(RELATIVE_PATH _rel_path "${UT_APP_SOURCE_DIR}" "${_app_file}")
            list(FIND UT_IGNORE_FILES "${_rel_path}" _ignore_index)
            if(_ignore_index EQUAL -1)
                message(WARNING "Test file not found: ${_test_file}")
            else()
                list(APPEND _skipped_files "${_rel_path}")
            endif()
        endif()
    endforeach()

    # Report skipped files
    if(_skipped_files)
        list(LENGTH _skipped_files _skipped_count)
        set(_skip_msg "========================================\n")
        string(APPEND _skip_msg " ${_skipped_count} source file(s) have NO test coverage:\n")
        foreach(_skipped ${_skipped_files})
            string(APPEND _skip_msg "   - ${_skipped}\n")
        endforeach()
        string(APPEND _skip_msg "========================================")
        message(WARNING "${_skip_msg}")
    endif()
endfunction()
