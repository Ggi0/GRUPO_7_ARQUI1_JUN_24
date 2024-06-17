from flask import Flask, request, jsonify
from flask_cors import CORS
import RPi.GPIO as GPIO
import sys
import time
import threading
from RPLCD.i2c import CharLCD

# * Initialize Flask app
app = Flask(__name__)

# * Enable CORS for all routes of the app 
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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

#Declaracion de puerto GPIO
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

# ---------- LASER -----------
# laser
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
bit0 = 14  # Pin 11 en la Raspberry Pi GPIO 14
bit1 = 12  # Pin 12 en la Raspberry Pi GPIO 12
bit2 = 4   # Pin 13 en la Raspberry Pi GPIO 4
bit3 = 15  # Pin 15 en la Raspberry Pi GPIO 15

# Configurar los pines GPIO para el sensor ultrasónico
TRIG = 27  # Pin 16 en la Raspberry Pi GPIO 27
ECHO = 22  # Pin 18 en la Raspberry Pi GPIO 22



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
#asd

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

def mostrar_estado_luces_ciclico(lcd, luz):
    habitaciones = nombres_habitaciones.copy()
    habitaciones[habitaciones.index(luz)] = f"Luz_{luz}:ON"

    try:
        mensaje = ""
        # Mostrar todos los estados en orden cíclico
        for habitacion in habitaciones:
            mensaje += habitacion + " -> OFF"

        mensaje = mensaje.rstrip(" -> ")  # Eliminar la flecha al final
        lcd.clear()
        lcd.write_string(mensaje)
        return "Información de luces actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)

def mostrar_estado_Banda(banda_activada):
    bandas = banda_activada.copy()
    index_activada = bandas.index("1")
    bandas[index_activada] = f"Banda_{index_activada}:ON"

    try:
        mensaje = ""
        # Mostrar todos los estados en orden cíclico
        for i, banda in enumerate(bandas):
            mensaje += banda + " -> OFF"

        mensaje = mensaje.rstrip(" -> ")  # Eliminar la flecha al final
        lcd.clear()
        lcd.write_string(mensaje)
        return "Información de bandas actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)

def mostrar_estado_porton(porton_activada):
    porton = porton_activada.copy()
    index_activada = porton.index("1")
    porton[index_activada] = f"Porton{index_activada}:ON"

    try:
        mensaje = ""
        # Mostrar todos los estados en orden cíclico
        for i, puerta in enumerate(porton):
            mensaje += puerta + " -> OFF"

        mensaje = mensaje.rstrip(" -> ")  # Eliminar la flecha al final
        lcd.clear()
        lcd.write_string(mensaje)
        return "Información del porton actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)
    
def mostrar_estado_alarma(alarma_activa):
    alarma = alarma_activa.copy()
    alarma_activada = alarma.index("1")
    alarma[alarma_activada] = f"Alarma{alarma_activada}:ON"

    try:
        mensaje = ""
        # Mostrar todos los estados en orden cíclico
        for i, alrm in enumerate(alarma):
            mensaje += alrm + " -> OFF"

        mensaje = mensaje.rstrip(" -> ")  # Eliminar la flecha al final
        lcd.clear()
        lcd.write_string(mensaje)
        return "Información de alarma actualizada en la pantalla LCD."
    except Exception as e:
        return str(e)


# --------- Funciones Laser --------------------

def luz_exterior():
    global luz_exterior
    
    if luz_exterior:
        GPIO.output(PIN_LEDf, GPIO.HIGH)
    
    else:
        GPIO.output(PIN_LEDf, GPIO.LOW)
        
    
    


def laser():
    global luz_recibida2
    luz_recibida2 = GPIO.input(PIN_F2)
    
    GPIO.output(PIN_LASER, GPIO.HIGH)
    
    
    if luz_recibida2:
        print("Mucha luz en FOTORESISTENCIA2: Apagando el buzzer")
        GPIO.output(PIN_BUZZER, GPIO.LOW)
    else:
        print("Poca luz en FOTORESISTENCIA2: Encendiendo el buzzer")
        GPIO.output(PIN_BUZZER, GPIO.HIGH)

        
    


def fotoresistencia1():
    global luz_recibida1
    global luz_exterior
    luz_recibida1 = GPIO.input(PIN_F1)
    while True:
        if luz_recibida1:
            print("Mucha luz en FOTORESISTENCIA1: Apagando el láser y el LED")
            GPIO.output(PIN_LASER, GPIO.LOW)
            GPIO.output(PIN_LEDf, GPIO.LOW)
        else:
            print("Poca luz en F1: Encendiendo el láser y el LED")
            laser()

            luz_exterior = True

        time.sleep(5) # Espera 5 segundos antes de repetir


# -------------- FUNCIONES SENSOR YAIR -------------

