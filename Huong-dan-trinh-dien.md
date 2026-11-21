# Trình diễn đánh giá Wi-Fi với Campus-Lab

**Thời lượng 10 phút · CHỈ SỬ DỤNG TRONG MÔI TRƯỜNG LAB ĐƯỢC PHÉP**

Trong buổi trình diễn, người nghe sẽ theo dõi ba BSSID cùng phát tên Campus-Lab, so sánh hai phiên xác lập khóa và đánh giá một thay đổi cấu hình. Các script đọc bộ mẫu cục bộ. Đầu ra là kết quả chạy thật trên dữ liệu giả lập. Riêng hình trích từ iLabs là tư liệu của khóa học. Mở sẵn [báo cáo có tám hình mới](Bao-cao-minh-hoa.docx), [thư mục hình](hinh/) và [nhật ký mẫu](demo/sample-output.txt) để chuyển nhanh giữa sơ đồ, lệnh và bằng chứng.

## Chạy ngay bản trình diễn

Trên máy Windows của bạn, mở PowerShell và dán cả khối sau. Bản trình diễn dùng Python 3 và dữ liệu JSON đi kèm nên có thể chạy ngay khi máy chưa cài Scapy.

```powershell
Set-Location -LiteralPath 'C:\Users\Duy\OneDrive\Desktop\AnNinhMang\Hacking-Wireless-Network\demo'
$env:PYTHONUTF8 = '1'
py -3 chay_demo.py
```

Trên Kali, mở terminal tại thư mục `demo` và chạy `python3 chay_demo.py`. Nhấn **Enter** sau khi trình bày xong mỗi bước. Nhập **q** ở điểm dừng để kết thúc. Để tập riêng phần bắt tay, dùng `py -3 chay_demo.py --buoc 3` trên Windows hoặc `python3 chay_demo.py --buoc 3` trên Kali. Để chạy cả bảy bước liên tục, thêm `--auto`. Mỗi bước in lệnh con, đầu ra thật và một gợi ý thuyết trình. Khi đầu vào được chuyển hướng, chương trình tự chạy liên tục.

**Kết quả để kiểm tra nhanh.** Bước 1 có ba BSSID. Bước 2 đánh dấu BSSID đuôi 03. Bước 3 báo thiếu M3 và lặp M2 ở S2. Bước 4 báo năm sự kiện từ giây 48 đến 66. Bước 7 in hai khối `before` và `after`. Phần bên dưới bổ sung bài đọc PCAP bằng Scapy, bài xem trạng thái giao diện bằng Bash và gợi ý chụp màn hình từng kết quả.

## Chuẩn bị trước giờ trình bày

### Kali Linux

Sao chép trọn thư mục `Hacking-Wireless-Network` vào Kali. Mở terminal ngay tại thư mục gốc đó. Các đường dẫn bên dưới đều tính từ vị trí được chỉ định, nên có thể đặt dự án ở bất kỳ thư mục cá nhân nào. Chạy phần cài đặt một lần trước giờ học, khi đang truy cập được nguồn gói. Các bài mẫu sau đó chạy ngoại tuyến.

```bash
sudo apt update
sudo apt install python3 python3-venv
cd demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python wifi_scanner.py --pcap data/beacons.pcap
```

Nếu thấy ba BSSID ở các kênh 1, 6 và 11, môi trường đã sẵn sàng cho cả bài đọc PCAP. Mở lại terminal vào hôm trình bày thì chuyển tới `demo` và kích hoạt lại môi trường bằng `source .venv/bin/activate`. Các script phân tích chạy được với tài khoản thường. Bài đọc trạng thái mặc định lấy mẫu đã lưu, nên máy ảo có thể dùng mô hình mạng thông thường.

### Chạy nhanh bằng PowerShell trên Windows

Trong chính workspace đã bàn giao, dùng đường dẫn sau. Lệnh đầu chỉ đổi thư mục làm việc. Hai lệnh tiếp tạo môi trường và cài Scapy. Việc gọi trực tiếp Python của môi trường ảo giúp tránh phụ thuộc chính sách thực thi script kích hoạt của PowerShell.

```powershell
Set-Location -LiteralPath 'C:\Users\Duy\OneDrive\Desktop\AnNinhMang\Hacking-Wireless-Network\demo'
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe wifi_scanner.py --pcap data/beacons.pcap
py -3 handshake_review.py
```

