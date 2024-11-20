import jack
import numpy as np
from Flanger import *
import gpiod

#BUTTON_PIN_LP = 23
#BUTTON_PIN_HP = 24
#BUTTON_PIN_BP = 25
#BUTTON_PIN_F  = 27
#chip = gpiod.Chip('gpiochip4')
#button_line = chip.get_line(BUTTON_PIN_F)
#button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
#
#if button_line.get_value() == 1:  # Boton presionado
#           # funcion de filtro

# Crear el cliente JACK
client = jack.Client("Flanger")

# Registrar puertos de entrada y salida
client.inports.register("input")
client.outports.register("output")


# Tamo del buffer circular, por ejemplo, 1024 muestras
buffer_size = 1024
buffer = np.zeros(buffer_size, dtype=np.int16)
write_index = 0  #ndice para escribir en el buffer

# Funcin de callback para procesar el audio
@client.set_process_callback
def process(frames):
    global write_index, buffer

    # Captura el audio de entrada
    in_data = client.inports[0].get_array()

    # Usamos el buffer circular
    for i in range(frames):
        # Escribir los datos en el buffer en la posicin correspondiente
        buffer[write_index] = np.int16(in_data[i]*32767)

        # Avanzamos el ndice de escritura, y si llega al final, volvemos al principio
        write_index = (write_index + 1) % buffer_size

    # Enviar los datos a la salida (en este caso, directamente sin modificar)
    out_data = client.outports[0].get_array()
    out_data[:] = buffer / 32767.0

     Effecto Flanger
    for i in range(len(buffer)):
        out_data[i] = flanger(buffer[i])
        # Normalizacion max-min para acotar valores
    out_data = out_data / max(np.abs(out_data))
    

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
                
        
        
        
        
        


