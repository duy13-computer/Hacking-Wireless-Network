"""Đếm cụm ngắt kết nối. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""
# Tái sử dụng hàm kiểm tra BSSID và giao diện cho file JSON.
from lab_common import mac, run


# Phân tích sự kiện trong từng BSS bằng cửa sổ trượt nửa mở 60 giây.
def check(data):
    """Tìm cửa sổ 60 giây có ít nhất năm sự kiện ngắt kết nối phân biệt."""
    # Lấy bảng sự kiện, vốn có thể đến sai thứ tự.
    rows = data["disconnects"]
    # Từ chối cấu trúc không phải mảng.
    if not isinstance(rows, list):
        # Cho biết chính xác trường cần sửa.
        raise ValueError("disconnects phải là danh sách.")
    # Với mỗi BSSID, lập ánh xạ từ mã sự kiện đến mốc giây tương đối.
    devices = {}
    # Duyệt từng sự kiện trước khi tính thống kê.
    for row in rows:
        # Một bản ghi phải có dạng đối tượng.
        if not isinstance(row, dict):
            # Tránh hiểu nhầm một chuỗi thành bản ghi.
            raise ValueError("Mỗi sự kiện phải là đối tượng.")
        # Kiểm tra địa chỉ ghi nhận trong sự kiện.
        address = mac(row.get("bssid"))
        # Mỗi sự kiện có mã riêng và số giây tính từ đầu bài.
        event_id, second = row.get("id"), row.get("second")
        # Mốc giây là số nguyên không âm, mã sự kiện là chuỗi có nội dung.
        if not isinstance(event_id, str) or not event_id.strip() or type(second) is not int or second < 0:
            # Báo trường thiếu thay vì suy diễn thời gian hoặc danh tính.
            raise ValueError("Sự kiện cần id có nội dung và second là số nguyên không âm.")
        # Gộp các sự kiện của đúng BSSID.
        registry = devices.setdefault(address, {})
        # Bản sao cùng mã và thời điểm chỉ được đếm một lần.
        if event_id in registry and registry[event_id] != second:
            # Cùng mã nhưng khác thời điểm là lỗi chất lượng dữ liệu.
            raise ValueError(f"{address}: mốc thời gian xung đột cho {event_id!r}.")
        # Ghi một sự kiện duy nhất theo mã.
        registry[event_id] = second
    # Miêu tả riêng trường hợp chưa quan sát sự kiện.
    if not devices:
        # Một tập dữ liệu trống không chứng minh mạng đã an toàn.
        print("Không có sự kiện trong mẫu.")
    # Tính cửa sổ đông nhất cho từng BSSID.
    for address, registry in sorted(devices.items()):
        # Sắp tăng dần để đầu cửa sổ chỉ phải đi về phía trước.
        times = sorted(registry.values())
        # Lưu chỉ số đầu, số lượng lớn nhất và khoảng thực tế.
        left, peak, start, end = 0, 0, 0, 0
        # Di chuyển đầu phải đến mỗi thời điểm mới.
        for right, second in enumerate(times):
            # Hai sự kiện cách nhau đúng 60 giây thuộc hai cửa sổ nửa mở.
            while second - times[left] >= 60:
                # Loại các sự kiện đã quá cũ.
                left += 1
            # Đếm cả hai đầu của dãy chỉ số.
            size = right - left + 1
            # Giữ lại cửa sổ có nhiều sự kiện nhất, ưu tiên lần đầu khi bằng nhau.
            if size > peak:
                # Lưu đầy đủ khoảng thời gian của kết quả.
                peak, start, end = size, times[left], second
        # Ngưỡng năm là tham số dạy học đã nêu ở chương 5.
        label = "CẢNH BÁO cụm ngắt kết nối" if peak >= 5 else "Dưới ngưỡng"
        # Báo số sự kiện riêng biệt, BSSID và mốc để tái tính.
        print(f"{address} | {label} | {peak} sự kiện | giây {start}–{end}")
    # Nhắc đúng giới hạn diễn giải của nhật ký.
    print("Đối chiếu lịch bảo trì, chuyển vùng và PMF để xác minh nguyên nhân.")


# Cung cấp điểm vào cho dòng lệnh.
if __name__ == "__main__":
    # Dùng mã thoát nhất quán cho dữ liệu sai.
    raise SystemExit(run(check))
