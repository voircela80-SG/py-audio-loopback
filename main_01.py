import pyaudiowpatch as pyaudio
import time

def start_audio_loopback(virtual_mic_name="CABLE Input"):
    p = pyaudio.PyAudio()

    try:
        # 1. Tìm driver WASAPI trên Windows
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        
        # 2. Tìm thiết bị Virtual Mic (Ví dụ: VB-Audio Cable Input)
        target_mic_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if virtual_mic_name.lower() in dev["name"].lower() and dev["maxOutputChannels"] > 0:
                target_mic_index = dev["index"]
                break

        if target_mic_index is None:
            print(f"[!] LỖI: Không tìm thấy thiết bị Virtual Mic '{virtual_mic_name}'.")
            print("👉 Hãy kiểm tra xem bạn đã cài VB-Audio Cable chưa.")
            return

        # 3. Tìm thiết bị WASAPI Loopback tương ứng với Speaker mặc định
        loopback_device = None
        for dev in p.get_loopback_device_info_generator():
            if default_speakers["name"] in dev["name"]:
                loopback_device = dev
                break

        if not loopback_device:
            print("[!] LỖI: Không thể kích hoạt WASAPI Loopback trên Loa mặc định.")
            return

        print("==================================================")
        print(f"-> NGUỒN (Speaker Loopback): {loopback_device['name']}")
        print(f"-> ĐÍCH  (Virtual Mic):       {virtual_mic_name}")
        print("==================================================")

        # 4. Mở luồng Output đẩy sang Virtual Mic
        output_stream = p.open(
            format=pyaudio.paInt16,
            channels=loopback_device["maxInputChannels"],
            rate=int(loopback_device["defaultSampleRate"]),
            output=True,
            output_device_index=target_mic_index
        )

        # 5. Callback truyền dữ liệu âm thanh trực tiếp (độ trễ siêu thấp)
        def audio_callback(in_data, frame_count, time_info, status):
            output_stream.write(in_data)
            return (None, pyaudio.paContinue)

        # 6. Mở luồng Capture từ Speaker
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
        print("\n[V] ENGINE ĐANG CHẠY NGẦM... Press Ctrl+C để dừng.\n")

        while input_stream.is_active():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[!] Đã dừng Engine.")
    except Exception as e:
        print(f"\n[!] Có lỗi xảy ra: {e}")
    finally:
        if 'input_stream' in locals():
            input_stream.stop_stream()
            input_stream.close()
        if 'output_stream' in locals():
            output_stream.stop_stream()
            output_stream.close()
        p.terminate()

if __name__ == "__main__":
    # Tên mặc định của VB-Audio Cable là "CABLE Input"
    start_audio_loopback("CABLE Input")