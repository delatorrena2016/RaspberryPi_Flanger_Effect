import jack
import numpy as np

# Crear el cliente JACK
client = jack.Client("PythonCapture")

# Registrar el puerto de entrada para capturar audio
client.inports.register("input")

# Función de callback para capturar el audio
@client.set_process_callback
def process(frames):
    # Captura el audio de entrada
    in_data = client.inports[0].get_array()
    
    # Convierte el audio capturado a un array de numpy
    audio_data = np.array(in_data, dtype=np.float32)
    
    # Aquí puedes procesar o guardar el audio capturado
    print("Audio capturado:", audio_data)

# Manejo de errores
@client.set_xrun_callback
def xrun(delay):
    print("Xrun occurred:", delay)

# Iniciar el cliente JACK
with client:
    print("JACK client is running... Press Ctrl+C to stop")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Capture stopped by user.")