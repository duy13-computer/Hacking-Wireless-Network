"""Tiện ích cho bài lab ngoại tuyến. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""
# Khai báo giao diện dòng lệnh.
import argparse
# Đọc bộ dữ liệu có cấu trúc JSON.
import json
# Lấy định danh người dùng hiệu lực trên POSIX.
import os
# Kiểm tra định dạng địa chỉ vô tuyến.
import re
# Gửi thông báo lỗi ra luồng chuẩn dành cho lỗi.
import sys
# Xử lý đường dẫn độc lập với thư mục đang đứng.
from pathlib import Path

# Dữ liệu đi kèm nằm cạnh các script.
DATA = Path(__file__).resolve().parent / "data"
# Chuỗi thống nhất xuất hiện trước kết quả của mọi bài.
DISCLAIMER = "CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP"


# Xác nhận chế độ ngoại tuyến và thông báo quyền tiến trình.
def banner():
    # In giới hạn phạm vi bài thực hành.
    print(DISCLAIMER)
    # Windows không sử dụng mô hình root/euid của POSIX.
    if not hasattr(os, "geteuid"):
        # Diễn đạt rõ trường hợp phép kiểm tra không áp dụng.
        print("Quyền root POSIX: không áp dụng trên hệ điều hành này.")
    # Máy Linux có thể cung cấp định danh người dùng hiệu lực.
    else:
        # Phân biệt quyền hiện tại trong khi vẫn chạy được bằng tài khoản thường.
        print("Quyền hiện tại:", "root" if os.geteuid() == 0 else "người dùng thường")


# Đọc một đối tượng JSON từ đĩa với hỗ trợ UTF-8 BOM.
def read_json(path):
    # Đọc toàn bộ tài liệu mẫu dưới dạng văn bản.
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    # Thuật toán cần truy cập các trường bằng tên.
    if not isinstance(data, dict):
        # Đưa lỗi định dạng về một thông báo nhất quán.
        raise ValueError("Gốc JSON phải là một đối tượng.")
    # Trả dữ liệu cho bài kiểm tra chuyên biệt.
    return data


# Chuẩn hóa BSSID dùng làm khóa tra cứu.
def mac(value):
    # Mỗi BSSID gồm sáu octet hệ mười sáu phân tách bằng dấu hai chấm.
    if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", value):
        # Từ chối địa chỉ thiếu hoặc sai định dạng.
        raise ValueError("Cần BSSID dạng 02:00:00:00:00:01.")
    # Hai cách viết hoa hoặc thường cùng dùng một định danh.
    return value.lower()


# Đọc và kiểm tra tập các hàng AP dùng cho bài kiểm kê và nhận diện AP trùng tên.
def ap_rows(data):
    # Truy cập danh sách quan sát.
    rows = data["aps"]
    # Mảng trống hợp lệ, còn dữ liệu vô hướng không đại diện một bảng.
    if not isinstance(rows, list):
        # Báo lỗi thay vì hiểu nhầm tập hợp các ký tự thành các hàng.
        raise ValueError("aps phải là một danh sách.")
    # Chuẩn hóa địa chỉ và bảo toàn trường chưa đo dưới dạng None.
    for row in rows:
        # Mỗi hàng phải là một đối tượng có tên trường.
        if not isinstance(row, dict):
            # Cho biết chính xác mảng có phần tử sai kiểu.
            raise ValueError("Mỗi hàng aps phải là một đối tượng.")
        # Sao chép để tránh thay đổi đầu vào của người học.
        item = dict(row, bssid=mac(row.get("bssid")))
        # SSID rỗng, SSID chưa thu được và chuỗi bảo vệ có ý nghĩa khác nhau.
        for key in ("ssid", "encryption"):
            # Chấp nhận chuỗi hoặc dữ liệu khuyết.
            if item.get(key) is not None and not isinstance(item[key], str):
                # Gắn tên trường vào lỗi để dễ sửa dữ liệu thí nghiệm.
                raise ValueError(f"{key} phải là chuỗi hoặc null.")
        # Số kênh và công suất thu trong mẫu là số nguyên, hoặc chưa quan sát.
        for key, lo, hi in (("channel", 1, 255), ("signal_dbm", -128, 127)):
            # Lấy số đo nếu có.
            number = item.get(key)
            # Loại giá trị Boolean vì JSON phân biệt chúng với số.
            if number is not None and (type(number) is not int or not lo <= number <= hi):
                # Cho biết dải số mô hình có thể biểu diễn.
                raise ValueError(f"{key} phải là số nguyên từ {lo} đến {hi}, hoặc null.")
        # Trả từng hàng để tái sử dụng bởi hai bài.
        yield item


# Quản lý đường dẫn tùy chọn và thống nhất mã thoát cho các bài đọc JSON.
def run(check, default="lab.json", argv=None):
    # Hiển thị thông tin sử dụng trước khi xử lý dữ liệu.
    banner()
    # Dùng mô tả của hàm kiểm tra cho phần trợ giúp.
    parser = argparse.ArgumentParser(description=check.__doc__)
    # Tệp do người học cung cấp tính từ thư mục làm việc; tệp mặc định nằm trong data.
    parser.add_argument("json", nargs="?", type=Path, default=DATA / default)
    # Cho phép gọi từ shell hoặc từ bài dùng tùy chọn bổ sung.
    args = parser.parse_args(argv)
    # Gom lỗi tệp và lỗi dữ liệu thành mã lỗi dễ kiểm thử.
    try:
        # Tách đọc tệp chung với xử lý chuyên môn của từng bài.
        check(read_json(args.json))
    # JSON sai, trường thiếu, sai kiểu và lỗi truy cập đều có thông báo rõ.
    except (OSError, ValueError, TypeError, KeyError) as exc:
        # Xuất thông báo tới stderr để có thể lưu kết quả riêng.
        print(f"Lỗi đầu vào: {exc}", file=sys.stderr)
        # Mã 2 dành cho đầu vào hoặc tham số sai.
        return 2
    # Mã 0 cho biết phép phân tích đã chạy xong, kể cả khi có cảnh báo.
    return 0
