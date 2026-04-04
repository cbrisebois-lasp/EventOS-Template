"""Handler for the run_coverage tool."""

from ..helpers.container import is_container_running
from ..helpers.exec import execute_in_container
from .formatting import format_failure


def handle_run_coverage(args):
    running = is_container_running()
    if not running.success:
        return format_failure("run_coverage", running)

    result = execute_in_container("cd test && make coverage", timeout=300)
    if not result.success:
        return format_failure("run_coverage", running, result)

    return f"{result.result}\n\nReport: test/build/coverage_report/index.html"
