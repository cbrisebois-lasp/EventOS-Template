"""Handler for the run_tests tool."""

from ..helpers.container import is_container_running
from ..helpers.exec import execute_in_container
from .formatting import format_failure


def handle_run_tests(args):
    running = is_container_running()
    if not running.success:
        return format_failure("run_tests", running)

    result = execute_in_container("make test", timeout=300)
    if not result.success:
        return format_failure("run_tests", running, result)

    return result.result
