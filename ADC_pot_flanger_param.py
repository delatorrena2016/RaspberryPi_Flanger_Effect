import smbus2
from gpiozero import InputDevice
import time

#VARIABLES DEL CONVERTIDOR ANALOGICO-DIGITAL
ADC_ch_0_3_dir= 0x49		#Direccion de dispositivo I2C, ADC ADS1115 para canales del 0 al 3 
ADC_ch_4_dir= 0x48  		#Direccion de dispositivo I2C, ADC ADS1115 para canal 4
ADC_conf_reg_dir= 0x01		#Direccion interna de ADC ADS1115 de configuration register
ADC_Hi_thresh_dir= 0x03		#Direccion interna de ADC ADS1115 de High Threshold Register
ADC_Lo_thresh_dir= 0x02		#Direccion interna de ADC ADS1115 de Low Threshold Register
ADC_conv_reg_dir= 0x00		#direccion interna de ADC ADS1115 de Conversion register
ADC_Hi_threshMSB= 0x80		#More significant byte de Hi_threshold 
ADC_Lo_threshMSB= 0x00		#More significant byte de Lo_threshold
ADC_Hi_threshLSB= 0x00		#Less significant byte de Hi_threshold 
ADC_Lo_threshLSB= 0x00		#Less significant byte de Lo_threshold
ADC_conf_inicialMSB= 0x43	#More significant byte de configuracion inicial del ADC ADS1115
ADC_conf_inicialLSB= 0xE8 	#Less significant byte de configuracion inicial del ADC ADS1115

#VARIABLES DE USO GENERAL
#Para Flanger (Inicializacion)
delay= int(500) #Delay maximo del flanger
depth= int(400) #Delay maximo real. Amplitud del LFO
lfo_freq= 0.9   #Frecuencia del LFO
feedback= 0.3   #Ganancia de la retroalimentacion de Flanger
wet_dry= 0.5    #Ganancia de muestra retardada (1-wet_dry para muestra actual)

#Para operación de la conversion analogica-digital 
conv_lock= 0                                    #Bloqueo de conversion (Conversion lock) Bloquea o permite que se lleve a cabo una conversion
ch_conv_actual= 0                               #Canal de conversion actual: Indice para seleccionar canal de conversion ADC (0-4) para callback en ejecucion
ch_conv_req= [0xC3, 0xD3, 0xE3, 0xF3, 0xC3]		#Requiscion de canal de conversion. Byte mas significativo del registro de configuracion para solicitar conversion por cada canal
conv_mem= [0,0,0,0,0]                           #Memoria de conversion. Vector con valores de conversiones previas 
margen_sens= 500                                #Margen de sensibilidad. Margen minimo para aceptar nuevo valor de conversion de parametro de usuario
exe_cont= 0										#Contador de ejecuciones de la funcion de callback
exe_p_conv= 13                                  #Ejecuciones para conversion: Determina cada cuantas ejecuciones de callback se solicita una nueva conversion
exe_p_lect= 6                                   #Ejecuciones para lectura: Determina cuantas ejecuciones de callback despues de la conversion ocurren para leerla

#BLOQUE DE INICIALIZACION DE ENTRADAS E I2C
#Inicializacion de instancia de I2C en libreria SMBUS
I2C_BUS= 1                  #En raspberry pi, usualmente se usa el bus 1 de I2C
bus= smbus2.SMBus(I2C_BUS)  #Nombre de la instanciacion

#Configuracion de puertos GPIO
#GPIO.setmode(GPIO.BCM)      #Para usar la numeracion de pines GPIO BCM

#ALERT/RDY ADC ch 0-3
conversion_flag0= 26    #GPIO usado como ALERT/RDY input del ADS1115 ch del 0 al 3
#para usar resistencia pull down interna, ALERT/RDY como entrada logica
gpio_conversion_flag0=InputDevice(conversion_flag0, pull_up=False)

#ALERT/RDY ch 4
conversion_flag1= 21    #GPIO usado como ALERT/RDY input del ADS1115 ch 4
#para usar resistencia pull down interna, ALERT/RDY como entrada logica
gpio_conversion_flag1=InputDevice(conversion_flag1, pull_up=False)

