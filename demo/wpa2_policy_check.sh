#!/usr/bin/env bash
# CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP
# Điểm vào shell cho bài kiểm tra độ dài và nguồn sinh đã khai báo.
set -eu
# Xác định thư mục đi kèm script cả khi người dùng đứng ở thư mục khác.
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
# Chuyển nguyên đối số tới Python; lab_common in banner, trạng thái quyền và mã lỗi.
exec python3 "$script_dir/defense_check.py" --policy "$@"
