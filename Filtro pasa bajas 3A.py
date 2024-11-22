import numpy as np
import scipy.signal as signal
import pyaudio
from scipy.io import wavfile

# Nuevos coeficientes del numerador y denominador
numerator = [1.151e-11, 6.504e-10, 3.418e-09, 3.396e-09, 6.379e-10, 1.115e-11]
denominator = [1, -5.895, 14.54, -19.2, 14.32, -5.719, 0.9557]

# Cargar el archivo de audio
fs, audio_data = wavfile.read("C:/Users/ismae/Downloads/audio_de_Prueba.wav")

# Normalizar el audio
audio_data = audio_data / np.max(np.abs(audio_data))

# Aplicar el filtro
filtered_audio = signal.lfilter(numerator, denominator, audio_data)

# Asegúrate de que los datos estén en el rango correcto para paInt16
filtered_audio = np.int16(filtered_audio / np.max(np.abs(filtered_audio)) * 32767)

# Reproducir el audio filtrado
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=fs, output=True)
stream.write(filtered_audio.tobytes())
stream.stop_stream()
stream.close()
p.terminate()

