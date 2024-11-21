delay        = 0.01
mod_width    = 0.003
mod_freq     = 1
fs           = 44.1E03 # sampling rate for audio CDs
ratio        = mod_freq / fs
M0           = np.floor(fs * delay)
width        = np.floor(fs * mod_width)
Nl           = 0.5 * fs
g            = 1 # notch depth [0,1]
phase        = 0
i_n          = 0
# maximum delay
# L = fs(delay + mod_width) + 2
delay_length = M0 + width + 2 # f441 + f132.3 + 2 = 575
delay_buffer = np.zeros(delay_length)

def lfo(i=1):
  global phase
  # no. of notches
  # if phase [offset = 0, 1/8], then [M0, fs(delay + md_width)]
  Mn = M0 + width*np.sin(2*np.pi*phase)
  # evolution of phase
  phase  = phase + (i * ratio)
  # closure over the phase, sin over one single period
  if(phase > 1.0):
    phase = phase - 1.0
  return Mn

def delay_line(i_m):
  global i_n, delay_buffer
  # We force index from zero and above for inputs
  idx = i_n - i_m
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

#Funcion principal de la librería, modula la muestra a procesar desde el programa principal
def flanger(x):
# We are on digital domain so we're forced to clip the delay line
#Al operar en tiempo discreto hay que redondear a entero las muestras de retardo
  m = np.floor(lfo())
  # how far in between [n-M, n-M+1] we want to find a value to compensate
  # for the previous
  eta = lfo() - m
  # Le pasamos el retardo digital m
  x_eta = ((1 - eta) * delay_line(m)) + (eta * delay_line(m + 1))

  push(x)
  return x + g * x_eta

