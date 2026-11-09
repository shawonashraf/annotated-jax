#!/usr/bin/env bash
# Build the site into website/_build.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --locked --only-group site python website/generate.py . website/_src
uv run --locked --only-group site sphinx-build -q -c website website/_src website/_build
