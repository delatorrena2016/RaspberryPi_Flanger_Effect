import numpy as np

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
  return int(Mn)

def delay_line(i_m):
  global i_n, delay_buffer
  # We force index from zero and above for inputs
  idx = i_n - i_m
  #print(i_n,i_m,idx)
  if idx < 0:
    idx = idx + delay_length
  return delay_buffer[idx]

def push(sample):
  global i_n, delay_buffer
   # push sample and closure on/over superior limit
  delay_buffer[i_n] = sample
  i_n = i_n + 1
  if i_n + 1 >= delay_length:
    i_n = i_n - delay_length

def flanger(x):        # Mixer de señales dry y wet
  #global count
  
  m = np.floor(lfo())  # Longitud de retardo M(n) calculado por LFO
  eta = lfo() - m      # retardo fraccional en las muestras, fraccion de indice entre n-M y n-M-1 

  #count = count + 1
  #if count > 1024:
  #  count = count - 1025
  
  # Linea de retardo interpolada, ahora M(n) varia suavemente en valores no discretos
  # x_eta = (1-eta)x(n-m) + eta x(n-m-1)
  x_eta = ((1 - eta) * delay_line(m)) + (eta * delay_line(m + 1))
  push(x)
  # Mixer o Relacion de entrada-salida para efecto flanger sencillo,
  # suma de la señal original (dry signal) x, y la señal retrasada (linea de retardo, aquí interpolada) x_eta,
  # escalada por parametro de profundidad g 
  return (feedback * x) + (gain * x_eta) 

