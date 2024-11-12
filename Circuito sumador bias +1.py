import numpy as np
import matplotlib.pyplot as plt

# Parámetros del circuito
R1 = 10e3  # Resistencia en ohmios (10 kOhms)
R2 = 6.8e3  # Resistencia en ohmios (6.8 kOhms)
C = 100e-6  # Capacitancia en faradios (100 uF)
Vs = 5      # Voltaje de alimentación en voltios (5V)

# Parámetros de la señal de entrada
f_senal = 60          # Frecuencia de la señal en Hz
Vi_amplitud = 2       # Amplitud de la señal de entrada
t = np.linspace(0, 0.1, 1000)  # Tiempo (0 a 0.1 segundos)

# Señal de entrada senoidal a 60 Hz
Vi = Vi_amplitud * np.sin(2 * np.pi * f_senal * t)

# Voltaje de referencia en Vo (debido al divisor de tensión con R1 y R2)
Vo_ref = Vs * (R2 / (R1 + R2))

# Simulación de la respuesta del circuito
# En este caso, la salida Vo será la señal desplazada con el voltaje de referencia
Vo = Vo_ref + Vi

# Graficar la señal de entrada y salida
plt.figure(figsize=(10, 5))
plt.plot(t, Vi, label="Señal de Entrada Vi (60 Hz)")
plt.plot(t, Vo, label="Señal de Salida Vo (desplazada)", color='red')
plt.axhline(Vo_ref, color='green', linestyle='--', label="Voltaje de referencia Vo_ref")
plt.title("Desplazamiento de una señal senoidal al semiplano positivo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Voltaje (V)")
plt.legend()
plt.grid()
plt.show()