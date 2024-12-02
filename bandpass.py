import numpy as np

# Definir las frecuencias de corte y la frecuencia de muestreo
low_cutoff = 1000.0  # Frecuencia de corte baja en Hz
high_cutoff = 4000.0  # Frecuencia de corte alta en Hz
fs = 44100  # Frecuencia de muestreo en Hz
Ts = 1 / fs  # Periodo de muestreo (s)

# Inicialización de salidas, actual y anterior, por muestra
y_n_low, y_n_1_low = 0, 0
y_n_high, y_n_1_high = 0, 0

# Cálculo de RC y coeficientes para el filtro pasa bajas
RC_low = 1 / (low_cutoff * 2 * np.pi)
a_low, b_low = Ts / (Ts + RC_low), RC_low / (Ts + RC_low)

# Cálculo de RC y coeficientes para el filtro pasa altas
RC_high = 1 / (high_cutoff * 2 * np.pi)
a_high, b_high = RC_high / (Ts + RC_high), -Ts / (Ts + RC_high)

def bandpassf(x_n):
    global y_n_low, y_n_1_low, y_n_high, y_n_1_high
    
    # Filtro pasa bajas
    y_n_1_low = y_n_low
    y_n_low = (a_low * x_n) + (b_low * y_n_1_low)
    
    # Filtro pasa altas
    y_n_1_high = y_n_high
    y_n_high = (a_high * y_n_low) + (b_high * y_n_1_high)
    
    return y_n_high

