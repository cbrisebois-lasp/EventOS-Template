#!/usr/bin/env bash
#
# Generate MCP helper graph.
# Must be run on the host (requires graphviz for rendered output).
#
# Usage:
#   ./tool_graph.sh              # render SVG (default)
#   ./tool_graph.sh svg          # render SVG
#   ./tool_graph.sh png          # render PNG
#   ./tool_graph.sh pdf          # render PDF
#   ./tool_graph.sh dot          # output raw DOT

set -euo pipefail

if [ -f /.dockerenv ]; then
    echo "Error: this script must be run on the host, not inside the container." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GENERATOR="$SCRIPT_DIR/generate_tool_graph.py"
OUTPUT_DIR="$SCRIPT_DIR/output"

mkdir -p "$OUTPUT_DIR"

usage() {
    echo "Generate MCP helper graph."
    echo ""
    echo "Usage: $(basename "$0") [format]"
    echo ""
    echo "Formats:"
    echo "  svg    Render SVG image (default)"
    echo "  png    Render PNG image"
    echo "  pdf    Render PDF document"
    echo "  dot    Print raw DOT to stdout"
    echo ""
    echo "Rendered output is written to: $OUTPUT_DIR/tool_hierarchy.<format>"
    echo ""
    echo "Requires graphviz for svg/png/pdf output."
}

FORMAT="${1:-svg}"

case "$FORMAT" in
    -h|--help|help)
        usage
        exit 0
        ;;
    dot)
        python3 "$GENERATOR"
        ;;
    svg|png|pdf)
        if ! command -v dot &>/dev/null; then
            echo "Error: graphviz is not installed. Install it with: brew install graphviz" >&2
            exit 1
        fi
        OUTPUT_FILE="$OUTPUT_DIR/tool_hierarchy.$FORMAT"
        python3 "$GENERATOR" -o "$OUTPUT_FILE"
        ;;
    *)
        echo "Unsupported format: $FORMAT" >&2
        echo ""
        usage >&2
        exit 1
        ;;
esac
