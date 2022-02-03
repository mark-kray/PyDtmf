import sounddevice as sd
import numpy as np
from Dtmf import detect_dtmf
from pynput.keyboard import Controller, KeyCode

# Trigger keyboard controls for the PC version of Hugo 4

# 5 bound to enter
# Rows 123 and 789 swapped, to match position of keys
# Between pc numpad and phone numpad
vk = KeyCode.from_vk
code_to_key = {
    '1': vk(103),   '2': vk(104),   '3': vk(105),
    '4': vk(100),   '5': vk(13),    '6': vk(102),
    '7': vk(97),    '8': vk(98),    '9': vk(99),
    '0': vk(96),    '*': vk(106)
}


def main():
    device_id = 1
    duration = 2000000  # seconds
    sample_rate = 44100
    block_duration = 0.05

    keyboard = Controller()

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
            print(f"Registered {code}")
            return
            key = code
            if code in code_to_key:
                key = code_to_key[code]
            keyboard.press(key)
            sd.sleep(100)
            keyboard.release(key)

    def callback(indata, frames, time, status):
        indata = np.transpose(indata)[0]
        detected = detect_dtmf(indata, sample_rate)
        register_detection(detected)

    with sd.InputStream(channels=1, callback=callback, samplerate=sample_rate,
                        blocksize=int(sample_rate*block_duration)):
        sd.sleep(int(duration * 1000))


if __name__ == '__main__':
    main()
