"""Execution helpers."""

from ..lib.paths import COMPOSE_CMD, CONTAINER_SERVICE, CONTAINER_USER, CONTAINER_WORKDIR
from ..lib.result import HelperResult
from ..lib.subprocess import run_subprocess


def execute_in_container(cmd, workdir=CONTAINER_WORKDIR, timeout=120):
    """Execute a command inside the container."""
    r = HelperResult(success=False)
    r.add_step("exec", cmd)
    full_cmd = COMPOSE_CMD + [
        "exec", "-T", "-u", CONTAINER_USER,
        "-w", workdir,
        CONTAINER_SERVICE, "sh", "-c", cmd,
    ]
    output, rc = run_subprocess(full_cmd, timeout=timeout)
    r.success = rc == 0
    r.result = output
    r.add_step("result", f"exit code {rc}")
    return r
