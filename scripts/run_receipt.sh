#!/bin/bash

set -euo pipefail

# dirname can return a relative path, so use pwd to get the absolute
repo_dir="$(cd "$(dirname "$0")/.." && pwd)"

exec "$repo_dir/.venv/bin/python" "$repo_dir/ReceiptPrinter.py"
