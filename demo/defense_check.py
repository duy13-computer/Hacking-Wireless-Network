#!/usr/bin/env python3
"""Đánh giá hồ sơ Wi-Fi ngoại tuyến. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""

import sys

from lab_common import run  # Nạp tệp, kiểm tra quyền, in banner và xử lý lỗi.
from wps_audit import wps_result  # Giữ cùng tiêu chí WPS ở cả hai bài.


def check_policy(data):
    """Đối chiếu siêu dữ liệu hai hồ sơ WPA2 với ngưỡng riêng của bài lab."""
    examples = data["wpa2_examples"]
    if not isinstance(examples, list) or not examples:
        raise ValueError("wpa2_examples phải là danh sách hồ sơ có dữ liệu")
    for number, profile in enumerate(examples, start=1):
        if profile["mode"] != "WPA2-Personal":
            raise ValueError(f"Hồ sơ {number} nằm ngoài phạm vi WPA2-Personal")
        length = profile["passphrase_length"]  # Chỉ dùng độ dài do người quản trị khai báo.
        origin = profile["passphrase_origin"]
        if type(length) is not int or not 8 <= length <= 63:
            raise ValueError(f"Hồ sơ {number} cần độ dài passphrase WPA2 từ 8 đến 63")
        if origin not in ("human", "random", "unknown"):
            raise ValueError("passphrase_origin phải là human, random hoặc unknown")
        if length < 20 or origin == "human":
            result = "KHÔNG ĐẠT"
        elif origin == "unknown":
            result = "CHƯA XÁC ĐỊNH"
        else:
            result = "ĐẠT"
        print(f"Mẫu {number} | {length} ký tự | nguồn {origin} | {result}")
    print("Tiêu chí minh họa: tối thiểu 20 ký tự và nguồn sinh ngẫu nhiên theo hồ sơ.")


def check(data):
    """Đọc các cờ quản trị. Không cần nhập mật khẩu hay kết nối đến AP."""
    for stage in ("before", "after"):
        profile = data["profiles"][stage]
        mode = profile["mode"]
        pmf = profile["pmf"]
        hidden = profile["hidden_ssid"]
        default = profile["default_credentials"]
        if mode not in ("WEP", "WPA-Personal", "WPA2-Personal", "WPA3-Personal", "open", "unknown"):
            raise ValueError("mode nằm ngoài danh mục mạng Personal của bài lab")
        if pmf not in ("off", "optional", "required", "unknown"):
            raise ValueError("Giá trị pmf không hợp lệ")
        if type(hidden) is not bool or (default is not None and type(default) is not bool):
            raise ValueError("hidden_ssid cần boolean, default_credentials cần boolean hoặc null")
        print(f"{stage} | hồ sơ khai báo")
        mode_status = {"WPA3-Personal": "đạt mục tiêu lab", "unknown": "chưa xác định"}
        print(f"  Chế độ {mode} | {mode_status.get(mode, 'chưa đạt mục tiêu WPA3 của lab')}")
        pmf_status = {"required": "bắt buộc", "optional": "tùy chọn", "off": "tắt", "unknown": "chưa rõ"}
        print(f"  PMF | {pmf_status[pmf]}")
        print("  WPS |", wps_result(profile["wps"]))
        print("  SSID |", "ẩn" if hidden else "quảng bá", "| thông tin hiển thị")
        default_status = {True: "KHÔNG ĐẠT, còn mặc định", False: "đã đổi theo hồ sơ", None: "CHƯA XÁC ĐỊNH"}
        print("  Thông tin quản trị mặc định |", default_status[default])
    print("Kết luận chỉ áp dụng cho dữ liệu khai báo trong hai hồ sơ.")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--policy"]:  # Chỉ truyền phần đường dẫn cho bộ đọc dùng chung.
        sys.exit(run(check_policy, argv=sys.argv[2:]))
    sys.exit(run(check))
