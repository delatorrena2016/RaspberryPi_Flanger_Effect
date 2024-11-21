import numpy as np
import scipy.signal as signal

def butter_lowpass_filter(data, cutoff, fs, order=5):
    """
    Aplica un filtro pasabajas a un arreglo de datos.

    Parámetros:
    data (array): Arreglo de datos de entrada.
    cutoff (float): Frecuencia de corte del filtro en Hz.
    fs (float): Frecuencia de muestreo en Hz.
    order (int): Orden del filtro. Por defecto es 5.

    Retorna:
    array: Arreglo de datos filtrados.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.lfilter(b, a, data)
    return y

# Ejemplo de uso
if __name__ == "__main__":
    # Parámetros del filtro
    cutoff_freq = 1000  # Frecuencia de corte en Hz
    sampling_rate = 44100  # Frecuencia de muestreo en Hz
    order = 5  # Orden del filtro

    # Generar una señal de ejemplo (ruido blanco)
    duration = 5  # Duración en segundos
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    data = np.random.normal(0, 1, t.shape)

    # Aplicar el filtro pasabajas
    filtered_data = butter_lowpass_filter(data, cutoff_freq, sampling_rate, order)

    # Aquí puedes agregar código para guardar o procesar los datos filtrados
    print(filtered_data)

