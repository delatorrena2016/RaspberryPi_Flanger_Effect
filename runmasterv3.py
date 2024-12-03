



import jack
import numpy as np
from Flanger import *
from LowPass import *
from Highpass import *
from bandpass import *
from gpiozero import LED, Button
from time import sleep


# Crear el cliente JACK
client = jack.Client("Flanger")

# Registrar puertos de entrada y salida
client.inports.register("input")
client.outports.register("output")



# Configura los leds de estado de los diferentes tratamientos digitales
ledf = LED(14)   # Flanger
ledl = LED(2)   # Low Pass Filter
ledh = LED(3)   # High Pass Filter
ledb = LED(4)   # Band Pass Filter

# Configura el botones de interfaz para la activacion o desactivacion de los diferentes tratamientos
buttonfla = Button(15) # Boton para Flanger
buttonlpf = Button(18) # Boton para lowpassfilter
buttonhpf = Button(23) # Boton para highpassfilter
buttonbpf = Button(24) # Boton para bandpassfilter

# Funcion de passthrough para la senal sin tratamiento digital
def passthrough(x):
    return x
# Se inicializan las variables de los filtros aplicados a la senal de salida, todos se inicializan como passthrough
f1 = passthrough
f2 = passthrough
f3 = passthrough
f4 = passthrough


# Se definen todas la funciones conmutativas para los botones de activacion de los diferentes tratamientos
def buttonfla_pressed():    # On Flanger
    global f1
    ledf.on()
    f1 = flanger

def buttonfla_released():    # Off Flanger
    global f1
    ledf.off()
    f1 = passthrough

def buttonlpf_pressed():    # On LowPassfilter
    global f2
    ledl.on()
    f2 = lowpassf

def buttonlpf_released():   # Off LowPassFilter
    global f2
    ledl.off()
    f2 = passthrough

def buttonhpf_pressed():    # On HighPassfilter
    global f3
    ledh.on()
    f3 = highpassf

def buttonhpf_released():    # Off highPassfilter
    global f3
    ledh.off()
    f3 = passthrough

def buttonbpf_pressed():    # On BandPassfilter
    global f4
    ledb.on()
    f4 = bandpassf

def buttonbpf_released():    # Off BandPassfilter
    global f4
    ledb.off()
    f4 = passthrough


# Se asocian los botones con las funciones definidas

buttonfla.when_pressed = buttonfla_pressed
buttonfla.when_released = buttonfla_released
buttonlpf.when_pressed = buttonlpf_pressed
buttonlpf.when_released = buttonlpf_released
buttonhpf.when_pressed = buttonhpf_pressed
buttonhpf.when_released = buttonhpf_released
buttonbpf.when_pressed = buttonbpf_pressed
buttonbpf.when_released = buttonbpf_released



# Tamono del buffer circular,  4096 muestras y definicion del formato, se inicializan las variables de la senal de entrada
buffer_size = 4096
buffer = np.zeros(buffer_size, dtype=np.int16)
write_index = 0  #ndice para escribir en el buffer

# Funcion de callback para procesar el audio
@client.set_process_callback
def process(frames):
    global write_index, buffer, f1, f2, f3, f4 

    # Captura el audio de entrada
    in_data = client.inports[0].get_array()

    # Usamos el buffer circular
    for i in range(frames):
        # Escribir los datos en el buffer en la posicion correspondiente
        buffer[write_index] = np.int16(in_data[i]*32767)

        # Avanzamos el indice de escritura, y si llega al final, volvemos al principio
        write_index = (write_index + 1) % buffer_size

        # Enviar los datos a la salida (en este caso, directamente sin modificar)
    out_data = client.outports[0].get_array()
    
   #empieza el tratamiento
    for i in range(len(buffer)):
        
        out_data[i] = (buffer[i])/32767.0
       
        
        out_data[i] = f4(f3(f2(f1(out_data[i])))) # Se aplican los 4 filtros a la senal de salida, de no tener filtros activos la senal = passthrough
       
       
    out_data[:] = out_data

    
       
    


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

