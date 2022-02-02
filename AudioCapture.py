import numpy
import sounddevice as sd
import numpy as np
from FreqAnalysis import freq_amp, sort_freq_amp
from pynput.keyboard import Key, Controller, KeyCode

# Dtms detection currently implemented with FFT, not ideal
# Try improving using this:
# https://www.chegg.com/homework-help/questions-and-answers/python-build-dtmf-decoder-code-accept-tonal-sequence-output-string-key-presses-rules-1-use-q24451553
# 2. Use a set of bandpass filters, not a FFT.
# 3. For full credit, use FIR filters of length 31 or less or second order (two pole) IIR filters. You get partial credit for working implementations that use larger filters.

vk = KeyCode.from_vk

dtms_frequencies = [697, 770, 852, 941, 1209, 1336, 1477, 1633]
codes = {
    697: {1209: '1', 1336: '2', 1477: '3', 1633: 'A'},
    770: {1209: '4', 1336: '5', 1477: '6', 1633: 'B'},
    852: {1209: '7', 1336: '8', 1477: '9', 1633: 'C'},
    941: {1209: '*', 1336: '0', 1477: '#', 1633: 'D'}
}

# 123 and 789 swapped, due to match position of keys
# Between pc numpad and phone numpad
code_to_key = {
    '7': vk(97),
    '8': vk(98),
    '9': vk(99),
    '4': vk(100),
    '5': vk(13),  # Enter
    '6': vk(102),
    '1': vk(103),
    '2': vk(104),
    '3': vk(105),
    '0': vk(96),
    '*': vk(106)
}


def main():
    device_id = 1
    duration = 2000000  # seconds
    sample_rate = 44100
    block_duration = 0.05

    signal_duration_requirement = 0.05
    band = 25

    keyboard = Controller()

    consecutive_block_requirement = signal_duration_requirement // block_duration
    print(consecutive_block_requirement)
    last_detected_code = ''
    consecutive_code_counter = 0

    def register_detection(code):
        nonlocal consecutive_code_counter
        nonlocal last_detected_code
        if code == '':
            last_detected_code = code
            consecutive_code_counter = 0
            return
        if code != last_detected_code:
            consecutive_code_counter = 0
            last_detected_code = code
        consecutive_code_counter += 1
        if consecutive_code_counter == consecutive_block_requirement:
            print(f"Registered {code}")
            key = code
            if code in code_to_key:
                key = code_to_key[code]
            keyboard.press(key)
            sd.sleep(100)
            keyboard.release(key)

    def callback(indata, frames, time, status):
        hamming_window = numpy.hamming(frames)
        indata = np.transpose(indata)[0]*100
        indata = np.multiply(hamming_window, indata)
        freq, amp = freq_amp(indata, sample_rate)
        freq, amp = sort_freq_amp(freq, amp)

        #print([(freq[i], amp[i]) for i in range(50)])

        if amp[0] > 1:
            responses = dict()
            response_count = dict()
            other = 0
            other_count = 0
            for i in range(len(freq)):
                if amp[i] < amp[0]/3:
                    break
                for dtms_freq in dtms_frequencies:
                    if abs(dtms_freq - freq[i]) <= band:
                        responses[dtms_freq] = responses.get(dtms_freq, 0) + amp[i]
                        response_count[dtms_freq] = response_count.get(dtms_freq, 0) + 1
                        break
                else:
                    other = other + amp[i]
                    other_count = other_count + 1

            for freq in responses.keys():
                responses[freq] /= response_count[freq]
            if other_count > 0:
                other /= other_count

            if len(responses) == 2 and other == 0: # and -1 not in responses:
                detected = sorted(list(responses.keys()))
                f1 = detected[0]
                f2 = detected[1]
                if responses[f1] > other and responses[f2] > other:
                    if f1 in codes.keys() and f2 in codes[f1].keys():
                        # print(sorted([(f, responses[f]) for f in responses], reverse=True, key=lambda x: x[1]))
                        # print(f"other: {other}")
                        code = codes[detected[0]][detected[1]]
                        register_detection(code)
                        return
        register_detection('')

    with sd.InputStream(channels=1, callback=callback, samplerate=sample_rate, blocksize=int(sample_rate*block_duration)):
        sd.sleep(int(duration * 1000))


if __name__ == '__main__':
    main()