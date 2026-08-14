#!/usr/bin/env bash
# Local quality gates — mirror of CI. Run before pushing.
#
#   bash scripts/gates.sh
#
# Gates: ruff format --check, ruff check, mypy, pytest, lint-arwaky-cli scan.

set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> [1/5] ruff format --check"
uv run ruff format --check modules/ tests/

echo "==> [2/5] ruff check"
uv run ruff check modules/ tests/

echo "==> [3/5] mypy"
uv run mypy modules/

echo "==> [4/5] pytest"
uv run python3 -m pytest tests/ -q

echo "==> [5/5] lint-arwaky-cli scan . (must be 0 violations)"
output=$(lint-arwaky-cli scan . 2>&1) || true
echo "$output" | tail -3
violations=$(echo "$output" | grep -oP 'Total:\s*\K\d+') || violations="PARSE_FAILURE"
echo "Violations: ${violations}"
[ "${violations}" = "0" ]

echo ""
echo "✅ All quality gates passed."
