import jack
import numpy as np
import scipy.signal as signal
from Flanger import *
import gpiod

# Crear el cliente JACK
client = jack.Client("Flanger")

# Registrar puertos de entrada y salida
client.inports.register("input")
client.outports.register("output")

# Inicialización de buffer (dry) de audio de JACK
buffer_size = 2048  # Tamaño del buffer circular
buffer = np.zeros(buffer_size, dtype=np.int16)  # Inicialización. 1024 elementos. Tipo: signed 16-bit integer
write_index = 0  # Índice para escribir en el buffer

# Inicialización de Buffer (wet) de audio procesado
mod_buffer = np.zeros(buffer_size, dtype=np.int16)
# Se define el Índice del dato del buffer (dry) a modular por flanger
mod_index = 0

# Definir los coeficientes del filtro pasabajas
order = 4  # Orden del filtro
cutoff_freq = 1000  # Frecuencia de corte en Hz
nyquist = 0.5 * 44100  # Frecuencia de Nyquist
normal_cutoff = cutoff_freq / nyquist
b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)

# Estado inicial del filtro
zi = signal.lfilter_zi(b, a)

# Función de callback para procesar el audio
@client.set_process_callback
def process(frames):  # Frames (muestras por procesar) es provisto por el servidor JACK
    global write_index, buffer, mod_index, mod_buffer, zi  # para usar variables declaradas fuera de la función

    # Captura el audio desde el 'buffer' del puerto de entrada
    in_data = client.inports[0].get_array()

    # Grabamos en el Buffer circular la información de in_data
    # La magnitud de frames define cuántos elementos grabaremos en buffer
    for i in range(frames):
        # Conversión a tipo de dato correcto
        buffer[write_index] = np.int16(in_data[i] * 32767)

        # Se aumenta el índice, se reinicia si llega al máximo tamaño del buffer
        write_index = (write_index + 1) % buffer_size

    # Aplicar el filtro pasabajas a los datos del buffer
    filtered_buffer, zi = signal.lfilter(b, a, buffer, zi=zi)

    # Efecto Flanger
    for i in range(frames):
        mod_buffer[i] = flanger(filtered_buffer[mod_index])
        mod_index = (mod_index + 1) % buffer_size

    # Enviar los datos filtrados a la salida
    out_data = client.outports[0].get_array()
    out_data[:] = mod_buffer[:frames] / 32767.0

# Manejo de errores
@client.set_xrun_callback
def xrun(delay):
    print("Xrun occurred:", delay)

# Iniciar el cliente JACK
with client:
    print("Flanger is running... Press Ctrl+C to stop")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Capture stopped by user.")
