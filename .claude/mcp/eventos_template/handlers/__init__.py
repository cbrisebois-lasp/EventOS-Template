"""Handler registry. Maps tool names to handler functions."""

from .build_app import handle_build_app
from .build_clean import handle_build_clean
from .container_build import handle_container_build
from .container_remove import handle_container_remove
from .container_start import handle_container_start
from .container_stop import handle_container_stop
from .list_tests import handle_list_tests
from .run_coverage import handle_run_coverage
from .run_tests import handle_run_tests

HANDLERS = {
    "container_start": handle_container_start,
    "container_stop": handle_container_stop,
    "container_build": handle_container_build,
    "container_remove": handle_container_remove,
    "build_app": handle_build_app,
    "build_clean": handle_build_clean,
    "run_tests": handle_run_tests,
    "list_tests": handle_list_tests,
    "run_coverage": handle_run_coverage,
}
