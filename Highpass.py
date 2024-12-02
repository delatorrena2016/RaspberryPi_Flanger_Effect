import numpy as np

cut_off_f  = 4000.0  # Frecuencia de corte en Hz
fs         = 44100   # Frecuencia de muestreo en Hz
Ts         = 1/fs    # Periodo de muestreo (s)

y_n, y_n_1 = 0, 0  # Inicialización de salidas, actual y anterior, por muestra
RC         = 1/(cut_off_f*2*np.pi)  # RC en términos de punto -3dB 
a, b       = RC/(Ts+RC), -Ts/(Ts+RC)  # Coeficientes de ecuación, por diferencias

def highpassf(x_n):
    global y_n, y_n_1  # Actualizar la inicialización de salidas
    y_n_1 = y_n        # Desplazamiento de muestras de salida

    y_n   = (a * x_n) + (b * y_n_1)  # Nuevo valor de salida
    return y_n

