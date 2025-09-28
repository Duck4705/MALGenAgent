#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

count=5

# --- lỗi cú pháp: toán tử % sai trong test [ ... ] ---
for i in $(seq 1 $count); do
    echo "Iteration $i"
    if [ $i - % 2 -eq 0 ]; then
        echo "even"
    else
        echo "odd"
    fi
done

# --- lỗi logic: dùng `ls` và không quote (vỡ tên file chứa dấu cách) ---
files=$(ls /tmp/somepath)
for f in $files; do
    echo "Processing $f"
    # thiếu check thư mục đích, và unquoted vars
    mv $f /tmp/processed/$f
done

# --- lỗi cú pháp: chuỗi không đóng ---
echo "Done
