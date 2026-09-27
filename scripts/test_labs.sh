#!/usr/bin/env bash
# Run each lab's tests in its own pytest process.
# Labs are self-contained and share module names (every lab has an llm.py), so running
# them in one process would let the first-imported module shadow the others.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -z "${PYTEST:-}" ]; then
  if [ -x .venv/bin/pytest ]; then PYTEST=.venv/bin/pytest; else PYTEST=pytest; fi
fi
status=0
for lab in labs/engineering/*/; do
  echo "== ${lab}"
  "$PYTEST" "$lab" -q -p no:cacheprovider || status=1
done
exit $status
