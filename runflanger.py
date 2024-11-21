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

#Inicializacion de buffer (dry) de audio de JACK
buffer_size = 2048  # Tamaño del buffer circular
buffer = np.zeros(buffer_size, dtype=np.int16)  #Inicializacion. 1024 elementos. Tipo: signed 16-bit integer
write_index = 0  #Índice para escribir en el buffer

#Inicializacion de Buffer (wet) de audio procesado
mod_buffer= np.array([], dtype=np.int16)
#Se define el Indice del dato del buffer (dry) a modular por flanger
mod_index= 0

# Función de callback para procesar el audio
@client.set_process_callback
def process(frames):    #Frames (muestras por procesar) es provisto por el servidor JACK
    global write_index, buffer  #para usar variables declaradas fuera de la funcion

    # Captura el audio desde el 'buffer' del puerto de entrada
    in_data = client.inports[0].get_array()

    #Grabamos en el Buffer circular la informacion de in_data
    #La magnitud de frames define cuantos elementos grabaremos en buffer
    for i in range(frames): 
        #Conversion a tipo de dato correcto 
        buffer[write_index] = np.int16(in_data[i]*32767)

        #Se aumenta el índice, se reinicia si llega al maximo tamaño del buffer
        write_index = (write_index + 1) % buffer_size

    #Enviar los datos a la salida 
    #out_data se define como el 'buffer' de salida de JACK
    out_data = client.outports[0].get_array()  
    #Se manda a la salida el buffer sin procesar (PROPUESTO A BORRAR!!!)
    #la informacion Tipo entero del buffer se Normaliza como punto flotante antes se mandarse a out_data
    #out_data[:] = buffer / 32767.0  

    #Efecto Flanger
    for i in range(len(frames)):
        mod_buffer[i] = flanger(buffer[mod_index])
        mod_index= (mod_index + 1) % buffer_size
        # Normalizacion max-min para acotar valores
    out_data[:] = mod_buffer / 32767.0
    

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
                
        
        
        
        
        


