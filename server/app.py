from flask import Flask, request, jsonify
from flask_cors import CORS
import RPi.GPIO as GPIO
import sys
import time
import threading

#LCD
from RPLCD.i2c import CharLCD

lcd = None

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# ----------------------------VARIABLES ----------------------


# Lista para almacenar el estado de los LEDs
leds = []

# Variable para almacenar el estado del motor
estado_motor = None
estado_servo= None

#velocidad servomotor
pwm = None

#variables laser 
luz_recibida1 = None
luz_recibida2 = None
luz_exterior = False
alarmaEncendida = False


#variables LCD
nombres_habitaciones = [
    "Recepcion",
    "Administracion",
    "Bano",
    "Conferencia",
    "Area de Descarga",
    "Patio",
    "Cafeteria",
    "Bodega"
]

cuarto_luz = None


pantalla = CharLCD('PCF8574', 0x27, auto_linebreaks=True)

# Tipo de configuracion de los puertos
GPIO.setmode(GPIO.BOARD)

# Desactivamos alertas de GPIO
GPIO.setwarnings(False)



# ------------------------- DECLARACION DE PUERTOS---------------------------


#MOTOR STEPPER 
#el pin 11 a 13 no se estan usan
LED1 = 11
MOTOR = 13
# LED verde es el pin 29 con GPIO 5
# LED Roja es el pin 16 con GPIo 23
PIN_IN1_STEPPER = 31
PIN_IN2_STEPPER = 33
PIN_IN3_STEPPER = 35
PIN_IN4_STEPPER = 37
PIN_IN5_LEDGREEN = 29
PIN_IN6_LEDRED = 16

#LUCES CUARTOS
PIN_A = 18
PIN_B = 22
PIN_C = 23

#SERVOMOTOR
PIN_SERVO = 12

# LASER 

PIN_LASER = 38 #GPIO20

# fotoresistencia
PIN_F1 = 11 # GPIO17 
PIN_F2 = 21 # GPIO19

# buzzer
PIN_BUZZER = 40 #GPIO21

# Luz externa
PIN_LEDf = 36 #GPIO16


# ---- Sensor yair ------
# Configurar los pines GPIO para los bits binarios
bit0 = 8  # Pin 11 en la Raspberry Pi GPIO 14
bit1 = 32 # Pin 12 en la Raspberry Pi GPIO 12
bit2 = 7   # Pin 13 en la Raspberry Pi GPIO 4
bit3 = 10  # Pin 15 en la Raspberry Pi GPIO 15


# Configurar los pines GPIO para el sensor ultras�nico
TRIG = 13  # Pin 16 en la Raspberry Pi GPIO 27
ECHO = 15  # Pin 18 en la Raspberry�Pi�GPIO�22

#Numero de puertos motor stepper utilizados para su programacion
StepPins = [PIN_IN1_STEPPER,PIN_IN2_STEPPER,PIN_IN3_STEPPER,PIN_IN4_STEPPER]


#Secuencia de movimiento stepper
Seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]

StepCount = len(Seq)
StepDir = 1 # Colocar 1 o 2 para sentido horario
            # Colocar -1 o -2 para sentido antihorario

# Initialise variables
StepCounter = 0

# ------------------ CONFIGURACIONES ----------------------


# Read wait time from command line
if len(sys.argv)>1:
  WaitTime = int(sys.argv[1])/float(1000)
else:
  WaitTime = 5/float(1000)

# Control de los hilos
running = False
pause = threading.Event()
pause.set()
iniciar_stepper = True

# Control creacion de api
crear = True

#---------------------FUNCIONES SENSOR --------------------------

def get_distance():
    # Enviar pulso TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Medir el tiempo de inicio y final del pulso ECHO
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calcular la duraci�n del pulso
    pulse_duration = pulse_end - pulse_start

    # Calcular la distancia
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

number = 0

