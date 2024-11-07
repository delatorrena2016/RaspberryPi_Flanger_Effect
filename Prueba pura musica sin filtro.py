import pygame
from pygame import mixer

# Inicializar Pygame y el mezclador
pygame.init()
mixer.init()

# Cargar y reproducir la música
mixer.music.load(r'C:\Users\ismae\Music\payaso.wav') # cambiar por un audio de su computadora con extencion wav
mixer.music.play()

# Bucle principal

input("xd") 
if pygame.K_KP_ENTER: mixer.music.stop()