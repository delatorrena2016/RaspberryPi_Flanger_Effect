import numpy as np
import pyaudio as pa
import scipy.fftpack as fourier
import scipy.signal as signal
import scipy.io.wavfile as waves

# Parámetros del filtro pasa bajas
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.lfilter(b, a, data)
    return y

def process_audio(cutoff_freq=1000, order=5, frames=1024*8, format=pa.paInt16, channels=1, fs=44100, duration_in_seconds=5):
    p = pa.PyAudio()

    stream = p.open(
        format=format,
        channels=channels,
        rate=fs,
        input=True,
        output=True,
        frames_per_buffer=frames
    )

    F = (fs / frames) * np.arange(0, frames // 2)

    try:
        while True:
            data = stream.read(frames)
            dataInt = np.frombuffer(data, dtype=np.int16)

            # Aplicar el filtro pasa bajas
            filtered_data = butter_lowpass_filter(dataInt, cutoff_freq, fs, order)

            M_gk = abs(fourier.fft(filtered_data) / frames)
            M_gk = M_gk[0:frames // 2]
            Posm = np.where(M_gk == np.max(M_gk))
            F_Found = F[Posm]

            # Aquí puedes agregar cualquier procesamiento adicional que necesites

    except KeyboardInterrupt:
        print("Interrumpido por el usuario")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Llamar a la función
process_audio()
