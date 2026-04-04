"""Handler for the list_tests tool."""

from ..helpers.container import is_container_running
from ..helpers.exec import execute_in_container
from .formatting import format_failure


def handle_list_tests(args):
    running = is_container_running()
    if not running.success:
        return format_failure("list_tests", running)

    result = execute_in_container(
        "cd test && make build > /dev/null 2>&1 && cd build && ctest -N",
        timeout=120,
    )
    if not result.success:
        return format_failure("list_tests", running, result)

    return result.result
