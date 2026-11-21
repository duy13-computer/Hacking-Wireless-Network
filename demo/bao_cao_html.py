"""Xuất các kết quả Campus-Lab ra một trang HTML độc lập, dùng được ngoại tuyến."""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from html import escape
from pathlib import Path
from string import Template

from lab_common import ap_rows, read_json
from wps_audit import wps_result


def txt(value):
    return escape(str(value), quote=True)


def tag(value, tone="plain"):
    return f'<span class="tag {tone}">{txt(value)}</span>'


def table(headers, rows):
    head = "".join(f'<th scope="col">{txt(cell)}</th>' for cell in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    if not body:
        body = f'<tr><td colspan="{len(headers)}">Chưa có quan sát trong mẫu.</td></tr>'
    return f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def metrics(items):
    return '<dl class="metrics">' + "".join(
        f'<div><dt>{txt(label)}</dt><dd>{txt(value)}</dd></div>' for label, value in items
    ) + '</dl>'


def inventory(data, output):
    aps = list(ap_rows(data))
    channels = {ap["channel"] for ap in aps if ap.get("channel") is not None}
    names = {ap["ssid"] for ap in aps if ap.get("ssid")}
    cards = metrics([("BSSID quan sát", len({ap["bssid"] for ap in aps})),
                     ("Tên mạng xác định", len(names)), ("Kênh quan sát", len(channels))])
    rows = []
    for ap in aps:
        signal = ap.get("signal_dbm")
        strength = "Chưa đo"
        if signal is not None:
            strength = f'<span class="signal"><meter min="-100" max="0" value="{signal}" aria-label="Tín hiệu"></meter><span>{signal} dBm</span></span>'
        mode = ap.get("encryption") or "Chưa rõ"
        ssid = ap.get("ssid")
        name = "Chưa quan sát" if ssid is None else ssid or "SSID rỗng"
        rows.append([f'<strong>{txt(name)}</strong>', f'<code>{txt(ap["bssid"])}</code>',
                     txt(ap.get("channel") or "—"), tag(mode, "amber" if mode.lower()=="open" else "plain"), strength])
    return cards + table(["SSID", "BSSID", "Kênh", "Bảo vệ", "Tín hiệu"], rows)


def membership(data, output):
    rows, statuses = [], []
    lines = iter(output.splitlines())
    for ap in ap_rows(data):
        prefix = f"{ap['bssid']} | {ap.get('ssid')!r} | "
        status = next((line[len(prefix):] for line in lines if line.startswith(prefix)), "Xem nhật ký gốc")
        statuses.append(status)
        candidate = status.startswith("ỨNG VIÊN")
        rows.append([f'<code>{txt(ap["bssid"])}</code>',txt(ap.get("ssid") or "—"),
                     tag("Cần xác minh","amber") if candidate else txt(status),
                     txt(status.removeprefix("ỨNG VIÊN ").strip()) if candidate else "—"])
    return metrics([("Quan sát", len(rows)),("Trong danh mục", statuses.count("Có trong danh mục.")),
                    ("Ứng viên trùng tên", sum(s.startswith("ỨNG VIÊN") for s in statuses))]) + table(
                    ["BSSID", "SSID", "Đối chiếu", "Dấu hiệu"], rows)


def sessions(data, output):
    blocks = []
    for name, labels in data["sessions"].items():
        seen = set()
        cells = []
        for label in labels:
            tone = ' class="repeat"' if label in seen else ""
            cells.append(f'<li{tone}>{txt(label)}</li>')
            seen.add(label)
        seq = "".join(cells)
        prefix = f"{name} | {' → '.join(labels) or '(trống)'}\n"
        # Lấy lời kết luận từ chính chương trình phân tích của phiên này.
        _, found, tail = output.partition(prefix)
        notes = []
        if found:
            for line in tail.splitlines():
                if not line.startswith("  "):
                    break
                notes.append(line.strip())
        summary = " · ".join(notes[:2])
        blocks.append(f'<article class="session"><div class="sessionhead"><h3>Phiên {txt(name)}</h3><span>{txt(summary)}</span></div>'
                      f'<ol class="sequence" aria-label="Thứ tự nhãn">{seq}</ol><p>{txt(" ".join(notes[2:]))}</p></article>')
    return "".join(blocks) + f'<p class="finding">{txt(output.splitlines()[-1])}</p>'


def disconnects(data, output):
    cards = []
    pattern = r"^([0-9a-f:]{17}) \| (.+?) \| (\d+) sự kiện \| giây (\d+)–(\d+)$"
    for address, result, peak, start, end in re.findall(pattern, output, flags=re.M):
        alert = result.startswith("CẢNH BÁO")
        badge = tag("Đạt ngưỡng cảnh báo" if alert else result, "amber" if alert else "plain")
        unique = {(r["id"],r["second"]) for r in data["disconnects"]
                  if r["bssid"].lower()==address and int(start)<=r["second"]<=int(end)}
        times = "".join(f'<li><strong>{s} s</strong><code>{txt(i)}</code></li>' for i,s in sorted(unique,key=lambda p:(p[1],p[0])))
        cards.append(f'<article class="session"><div class="sessionhead"><h3><code>{txt(address)}</code></h3>{badge}</div>'
                     f'<p><strong>{peak} sự kiện riêng biệt</strong> · Giây {start}–{end}</p><ol class="times">{times}</ol></article>')
    content = "".join(cards) or "<p>Không có sự kiện trong mẫu.</p>"
    return content + f'<p class="finding">{txt(output.splitlines()[-1])}</p>'


def wps(data, output):
    panels = []
    for key, label in [("before", "Trước khắc phục"), ("after", "Sau khắc phục")]:
        mode = data["profiles"][key]["wps"]
        result = wps_result(mode)
        short, _, detail = result.partition(" — ")
        tone = {"off": "teal", "pin": "amber", "pbc": "amber"}.get(mode, "plain")
        panels.append(f'<article class="profile"><h3>{label}</h3>{tag(short,tone)}<p>{txt(detail)}</p></article>')
    return '<div class="pair">'+"".join(panels)+'</div>'


def policy(data, output):
    rows = []
    pattern = r"^Mẫu (\d+) \| (\d+) ký tự \| nguồn (human|random|unknown) \| (.+)$"
    origins = {"human": "Người chọn", "random": "Sinh ngẫu nhiên", "unknown": "Chưa rõ"}
    for n, length, origin, result in re.findall(pattern, output, re.M):
        tone = {"ĐẠT": "teal", "KHÔNG ĐẠT": "amber"}.get(result, "plain")
        rows.append([f"Mẫu {n}", f"{length} ký tự", origins[origin], tag(result, tone)])
    return table(["Hồ sơ","Độ dài khai báo","Nguồn sinh","Theo tiêu chí lab"],rows)


def configuration(data, output):
    fields = [
        ("mode","Chế độ Wi-Fi",{}),
        ("pmf","Bảo vệ khung quản lý (PMF)",{"optional":"Tùy chọn","required":"Bắt buộc","off":"Tắt","unknown":"Chưa rõ"}),
        ("wps","Đăng ký WPS",{"pin":"Bật PIN","pbc":"Nút nhấn","off":"Tắt",None:"Chưa rõ","unknown":"Chưa rõ"}),
        ("default_credentials","Thông tin quản trị mặc định",{True:"Còn mặc định",False:"Đã đổi theo hồ sơ",None:"Chưa xác định"}),
        ("hidden_ssid","Hiển thị SSID",{True:"Ẩn",False:"Quảng bá"}),
    ]
    rows=[]
    for key,label,translations in fields:
        old,new=(data["profiles"][k][key] for k in ("before","after"))
        a,b=translations.get(old,old),translations.get(new,new)
        rows.append([txt(label),txt(a),f'<strong>{txt(b)}</strong>',tag("Đã đổi","blue") if old!=new else txt("Giữ nguyên")])
    return table(["Thuộc tính","Trước khắc phục","Sau khắc phục","Thay đổi"],rows)


VIEWS = (
    (inventory,"Kiểm kê Wi-Fi","Đối chiếu BSSID, kênh và mức tín hiệu của các điểm phát quan sát được."),
    (membership,"Danh mục AP","Kiểm tra điểm phát nào dùng cùng tên mạng với AP đã đăng ký."),
    (sessions,"Phiên bắt tay","Đọc thứ tự M1–M4 của từng phiên. Nhãn lặp được đánh dấu trong chuỗi."),
    (disconnects,"Ngắt kết nối","Cửa sổ trượt 60 giây. Ngưỡng cảnh báo của bài là 5 sự kiện riêng biệt trên cùng BSSID."),
    (wps,"Đăng ký WPS","Đối chiếu hai hồ sơ với mục tiêu tắt WPS của bài thực hành."),
    (policy,"Chính sách WPA2","Tiêu chí của bài là ít nhất 20 ký tự, sinh ngẫu nhiên theo hồ sơ khai báo."),
    (configuration,"Cấu hình AP","So sánh hai bản khai cấu hình trên cùng một tập thuộc tính."),
)


def export_report(demo_dir, steps, selected=None):
    """Chạy các bài trên cùng một bản sao đầu vào. Chỉ công bố tệp sau khi xuất thành công."""
    data = read_json(demo_dir / "data" / "lab.json")
    cards, links = [], []
    stamp = datetime.now().astimezone().strftime("%d/%m/%Y · %H:%M %z")
    with tempfile.TemporaryDirectory() as tempdir:
        dataset = Path(tempdir) / "lab.json"
        dataset.write_text(json.dumps(data, ensure_ascii=False), encoding="utf8")
        for n, (heading, command, _) in enumerate(steps, 1):
            if selected is not None and n != selected:
                continue
            result = subprocess.run(
                [sys.executable, "-B", "-X", "utf8", *command, str(dataset)],
                cwd=demo_dir, stdout=subprocess.PIPE, encoding="utf8", check=True,
            )
            render, short, sub = VIEWS[n - 1]
            content = render(data, result.stdout)
            step_id = f"buoc-{n}"
            links.append(f'<a href="#{step_id}"><span class="index">{n:02}</span>{txt(short)}</a>')
            cards.append(f'<section id="{step_id}" aria-labelledby="t{n}" class="step"><header class="stephead">'
                         f'<div class="eyebrow">Bước {n} / {len(steps)}</div><h2 id="t{n}" tabindex="-1">{txt(heading)}</h2>'
                         f'<p>{txt(sub)}</p></header>{content}<details><summary>Xem kết quả terminal</summary>'
                         f'<pre><b>$ python {txt(" ".join(command))}</b>\n{txt(result.stdout.rstrip())}</pre></details></section>')
    template = Template((demo_dir / "mau_ket_qua.html").read_text(encoding="utf8"))
    document = template.substitute(navigation="".join(links), sections="".join(cards), generated=txt(stamp))
    filename = "Ket-qua-Campus-Lab.html" if selected is None else f"Ket-qua-buoc-{selected}.html"
    target = demo_dir / filename
    with tempfile.NamedTemporaryFile(dir=demo_dir, delete=False) as tmp:
        pending = Path(tmp.name)
    try:
        pending.write_text(document, encoding="utf8")
        os.replace(pending, target)
    finally:
        pending.unlink(missing_ok=True)
    return target
