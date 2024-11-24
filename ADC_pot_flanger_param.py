import smbus2
import RPi.GPIO as GPIO
import time
import array

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

#Inicializacion de instancia de i2c en libreria SMBUS
I2C_BUS= 1 #En raspberry pi, usualmente se usa el bus 1 de I2C
bus= smbus2.SMBus(I2C_BUS)

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

#definicion de vector de resultado de conversion del ADC
flanger_param= array.array('H', [0, 0, 0, 0, 0])

#Configura un puerto GPIO como entrada para apagar el ciclo while de programa principal
GPIO.setmode(GPIO.BCM) #Configura el modo GPIO
control_input= 19  #GPIO usado como entrada de control
GPIO.setup(control_input, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #para usar resistencia pull down interna, control input como entrada logica

#ALERT/RDY ADC ch 0-3
conversion_flag0= 26 #GPIO usado como ALERT/RDY input del ADS1115 ch del 0 al 3
GPIO.setup(conversion_flag0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #para usar resistencia pull down interna, ALERT/RDY como entrada logica

#ALERT/RDY ch 4
conversion_flag1= 21 #GPIO usado como ALERT/RDY input del ADS1115 ch 4
GPIO.setup(conversion_flag1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #para usar resistencia pull down interna, ALERT/RDY como entrada logica

#Esta funcion actualiza los valores del vector de parametros del flanger mediante la conversion en todos los canales de ambos ADS1115
def obtener_param():
    ch_conv_req= [0xC3, 0xD3, 0xE3, 0xF3, 0xC3]		#valores de MSB del registro de configuracion para solicitar conversion por cada canal
    #Iteracion para convertir en los 5 canales analogicos
    for i in range(5):	
        #Para canales del 0 al 3
        if i<4:
            bus.write_i2c_block_data(ADC_ch_0_3_dir, ADC_conf_reg_dir, [ch_conv_req[i], ADC_conf_inicialLSB]) #solicitud de conversion
            while GPIO.input(conversion_flag0)== GPIO.LOW: #espera para la conversion
                time.sleep(0.002)
            lectura= bus.read_word_data(ADC_ch_0_3_dir, ADC_conv_reg_dir) #lectura de la conversion
        #Para canal 4
        else:
            bus.write_i2c_block_data(ADC_ch_4_dir, ADC_conf_reg_dir, [ch_conv_req[i], ADC_conf_inicialLSB]) #solicitud de conversion
            while GPIO.input(conversion_flag1)== GPIO.LOW:	#espera para la conversion
                time.sleep(0.002)
            lectura= bus.read_word_data(ADC_ch_4_dir, ADC_conv_reg_dir)	#lectura de la conversion
        resultado= ((lectura & 0xFF)<<8) | (lectura>>8) #se invierten los bytes de la lectura de conversion del ADC
        if resultado>= 0x8000: #se descartan lecturas de ADC menores a 0V
            resultado= 0
        flanger_param[i]= resultado #asignacion de lectura del ADC a elemento del vector
    return 0


while GPIO.input(control_input)== GPIO.LOW:
    obtener_param()	#se solicita actualizar el vector de parametros por medio de conversiones AD
    for i in range(len(flanger_param)):
        print(f"Parametro de flanger {i}: {flanger_param[i]}")
        
    time.sleep(1)
