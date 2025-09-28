#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

count=5

for i in $(seq 1 "$count"); do
    echo "Iteration $i"
    # dùng arithmetic expression
    if (( i % 2 == 0 )); then
        echo "even"
    else
        echo "odd"
    fi
done

# safer: iterate files safely
mkdir -p /tmp/processed
# use glob or while-read to handle spaces/newlines
shopt -s nullglob
for f in /tmp/somepath/*; do
    [ -e "$f" ] || continue
    echo "Processing: $f"
    mv -- "$f" "/tmp/processed/$(basename "$f")"
done

echo "Done"
