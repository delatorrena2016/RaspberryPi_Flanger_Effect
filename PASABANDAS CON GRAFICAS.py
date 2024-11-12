import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, lfilter

# Función para aplicar el filtro pasabanda
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band', analog=False)
    y = lfilter(b, a, data)
    return y

# Cargar el archivo de audio original
fs, data = wavfile.read(r'C:\Users\HP\Music\cancion.wav')

# Definir las frecuencias de corte del filtro pasabanda
lowcut = 500   # Frecuencia de corte baja en Hz
highcut = 5000 # Frecuencia de corte alta en Hz

# Aplicar el filtro pasabanda
filtered_data = butter_bandpass_filter(data, lowcut, highcut, fs)

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
plt.legend(loc="upper right")  # Especifica una ubicación fija para la leyenda

# Gráfico del audio filtrado
plt.subplot(2, 1, 2)
plt.plot(t, filtered_data, label='Filtrado', color='purple')
plt.title('Audio Filtrado - Pasa Banda')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid()
plt.legend(loc="upper right")  # Especifica una ubicación fija para la leyenda

plt.tight_layout()
plt.show()
