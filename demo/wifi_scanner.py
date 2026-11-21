"""Kiểm kê từ tệp ngoại tuyến. CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP."""
# Xây dựng giao diện chọn JSON hoặc tệp PCAP.
import argparse
# Đọc bảng AP do NetworkManager lưu nếu người học chọn chế độ cục bộ.
import subprocess
# Xuất các lỗi định dạng vào stderr.
import sys
# Đọc đường dẫn độc lập với nền tảng.
from pathlib import Path
# Chia sẻ quy tắc kiểm tra BSSID, trường đo lường và thông báo quyền.
from lab_common import DATA, ap_rows, banner, read_json


# Tạo bảng AP từ tệp PCAP chứa beacon, giữ lần xuất hiện cuối của mỗi BSSID.
def from_pcap(path):
    # Chỉ nạp Scapy khi người học chọn đầu vào nhị phân.
    from scapy.layers.dot11 import Dot11, Dot11Beacon, RadioTap
    # Bắt lỗi tệp rỗng hoặc định dạng không được Scapy hỗ trợ.
    from scapy.error import Scapy_Exception
    # PcapReader chỉ đọc từ đường dẫn cục bộ.
    from scapy.utils import PcapReader
    # Lưu quan sát mới nhất theo thứ tự trong tệp.
    latest = {}
    # Phân biệt lỗi giải mã với lỗi cú pháp tùy chọn.
    try:
        # Tự động đóng tệp khi vòng lặp kết thúc.
        with PcapReader(str(path)) as packets:
            # Đọc tuần tự, chỉ xử lý từng khung đang xét.
            for packet in packets:
                # Bài tập này dùng tệp chỉ gồm các beacon 802.11.
                if not packet.haslayer(Dot11Beacon):
                    # Không đưa gói khác loại vào số liệu kiểm kê.
                    raise ValueError("Tệp minh họa chỉ được chứa beacon 802.11.")
                # Tách các trường quản lý trong beacon.
                stats = packet[Dot11Beacon].network_stats()
                # Địa chỉ thứ ba của beacon là BSSID.
                address = packet[Dot11].addr3
                # Đọc RSSI chỉ khi tiêu đề RadioTap thực sự có cờ đo công suất.
                radio = packet.getlayer(RadioTap)
                # None phân biệt thiếu đo đạc với mức tín hiệu 0 dBm.
                signal = getattr(radio, "dBm_AntSignal", None)
                # Scapy tóm tắt các bộ xác thực được quảng bá qua RSN và WPA.
                suites = sorted(stats.get("crypto", set()))
                # Đồng bộ nhãn với tệp JSON minh họa để so sánh hai nguồn.
                labels = {"WPA2/PSK": "WPA2-PSK", "OPN": "Open", "WEP": "Privacy, chưa rõ bộ mật mã"}
                # Giữ nguyên các tên cơ chế Scapy trả về bên ngoài ví dụ này.
                encryption = ", ".join(labels.get(s, s) for s in suites) or None
                # Kênh dưới đây lấy từ thông tin kênh quảng bá trong beacon khi có.
                latest[address] = dict(bssid=address, ssid=stats.get("ssid"), channel=stats.get("channel"),
                                       encryption=encryption, signal_dbm=signal)
    # Phiên bản Scapy có thể từ chối tệp hỏng bằng lỗi riêng hoặc EOF.
    except (Scapy_Exception, EOFError, IndexError) as exc:
        # Đổi sang lỗi đầu vào để dùng chung đường báo lỗi JSON và PCAP.
        raise ValueError(f"Không đọc được beacon PCAP: {exc}") from exc
    # Dùng cùng cấu trúc với nhánh JSON.
    return {"aps": list(latest.values())}


# In giá trị hoặc nhãn thiếu số liệu.
def display(value):
    # Bảo toàn số không, một giá trị đo hợp lệ.
    return "chưa quan sát" if value is None else str(value)


