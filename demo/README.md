# Thực hành phân tích Wi-Fi với dữ liệu Campus-Lab

**CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP**

**Xem kết quả trong trình duyệt.** Mở [bản trình chiếu Campus-Lab](Ket-qua-Campus-Lab.html). Dùng phím **← →** để chuyển bước, **Xem kết quả terminal** để đối chiếu nhật ký, hoặc **In báo cáo** để lưu PDF. Trang mở trực tiếp từ ổ đĩa và dùng được ngoại tuyến.

Để cập nhật báo cáo sau khi sửa dữ liệu mẫu, chạy `py -3 chay_demo.py --html` trên Windows hoặc `python3 chay_demo.py --html` trên Kali tại thư mục này. Thêm `--buoc 3` để lưu riêng kết quả bắt tay vào `Ket-qua-buoc-3.html`.

Để trình diễn ngay bảy bước bằng dữ liệu có sẵn, mở terminal tại thư mục này và chạy `py -3 chay_demo.py` trên Windows hoặc `python3 chay_demo.py` trên Kali. Nhấn Enter để chuyển bước. Thêm `--buoc 3` để tập riêng phần bắt tay hoặc `--auto` để chạy liên tục. [Kịch bản thuyết trình và tám hình minh họa](../Huong-dan-trinh-dien.md)

Tại sao cùng một tên mạng lại xuất hiện với nhiều BSSID? Có thể kết luận gì khi chỉ thấy ba trong bốn nhãn thông điệp của một phiên xác lập khóa? Bài thực hành dùng các tệp mẫu Campus-Lab để trả lời hai câu hỏi này và so sánh cấu hình trước, sau khắc phục. Chương 5 của báo cáo trình bày cách diễn giải kết quả. Tài liệu mã nguồn cung cấp bản mã và giải thích theo dòng. [Báo cáo](../Bao-cao.md) · [Mã nguồn có chú giải](../Code-demo.md)

## 1. Chuẩn bị trên Kali Linux

Mở terminal ở thư mục `Hacking-Wireless-Network`. Cài Python và gói tạo môi trường ảo bằng tài khoản có quyền cài gói hệ thống. Việc cài đặt cần nguồn gói khả dụng. Sau khi chuẩn bị, các bài đọc dữ liệu mẫu chạy ngoại tuyến.

