import threading
import time
import sys
import pyaudiowpatch as pyaudio
from PIL import Image, ImageDraw
import pystray

# --- GLOBAL VARIABLES ---
engine_running = False
stop_event = threading.Event()
engine_thread = None
icon = None

def loopback_worker(virtual_mic_name="CABLE Input"):
    """ Luồng xử lý âm thanh ngầm (Engine) """
    global engine_running
    p = pyaudio.PyAudio()

    try:
        # 1. Tìm driver WASAPI
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        
        # 2. Tìm Virtual Mic Target
        target_mic_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if virtual_mic_name.lower() in dev["name"].lower() and dev["maxOutputChannels"] > 0:
                target_mic_index = dev["index"]
                break

        if target_mic_index is None:
            print(f"[!] Lỗi: Không tìm thấy '{virtual_mic_name}'")
            engine_running = False
            return

        # 3. Tìm Loopback Device
        loopback_device = None
        for dev in p.get_loopback_device_info_generator():
            if default_speakers["name"] in dev["name"]:
                loopback_device = dev
                break

        if not loopback_device:
            engine_running = False
            return

        # 4. Mở Stream Render sang Virtual Mic
        output_stream = p.open(
            format=pyaudio.paInt16,
            channels=loopback_device["maxInputChannels"],
            rate=int(loopback_device["defaultSampleRate"]),
            output=True,
            output_device_index=target_mic_index
        )

        def audio_callback(in_data, frame_count, time_info, status):
            if stop_event.is_set():
                return (None, pyaudio.paComplete)
            output_stream.write(in_data)
            return (None, pyaudio.paContinue)

        # 5. Mở Stream Capture từ Loa
        input_stream = p.open(
            format=pyaudio.paInt16,
            channels=loopback_device["maxInputChannels"],
            rate=int(loopback_device["defaultSampleRate"]),
            input=True,
            input_device_index=loopback_device["index"],
            stream_callback=audio_callback
        )

        input_stream.start_stream()
        output_stream.start_stream()
        engine_running = True
        update_tray_icon()

        # Giữ luồng chạy cho đến khi nhận tín hiệu stop
        while not stop_event.is_set():
            time.sleep(0.2)

    except Exception as e:
        print(f"[!] Lỗi Engine: {e}")
    finally:
        engine_running = False
        update_tray_icon()
        if 'input_stream' in locals():
            input_stream.stop_stream()
            input_stream.close()
        if 'output_stream' in locals():
            output_stream.stop_stream()
            output_stream.close()
        p.terminate()

def start_engine():
    global engine_thread, stop_event
    if not engine_running:
        stop_event.clear()
        engine_thread = threading.Thread(target=loopback_worker, daemon=True)
        engine_thread.start()

def stop_engine():
    global stop_event
    stop_event.set()

# --- DẢI TẠO ICON ĐỘNG (Xanh = Chạy, Đỏ = Dừng) ---
def create_icon_image(color):
    """ Tạo 1 ảnh Icon tròn màu đè lên nền trong suốt """
    image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    d.ellipse((8, 8, 56, 56), fill=color)
    return image

def update_tray_icon():
    """ Cập nhật màu Icon và chữ gợi ý (Tooltip) theo trạng thái """
    if icon:
        if engine_running:
            icon.icon = create_icon_image('green')
            icon.title = "Audio Loopback: ĐANG CHẠY"
        else:
            icon.icon = create_icon_image('red')
            icon.title = "Audio Loopback: ĐÃ DỪNG"

# --- TRAY ACTION HANDLERS ---
def on_toggle_clicked(icon_obj, item):
    if engine_running:
        stop_engine()
    else:
        start_engine()

def on_exit_clicked(icon_obj, item):
    stop_engine()
    icon_obj.stop()
    sys.exit()

# --- MAIN SYSTEM TRAY PROGRAM ---
def main():
    global icon
    
    # Tạo menu chuột phải
    menu = pystray.Menu(
        pystray.MenuItem("Bật / Tắt Loopback", on_toggle_clicked),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Thoát", on_exit_clicked)
    )

    # Khởi tạo Icon ở trạng thái Dừng (Màu đỏ)
    icon = pystray.Icon(
        "AudioLoopback",
        icon=create_icon_image('red'),
        title="Audio Loopback Engine",
        menu=menu
    )

    # Tự động bật Engine ngay khi khởi chạy
    start_engine()

    # Vòng lặp chính chạy System Tray
    icon.run()

if __name__ == "__main__":
    main()