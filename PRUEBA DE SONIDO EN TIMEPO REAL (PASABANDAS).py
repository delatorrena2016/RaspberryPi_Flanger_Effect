import matplotlib
import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import scipy.fftpack as fourier
from scipy.signal import butter, lfilter
import winsound
import scipy.io.wavfile as waves

matplotlib.use('tkAgg')

# Parámetros de audio y gráficos
FRAMES = 1024 * 8 <
FORMAT = pa.paInt16
CHANNELS = 1
Fs = 44100  # Frecuencia de muestreo


# Configuración del filtro pasa banda
def butter_bandpass(lowcut, highcut, Fs, order=5):
    nyq = 0.5 * Fs  # Frecuencia de Nyquist
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a


def bandpass_filter(data, lowcut, highcut, Fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, Fs, order=order)
    y = lfilter(b, a, data)
    return y


# Parámetros del filtro pasa banda
lowcut = 500  # Frecuencia de corte baja en Hz
highcut = 5000  # Frecuencia de corte alta en Hz
order = 6  # Orden del filtro

# Inicialización de PyAudio y configuración del stream
p = pa.PyAudio()
Stream = p.open(format=FORMAT, channels=CHANNELS, rate=Fs, input=True, output=True, frames_per_buffer=FRAMES)

# Configuración de los gráficos
fig, (ax, ax1) = plt.subplots(2)
X_audio = np.arange(0, FRAMES, 1)
X_fft = np.linspace(0, Fs, FRAMES)
line, = ax.plot(X_audio, np.random.rand(FRAMES), 'r')
line_fft, = ax1.semilogx(X_fft, np.random.rand(FRAMES), 'b')

ax.set_ylim(-32500, 32500)
ax.set_xlim(0, FRAMES)

Fmin = 1
Fmax = 5000
ax1.set_xlim(Fmin, Fmax)

fig.show()

F = (Fs / FRAMES) * np.arange(0, FRAMES // 2)  # Vector de frecuencias para la FFT

# Bucle principal de adquisición y procesamiento
while True:
    data = Stream.read(FRAMES)
    dataInt = struct.unpack(str(FRAMES) + 'h', data)  # Conversión de bytes a enteros

    # Aplicación del filtro pasa banda
    dataInt = bandpass_filter(dataInt, lowcut, highcut, Fs, order)

    # Actualización de la señal en el dominio temporal
    line.set_ydata(dataInt)

    # FFT y cálculo de la magnitud del espectro
    M_gk = abs(fourier.fft(dataInt) / FRAMES)

    # Actualización de la gráfica de la FFT
    ax1.set_ylim(0, np.max(M_gk + 10))
    line_fft.set_ydata(M_gk)

    # Encontrar la frecuencia dominante
    M_gk = M_gk[0:FRAMES // 2]
    Posm = np.where(M_gk == np.max(M_gk))
    F_Found = F[Posm]

    print(int(F_Found))  # Imprime la frecuencia dominante en Hz

    # Refresca los gráficos
    fig.canvas.draw()
    fig.canvas.flush_events()
