import pygame
from pygame import mixer
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

# Función para aplicar el filtro pasa bajas
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

# Inicializar Pygame y el mezclador
pygame.init()
mixer.init()

# Cargar y procesar la música
fs, data = wavfile.read(r'C:\Users\ismae\Music\payaso.wav')  # Asegúrate de usar un archivo .wav
cutoff = 10000 # Frecuencia de corte del filtro pasa bajas
filtered_data = butter_lowpass_filter(data, cutoff, fs)

# Guardar el archivo filtrado temporalmente
wavfile.write(r'C:\Users\ismae\Music\payaso_filtered.wav', fs, np.int16(filtered_data))

# Cargar y reproducir la música filtrada
mixer.music.load(r'C:\Users\ismae\Music\payaso_filtered.wav')
mixer.music.play()

# Bucle principal
input("xd") 
if pygame.K_KP_ENTER: mixer.music.stop()
