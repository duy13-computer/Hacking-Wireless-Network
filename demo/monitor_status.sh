#!/usr/bin/env bash
# Đọc trạng thái giao diện hiện có từ bản mẫu hoặc truy vấn cục bộ.
set -eu
printf '%s\n' 'CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP'
printf 'UID hiện tại %s. Bài đọc trạng thái không yêu cầu root.\n' "$(id -u)"
# Mặc định đọc fixture đặt cạnh script.
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
if (( $# > 1 )); then
    printf 'Cách dùng: bash monitor_status.sh [--local | đường_dẫn_tệp]\n' >&2
    exit 2
fi
case "${1:-}" in
    --local)
        # iw dev chỉ liệt kê cấu hình giao diện có sẵn trên máy Kali.
        if ! command -v iw >/dev/null; then
            printf 'Thiếu iw. Cài gói iw hoặc dùng dữ liệu ngoại tuyến.\n' >&2
            exit 2
        fi
        snapshot=$(iw dev) || { printf 'Truy vấn iw dev thất bại.\n' >&2; exit 2; }
        printf 'Nguồn: trạng thái giao diện cục bộ.\n'
        ;;
    -h|--help)
        printf 'Cách dùng: bash monitor_status.sh [--local | đường_dẫn_tệp]\n'
        exit 0
        ;;
    *)
        input_file=${1:-"$script_dir/data/iw-dev.txt"}
        # Đọc một tệp văn bản đã xuất. Bash giữ thông tin lỗi nếu đường dẫn không hợp lệ.
        [[ -f "$input_file" && -r "$input_file" ]] || { printf 'Không đọc được tệp.\n' >&2; exit 2; }
        snapshot=$(cat -- "$input_file") || exit 2
        printf 'Nguồn: tệp ngoại tuyến %s\n' "$input_file"
        ;;
esac
# Mỗi dòng Interface mở một bản ghi; dòng type thuộc về giao diện ngay trước nó.
printf '%s\n' "$snapshot" | awk '
    $1 == "Interface" { iface = $2; next }
    $1 == "type" && iface != "" { print iface, "|", $2; found++; iface = "" }
    END { if (!found) print "Chưa quan sát được cặp Interface/type có tên." }
'
