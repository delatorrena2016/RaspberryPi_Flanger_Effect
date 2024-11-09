import matplotlib
import numpy as np
import pyaudio as pa 
import struct 
import matplotlib.pyplot as plt
import scipy.fftpack as fourier
import winsound
import scipy.io.wavfile as waves 
matplotlib.use('tkAgg')

#%matplotlib notebook

FRAMES = 1024*8                      #Tamaño del paquete ap procesar 
FORMAT = pa.paInt16                  # Formato de lectura INT 16 bits

CHANNELS = 1

Fs = 44100                          #Frecuencia de muestreo tipica para 

p= pa.PyAudio()

Stream = p.open(                    #Abrimos el canal de audio 
    format =FORMAT,
    channels = CHANNELS,
    rate = Fs,
    input =True,
    output = True,
    frames_per_buffer=FRAMES

)
## se crea una grafica que contiente dos subplots y se configura los ejes

fig, (ax, ax1) = plt.subplots(2)

X_audio =np.arange(0,FRAMES,1)
X_fft = np.linspace(0, Fs, FRAMES)
line, = ax.plot(X_audio, np.random.rand(FRAMES), 'r')
line_fft, = ax1.semilogx(X_fft, np.random.rand(FRAMES), 'b')

ax.set_ylim(-32500, 32500)
ax.set_xlim(0, FRAMES)

Fmin = 1
Fmax = 5000
ax1.set_xlim(Fmin,Fmax)

fig.show()

F= (Fs/FRAMES)*np.arange(0,FRAMES // 2)                     #Creamos el vector de frecuencias para encontrar la frecuencia dominante 
while True:
    data =Stream.read(FRAMES)
    dataInt = struct.unpack(str(FRAMES) + 'h', data)        #Convertimos los datos que se encuentran empaquetados en bytes 

    line.set_ydata(dataInt)                                 # Asignamos los datos a la curva de la variacion temporal 

    M_gk = abs(fourier.fft(dataInt)/FRAMES)                 # Calculamos la FFT y la magnitud de la FFT del paquete de datos

    ax1.set_ylim(0,np.max(M_gk+10))
    line_fft.set_ydata(M_gk)                                #asignamos la magnitud de la FFT a la curva del espectro
    M_gk = M_gk[0:FRAMES//2]
    Posm = np.where(M_gk == np.max(M_gk))
    F_Found = F[Posm]
    
    print(int(F_Found))
    
    fig.canvas.draw()
    fig.canvas.flush_events()
    