def loop():
    # Funciones del ultrasonico
    var1 = 0
    global number
    while True:
        # Obtener la distancia medida por el sensor ultras�nico
        distance = get_distance()
        print('Persona detectada')
        print(f"Distancia: {distance} cm")

        # Incrementar o decrementar el contador seg�n la distancia medida
        if distance >= 0 and distance <= 7:
            number += 1
            if number > 9:
                number = 0
        elif distance > 7 and distance <= 14:
            if number > 0:
                number -= 1

        # Enviar el numero actual en formato binario a los pines
        GPIO.output(bit0, number & 0b0001)
        GPIO.output(bit1, number & 0b0010)
        GPIO.output(bit2, number & 0b0100)
        GPIO.output(bit3, number & 0b1000)

        # Esperar un poco para evitar m�ltiples cambios por una sola detecci�n
        time.sleep(1)


#Funciones LCD


def inicializar_lcd(i2c_addr):
    
    return CharLCD('PCF8574', i2c_addr, auto_linebreaks=True)


def mostrar_bienvenida(lcd):
    
    try:
        lcd.clear()
        lcd.write_string("<GRUPO7_ARQUI1>")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("<VACAS_JUN_2024>")
        time.sleep(10)
        lcd.clear()
        return "Mensaje de bienvenida mostrado en la pantalla LCD."
    except Exception as e:
        return str(e)




def mostrar_estado_luces_ciclico(luz):
    estados = []
    for i in range(len(nombres_habitaciones)):
        if i == luz:
            estados.append(f"{nombres_habitaciones[i]} on")
        else:
            estados.append(f"{nombres_habitaciones[i]} off")

    try:
        mensaje = ""
        # Mostrar todos los estados en orden cíclico
        for habitacion in estados:
            mensaje += habitacion + "-> "

        mensaje = mensaje.rstrip(" -> ")  # Eliminar la flecha al final
        

        lcd.clear()
        lcd.write_string(mensaje)
        time.sleep(0.5)

        print(mensaje)
        return "Información de luces actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)

def mostrar_estado_Banda(estado_banda):
    

    try:
        mensaje = "Estado Banda: " + estado_banda

        lcd.clear()
        lcd.write_string(mensaje)
        time.sleep(0.5)
        print(mensaje)
        return "Información de bandas actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)

def mostrar_estado_porton(estado_porton):
    

    try:
        mensaje = "Estado Porton: " + estado_porton

        lcd.clear()
        lcd.write_string(mensaje)
        time.sleep(0.5)

        print(mensaje)
        return "Información del porton actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)
    
def mostrar_estado_alarma(estado_alarma):

    try:
        mensaje = "Estado Alarma: " + estado_alarma

        lcd.clear()
        lcd.write_string(mensaje)
        time.sleep(0.5)
        print(mensaje)


        return "Información de alarma actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)

def mostrar_estado_sensor(estado_persona):

    try:
        mensaje = "Persona: " + estado_persona
        lcd.clear()
        lcd.write_string(mensaje)
        time.sleep(0.5)
        print(mensaje)

        return "Información de alarma actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)

def mostrar_estado_foto(luzexterior):

    try:
        mensaje = "Luz exterior: " + luzexterior 
        lcd.clear()
        lcd.write_string(mensaje)
        time.sleep(0.5)

        print(mensaje)
        return "Información de alarma actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)


# --------- Funciones Laser --------------------


def estado_luz_exterior():
    global luz_exterior
    
    if luz_exterior:
        GPIO.output(PIN_LEDf, GPIO.HIGH)
        mostrar_estado_foto("Encendida")
    
    else:
        GPIO.output(PIN_LEDf, GPIO.LOW)
        mostrar_estado_foto("apagada")
        
    
    
def laser():
    global luz_recibida2
    global alarmaEncendida
    
    GPIO.output(PIN_LASER, GPIO.HIGH)
    
    while True:
        luz_recibida2 = GPIO.input(PIN_F2)

        if luz_recibida2:
            GPIO.output(PIN_BUZZER, GPIO.HIGH)
            mostrar_estado_alarma("Activada")
            alarmaEncendida = True

        else:
            GPIO.output(PIN_BUZZER, GPIO.LOW)
            mostrar_estado_alarma("Desactivada")
            alarmaEncendida = False

        time.sleep(1)

        

