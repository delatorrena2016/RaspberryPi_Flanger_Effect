# importamos librerias
from scipy import signal 
import numpy as np 
import sounddevice as sd 

#declaramos las constantes 

sampling_rate = 44100  # frecuencia de muestreo 
duration_in_seconds = 5 # duracion de la señal en segundos 
lowpass = False # determina el filtro 
amplitude = 0.3 # configuracion para las bocinas 

duration_in_samples = int(duration_in_seconds*sampling_rate) #duracion de las muestras

# generamos ruido blanco
white_noise = np.random.default_rng().uniform(-1,1, duration_in_samples)
input_signal = white_noise

#Definimos frecuencias de corte 
cutoff_frequency = np.geomspace(20000, 20, input_signal.shape[0])

allpass_output = np.zeros_like(input_signal) # inicializamos un arreglo de ceros del mismo tamaño de la entrada

#crea una constante
dn_1 = 0
# creamos un for para ir muestra por muestra
for n in range(input_signal.shape[0]):
    break_frequency = cutoff_frequency[n]

    #calcuulamos el filtro pasatodo
    tan = np.tan(np.pi * break_frequency/sampling_rate)

    a1 = (tan -1) / (tan+1) #calcula la tangente del ángulo correspondiente a la frecuencia de corte normalizada por la tasa de muestreo.

    allpass_output[n] = a1*input_signal[n]+dn_1

    dn_1 = input_signal[n]- a1* allpass_output[n] #Esta línea actualiza la variable de estado

if lowpass:
    allpass_output *= -1
filter_output =input_signal+allpass_output


filter_output *= 0.5

filter_output *= amplitude

sd.play(filter_output, sampling_rate)

sd.wait()

