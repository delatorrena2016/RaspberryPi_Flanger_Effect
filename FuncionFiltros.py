import matplotlib
import numpy as np
import pyaudio as pa
import matplotlib.pyplot as plt
import scipy.fftpack as fourier
import scipy.signal as signal
matplotlib.use('tkAgg')

def audio_processing(filter_type='lowpass', low_cutoff_freq=400, high_cutoff_freq=4000, order=5):
    # Parámetros del filtro
    # Se pueden pasar como argumentos de la función

    # Funciones para diseñar y aplicar los filtros
    def butter_lowpass_filter(data, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        y = signal.lfilter(b, a, data)
        return y

    def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = signal.butter(order, [low, high], btype='band')
        y = signal.lfilter(b, a, data)
        return y

    def butter_highpass_filter(data, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        y = signal.lfilter(b, a, data)
        return y

    FRAMES = 1024*8  # Tamaño del paquete a procesar
    FORMAT = pa.paInt16  # Formato de lectura INT 16 bits
    CHANNELS = 1
    Fs = 44100  # Frecuencia de muestreo típica

    p = pa.PyAudio()

    Stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=Fs,
        input=True,
        frames_per_buffer=FRAMES
    )

    # Se crea una gráfica que contiene dos subplots y se configuran los ejes
    fig, (ax, ax1) = plt.subplots(2)

    X_audio = np.arange(0, FRAMES, 1)
    X_fft = np.linspace(0, Fs, FRAMES)
    line, = ax.plot(X_audio, np.random.rand(FRAMES), 'r')
    line_fft, = ax1.semilogx(X_fft, np.random.rand(FRAMES), 'b')

    ax.set_ylim(-32500, 32500)
    ax.set_xlim(0, FRAMES)

    Fmin = 1
    Fmax = 20000  # Ajustar el límite superior a 20 kHz
    ax1.set_xlim(Fmin, Fmax)

    fig.show()

    F = (Fs / FRAMES) * np.arange(0, FRAMES // 2)
    while True:
        data = Stream.read(FRAMES)
        dataInt = np.frombuffer(data, dtype=np.int16)

        # Seleccionar y aplicar el filtro
        if filter_type == 'lowpass':
            filtered_data = butter_lowpass_filter(dataInt, low_cutoff_freq, Fs, order)
        elif filter_type == 'bandpass':
            filtered_data = butter_bandpass_filter(dataInt, low_cutoff_freq, high_cutoff_freq, Fs, order)
        elif filter_type == 'highpass':
            filtered_data = butter_highpass_filter(dataInt, high_cutoff_freq, Fs, order)
        else:
            raise ValueError("Tipo de filtro desconocido")

        line.set_ydata(filtered_data)

        M_gk = abs(fourier.fft(filtered_data) / FRAMES)
        ax1.set_ylim(0, np.max(M_gk + 10))
        line_fft.set_ydata(M_gk)
        M_gk = M_gk[0:FRAMES // 2]
        Posm = np.where(M_gk == np.max(M_gk))
        F_Found = F[Posm]

        fig.canvas.draw()
        fig.canvas.flush_events()

# Ejemplo de uso de la función
audio_processing(filter_type='bandpass', low_cutoff_freq=100, high_cutoff_freq=1000, order=5)
