"""Đối chiếu AP trùng tên. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""
# Nhập cùng một bộ kiểm tra địa chỉ và trình chạy với bài kiểm kê.
from lab_common import ap_rows, mac, run


# So khớp danh mục đăng ký với những gì bộ dữ liệu mô tả.
def check(data):
    """Tìm BSSID ngoài danh mục có cùng SSID với một BSSID đã đăng ký."""
    # Danh mục tài sản được cung cấp độc lập với danh sách AP quan sát.
    inventory = data["authorized_bssids"]
    # Một chuỗi đơn lẻ không thể thay thế cho danh sách địa chỉ.
    if not isinstance(inventory, list):
        # Dừng nếu danh mục sai định dạng.
        raise ValueError("authorized_bssids phải là danh sách.")
    # Chuẩn hóa chữ hoa và loại địa chỉ đăng ký lặp.
    allowed = {mac(value) for value in inventory}
    # Giữ các hàng để đối chiếu hai lượt bằng cùng một ảnh chụp dữ liệu.
    rows = list(ap_rows(data))
    # Lưu chế độ bảo vệ đã quan sát tại các AP đăng ký cho từng SSID.
    reference = {}
    # Chỉ AP có trong danh mục được dùng làm mẫu so sánh.
    for row in rows:
        # SSID trống hoặc mất trường không đại diện một tên đã xác định.
        if row["bssid"] in allowed and row.get("ssid"):
            # Giữ cả trường hợp không đo được bảo vệ để tránh suy đoán.
            reference.setdefault(row["ssid"], set()).add(row.get("encryption"))
    # Duyệt cả mẫu hợp lệ và ứng viên ngoài danh mục.
    for row in rows:
        # Làm rõ sự khác biệt giữa tên đã quan sát và dữ liệu rỗng.
        name = row.get("ssid")
        # Địa chỉ có trong sổ là một bằng chứng kiểm kê.
        if row["bssid"] in allowed:
            # Gắn nhãn vừa đủ cho kết luận có thể rút ra.
            status = "Có trong danh mục."
        # Không có mẫu cùng tên hoặc SSID đang trống.
        elif not name or name not in reference:
            # Giữ trường hợp ngoài sổ để người học phân loại.
            status = "Ngoài danh mục; thiếu đối chứng cùng SSID."
        # Một tên mạng đã xuất hiện trên thiết bị đăng ký.
        else:
            # Phát hiện ứng viên cần xác minh và giữ giới hạn bằng chứng.
            status = "ỨNG VIÊN trùng SSID, BSSID ngoài danh mục."
            # Trường bảo vệ cần có ở cả hai bên để so sánh.
            modes = reference[name] - {None, ""}
            # So sánh đúng nhãn của cùng một nguồn dữ liệu.
            if modes and row.get("encryption") and row["encryption"] not in modes:
                # Nêu chênh lệch cụ thể có thể kiểm tra lại.
                status += f" Chế độ {row['encryption']!r} khác {sorted(modes)!r}."
        # Dùng biểu diễn an toàn cho tên có ký tự điều khiển.
        print(f"{row['bssid']} | {name!r} | {status}")
    # Nếu ảnh chụp trống thì không thể hình thành đối chứng.
    if not rows:
        # Báo giới hạn quan sát thay cho kết luận toàn mạng.
        print("Không có AP trong mẫu.")


# Chỉ chạy phân tích khi người dùng gọi chính tệp này.
if __name__ == "__main__":
    # Trả mã kết thúc của bộ xử lý đầu vào.
    raise SystemExit(run(check))