```bash
sudo apt update
sudo apt install python3 python3-venv
cd demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Nếu muốn xem trạng thái giao diện Wi-Fi thật của chính máy Kali ở bước 7, có thể cài thêm tiện ích `iw`. Máy ảo chỉ cần quyền đọc tệp để làm các bài dùng dữ liệu mẫu.

```bash
sudo apt install iw
```

Dùng tài khoản thông thường cho các lệnh thực hành bên dưới. Đặc quyền dùng để cài gói ở trên tách biệt với quyền đọc dữ liệu. Bộ script hiển thị banner sử dụng và không cần người học cung cấp mật khẩu Wi-Fi, PIN WPS, tài khoản hay dữ liệu của người khác.

## 2. Kiểm kê các AP quan sát được

```bash
python wifi_scanner.py
```

Ghi SSID, BSSID, kênh, chế độ bảo vệ và tín hiệu của từng hàng. Có hai BSSID đã được phê duyệt cho Campus-Lab và một BSSID ngoài sổ cùng phát tên này. Số dòng quan sát không nhất thiết bằng số AP vật lý. SSID dùng để nhận diện dịch vụ, còn BSSID giúp tách các điểm phát được quan sát.

Để so sánh hai cách biểu diễn cùng ba AP, chạy thêm lệnh sau. Scapy đọc trực tiếp tệp PCAP gồm ba beacon tổng hợp. Kênh và tín hiệu (dBm) của từng BSSID phải trùng với đầu vào JSON.

```bash
python wifi_scanner.py --pcap data/beacons.pcap
```

Trên máy Linux có NetworkManager, `python wifi_scanner.py --cache` đọc danh sách AP mà hệ điều hành đã lưu. Tùy chọn `--rescan no` giữ nguyên bộ nhớ đệm nên kết quả có thể cũ hoặc trống. Cột SIGNAL của nguồn này dùng phần trăm, khác đơn vị dBm của mẫu. Tiện ích `nmcli` nằm trong gói `network-manager`. [Tài liệu chính thức của NetworkManager](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html)

## 3. Kiểm tra dấu hiệu AP trùng tên

```bash
python evil_twin_detector.py
```

Tìm hàng có SSID Campus-Lab, BSSID ngoài sổ và chế độ Open. Đây là một ứng viên cần điều tra. Để phân biệt AP bị cấu hình nhầm với hành vi giả mạo, đối chiếu đơn vị quản lý và phiếu thay thiết bị. Dữ liệu hiện có chưa chứng minh một máy khách đã chọn kết nối tới AP ấy.

## 4. Dựng lại trình tự bắt tay

```bash
python handshake_review.py
```

S1 có M1, M2, M3, M4 theo thứ tự. S2 có M1, M2, M2, M4. Ghi “thiếu quan sát M3, có M2 lặp” cho S2. Bốn nhãn hợp lệ trong S1 cho biết chuỗi quan sát đủ theo mô hình. Chúng không cung cấp phép kiểm tra mật mã đối với khóa hoặc bằng chứng về dữ liệu ứng dụng.

## 5. Phân tích cụm ngắt kết nối

```bash
python deauth_detector.py
```

Đọc số sự kiện đã khử trùng trong cửa sổ trượt 60 giây của từng BSSID. Ngưỡng mẫu là năm sự kiện. Đối chiếu số sự kiện với số dòng log khi cùng sự kiện xuất hiện hai lần. Một cụm vượt ngưỡng có thể đi cùng bảo trì, mất nguồn hoặc một hiện tượng cần điều tra sâu hơn. Ghi riêng thời điểm, phạm vi và bằng chứng còn thiếu.

## 6. Kiểm tra WPS, chính sách WPA2 và cấu hình AP

```bash
python wps_audit.py
bash wpa2_policy_check.sh
python defense_check.py
```

| Phép kiểm | Kết quả cần nhận ra | Cách diễn giải |
|---|---|---|
| Đăng ký WPS | Hồ sơ trước bật PIN, hồ sơ sau tắt WPS | Trạng thái đường đăng ký được công bố trong cấu hình |
| Chính sách WPA2 | Hồ sơ khóa 12 ký tự do người chọn yếu hơn tiêu chí khóa ngẫu nhiên từ 20 ký tự của bài | Căn cứ là nguồn sinh và độ dài khai báo |
| Mã hóa và PMF | WPA2-Personal, PMF tùy chọn chuyển sang WPA3-Personal, PMF bắt buộc | Bằng chứng về chính sách khai báo của AP mẫu |
| Truy cập quản trị | Trạng thái đổi thông tin mặc định từ chưa rõ sang đã xác nhận | Mức tin cậy còn phụ thuộc việc duy trì sổ quản trị |

Khi trả lời, dẫn ra trường dữ liệu liên quan và ghi rõ tiêu chí là của bài lab. Chuyển một trường từ chưa rõ sang đạt đòi hỏi bằng chứng mới. Không suy ra tốc độ dò khóa hoặc entropy thực tế chỉ từ độ dài khai báo.

## 7. Đọc hai giao diện mẫu và so sánh với máy học viên

```bash
bash monitor_status.sh
```

Lệnh mặc định đọc bản xuất trong `data/iw-dev.txt`. Kết quả có `wlan-lab0 | managed` và `mon-lab0 | monitor`. Khi cần xem chính máy Kali, dùng `bash monitor_status.sh --local` sau khi cài `iw`. Tùy chọn này chỉ đọc trạng thái hiện tại. Máy ảo có thể không thấy card Wi-Fi của máy chủ, hãy ghi kết quả ấy riêng với hai giao diện giả lập.

## 8. Nộp phiếu thực hành

Ghi một hàng cho mỗi phép kiểm. Cột bằng chứng nêu tên tệp hoặc định danh phiên, thuộc tính và giá trị đủ để nhóm khác kiểm tra lại. Cột kết luận mô tả điều dữ liệu xác nhận. Cột tiếp theo dành cho việc còn phải xác minh.

| Câu hỏi | Bằng chứng từ bộ mẫu | Kết luận | Điều cần xác minh thêm |
|---|---|---|---|
| Có dấu hiệu trùng tên mạng nào? | | | |
| S1 và S2 khác nhau tại đâu? | | | |
| Ngưỡng ngắt kết nối kích hoạt khi nào? | | | |
| Cấu hình trước và sau khác gì? | | | |

Nếu lệnh Python thiếu mô-đun, kiểm tra đã kích hoạt `.venv` trong cửa sổ terminal hiện tại và cài đúng tệp `requirements.txt`. Khi một đầu vào bị lỗi, giữ bản gốc để chạy lại phép kiểm và ghi tên tệp, lỗi đã thấy vào phiếu. Sau khi hoàn thành, thoát môi trường ảo bằng `deactivate`.

Để đối chiếu các lệnh mẫu, xem [nhật ký đã chạy](sample-output.txt). Mã thoát 0 nghĩa là script đã đọc và đánh giá được đầu vào, kể cả khi một chính sách không đạt. Mã 2 cho biết lỗi tham số, phụ thuộc hoặc dữ liệu. Hai chế độ đọc trạng thái máy thật cần được xác minh trên máy Kali của người học.