# Kiểm kê từng BSSID riêng biệt.
def main():
    # Hiện thông báo giới hạn lab và quyền hiệu lực.
    banner()
    # Ghi rõ nguồn dữ liệu được phép chọn.
    parser = argparse.ArgumentParser(description="Đọc JSON hoặc beacon PCAP ngoại tuyến.")
    # Cho chọn một trong hai nguồn độc lập.
    sources = parser.add_mutually_exclusive_group()
    # Đường dẫn JSON có thể bỏ qua để dùng mẫu đi kèm.
    sources.add_argument("json", nargs="?", type=Path, help="Tệp JSON, mặc định data/lab.json")
    # Chế độ Scapy nhận một tệp beacon đã lưu, không cần thiết bị vô tuyến.
    sources.add_argument("--pcap", type=Path, help="Tệp beacon 802.11 ngoại tuyến")
    # Chế độ tùy chọn lấy danh sách đã có trên chính máy, không yêu cầu quét lại.
    sources.add_argument("--cache", action="store_true", help="Đọc bộ nhớ đệm của NetworkManager trên Linux")
    # Phân tích tham số một lần trước khi đọc.
    args = parser.parse_args()
    # Lỗi nguồn và định dạng đều được trả về mã 2.
    try:
        # Giữ nguyên thang đo của NetworkManager khi dùng dữ liệu của hệ điều hành.
        if args.cache:
            # Chỉ định trực tiếp chương trình và đối số, tắt màu và làm mới kết quả.
            command = ["nmcli", "--colors", "no", "-f", "SSID,BSSID,CHAN,SECURITY,SIGNAL", "device", "wifi", "list", "--rescan", "no"]
            # Tách đầu ra và lỗi, giới hạn thời gian đợi NetworkManager.
            result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=True)
            # Ghi rõ nguồn và đơn vị của cột cuối.
            print("Nguồn: bộ nhớ đệm NetworkManager. SIGNAL là phần trăm (0–100).")
            # Hiển thị bảng do NetworkManager tạo, giữ nguyên các trường chưa biết.
            print(result.stdout.rstrip() or "Bộ nhớ đệm chưa có dữ liệu.")
            # Kết thúc phép đọc bảng cục bộ.
            return 0
        # Chọn rõ ràng một trong hai trình đọc.
        data = from_pcap(args.pcap) if args.pcap else read_json(args.json or DATA / "lab.json")
        # Kiểm tra hết các hàng trước khi in kết quả.
        rows = list(ap_rows(data))
        # Nêu cột và đơn vị để có thể ghi lại bằng chứng.
        print("SSID | BSSID | Kênh | Bảo vệ quảng bá | Tín hiệu (dBm)")
        # BSSID vẫn là một hàng độc lập khi nhiều AP quảng bá cùng tên.
        for row in rows:
            # SSID ẩn thường đi kèm trường rỗng, khác với trường không có.
            name = row.get("ssid")
            # Hiển thị tên ở dạng có thoát ký tự điều khiển.
            shown = "chưa quan sát" if name is None else repr(name) if name else "(SSID rỗng)"
            # Chuyển từng phép đo sang nhãn có ý nghĩa khi trường bị thiếu.
            values = [shown, row["bssid"], display(row.get("channel")), display(row.get("encryption")), display(row.get("signal_dbm"))]
            # Tách cột nhất quán cho cả JSON và PCAP.
            print(" | ".join(values))
        # Tóm tắt số BSS được ghi trong nguồn.
        print(f"Số hàng BSS trong mẫu: {len(rows)}")
    # Phân biệt thiếu gói Scapy với lỗi tệp dữ liệu.
    except ImportError as exc:
        # Gợi ý cài đúng môi trường đã ghi trong requirements.txt.
        print(f"Thiếu thư viện đọc PCAP; hãy cài requirements.txt: {exc}", file=sys.stderr)
        # Trả mã lỗi có thể kiểm tra từ shell.
        return 2
    # Bắt các lỗi hệ thống tệp, trường bắt buộc và giá trị không hợp lệ.
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        # Chỉ rõ lỗi đầu vào.
        print(f"Lỗi đầu vào: {exc}", file=sys.stderr)
        # Phân biệt thất bại với kết quả không thấy AP.
        return 2
    # Phân tích xong.
    return 0


# Cho phép chạy trực tiếp bằng python3.
if __name__ == "__main__":
    # Trả mã trạng thái của bài kiểm kê.
    raise SystemExit(main())
