import numpy as np
import wave
import matplotlib.pyplot as plt
from Dtmf import freq_amp, sort_freq_amp, detect_dtmf

# Show time and freq domain representation of the given signal
# Print the most significant frequencies by amplitude
# Print the detected DTMF signal


def main():
    fname = "../PhoneAudio/1.wav"
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
    plt.plot(freq, amp)
    plt.show()

    freq, amp = sort_freq_amp(freq, amp)
    print("10 most significant frequencies:")
    print(f"Freq: {freq[:10]}")
    print(f"Amp: {amp[:10]}")
    print()
    print(f"Detected dtmf tone: {detect_dtmf(ys, sample_rate)}")


if __name__ == '__main__':
    main()
