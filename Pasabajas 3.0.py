import matplotlib
import numpy as np
import pyaudio as pa
import matplotlib.pyplot as plt
import scipy.fftpack as fourier
import scipy.signal as signal
import scipy.io.wavfile as waves
matplotlib.use('tkAgg')

# Parámetros del filtro pasa bajas
cutoff_freq = 1000  # Frecuencia de corte en Hz
order = 5  # Orden del filtro

# Función para diseñar y aplicar el filtro pasa bajas
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.lfilter(b, a, data)
    return y

FRAMES = 1024*8  # Tamaño del paquete a procesar
FORMAT = pa.paInt16  # Formato de lectura INT 16 bits
CHANNELS = 1
Fs = 44100  # Frecuencia de muestreo típica

p = pa.PyAudio()

Stream = p.open(  # Abrimos el canal de audio
    format=FORMAT,
    channels=CHANNELS,
    rate=Fs,
    input=True,
    output=True,
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
Fmax = 5000
ax1.set_xlim(Fmin, Fmax)

fig.show()

F = (Fs / FRAMES) * np.arange(0, FRAMES // 2)  # Creamos el vector de frecuencias para encontrar la frecuencia dominante
while True:
    data = Stream.read(FRAMES)
    dataInt = np.frombuffer(data, dtype=np.int16)  # Convertimos los datos que se encuentran empaquetados en bytes

    # Aplicar el filtro pasa bajas
    filtered_data = butter_lowpass_filter(dataInt, cutoff_freq, Fs, order)

    line.set_ydata(filtered_data)  # Asignamos los datos filtrados a la curva de la variación temporal

    M_gk = abs(fourier.fft(filtered_data) / FRAMES)  # Calculamos la FFT y la magnitud de la FFT del paquete de datos

    ax1.set_ylim(0, np.max(M_gk + 10))
    line_fft.set_ydata(M_gk)  # Asignamos la magnitud de la FFT a la curva del espectro
    M_gk = M_gk[0:FRAMES // 2]
    Posm = np.where(M_gk == np.max(M_gk))
    F_Found = F[Posm]


    fig.canvas.draw()
    fig.canvas.flush_events()
