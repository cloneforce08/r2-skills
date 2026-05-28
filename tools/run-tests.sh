#!/usr/bin/env bash
# -----------------------------------------------------------------------------
set -euo pipefail
__FILE="${BASH_SOURCE[0]}"
__FILENAME=$(basename "$__FILE")
__DIR=$(cd "$(dirname "$__FILE")" >/dev/null 2>&1 && pwd)
# -----------------------------------------------------------------------------

python3 -m unittest discover -v -s "${__DIR}/../skills/r2-rda/scripts/tests/"