#Selector del filtro y bypass de flanger
flanger_bypass_sel= 5   #GPIO Input para seleccionar flanger
lowpass_sel= 6          #GPIO Input para seleccionar filtro pasa-bajas
bandpass_sel= 13        #GPIO Input para seleccionar filtro pasa-banda
highpass_sel= 19        #GPIO Input para seleccionar filtro pasa-altas
#Selectores como entradas con resistencia pull down interna
GPIO.setup(flanger_bypass_sel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Selectores 
GPIO.setup(lowpass_sel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(bandpass_sel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(highpass_sel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

#BLOQUE DE CONFIGURACION DEL CONVERTIDOR ANALOGICO-DIGITAL
#Ambos dispositivos ADC ADS1115 se configuran con la siguiente palabra en el registro config_register (0x01): 01000011 11101000 (0x43E8)
#Lo anterior conlleva:
#Power-down state
#Usar de inicio el canal 1 del ADC
#Rango de conversion de +/- 4V
#Modo single-shot
#860 sps (max)
#flag de conversion en pin ALERT/RDY en logica positiva
bus.write_i2c_block_data(ADC_ch_0_3_dir, ADC_conf_reg_dir, [ADC_conf_inicialMSB, ADC_conf_inicialLSB])
bus.write_i2c_block_data(ADC_ch_4_dir, ADC_conf_reg_dir, [ADC_conf_inicialMSB, ADC_conf_inicialLSB])

#Seguidamente se configuran los registros threshold de ambos ADS1115 para operar el pin ALERT/RDY como flag de conversion ready
bus.write_i2c_block_data(ADC_ch_0_3_dir, ADC_Hi_thresh_dir, [ADC_Hi_threshMSB, ADC_Hi_threshLSB])
bus.write_i2c_block_data(ADC_ch_0_3_dir, ADC_Lo_thresh_dir, [ADC_Lo_threshMSB, ADC_Lo_threshLSB])
bus.write_i2c_block_data(ADC_ch_4_dir, ADC_Lo_thresh_dir, [ADC_Lo_threshMSB, ADC_Lo_threshLSB])
bus.write_i2c_block_data(ADC_ch_4_dir, ADC_Hi_thresh_dir, [ADC_Hi_threshMSB, ADC_Hi_threshLSB])

#BLOQUE DE FUNCIONES
#Funcion de normalizacion de lectura del ADC
def norm_conv (lectura):
    global conv_mem

    resultado= ((lectura & 0xFF)<<8) | (lectura>>8) #se invierten los bytes de la lectura de conversion del ADC
    if resultado>= 0x8000: #se descartan lecturas de ADC menores a 0V
        resultado= 0
    
    #La siguiente condicion asegura que el resultado obtenido supera el margen minimo para considerarse un cambio en el parametro por el usuario
    if resultado-margen_sens <= conv_mem[ch_conv_actual] <= resultado+margen_sens:
        resultado= conv_mem[ch_conv_actual]
    else:
        conv_mem[ch_conv_actual]= resultado

    resultado /= 26485  #Se divide la lectura para normalizarse entre 0 y 1

    return(resultado)

#Funcion para leer conversion del ADC_0 
def ADC0_reading():
    global delay, depth, lfo_freq, feedback, conv_lock, ch_conv_actual

    lectura= bus.read_word_data(ADC_ch_0_3_dir, ADC_conv_reg_dir) #lectura de la conversion del ADC de forma "cruda"
    resultado= norm_conv(lectura)   #Se normaliza la conversion

    #Selectores de variable para modificar parametros de flanger
    if(ch_conv_actual==0):
        delay= int(resultado*1024)      #Retardo maximo absoluto
    elif(ch_conv_actual==1):
        depth= int(resultado*delay)     #Retardo maximo real
    elif(ch_conv_actual==2):
        lfo_freq= 0.01+(resultado*.99)  #Frecuencia de LFO
    else:
        feedback= resultado*0.9         #Ganancia de retroalimentacion
    
    ch_conv_actual += 1 #Se actualiza la siguiente eleccion de canal a convertir
    conv_lock= 0        #Se deshabilita el bloqueo de conversion

#Funcion para leer conversion del ADC_1
def ADC1_reading():
    global  wet_dry, conv_lock, ch_conv_actual

    lectura= bus.read_word_data(ADC_ch_4_dir, ADC_conv_reg_dir)	#lectura de la conversion del ADC de forma "cruda"
    wet_dry= norm_conv(lectura)   #Se normaliza la conversion y se asgina a parametro wet_dry

    ch_conv_actual= 0   #Se reinicia la seleccion de canal
    conv_lock= 0        #Se deshabilita el bloqueo de conversion

def funcion_callback():
    global  conv_lock, exe_cont, ch_conv_actual 
    
    #Solicitud de conversion. Se ejecuta si no hay una conversion previa pendiente de lectura y si exe_cont esta en 0
    if(conv_lock== 0 and exe_cont==0):
        #Solicitud de conversion para el ADC0
        if(ch_conv_actual<4):
            bus.write_i2c_block_data(ADC_ch_0_3_dir, ADC_conf_reg_dir, [ch_conv_req[ch_conv_actual], ADC_conf_inicialLSB])
        #Solicitud de conversion del ADC1
        else:
            bus.write_i2c_block_data(ADC_ch_4_dir, ADC_conf_reg_dir, [ch_conv_req[ch_conv_actual], ADC_conf_inicialLSB])
        conv_lock= 1    #Se activa el bloqueo de conversion
    
    #Solicitud de lectura en caso de que hayan pasado 'exe_p_lect' ejecuciones de callback despues de la solicitud de conversion
    if (exe_cont== exe_p_lect):
        #Solicitud de lectura del ADC0
        if (gpio_conversion_flag0.is_active and ch_conv_actual<4):
            ADC0_reading()
        #Solicitud de lectura del ADC1
        if (gpio_conversion_flag1.is_active and ch_conv_actual==4 and conv_lock==1):
            ADC1_reading()
    
    #Se aumenta el contador de ejecuciones de callback. Se reinicia si alcanza el valor de reset exe_p_conv
    exe_cont= (exe_cont+1)%exe_p_conv

    print(f"Parametro Delay: ", delay)
    print(f"Parametro Depth: ", depth)
    print(f"Parametro LFO Frecuency: ", lfo_freq)
    print(f"Parametro Feedback: ", feedback)
    print(f"Parametro Wet/Dry: ", wet_dry)
        
    