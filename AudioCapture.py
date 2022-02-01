import numpy
import sounddevice as sd
import numpy as np
from FreqAnalysis import freq_amp, sort_freq_amp

# Dtms detection currently implemented with FFT, not ideal
# Try improving using this:
# https://www.chegg.com/homework-help/questions-and-answers/python-build-dtmf-decoder-code-accept-tonal-sequence-output-string-key-presses-rules-1-use-q24451553
# 2. Use a set of bandpass filters, not a FFT.
# 3. For full credit, use FIR filters of length 31 or less or second order (two pole) IIR filters. You get partial credit for working implementations that use larger filters.

dtms_frequencies = [697, 770, 852, 941, 1209, 1336, 1477, 1633]
codes = {
    697: {1209: '1', 1336: '2', 1477: '3', 1633: 'A'},
    770: {1209: '4', 1336: '5', 1477: '6', 1633: 'B'},
    852: {1209: '7', 1336: '8', 1477: '9', 1633: 'C'},
    941: {1209: '*', 1336: '0', 1477: '#', 1633: 'D'}
}

band = 25

for i in range(len(dtms_frequencies)-1):
    print(dtms_frequencies[i+1] - dtms_frequencies[i])


def main():
    device_id = 1
    duration = 20000  # seconds
    sample_rate = 44100
    block_duration = 0.05
    signal_duration_requirement = 0.1
    # devices = sd.query_devices()[device_id]

    consecutive_block_requirement = signal_duration_requirement // block_duration
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

    def callback(indata, frames, time, status):
        hamming_window = numpy.hamming(frames)
        indata = np.transpose(indata)[0]*100
        indata = np.multiply(hamming_window, indata)
        #print(indata)
        freq, amp = freq_amp(indata, sample_rate)
        freq, amp = sort_freq_amp(freq, amp)

        if amp[0] > 1:
            responses = dict()
            avg_amp = sum(amp)/len(amp)
            for i in range(len(freq)):
                if amp[i] < amp[0]/2:
                    break
                for dtms_freq in dtms_frequencies:
                    if abs(dtms_freq - freq[i]) <= band:
                        responses[dtms_freq] = responses.get(dtms_freq, 0) + amp[i]
                        break
                else:
                    responses[-1] = responses.get(-1, 0) + amp[i]

            if len(responses) == 2 and -1 not in responses:
                detected = sorted(list(responses.keys()))
                code = codes[detected[0]][detected[1]]
                register_detection(code)
                return
            #print(responses)
            #print(f"Freq: {freq[:10]}")
            #print(f"Amp: {amp[:10]}")
        register_detection('')

    with sd.InputStream(channels=1, callback=callback, samplerate=sample_rate, blocksize=int(sample_rate*block_duration)):
        sd.sleep(int(duration * 1000))


if __name__ == '__main__':
    main()

