#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 calculation.inp [calculation.out]" >&2
  exit 2
fi
: "${ORCA_EXE:?Set ORCA_EXE to the full path of the ORCA executable}"
input="$1"
output="${2:-${input%.inp}.out}"
cd "$(dirname "$input")"
"$ORCA_EXE" "$(basename "$input")" > "$(basename "$output")"
grep -q "ORCA TERMINATED NORMALLY" "$(basename "$output")"
echo "Completed: $output"
