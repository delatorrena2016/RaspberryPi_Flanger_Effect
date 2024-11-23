import numpy as np

cut_off_f  = 90.0 # Frecuencia de corte
fs         = 44100
Ts         = 1/fs # Periodo de muestreo (s)

y_n, y_n_1 = 0, 0 # Inicializacion de salidas, actual y anterior,
#por muestra
RC         = 1/(cut_off_f*2*np.pi) # RC en terminos de punto -3dB 
a, b       = Ts/(Ts+RC), RC/(Ts+RC) # Coeficientes de ecuacion,
#por diferencias


def lowpassf(x_n):
    global y_n, y_n_1 # Actualizar la inicializacion de salidas
    y_n_1 = y_n   # Desplazamiento de muestras de salida

    y_n   = (a * x_n) + (b * y_n_1) # Nuevo valor de salida
    return y_n