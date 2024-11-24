import smbus2
import RPi.GPIO as GPIO
import time
import array

#VARIABLES DEL CONVERTIDOR ANALOGICO-DIGITAL
ADC_ch_0_3_dir= 0x49		#Direccion de dispositivo I2C, ADC ADS1115 para canales del 0 al 3 
ADC_ch_4_dir= 0x48  		#Direccion de dispositivo I2C, ADC ADS1115 para canal 4
ADC_conf_reg_dir= 0x01		#Direccion interna de ADC ADS1115 de configuration register
ADC_Hi_thresh_dir= 0x03		#Direccion interna de ADC ADS1115 de High Threshold Register
ADC_Lo_thresh_dir= 0x02		#Direccion interna de ADC ADS1115 de Low Threshold Register
ADC_conv_reg_dir= 0x00		#direccion interna de ADC ADS1115 de Conversion register
ADC_Hi_threshMSB= 0x80		#More significant byte de Hi_threshold 
ADC_Lo_threshMSB= 0x00		#More significant byte de Lo_threshold
ADC_Hi_threshLSB= 0x02		#Less significant byte de Hi_threshold 
ADC_Lo_threshLSB= 0x01		#Less significant byte de Lo_threshold
ADC_conf_inicialMSB= 0x43	#More significant byte de configuracion inicial del ADC ADS1115
ADC_conf_inicialLSB= 0xE8 	#Less significant byte de configuracion inicial del ADC ADS1115

#Se definen las variables de parametros de Flanger
delay= int(500) #Delay maximo del flanger
depth= int(400) #Delay maximo real. Amplitud del LFO
lfo_freq= 0.9   #Frecuencia del LFO
feedback= 0.3   #Ganancia de la retroalimentacion de Flanger
wet_dry= 0.5    #Ganancia de muestra retardada (1-wet_dry para muestra actual)

conv_lock= 0                                    #Define si se lleva cabo una solicitud de conversion en la funcion de callback (procesamiento) en ejecucion
ch_conv_actual= 1                               #Indice para seleccionar canal de conversion ADC (0-4)
ch_conv_req= [0xC3, 0xD3, 0xE3, 0xF3, 0xC3]		#valores de MSB del registro de configuracion para solicitar conversion por cada canal
    
#CONFIGURACION DE PUERTOS GPIO
#ALERT/RDY ADC ch 0-3
conversion_flag0= 26 #GPIO usado como ALERT/RDY input del ADS1115 ch del 0 al 3
GPIO.setup(conversion_flag0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #para usar resistencia pull down interna, ALERT/RDY como entrada logica

#ALERT/RDY ch 4
conversion_flag1= 21 #GPIO usado como ALERT/RDY input del ADS1115 ch 4
GPIO.setup(conversion_flag1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #para usar resistencia pull down interna, ALERT/RDY como entrada logica

#BLOQUE DE INICIALIZACION Y CONFIGURACION
#Inicializacion de instancia de i2c en libreria SMBUS
I2C_BUS= 1 #En raspberry pi, usualmente se usa el bus 1 de I2C
bus= smbus2.SMBus(I2C_BUS)  #Nombre de la instanciacion

GPIO.setmode(GPIO.BCM)  #Para usar la numeracion de pines GPIO BCM

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

#Funcion de normalizacion de lectura del ADC
def norm_conv (lectura):
    resultado= ((lectura & 0xFF)<<8) | (lectura>>8) #se invierten los bytes de la lectura de conversion del ADC
    if resultado>= 0x8000: #se descartan lecturas de ADC menores a 0V
        resultado= 0
    resultado /= 26385  #Se divide la lectura para normalizarse entre 0 y 1

    return(resultado)

#Funcion callback para leer conversion del ADC_0 
def ADC0_reading(channel):
    global delay, depth, lfo_freq, feedback, conv_lock

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
    
    conv_lock= 0    #Se deshabilita el bloqueo de conversion

def ADC1_reading(channel):
    global  wet_dry, conv_lock

    lectura= bus.read_word_data(ADC_ch_4_dir, ADC_conv_reg_dir)	#lectura de la conversion del ADC de forma "cruda"
    wet_dry= norm_conv(lectura)   #Se normaliza la conversion y se asgina a parametro wet_dry

    conv_lock= 0    #Se deshabilita el bloqueo de conversion

#Esta funcion actualiza los valores del vector de parametros del flanger mediante la conversion en todos los canales de ambos ADS1115
def obtener_param():
    #Iteracion para convertir en los 5 canales analogicos
    for i in range(5):	
        #Para canales del 0 al 3
        if i<4:
            while GPIO.input(conversion_flag0)== GPIO.LOW: #espera para la conversion
                time.sleep(0.002)
            #Para canal 4
        else:
            while GPIO.input(conversion_flag1)== GPIO.LOW:	#espera para la conversion
                time.sleep(0.002)
            
        flanger_param[i]= resultado #asignacion de lectura del ADC a elemento del vector
    return 0

#Se definen las detecciones de evento de los flags de conversion de cada ADC
GPIO.add_event_detect(conversion_flag0, GPIO.RISING, callback=ADC0_reading)
GPIO.add_event_detect(conversion_flag1, GPIO.RISING, callback=ADC1_reading)

for _ in range (20):

    #Solicitud de conversion. Se ejecuta si no hay una conversion previa pendiente de lectura
    if(conv_lock== 0):
        if(ch_conv_actual<4):
            #Solicitud de conversion al ADC_0 para el canal especificado por ch_conv_actual
            bus.write_i2c_block_data(ADC_ch_0_3_dir, ADC_conf_reg_dir, [ch_conv_req[ch_conv_actual], ADC_conf_inicialLSB]) #solicitud de conversion
        else:
            #Solicitud de conversion al ADC_1 para el canal especificado por ch_conv_actual
            bus.write_i2c_block_data(ADC_ch_4_dir, ADC_conf_reg_dir, [ch_conv_req[ch_conv_actual], ADC_conf_inicialLSB]) #solicitud de conversion
        conv_lock= 1

    print(f"Parametro Delay:")
        
    time.sleep(1)
