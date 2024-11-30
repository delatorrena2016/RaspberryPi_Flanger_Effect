import numpy as np

# Parmetros del flanger
depth = 0.7  # Profundidad del efecto (entre 0 y 1)
rate = 0.25  # Velocidad de modulacin (en Hz)
max_delay = 0.005  # Mximo tiempo de retardo en segundos

# Crear un buffer para almacenar los valores retrasados
delay_buffer = np.zeros(44100)  # 1 segundo de delay a 44.1 kHz
delay_index = 0  # ndice para acceder al buffer de delay

def flanger(input_sample, sample_rate=44100):
    global delay_index, delay_buffer

    # Calcular el tiempo de retardo modulado
    modulated_delay = int(max_delay * sample_rate * (1 + depth * np.sin(2 * np.pi * rate * delay_index / sample_rate)))
    
    # Calcular el ndice de muestra retrasada, asegurndose de que no sea mayor que el tamao del buffer
    delayed_index = (delay_index - modulated_delay) % len(delay_buffer)
    
    # Obtener el valor del buffer de delay
    delayed_sample = delay_buffer[delayed_index]

    # Almacenar la muestra actual en el buffer de delay
    delay_buffer[delay_index] = input_sample

    # Incrementar el ndice del delay y hacer el wrap alrededor
    delay_index = (delay_index + 1) % len(delay_buffer)

    # Salida del flanger: mezcla la seal con la muestra retrasada
    return input_sample + delayed_sample * depth
