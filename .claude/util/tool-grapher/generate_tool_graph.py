#!/usr/bin/env python3
"""
Parse the MCP server package and generate a DOT graph of helper relationships.

Nodes represent helper functions. Edges represent sequential calls within a
handler — if a handler calls helper A then helper B, an edge A → B is drawn
and labeled with the handler name and call index (e.g. "run_tests [1→2]").

Usage:
    python3 generate_tool_graph.py              # print DOT to stdout
    python3 generate_tool_graph.py -o graph.svg # render SVG (requires graphviz)
    python3 generate_tool_graph.py -o graph.dot # write DOT file
"""

import ast
import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HANDLERS_DIR = os.path.join(SCRIPT_DIR, "..", "..", "mcp", "eventos_template", "handlers")
HELPERS_DIR = os.path.join(SCRIPT_DIR, "..", "..", "mcp", "eventos_template", "helpers")


def discover_helpers():
    """Collect all helper function names from the helpers/ package."""
    helpers = set()
    for filename in os.listdir(HELPERS_DIR):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
        filepath = os.path.join(HELPERS_DIR, filename)
        with open(filepath) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                helpers.add(node.name)
    return helpers


def resolve_imports(tree):
    """Build a map of local names to imported function names.

    Handles 'from ..helpers.foo import bar' and
    'from ..helpers.foo import bar as baz'.
    """
    alias_map = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "helpers" in node.module:
            for alias in node.names:
                local_name = alias.asname if alias.asname else alias.name
                alias_map[local_name] = alias.name
    return alias_map


def find_ordered_calls(func_node, targets):
    """Walk a function body in source order and return helper calls in order."""
    calls = []
    for child in ast.walk(func_node):
        if isinstance(child, ast.Call):
            name = None
            if isinstance(child.func, ast.Name):
                name = child.func.id
            elif isinstance(child.func, ast.Attribute):
                name = child.func.attr
            if name and name in targets:
                calls.append((child.lineno, name))
    calls.sort(key=lambda x: x[0])
    # Deduplicate consecutive same-name calls
    seen = set()
    ordered = []
    for _, name in calls:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def parse_handler_chains(helpers):
    """Parse all handler files and return {handler_name: [helper_name, ...]}."""
    chains = {}
    for filename in os.listdir(HANDLERS_DIR):
        if not filename.endswith(".py") or filename.startswith("__") or filename == "formatting.py":
            continue
        filepath = os.path.join(HANDLERS_DIR, filename)
        with open(filepath) as f:
            tree = ast.parse(f.read())

        # Resolve imports to get local name -> helper name mapping
        alias_map = resolve_imports(tree)
        local_targets = set(alias_map.keys())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("handle_"):
                # Strip "handle_" prefix for the display name
                handler_name = node.name[len("handle_"):]
                ordered_local = find_ordered_calls(node, local_targets)
                # Map local names back to actual helper function names
                ordered_helpers = [alias_map.get(name, name) for name in ordered_local]
                if ordered_helpers:
                    chains[handler_name] = ordered_helpers
    return chains


def generate_dot(chains):
    """Generate DOT source from handler call chains."""
    lines = [
        "digraph helper_graph {",
        '    rankdir=LR;',
        '    node [fontname="Helvetica" fontsize=11];',
        '    edge [fontname="Helvetica" fontsize=9 color="#666666"];',
        "",
        "    // Helper nodes",
        '    node [shape=ellipse style=filled fillcolor="#50C878" fontcolor=white];',
    ]

    # Collect all helpers that appear in any chain
    all_helpers = set()
    for helper_list in chains.values():
        all_helpers.update(helper_list)
    for helper in sorted(all_helpers):
        lines.append(f'    "{helper}";')

    lines.append("")
    lines.append("    // Handler start nodes")
    lines.append('    node [shape=circle style=filled fillcolor="#D94A4A" fontcolor=white];')
    for handler in sorted(chains.keys()):
        start = f"{handler}_start"
        lines.append(f'    "{start}" [label="{handler}"];')

    lines.append("")
    lines.append("    // Handler end nodes")
    lines.append('    node [shape=box style=filled fillcolor="#4A90D9" fontcolor=white];')
    for handler in sorted(chains.keys()):
        end = f"{handler}_end"
        lines.append(f'    "{end}" [label="{handler}"];')

    lines.append("")
    lines.append("    // Handler call chain edges")

    for handler, helper_list in sorted(chains.items()):
        start = f"{handler}_start"
        end = f"{handler}_end"

        # Start node -> first helper
        first = helper_list[0]
        lines.append(f'    "{start}" -> "{first}";')

        # Helper -> helper edges
        for i in range(len(helper_list) - 1):
            src = helper_list[i]
            dst = helper_list[i + 1]
            lines.append(f'    "{src}" -> "{dst}" [label="{handler}"];')

        # Last helper -> end node
        last = helper_list[-1]
        lines.append(f'    "{last}" -> "{end}";')

    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate MCP helper graph")
    parser.add_argument("-o", "--output", help="Output file (.svg, .png, .pdf, or .dot)")
    args = parser.parse_args()

    helpers = discover_helpers()
    chains = parse_handler_chains(helpers)
    dot_source = generate_dot(chains)

    if not args.output:
        print(dot_source)
        return

    if args.output.endswith(".dot"):
        with open(args.output, "w") as f:
            f.write(dot_source)
        print(f"DOT written to {args.output}")
        return

    ext = os.path.splitext(args.output)[1].lstrip(".")
    if ext not in ("svg", "png", "pdf"):
        print(f"Unsupported format: {ext}. Use .svg, .png, .pdf, or .dot", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(
            ["dot", f"-T{ext}", "-o", args.output],
            input=dot_source, text=True, capture_output=True,
        )
        if result.returncode != 0:
            print(f"Graphviz error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"{ext.upper()} written to {args.output}")
    except FileNotFoundError:
        print(
            "Graphviz 'dot' not found. Install graphviz or use -o graph.dot for raw DOT output.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
