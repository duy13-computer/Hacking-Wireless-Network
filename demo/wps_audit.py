#!/usr/bin/env python3
"""Đọc trạng thái WPS khai báo. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""

import sys

from lab_common import run  # Bộ đọc tệp ngoại tuyến và banner chung.

WPS_RESULTS = {
    "pin": "KHÔNG ĐẠT — hồ sơ cho phép đăng ký bằng PIN ngoài.",
    "pbc": "KHÔNG ĐẠT mục tiêu tắt WPS — đang bật phương thức nút nhấn.",
    "off": "ĐẠT — hồ sơ khai báo đã tắt WPS.",
    "unknown": "CHƯA XÁC ĐỊNH — cần bản xuất chỉ rõ phương thức đăng ký.",
}


def wps_result(value):
    """Ánh xạ giá trị khai báo sang kết luận của riêng tiêu chí WPS."""
    if value is None:
        value = "unknown"  # JSON null biểu thị dữ liệu chưa rõ.
    if not isinstance(value, str) or value not in WPS_RESULTS:
        raise ValueError("wps phải là pin, pbc, off, unknown hoặc null")
    return WPS_RESULTS[value]


def check(data):
    """So sánh bản xuất cấu hình ở hai thời điểm được đặt tên sẵn."""
    for stage in ("before", "after"):
        profile = data["profiles"][stage]
        print(f"{stage} | WPS | {wps_result(profile['wps'])}")
    print("Kiểm chứng ngoài mô hình cần đối chiếu cấu hình đang chạy tại AP.")


if __name__ == "__main__":
    sys.exit(run(check))  # Thông tin quyền và lỗi đầu vào do bộ đọc chung xử lý.
