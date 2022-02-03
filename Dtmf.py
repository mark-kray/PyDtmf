import numpy as np

_dtmf_frequencies = [697, 770, 852, 941, 1209, 1336, 1477, 1633]
_codes = {
    697: {1209: '1', 1336: '2', 1477: '3', 1633: 'A'},
    770: {1209: '4', 1336: '5', 1477: '6', 1633: 'B'},
    852: {1209: '7', 1336: '8', 1477: '9', 1633: 'C'},
    941: {1209: '*', 1336: '0', 1477: '#', 1633: 'D'}
}

# Empirically selected band size. Bands around dtmf frequencies never overlap
_freq_band = 25


# Input: signal in time domain, sample rate of signal
# Output:  list of frequencies and list of corresponding amplitudes
def freq_amp(signal, sample_rate):
    n_samples = len(signal)
    np_fft = np.fft.fft(signal)
    amplitudes = 2 / n_samples * np.abs(np_fft)
    frequencies = np.fft.fftfreq(n_samples) * sample_rate
    # Only half of the frequencies are provided, because the other half are mirrored negative
    return frequencies[:len(frequencies) // 2], amplitudes[:len(np_fft) // 2]


def sort_freq_amp(freq, amp):
    p = np.argsort(-amp)
    return freq[p], amp[p]


# Input: signal in time domain, sample rate of signal
# Output: detected dtmf signal
# Signals are detected if no significant amplitude in any other frequency range is measured
# Detection has been tested on samples of 50ms in duration
def detect_dtmf(samples, sample_rate):
    # Hanning window applied
    hanning_window = np.hanning(len(samples))
    samples = np.multiply(hanning_window, samples)
    freq, amp = freq_amp(samples, sample_rate)
    max_amp = max(amp)
    responses = dict()
    other = 0
    for i in range(len(freq)):
        if amp[i] < max_amp/3:
            continue
        for dtms_freq in _dtmf_frequencies:
            if abs(dtms_freq - freq[i]) <= _freq_band:
                responses[dtms_freq] = responses.get(dtms_freq, 0) + amp[i]
                break
        else:
            other += amp[i]

    if len(responses) == 2 and other == 0:
        detected = sorted(list(responses.keys()))
        f1 = detected[0]
        f2 = detected[1]
        if f1 in _codes.keys() and f2 in _codes[f1].keys():
            code = _codes[detected[0]][detected[1]]
            return code
    return None
