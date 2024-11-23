import numpy as np

delay        = 0.01
mod_width    = 0.003
mod_freq     = 1                        # Rapidez del movimiento de las muescas (Hz)
fs           = 44.1E03                  # Tasa de muestreo (Hz)
ratio        = mod_freq / fs            # Taza de desplazamiento de muescas por cada muestra tomada
M0           = np.floor(fs * delay)     # Longitud de retardo promedio o promedio densidad de muescas
width        = np.floor(fs * mod_width) # Barrido o Oscilacion de retardo maximo
g            = 1                        # Profundidad de las muescas [0,1]
phase        = 0                        # Desface inicial nulo
i_n          = 0                        # Inicialización de indice 
# maximum delay
# L = fs(delay + mod_width) + 2
delay_length = int(M0 + width + 2) # f441 + f132.3 + 2 = 575
delay_buffer = np.zeros(delay_length)

def lfo(i=1):  # Modulador de longitud de retrazo M
  global phase
  # Mn o M(n) es el numero de picos en la respuesta de frecuencia,
  # centrados al rededor de las frecuencias k(2pi/M), k=0,1,...,M-1.
  # Extremos entre (M0-width, M0+width)
  Mn = M0 + width*np.sin(2*np.pi*phase)
  # Se suma al valor anterior el "ratio" 0,2.27e-5,4.53e-5,...
  phase  = phase + (i * ratio)  # Modulacion lenta caracteristica de flanging
  # cerradura sobre un solo periodo fase toma [offset = 0, 1]
  if(phase > 1.0):
    phase = phase - 1.0
  return int(Mn)

def delay_line(i_m):
  global i_n, delay_buffer

  idx = i_n - i_m  # Indice actual menos modulado
  if idx < 0:
    idx = idx + delay_length
  return delay_buffer[idx]

def push(sample):
  global i_n, delay_buffer

  delay_buffer[i_n] = sample  # Llenado punto a punto de buffer de retardo
  i_n = i_n + 1   # Actualizacion de indice
  # Llegamos al penultimo valor, tomamos el ultimo con indice negativo,
  # e iniciamos desde 0
  if i_n + 1 >= delay_length:
    i_n = i_n - delay_length

def flanger(x):        # Mixer de señales dry y wet

  m = np.floor(lfo())  # Longitud de retardo M(n) calculado por LFO
  eta = lfo() - m      # retardo fraccional en las muestras, fraccion de indice entre n-M y n-M-1 
  # Linea de retardo interpolada, ahora M(n) varia suavemente en valores no discretos
  # x_eta = (1-eta)x(n-m) + eta x(n-m-1)
  x_eta = ((1 - eta) * delay_line(m)) + (eta * delay_line(m + 1))

  push(x) # Llenado de buffer de retardo
  # Mixer o Relacion de entrada-salida para efecto flanger sencillo,
  # suma de la señal original (dry signal) x, y la señal retrasada (linea de retardo, aquí interpolada) x_eta,
  # escalada por parametro de profundidad g 
  return x + g * x_eta 

