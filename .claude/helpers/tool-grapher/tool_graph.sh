#!/usr/bin/env bash
#
# Generate MCP tool hierarchy graph.
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
MCP_SERVER="$SCRIPT_DIR/../../mcp/eventos-template.py"
OUTPUT_DIR="$SCRIPT_DIR/output"

mkdir -p "$OUTPUT_DIR"

FORMAT="${1:-svg}"
OUTPUT_FILE="$OUTPUT_DIR/tool_hierarchy.$FORMAT"

case "$FORMAT" in
    dot)
        python3 "$GENERATOR" -s "$MCP_SERVER"
        ;;
    svg|png|pdf)
        if ! command -v dot &>/dev/null; then
            echo "Error: graphviz is not installed. Install it with: brew install graphviz" >&2
            exit 1
        fi
        python3 "$GENERATOR" -s "$MCP_SERVER" -o "$OUTPUT_FILE"
        ;;
    *)
        echo "Unsupported format: $FORMAT" >&2
        echo "Usage: $(basename "$0") [svg|png|pdf|dot]" >&2
        exit 1
        ;;
esac