"""
Explica cómo el sensor ultrasónico mide la distancia y 
cómo se calcula la distancia en centímetros.
"""

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

    # Calcular la duración del pulso
    pulse_duration = pulse_end - pulse_start

    # Calcular la distancia
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

number = 0

"""
Describe el proceso continuo de medir la distancia, 
actualizar un contador basado en la distancia medida, 
y reflejar este contador en los pines GPIO en formato binario.
"""

def loop():
    global number
    while True:
        # Obtener la distancia medida por el sensor ultrasónico
        distance = get_distance()
        print('Persona detectada')
        print(f"Distancia: {distance} cm")

        # Incrementar o decrementar el contador según la distancia medida
        if distance >= 0 and distance <= 7:
            number += 1
            if number > 9:
                number = 0
        elif distance > 7 and distance <= 14:
            if number > 0:
                number -= 1

        # Enviar el número actual en formato binario a los pines
        GPIO.output(bit0, number & 0b0001)
        GPIO.output(bit1, number & 0b0010)
        GPIO.output(bit2, number & 0b0100)
        GPIO.output(bit3, number & 0b1000)

        # Esperar un poco para evitar múltiples cambios por una sola detección
        time.sleep(1)










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
        print(PIN_IN1_STEPPER)
        print(PIN_IN2_STEPPER)
        print(PIN_IN3_STEPPER)
        print(PIN_IN4_STEPPER)
        GPIO.output(PIN_IN5_LEDGREEN, 1)
        GPIO.output(PIN_IN6_LEDRED,   0)
    else:
        stop_motor()
        print("Motor detenido")
        GPIO.output(PIN_IN5_LEDGREEN, 0)
        GPIO.output(PIN_IN6_LEDRED,   1)
    
        
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

    else:
        angle = 0
        move_servo(pwm, angle)
        print("Puerta cerrada")
        print(PIN_SERVO)
    
        
    #Tambien la opcion de detener totalmente el motor pero hay que inicializar de nuevo
    #Es con la siguiente linea
    #stop_motor()
    
    return jsonify({"mensaje": "Estado del motor actualizado correctamente"}), 200
   
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
    
    # ---- Sensor YAIR -----------
    # Configurar los pines como salidas
    GPIO.setup([bit0, bit1, bit2, bit3], GPIO.OUT)

    # Configurar los pines para el sensor ultrasónico
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    
    
    # --- PANTALLA LCD ---
    # Mostrar mensaje de bienvenida durante 10 segundos
    global lcd
    pantalla = mostrar_bienvenida(lcd)

    # ----- Iniciar apagados los puertos -------
    GPIO.output(LED1, 0)
    GPIO.output(MOTOR, 0)
    
    #Iniciar apagados los puertos
    GPIO.output(PIN_IN1_STEPPER,0)
    GPIO.output(PIN_IN2_STEPPER,0)
    GPIO.output(PIN_IN3_STEPPER,0)
    GPIO.output(PIN_IN4_STEPPER,0)
    GPIO.output(PIN_IN5_LEDGREEN,0)
    GPIO.output(PIN_IN6_LEDRED, 1)
    
    
    # ----- Sensor YAIR  set mode y output------
    # Configurar el modo de numeración de pines --> AQUI SE MODIFICA GPIO en vez de PIN -> SI MODIFICA TODOS COMENTARLO
    # No se si va modificar todo los demas pines.
    #LO COMENTE MEJOR QUE TAL SI MODIFICA TODOS LOS PINES, investigar aún
    # por lo tanto es problable que no funcione lo del yair carrito
    #GPIO.setmode(GPIO.BCM)

    # Inicializar el pin TRIG en bajo
    GPIO.output(TRIG, False)
    time.sleep(2)



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
    print(PIN_A)
    print(PIN_B)
    print(PIN_C)

#LASER

# * en cuenta esta seccion de codigo
@app.route('/api/Luz_Exterior', methods=['POST'])
def handle_data4():

    data = request.json
    global luz_exterior
# Aquí puedes hacer lo que necesites con la variable 'selected_area'
    estado_luz = data.get('estado')
    if estado_luz == 1:
        luz_exterior= True
    else:
        luz_exterior= False
    
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
    alarma = alarmaEncendida
    if alarmaEncendida is None:
        return jsonify({"error": "El estado de la alarma no ha sido configurado aun"}), 404
    
    return jsonify({"estado_alarma exterior": alarma}), 200   


# SENSOR yair 
@app.route('/api/contador_personas', methods=['GET'])
def handle_data7():
    global number
    data = request.json
    
    # Aquí puedes hacer lo que necesites con la variable 'selected_area'
    cantidad = data.get('estado')
    if cantidad is None:
        return jsonify({"error": "El sensor Ultrasonico no ha sido configurado aun"}), 404
    
    return jsonify({"contador_personas": cantidad}), 200

    

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