import numpy as np

center_frequency = 1500.0  # Frecuencia de corte en Hz
fs         = 44100   # Frecuencia de muestreo en Hz
Ts         = 1/fs    # Periodo de muestreo (s)
Q = 0.5 #1500/3000               # Ancho de banda relativo

x1, x2, y1, y2 = 0, 0, 0, 0  # Inicialización de salidas, actual y anterior, por muestra 


def bandpassf(x):
    global x1, x2, y1, y2  # Actualizar la inicialización de salidas
    BW = center_frequency / Q        # Desplazamiento de muestras de salida
    tan = np.tan(np.pi * BW / fs)
    c = (tan - 1) / (tan + 1)
    d = - np.cos(2 * np.pi *center_frequency / fs)
    b = [-c, d * (1 - c), 1]
    a = [1, d * (1 - c), -c]

    y = b[0] * x + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
    y2 = y1
    y1 = y
    x2 = x1
    x1 = x
    
    return y

