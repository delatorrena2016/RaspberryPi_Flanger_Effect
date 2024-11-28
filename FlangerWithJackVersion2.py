import jack
import numpy as np
import math

#Variables de uso general
pi= 3.14159

# Crear el cliente JACK
client = jack.Client("Flanger")

# Registrar puertos de entrada y salida
client.inports.register("input")
client.outports.register("output")

#Declaracion del buffer circular
buffer_size = 2048                              #Tamaño del buffer
buffer = np.zeros(buffer_size, dtype=np.int16)  #Buffer circular con 
write_index = 0                                 #Índice para escribir en el buffer

#Parametros de flanger
delay= int(1000) #Delay maximo del flanger
depth= int(500) #Delay maximo real. Amplitud del LFO
lfo_freq= 0.9   #Frecuencia del LFO
feedback= 0.3   #Ganancia de la retroalimentacion de Flanger
wet_dry= 0.5    #Ganancia de muestra retardada (1-wet_dry para muestra actual)

#Parametros de LFO
samp_per_cyc= int(44100/lfo_freq)    #Numero de muestras para evaluar un ciclo del LFO a Frecuencia de muestreo
angle_step= 2*pi/samp_per_cyc   #Paso entre muestra del LFO en radianes
step_actual= 0

# Función de callback para procesar el audio
@client.set_process_callback
def process(frames):
    #Variables globales
    global write_index, buffer, step_actual

    #Captura el audio de entrada en un vector normalizado
    in_data = client.inports[0].get_array()

    #Actualizamos el buffer circular con la ultima informacion de entrada
    buffer[write_index:write_index+len(in_data)]= np.int16(in_data*32767)
    write_index = (write_index+len(in_data))%buffer_size
    
    #EFECTO FLANGER
    #Declaración de vector de buffer procesado
    mod_sample= np.zeros(frames, dtype=np.int16)

    mod_ind= write_index-frames  #Indice de modulacion para la muestra en buffer a procesar
    if(mod_ind<0):
        mod_ind += buffer_size   #Se garantiza la ciclicidad del indice
    
    #Vector de step_actual para esta llamada de callback
    pasos_ret= np.arange(step_actual, step_actual+len(in_data), dtype=int)
    step_actual= (step_actual+len(in_data))%samp_per_cyc 

    #vector de retardo absoluto
    retardo_abs = np.array(depth*(1 + np.sin(pasos_ret*angle_step)), dtype=int)
    retardo_abs = np.where(retardo_abs < 0, retardo_abs + 1000, retardo_abs)

    senal_ret= buffer[retardo_abs[0]]
    mod_ind_vect= np.arange(mod_ind, mod_ind+len(in_data), dtype=int)

    for sample in range(frames):  
        #Calculo de la señal de retardo retroalimentacion sumada
        if (sample>0):
            senal_ret= np.clip(feedback*mod_sample[sample-1] + buffer[retardo_abs[sample]], -32768, 32767).astype(np.int16)
        
        mod_sample[sample] = np.clip((1 - wet_dry) * buffer[mod_ind_vect[sample]] + wet_dry * senal_ret, -32768, 32767).astype(np.int16)
        
    # Enviar los datos procesados a la salida 
    out_data = client.outports[0].get_array()
    out_data[:] =  mod_sample/ 32767.0
     

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
                