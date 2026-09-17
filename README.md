# Py Audio Loopback (System Tray App)

Ứng dụng chạy ngầm trên khay hệ thống (System Tray) bằng Python, hỗ trợ bắt âm thanh hệ thống (System Audio Output / WASAPI Loopback) và chuyển tiếp trực tiếp vào Microphone ảo (VB-Audio Virtual Cable). 

Ứng dụng giúp truyền tải âm thanh máy tính sang các nền tảng nhận diện giọng nói hoặc công cụ AI (Google Dịch, Gemini, Copilot, Zoom, MS Teams...) một cách dễ dàng.

---

## 🌟 Tính năng chính

* **Chạy ngầm tiện lợi:** Tích hợp icon trên khay hệ thống (System Tray) với trạng thái bật/tắt trực quan.
* **Bắt âm thanh vòng lặp (Loopback):** Thu lại toàn bộ âm thanh đang phát trên Windows (loa/tai nghe).
* **Đầu ra mic ảo:** Truyền trực tiếp dữ liệu âm thanh tới **CABLE Input (VB-Audio Virtual Cable)**.
* **Tự động khôi phục:** Tự động kết nối lại thiết bị âm thanh khi có thay đổi.

---

## 🛠 Yêu cầu hệ thống

1. **Hệ điều hành:** Windows 10 / 11.
2. **Phần mềm bắt buộc:** [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) (Cài đặt để có thiết bị mic ảo `CABLE Input` / `CABLE Output`).
3. **Python:** Phiên bản 3.10 trở lên (nếu chạy từ mã nguồn).

---

## 🚀 Hướng dẫn cài đặt & Chạy từ nguồn

1. **Cloning Repository:**
   ```bash
   git clone [https://github.com/voircela80-SG/py-audio-loopback.git](https://github.com/voircela80-SG/py-audio-loopback.git)
   cd py-audio-loopback