Các lệnh `python <tệp>.py` đọc JSON trong phần trình diễn có thể dùng `py -3 <tệp>.py` ngay trong PowerShell. Riêng tùy chọn `--pcap` dùng Python đã cài Scapy như ví dụ trên. Với hai bài shell, trình bày trên Kali để chạy đúng lệnh. Nếu chỉ có PowerShell, chạy `py -3 defense_check.py --policy` để gọi trực tiếp cùng phép chấm WPA2. Có thể xem nội dung nguồn của bài trạng thái bằng `Get-Content -LiteralPath .\data\iw-dev.txt` và mở phần kết quả Bash tương ứng trong nhật ký mẫu. Dòng báo quyền ở Windows và dòng UID ở Linux phản ánh máy đang chạy.

## Kịch bản trình diễn 10 phút

### 00:00–01:00 · Xác định thiết bị và đối tượng được bảo vệ

**Chiếu** [Hình 1.1 – đường đi tới thư viện](hinh/hinh-1-1.png) rồi [Hình 2.2 – các vai trò xác thực](hinh/hinh-2-2.png). Chỉ vào liên kết vô tuyến ở hình đầu và lần theo đường quyết định xác thực trong hình sau.

**Nói** “Mạng có cùng SSID có thể được phát từ nhiều radio. Để xác minh một máy được vào đúng dịch vụ, cần phân biệt định danh BSSID, danh tính dùng khi xác thực và quyền cấp sau kết nối.” Hình 2.2 giải thích mô hình Enterprise. Hồ sơ trước/sau của bài thực hành sử dụng Personal để người nghe dễ thấy thay đổi PMF và WPS.

### 01:00–02:00 · Xác định nguồn của bằng chứng

**Chiếu** [Hình 4.1 – quy trình đánh giá](hinh/hinh-4-1.png), [Hình 5.1 – nguồn dữ liệu](hinh/hinh-5-1.png) và [Hình E.1 – ghi chú iLabs](hinh/hinh-e-1.png).

**Nói** “Nhánh bổ sung bằng chứng trong quy trình cho phép kết luận một trường chưa rõ. Trong video ở phút 02:00, iLabs giải thích vì sao học viên nhận một tệp thu đã có sẵn. Ở đây, ta dùng một bộ Campus-Lab riêng. Sổ tài sản, ba beacon mẫu, nhãn phiên và cấu hình AP trả lời những câu hỏi khác nhau.” Khi người nghe hỏi về nguồn hình, chỉ vào phần trích tiếng Anh và bản dịch trong E.1.

### 02:00–03:30 · Đọc ba beacon và xác định AP ngoài sổ

Trong thư mục `demo`, chạy lần lượt các lệnh sau.

```bash
python wifi_scanner.py
python wifi_scanner.py --pcap data/beacons.pcap
python evil_twin_detector.py
```

**Cho xem** ba hàng ở cả hai lần đọc. Chỉ vào BSSID kết thúc bằng `03`, kênh 11, chế độ Open và tín hiệu mẫu −43 dBm. Hai BSSID kết thúc bằng `01` và `02` dùng WPA2-PSK và có tên trong sổ. **Nói** “Mạng mở dùng cùng tên là ứng viên để đối chiếu lịch lắp thiết bị. Chỉ dữ liệu này chưa xác nhận chủ sở hữu hay hậu quả.” Ảnh chụp nên giữ cả tiêu đề các cột và dòng kết luận ứng viên.

### 03:30–05:20 · So sánh trình tự hai phiên

**Chiếu** [Hình 2.1 – trình tự bốn thông điệp](hinh/hinh-2-1.png) và [Hình C.1 – hai phiên trong bộ mẫu](hinh/hinh-c-1.png). Cho người nghe vài giây đọc cột thứ ba trước khi mở terminal.

```bash
python handshake_review.py
```

**Cho xem** S1 có M1 → M2 → M3 → M4. Ở S2, vị trí ba là M2 lặp. Terminal in `Thiếu: M3` và `Lặp: M2 ×2`. **Nói** “Kết luận hẹp nhất là bộ dữ liệu S2 thiếu quan sát M3. Muốn kết luận về kết quả xác thực, cần dấu vết độc lập từ máy khách hoặc AP.” [Hình E.2 – nhật ký của lệnh phân tích](hinh/hinh-e-2.png) là bản chụp trình bày đầy đủ stdout của một lần chạy trên Windows. Dùng E.2 để đối chiếu hoặc để người ở cuối phòng đọc lại.

### 05:20–06:35 · Đối chiếu cụm ngắt kết nối

```bash
python deauth_detector.py
```

