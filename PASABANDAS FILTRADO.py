import pygame
from pygame import mixer
import numpy as np
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

# Inicializar Pygame y el mezclador
pygame.init()
mixer.init()

# Cargar y procesar la música
fs, data = wavfile.read(r'C:\Users\HP\Music\cancion.wav')  # Asegúrate de usar un archivo .wav
lowcut = 500    # Frecuencia de corte baja en Hz
highcut = 5000  # Frecuencia de corte alta en Hz
filtered_data = butter_bandpass_filter(data, lowcut, highcut, fs)

# Normalizar el audio filtrado para asegurar una buena amplitud
filtered_data = filtered_data / np.max(np.abs(filtered_data)) * 32767

# Guardar el archivo filtrado temporalmente
wavfile.write(r'C:\Users\HP\Music\cancion.wav', fs, np.int16(filtered_data))

# Cargar y reproducir la música filtrada
mixer.music.load(r'C:\Users\HP\Music\cancion.wav')
mixer.music.play()

# Bucle principal
input("Presiona Enter para detener la reproducción.")
mixer.music.stop()
