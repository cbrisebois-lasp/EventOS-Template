"""Handler for the container_remove tool."""

from ..helpers.container import remove_container
from .formatting import format_failure


def handle_container_remove(args):
    result = remove_container()
    if not result.success:
        return format_failure("container_remove", result)
    return result.result
