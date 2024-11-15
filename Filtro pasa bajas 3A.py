from scipy import signal
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

sampling_rate = 44100
duration_in_seconds = 5
highpass = False
amplitude = 0.3

duration_in_samples = int(duration_in_seconds * sampling_rate)

white_noise = np.random.default_rng().uniform(-1, 1, duration_in_samples)
input_signal = white_noise

cutoff_frequency = np.geomspace(2000, 20, input_signal.shape[0])

allpass_output = np.zeros_like(input_signal)

dn_1 = 0

for n in range(input_signal.shape[0]):
    break_frequency = cutoff_frequency[n]

    tan = np.tan(np.pi * break_frequency / sampling_rate)

    a1 = (tan - 1) / (tan + 1)

    allpass_output[n] = a1 * input_signal[n] + dn_1

    dn_1 = input_signal[n] - a1 * allpass_output[n]

if highpass:
    allpass_output *= -1

filter_output = input_signal + allpass_output

filter_output *= 0.5

filter_output *= amplitude

# Graficar las señales
plt.figure(figsize=(12, 6))

plt.subplot(3, 1, 1)
plt.plot(input_signal)
plt.title('Señal de Ruido Blanco')
plt.xlabel('Muestra')
plt.ylabel('Amplitud')

plt.subplot(3, 1, 2)
plt.plot(allpass_output)
plt.title('Salida del Filtro Allpass')
plt.xlabel('Muestra')
plt.ylabel('Amplitud')

plt.subplot(3, 1, 3)
plt.plot(filter_output)
plt.title('Señal Filtrada')
plt.xlabel('Muestra')
plt.ylabel('Amplitud')

plt.tight_layout()
plt.show()

# Reproducir la señal filtrada
sd.play(filter_output, sampling_rate)
sd.wait()