**Cho xem** BSSID kết thúc bằng `01` có năm sự kiện riêng biệt từ giây 48 tới 66. Mở mục `disconnects` trong `data/lab.json` và chỉ hai bản ghi cùng mã `E02`. **Nói** “Cửa sổ trượt 60 giây gom được cả cụm đi qua mốc một phút. Bản sao E02 chỉ đóng góp một lần. Cảnh báo này cần đối chiếu lịch bảo trì, chuyển vùng và trạng thái PMF để xác định nguyên nhân.” Chụp cả khoảng thời gian và mã BSSID để người xem có thể tính lại.

### 06:35–08:25 · Đọc kết quả trước và sau khắc phục

```bash
python wps_audit.py
bash wpa2_policy_check.sh
python defense_check.py
```

**Cho xem** bản trước dùng WPA2-Personal, PMF tùy chọn, WPS PIN bật, trạng thái thông tin quản trị chưa rõ. Bản sau khai báo WPA3-Personal, PMF bắt buộc, WPS tắt và đã đổi thông tin mặc định theo hồ sơ. Ở bài chính sách WPA2 riêng, hồ sơ 12 ký tự do người chọn không đạt, còn hồ sơ 20 ký tự sinh ngẫu nhiên đạt tiêu chí nội bộ của bài.

**Nói** “Đây là phép kiểm trên cấu hình và siêu dữ liệu cấp khóa. Ở đơn vị thật, bước nghiệm thu tiếp theo là xác nhận AP đã áp phiên bản cấu hình và máy khách thương lượng đúng chế độ.” Chụp hai khối `before`, `after` ở cùng một khung hình để thấy rõ trạng thái chưa xác định thay đổi ra sao.

### 08:25–09:10 · Phân biệt giao diện mẫu và máy đang chạy

```bash
bash monitor_status.sh
```

**Cho xem** nguồn dữ liệu là tệp `data/iw-dev.txt` và hai dòng `wlan-lab0 | managed`, `mon-lab0 | monitor`. **Nói** “Đây là bản xuất mẫu nên người học có thể tái hiện trên máy ảo. Nếu cần chứng minh hiện trạng card trên chính máy Kali, phải có một phép đọc cục bộ riêng.” Khi lớp có thiết bị phù hợp và đã cài `iw`, tùy chọn `bash monitor_status.sh --local` chỉ đọc trạng thái giao diện của máy đang dùng. Kết quả phụ thuộc phần cứng.

### 09:10–10:00 · Chốt kết luận và bàn giao

Đặt cạnh nhau hình C.1, hình E.2 và checklist ở Chương 6. Yêu cầu một người nghe nêu một sự kiện quan sát, một suy luận và một phép kiểm còn thiếu. Có thể dùng câu trả lời “ngoài sổ và Open”, “có nguy cơ chọn nhầm AP”, “đối chiếu phiếu lắp đặt và quyết định kết nối ở endpoint”. Kết thúc bằng cách ghi chủ thể xử lý và bằng chứng cần thu. Khi bàn giao, kèm ảnh đầu ra đọc AP, hai phiên, cụm ngắt kết nối, cấu hình trước/sau và [toàn văn kết quả các lệnh](demo/sample-output.txt).

## Tra cứu tám hình theo loại bằng chứng

| Hình | Loại | Vai trò trong buổi trình diễn |
|---|---|---|
| [1.1](hinh/hinh-1-1.png) | Sơ đồ nguyên lý | Phân biệt tuyến dữ liệu với danh tính điểm truy cập |
| [2.1](hinh/hinh-2-1.png) | Sơ đồ giao thức | Trình tự kỳ vọng của một phiên bắt tay |
| [2.2](hinh/hinh-2-2.png) | Sơ đồ kiến trúc | Vai trò supplicant, authenticator và dịch vụ xác thực |
| [4.1](hinh/hinh-4-1.png) | Sơ đồ phương pháp | Điểm ra quyết định khi bằng chứng chưa đủ |
| [5.1](hinh/hinh-5-1.png) | Thiết kế thực nghiệm | Phân biệt đầu vào của các phép so sánh |
| [C.1](hinh/hinh-c-1.png) | Trực quan hóa dữ liệu mẫu | Căn bốn vị trí theo từng phiên, nhận ra M2 lặp |
| [E.1](hinh/hinh-e-1.png) | Ảnh trích video gốc | Bối cảnh dùng tệp thu mẫu của iLabs tại 02:00 |
| [E.2](hinh/hinh-e-2.png) | Stdout từ lần chạy thực tế trên dữ liệu mẫu | Xác minh chương trình báo thiếu M3 và lặp M2 |

