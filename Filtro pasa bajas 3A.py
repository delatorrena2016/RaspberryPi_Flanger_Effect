import numpy as np
import scipy.signal as signal
numerator = [6.152e22] 
denominator = [1, 2.094e04, 2.646e08, 1.994e12, 1.045e16, 3.264e19, 6.152e22]

def filter_data(lpt, fs=44100, chunk_size=1024):
    """
    Aplica un filtro a los datos de entrada y devuelve los datos filtrados.

    Args:
        lpt (numpy array): Datos de entrada a filtrar.
        numerator (list): Coeficientes del numerador de la función de transferencia.
        denominator (list): Coeficientes del denominador de la función de transferencia.
        fs (int): Frecuencia de muestreo.
        chunk_size (int): Tamaño del bloque de datos a procesar.

    Returns:
        numpy array: Datos filtrados.
    """
    # Crear la función de transferencia (dominio de Laplace)
    system = signal.TransferFunction(numerator, denominator)

    # Normalizar los datos de entrada
    lpt = lpt / np.max(np.abs(lpt))

    # Crear un array vacío para la salida filtrada
    filtered_data = np.zeros_like(lpt)

    # Filtrar los datos en bloques (simulando procesamiento en tiempo real)
    num_samples = len(lpt)
    for i in range(0, num_samples, chunk_size):
        data_chunk = lpt[i:i + chunk_size]
        filtered_chunk = signal.lfilter(numerator, [1], data_chunk)
        filtered_data[i:i + chunk_size] = filtered_chunk

    return filtered_data