def fotoresistencia1():
    global luz_recibida1
    global luz_exterior
    
    while True:
        luz_recibida1 = GPIO.input(PIN_F1)
        print(luz_recibida1)
        if luz_recibida1:
            GPIO.output(PIN_LASER, GPIO.HIGH)
            GPIO.output(PIN_LEDf, GPIO.HIGH)
            luz_exterior = True
            laser()
            

        else:
            luz_exterior = False
            GPIO.output(PIN_LASER, GPIO.LOW)
            GPIO.output(PIN_LEDf, GPIO.LOW)

        time.sleep(1) # Espera 5 segundos antes de repetir


def hilo_fotoresistencia():
    hilo = threading.Thread(target=fotoresistencia1)
    hilo.start()
    

#LUCES CUARTOS
def decimal_to_binary(decimal):
    print("recibido "+ str(decimal))
    binary = format(int(decimal), '03b')
    return [int(bit) for bit in binary]

def set_demultiplexer(value):
    binary_value = decimal_to_binary(value)
    GPIO.output(PIN_A, binary_value[0])
    GPIO.output(PIN_B, binary_value[1])
    GPIO.output(PIN_C, binary_value[2])
    mostrar_estado_luces_ciclico(value)


#Funcion para activar el servo motor
def init_servo(pin, frequency=50):
    global pwm
    """
    Inicializa el servo motor en el pin especificado con la frecuencia dada.
    """
    if pwm is not None:
        pwm.stop()
        GPIO.cleanup(pin)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, frequency)
    pwm.start(0)
    return pwm

def move_servo(pwm, angle):
    """
    Mueve el servo motor al �ngulo especificado.
    """
    duty_cycle = angle / 18.0 + 2.5
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(50)  # Aumentar el tiempo para asegurar que el servo se mueva
    #pwm.ChangeDutyCycle(duty_cycle)  # Mant�n el pulso activo para asegurar el movimiento
    #time.sleep(0.5)  # Asegurar tiempo suficiente para que el servo se mueva completamente
    pwm.ChangeDutyCycle(0)  # Detener el pulso para no mantener el servo en movimiento

def stop_servo(pwm):
    """
    Detiene el servo motor.
    """
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    GPIO.cleanup()

def activar_motor_stepper():
    global StepCount
    global StepCounter
    while running:
        pause.wait()  # Pausar el hilo si se desactiva el evento
        #print(StepCounter)
        #print(Seq[StepCounter])

        for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin] != 0:
                #print("Enable GPIO %i" % xpin)
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        StepCounter += StepDir

        # Si llegamos al final de la secuencia, empezar de nuevo
        if StepCounter >= StepCount:
            StepCounter = 0
        if StepCounter < 0:
            StepCounter = StepCount + StepDir

        time.sleep(WaitTime)

def start_motor():
    global running
    if not running:
        running = True
        threading.Thread(target=activar_motor_stepper, daemon=True).start()
        print("Motor iniciado")

def stop_motor():
    global running
    running = False
    print("Motor detenido")
    


def pause_motor():
    pause.clear()
    print("Motor pausado")

def resume_motor():
    pause.set()
    print("Motor reanudado")
    
    

@app.route('/api/activarLed', methods=['POST'])
def activar_led():
    global leds
    data = request.json
    cuarto = data.get('cuarto')
    estado = data.get('estado')

    if not isinstance(cuarto, int) or not isinstance(estado, int):
        return jsonify({"error": "Los parámetros 'cuarto' y 'estado' deben ser numéricos"}), 400

    # Buscar si el cuarto ya existe en la lista
    found = False
    for led in leds:
        if led['cuarto'] == cuarto:
            led['estado'] = estado
            found = True
            break
    
    if not found:
        leds.append({"cuarto": cuarto, "estado": estado})
    
    return jsonify({"mensaje": "Estado del LED actualizado correctamente"}), 200

