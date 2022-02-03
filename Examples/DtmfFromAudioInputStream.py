import sounddevice as sd
import numpy as np
from Dtmf import detect_dtmf


def main():
    # Run sd.query_devices() and set the correct sound device
    # None = default input device
    device_id = None
    duration = 2000000  # seconds
    sample_rate = 44100
    block_duration = 0.05  # 50ms

    last_detected_code = None
    consecutive_code_counter = 0

    def register_detection(code):
        nonlocal consecutive_code_counter
        nonlocal last_detected_code
        if code is None:
            last_detected_code = code
            consecutive_code_counter = 0
            return
        if code != last_detected_code:
            last_detected_code = code
            consecutive_code_counter = 0
        consecutive_code_counter += 1
        if consecutive_code_counter == 1:
            print(f"Registered dtmf: {code}")

    def callback(indata, frames, time, status):
        indata = np.transpose(indata)[0]
        detected = detect_dtmf(indata, sample_rate)
        register_detection(detected)

    with sd.InputStream(device=device_id, channels=1, callback=callback, samplerate=sample_rate,
                        blocksize=int(sample_rate*block_duration)):
        sd.sleep(int(duration * 1000))


if __name__ == '__main__':
    main()
