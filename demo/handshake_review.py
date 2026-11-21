#!/usr/bin/env python3
"""Đọc nhãn M1…M4 trong dữ liệu tổng hợp. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""

from collections import Counter
import sys

from lab_common import run  # Bộ đọc JSON, banner, thông tin quyền và xử lý lỗi chung.

EXPECTED = ("M1", "M2", "M3", "M4")  # Thứ tự các nhãn của một phiên trong mô hình.


def check(data):
    """Mỗi khóa trong sessions là một phiên, mỗi danh sách giữ thứ tự quan sát."""
    sessions = data["sessions"]
    if not isinstance(sessions, dict) or not sessions:
        raise ValueError("sessions phải là đối tượng JSON có ít nhất một mã phiên")
    for session_id, labels in sessions.items():
        if not session_id.strip() or not isinstance(labels, list):
            raise ValueError("Mỗi mã phiên phải có tên và danh sách nhãn sự kiện")
        if any(label not in EXPECTED for label in labels):
            raise ValueError(f"{session_id} chứa nhãn ngoài M1, M2, M3, M4")
        counts = Counter(labels)  # Đếm trong từng phiên để hai máy không bị gộp.
        missing = [label for label in EXPECTED if counts[label] == 0]
        repeats = [f"{label} ×{counts[label]}" for label in EXPECTED if counts[label] > 1]
        positions = [EXPECTED.index(label) for label in labels]  # Mã hóa thứ tự nhãn.
        backwards = any(a > b for a, b in zip(positions, positions[1:]))
        print(f"{session_id} | {' → '.join(labels) or '(trống)'}")
        print("  Thiếu:", ", ".join(missing) or "không")
        print("  Lặp:", ", ".join(repeats) or "không")
        if backwards:
            print("  Thứ tự quan sát có nhãn quay ngược. Cần xác minh cách gán phiên.")
        elif missing:
            print("  Chưa quan sát đủ bốn nhãn.")
        else:
            print("  Đủ bốn nhãn theo thứ tự quan sát.")
    print("Bản ghi mô tả nhãn sự kiện. Xác thực thành công cần nguồn xác nhận độc lập.")


if __name__ == "__main__":
    sys.exit(run(check))  # Trả mã xử lý đầu vào cho shell.