@app.route('/api/verEstadoLED', methods=['GET'])
def ver_estado_led():
    global leds
    cuarto = request.args.get('cuarto', type=int)

    if cuarto is None:
        return jsonify({"error": "El parámetro 'cuarto' es necesario y debe ser numérico"}), 400

    for led in leds:
        if led['cuarto'] == cuarto:
            return jsonify({"cuarto": cuarto, "estado": led['estado']}), 200
    
    return jsonify({"error": "Cuarto no encontrado"}), 404

#MOTOR STEPPER
@app.route('/api/activarMotor', methods=['POST'])
def activar_motor():
    global estado_motor
    global iniciar_stepper
    data = request.json
    estado = data.get('estado')

    if not isinstance(estado, int):
        return jsonify({"error": "El parámetro 'estado' debe ser numérico"}), 400

    estado_motor = estado
     #Codigo para activar motor
    if estado_motor == 1:
        start_motor()
        print("Motor activado")
        GPIO.output(PIN_IN5_LEDGREEN, 1)
        GPIO.output(PIN_IN6_LEDRED,   0)
        mostrar_estado_Banda("ACTIVADO")
    else:
        stop_motor()
        print("Motor detenido")
        GPIO.output(PIN_IN5_LEDGREEN, 0)
        GPIO.output(PIN_IN6_LEDRED,   1)
        mostrar_estado_Banda("DESACTIVADO")
    
        
    #Tambien la opcion de detener totalmente el motor pero hay que inicializar de nuevo
    #Es con la siguiente linea
    #stop_motor()
    
    return jsonify({"mensaje": "Estado del motor actualizado correctamente"}), 200

#SERVOMOTOR
@app.route('/api/activarServoMotor', methods=['POST'])
def activar_servomotor():

    global estado_servo
    global pwm
    
    data = request.json
    estado = data.get('estado')
    pwm = init_servo(PIN_SERVO)
    angle = 90

    if not isinstance(estado, int):
        return jsonify({"error": "El par�metro 'estado' debe ser num�rico"}), 400

    estado_servo = estado
     #Codigo para activar motor
    if estado_servo == 1:
        move_servo(pwm, angle)
        print("Motor activado")
        print(PIN_SERVO)
        mostrar_estado_porton("ABIERTO")

    else:
        angle = 0
        move_servo(pwm, angle)
        print("Puerta cerrada")
        print(PIN_SERVO)
        mostrar_estado_porton("CERRADO")
    
        
    #Tambien la opcion de detener totalmente el motor pero hay que inicializar de nuevo
    #Es con la siguiente linea
    #stop_motor()999999999999
    
    return jsonify({"mensaje": "Estado del motor actualizado correctamente"}), 200
   

    



#LASER


@app.route('/api/Luz_Exterior', methods=['POST'])
def handle_data4():

    data = request.json
    print(data)
    global luz_exterior
# Aquí puedes hacer lo que necesites con la variable 'selected_area'
    estado_luz = data.get('estado')

    print(estado_luz)

    if estado_luz == 1:
        luz_exterior= True
        estado_luz_exterior()
    else:
        luz_exterior= False
        estado_luz_exterior()
    
    return jsonify({'error': 'informacion no proporcionada'}), 400

@app.route('/api/estado_Luz_exterior', methods=['GET'])
def handle_data_5():
    global luz_exterior
    luz = luz_exterior
    if luz_exterior is None:
        return jsonify({"error": "El estado de la luz no ha sido configurado a�n"}), 404
    
    return jsonify({"estado_luz exterior": luz}), 200   

# --- metodo get para la alarma
@app.route('/api/estado_alarma', methods=['GET'])
def handle_data_6():

    global alarmaEncendida
    alarmaEncendida = True

    if alarmaEncendida:
        alarma = "Alarma Encendida"
    else:
        alarma = "Alarma Desactivada"


    if alarmaEncendida is None:
        return jsonify({"error": "El estado de la alarma no ha sido configurado aun"}), 404
    
    return jsonify({"estado_alarma_exterior": alarma}), 200   

    

