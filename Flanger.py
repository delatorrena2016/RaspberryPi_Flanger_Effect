import numpy as np
import math

delay        = 0.003                    # [0.003,0.01] retardo máximo de 3ms 
mod_width    = 0.003                    # Cant. de profundidad
mod_freq     = 1                        # Rapidez del movimiento de las muescas (Hz)
fs           = 44.1E03                  # Tasa de muestreo (Hz)

# Cambio a muestras
M0           = np.floor(delay * fs)     # Retardo por muestra 
width        = np.floor(mod_width * fs) # Barrido o Oscilacion de retardo maximo por muestra
ratio        = mod_freq / fs            # Frecuencia de modulación por muestra
# Control de la mezcla [0,1]
feedback     = 1                        # Intensidad de la señal original
gain         = 0.8                      # Profundidad de las muescas o flangeo 
# Inicializacion
phase        = 0                        # Desface inicial nulo
i_n          = 0                        # Inicialización de indice 
# Retardo máximo y buffer de línea de retardo
# El tamaño del buf. retardo es una unidad más grande que el,
# valor máximo que M(n) puede tomar.
delay_length = int(2 + M0 + width)
delay_buffer = np.zeros(delay_length)
#count        = 0

def lfo(i=1):  # Modulador de longitud de retardo M
  global phase
  # Mn o M(n) es el numero de picos en la respuesta de frecuencia,
  # centrados al rededor de las frecuencias k(2pi/M), k=0,1,...,M-1.
  # Extremos entre (M0-width, M0+width)
  Mn = 1 + M0 + width*np.sin(2*np.pi*phase)
  # Se suma al valor anterior el "ratio" 0,2.27e-5,4.53e-5,...
  #phase = count * ratio
  phase  = phase + (i * ratio)  # Modulacion lenta lineal caracteristica de flanging
  # cerradura sobre un solo periodo fase toma [offset = 0, 1]
  if(phase > 1.0):
    phase = phase - 1.0
  return Mn

def delay_line(i_m):
  # We force index from zero and above for inputs
  idx = i_n - i_m
  #print(i_n,i_m,idx)
  if idx < 0:
    idx = idx + delay_length
  return delay_buffer[idx]

def push(sample):
  global i_n, delay_buffer
  # Asignación punto a punto del buffer al buf. de retardo.
  delay_buffer[i_n] = sample 
  # Asignación de izquierda a derecha [0, len(delay_buffer)-1].
  i_n = i_n + 1 
  if i_n == delay_length:
    i_n = i_n - delay_length
  # No asignamos punto al último espacio del buf. de retardo,
  # Así como nunca lo leemos (por inicialización 0).

def flanger(x):        # Mixer de señales dry y wet
  #global count
  osc = lfo()
  m = int(osc)  # Longitud de retardo M(n) calculado por LFO
  # Manejo de error de truncamiento al acercarse al limite superior
  if m == osc:   
    m = m - 1
  eta = osc - m      # Retardo fraccional entre muestras, indice de entre n-M y n-M-1 
  
  #count = count + 1
  #if count > 1024:
  #  count = count - 1025
  
  # Linea de retardo interpolada, ahora M(n) varia suavemente en valores no discretos
  # x_eta = x(n-m-eta) = (1-eta)*x(n-m) + eta*x(n-m-1)
  x_eta = ((1 - eta) * delay_line(m)) + (eta * delay_line(m + 1))
  push(x) # Nuevo punto en buf. de retardo

  # suma de la señal original (dry signal) x, y la señal retrasada (linea de retardo, aquí interpolada) x_eta 
  return (feedback * x) + (gain * x_eta) # Ecuación de diferencias de flangeo

