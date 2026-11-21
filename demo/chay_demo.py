"""Trình diễn Campus-Lab. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""

import argparse
import subprocess
import sys
from pathlib import Path

from lab_common import banner


# Mỗi mục gồm tiêu đề, đối số chạy một script và một gợi ý để thảo luận kết quả.
STEPS = (
    ("Kiểm kê Wi-Fi", ("wifi_scanner.py",),
     "Chỉ ra ba BSSID ở kênh 1, 6, 11. Cùng một SSID có thể do nhiều radio phát."),
    ("Đối chiếu AP với sổ tài sản", ("evil_twin_detector.py",),
     "BSSID đuôi 03 phát mạng mở và nằm ngoài sổ. Muốn xác định chủ sở hữu, cần kiểm tra phiếu triển khai."),
    ("Đọc hai phiên bắt tay", ("handshake_review.py",),
     "Mở Hình C.1. S1 đủ bốn nhãn. S2 cũng có bốn dòng nhưng lặp M2 và thiếu quan sát M3."),
    ("Tìm cụm ngắt kết nối", ("deauth_detector.py",),
     "Ở BSSID đuôi 01 có năm sự kiện riêng từ giây 48 đến 66. Đối chiếu bảo trì trước khi kết luận nguyên nhân."),
    ("Kiểm tra đăng ký bằng WPS", ("wps_audit.py",),
     "So sánh before và after. Hồ sơ đầu cho phép đăng ký bằng PIN, hồ sơ sau tắt WPS."),
    ("Chấm chính sách WPA2", ("defense_check.py", "--policy"),
     "So sánh nguồn sinh và độ dài khai báo. Hồ sơ ngẫu nhiên 20 ký tự đạt tiêu chí riêng của bài."),
    ("Đối chiếu cấu hình sau khắc phục", ("defense_check.py",),
     "Nêu ba thay đổi dễ thấy trong hồ sơ sau: WPA3-Personal, PMF bắt buộc và WPS tắt. Triển khai thật cần được nghiệm thu tại AP."),
)


def main():
    parser = argparse.ArgumentParser(description="Trình diễn từng bước với dữ liệu Campus-Lab có sẵn.")
    parser.add_argument("--auto", action="store_true", help="Chạy liên tục, bỏ qua khoảng dừng giữa các bước.")
    parser.add_argument("--buoc", type=int, choices=range(1, len(STEPS) + 1), metavar="1–7",
                        help="Chỉ trình bày bước được chọn, từ 1 đến 7.")
    args = parser.parse_args()
    demo_dir = Path(__file__).resolve().parent
    banner()
    print("Campus-Lab | Dữ liệu mẫu trong thư mục data/", flush=True)
    for number, (title, command, note) in enumerate(STEPS, start=1):
        if args.buoc is not None and number != args.buoc:
            continue
        print(f"\n[{number}/{len(STEPS)}] {title}", flush=True)
        print("$ python " + " ".join(command), flush=True)
        # Dùng chính Python hiện tại và mẫu đi kèm, độc lập với vị trí mở terminal.
        subprocess.run([sys.executable, "-B", "-X", "utf8", *command], cwd=demo_dir, check=True)
        print(f"\nGợi ý thuyết trình — {note}", flush=True)
        if not args.auto and args.buoc is None and number < len(STEPS) and sys.stdin.isatty():
            if input("Enter để tiếp tục, q để dừng: ").strip().lower() == "q":
                print("Đã dừng theo lựa chọn.")
                return 0
    print("\nĐã hoàn tất phần trình diễn đã chọn.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nĐã dừng trình diễn.", file=sys.stderr)
        sys.exit(130)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Không chạy được bước hiện tại: {exc}", file=sys.stderr)
        sys.exit(2)
