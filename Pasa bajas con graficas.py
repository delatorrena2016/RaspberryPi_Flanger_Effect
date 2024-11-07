import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, lfilter

# Función para aplicar el filtro pasa bajas
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

# Cargar el archivo de audio original
fs, data = wavfile.read(r'C:\Users\ismae\Music\payaso.wav')

# Aplicar el filtro pasa bajas
cutoff = 1000  # Frecuencia de corte del filtro pasa bajas
filtered_data = butter_lowpass_filter(data, cutoff, fs)

# Crear un vector de tiempo
t = np.linspace(0, len(data) / fs, num=len(data))

# Graficar el audio original y el filtrado
plt.figure(figsize=(12, 6))

# Gráfico del audio original
plt.subplot(2, 1, 1)
plt.plot(t, data, label='Original')
plt.title('Audio Original')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid()
plt.legend()

# Gráfico del audio filtrado
plt.subplot(2, 1, 2)
plt.plot(t, filtered_data, label='Filtrado', color='Pink')
plt.title('Audio Filtrado')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