# LUCES
@app.route('/api/onLED', methods=['POST'])
def handle_data():
    data = request.json
    # Aquí puedes hacer lo que necesites con la variable 'selected_area'
    selected_area = data.get('index')
    if selected_area is not None:

        set_demultiplexer(int(selected_area))
        print("Área seleccionada:", selected_area)


        
        return jsonify({'message': 'Datos recibidos correctamente'})
        

    return jsonify({'error': 'indice no proporcionado'}), 400

@app.route('/api/offLED', methods=['POST'])
def handle_data_1():
    data = request.json
    selected_area = data.get('area')
    # Aquí puedes hacer lo que necesites con la variable 'selected_area'
    print("Área seleccionada:", selected_area)
    print("Área seleccionada se apaga:", selected_area)
    return 'Datos recibidos correctamente'

# SENSOR


@app.route('/api/contador_personas', methods=['GET'])
def handle_data7():
    # Devuelve el numero actual de personas detectadas.
    
    global number
    number = 9
    cantidadClientes = number
    if  number is None:
        return jsonify({"error": "El contador no esta configurado."}), 404
    
    return jsonify({"contador_personas": cantidadClientes}), 200


#Codigo que se ejecuta solo una vez
def setup():
    #Declaracion de GPIO input o output
    #GPIO.setup(LED1, GPIO.OUT)
    
    # ---- MOTORES ----
    GPIO.setup(MOTOR, GPIO.OUT)

    # LEDS DEL MOTOR STEPPER
    GPIO.setup(PIN_IN5_LEDGREEN, GPIO.OUT)
    GPIO.setup(PIN_IN6_LEDRED, GPIO.OUT)
    
    #MOTOR STEPPER
    GPIO.setup(PIN_IN1_STEPPER,GPIO.OUT)
    GPIO.setup(PIN_IN2_STEPPER,GPIO.OUT)
    GPIO.setup(PIN_IN3_STEPPER,GPIO.OUT)
    GPIO.setup(PIN_IN4_STEPPER,GPIO.OUT)

    # ---- LUCES CUARTOS ----
    GPIO.setup(PIN_A, GPIO.OUT)
    GPIO.setup(PIN_B, GPIO.OUT)
    GPIO.setup(PIN_C, GPIO.OUT)

    # ---- SERVOMOTOR ----
    GPIO.setup(PIN_SERVO, GPIO.OUT)
    
     # ---- LASER ----
    GPIO.setup(PIN_LASER, GPIO.OUT)
    GPIO.setup(PIN_LEDf, GPIO.OUT)
    GPIO.setup(PIN_BUZZER, GPIO.OUT)
    GPIO.setup(PIN_F1, GPIO.IN)
    GPIO.setup(PIN_F2, GPIO.IN)


    # ---- LASER ----
    GPIO.setup(PIN_LASER, GPIO.OUT)
    GPIO.setup(PIN_LEDf, GPIO.OUT)
    GPIO.setup(PIN_BUZZER, GPIO.OUT)
    GPIO.setup(PIN_F1, GPIO.IN)
    GPIO.setup(PIN_F2, GPIO.IN)
    
    # --- PANTALLA LCD ---
    # Mostrar mensaje de bienvenida durante 10 segundos
    
    global lcd
    pantalla = mostrar_bienvenida(lcd)
    

    # ----- Iniciar apagados los puertos -------
    #GPIO.output(LED1, 0)
    GPIO.output(MOTOR, 0)
    #Iniciar apagados los puertos
    GPIO.output(PIN_IN1_STEPPER,0)
    GPIO.output(PIN_IN2_STEPPER,0)
    GPIO.output(PIN_IN3_STEPPER,0)
    GPIO.output(PIN_IN4_STEPPER,0)
    GPIO.output(PIN_IN5_LEDGREEN,0)
    GPIO.output(PIN_IN6_LEDRED, 1)

    # ----- Sensor YAIR  set mode y output------

    # Inicializar el pin TRIG en bajo
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(2)  


    hilo_fotoresistencia()



 




try:

    
    while True:
        time.sleep(1)  # Mantener el hilo principal dormido

        if crear == True:
            if __name__ == '__main__':
                setup()
                
                crear = False
                app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
        
except KeyboardInterrupt:
        running = False
        GPIO.cleanup()