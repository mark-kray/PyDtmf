import wave
import numpy as np
import matplotlib.pyplot as plt
import sys

np.set_printoptions(threshold=sys.maxsize)


def freq_amp(signal, sample_rate):
    n_samples = len(signal)
    np_fft = np.fft.fft(signal)
    amplitudes = 2 / n_samples * np.abs(np_fft)
    frequencies = np.fft.fftfreq(n_samples) * sample_rate
    return frequencies[:len(frequencies) // 2], amplitudes[:len(np_fft) // 2]


def sort_freq_amp(freq, amp):
    p = np.argsort(-amp)
    return freq[p], amp[p]


def main():
    fname = "1.wav"
    wav_file = wave.open(fname, 'r')
    n_samples = wav_file.getnframes()
    sample_rate = wav_file.getframerate()
    audio = wav_file.readframes(n_samples)
    ys = np.frombuffer(audio, dtype=np.int16)
    xs = np.linspace(0, n_samples/sample_rate, n_samples)
    freq, amp = freq_amp(ys, sample_rate)
    plt.subplot(2, 1, 1)
    plt.plot(xs, ys)
    plt.subplot(2, 1, 2)
    # Only half of the frequencies are provided, because the other half are mirrored negative
    plt.plot(freq, amp)
    plt.show()
    freq, amp = sort_freq_amp(freq, amp)
    print(freq[:10])
    print(amp[:10])


if __name__ == '__main__':
    main()
