#!/usr/bin/env python3
"""Entry point for the EventOS-Template MCP server."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eventos_template.server import main

main()
