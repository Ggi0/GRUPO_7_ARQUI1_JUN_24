from flask import Flask, request, jsonify
from flask_cors import CORS
from motorStepper import StepperMotor
from servoMotor import ServoMotor
import RPi.GPIO as GPIO
import sys
import time
import threading

# * Initialize Flask app
app = Flask(__name__)

# * Enable CORS for all routes of the app 
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Lista para almacenar el estado de los LEDs
leds = []

# Variable para almacenar el estado del motor
estado_motor = None
estado_servo_motor = None

# Tipo de configuración de los puertos
GPIO.setmode(GPIO.BOARD)

# Desactivamos alertas de GPIO
GPIO.setwarnings(False)

# Control de creación de API
crear = True

# Declaración de puertos GPIO
LED1 = 11
MOTOR = 13
PIN_IN1_STEPPER = 31
PIN_IN2_STEPPER = 33
PIN_IN3_STEPPER = 35
PIN_IN4_STEPPER = 37

# Declaracion de puerto GPIO
LED1 = 11
LED2 = 15
LED3 = 16
SERVO_PIN = 18

# Configurar pines como salida
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)


# Función para activar el puerto específico y en un estado específico
def controlar_gpio(puerto, estado):
    if puerto == 1:
        GPIO.output(LED1, estado)
    elif puerto == 2:
        GPIO.output(LED2, estado)
    elif puerto == 3:
        GPIO.output(LED3, estado)
    elif puerto == 2:
        GPIO.output(MOTOR, estado)
    else:
        print("No existe el puerto para activarlo.")
        

# Instancia del motor stepper
step_pins = [PIN_IN1_STEPPER, PIN_IN2_STEPPER, PIN_IN3_STEPPER, PIN_IN4_STEPPER]
seq = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

# * Instancia del motor stepper
motor_stepper = StepperMotor(step_pins, seq)

# Crear instancia del servo motor
servo_motor = ServoMotor(SERVO_PIN)

"""
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        "users" : [
            "arman",
            "zack",
            "tin"
        ]   
    })
"""

# * API para controlar el motor stepper (POST)
# * POS sirve para enviar datos al servidor
@app.route('/api/activarLedStepper', methods=['POST'])
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

    controlar_gpio(cuarto, estado)
    
    return jsonify({"mensaje": "Estado del LED actualizado correctamente"}), 200

# * API para controlar el motor stepper (GET)
# * GET sirve para obtener datos del servidor
@app.route('/api/verEstadoLEDStepper', methods=['GET'])
def ver_estado_led():
    global leds
    cuarto = request.args.get('cuarto', type=int)

    if cuarto is None:
        return jsonify({"error": "El parámetro 'cuarto' es necesario y debe ser numérico"}), 400

    for led in leds:
        if led['cuarto'] == cuarto:
            return jsonify({"cuarto": cuarto, "estado": led['estado']}), 200
    
    return jsonify({"error": "Cuarto no encontrado"}), 404

# * API para controlar el motor stepper (POST)
@app.route('/api/activarMotorStepper', methods=['POST'])
def activar_motor():
    global estado_motor
    data = request.json
    estado = data.get('estado')

    if not isinstance(estado, int):
        return jsonify({"error": "El parámetro 'estado' debe ser numérico"}), 400

    estado_motor = estado
    # Código para activar motor
    if estado_motor == 1:
        motor_stepper.start()
        print("Motor activado")
    else:
        motor_stepper.stop()
        print("Motor detenido")
    
    return jsonify({"mensaje": "Estado del motor actualizado correctamente"}), 200

# * API para controlar el motor stepper (GET)
@app.route('/api/verEstadoMotorStepper', methods=['GET'])
def ver_estado_motor():
    global estado_motor

    if estado_motor is None:
        return jsonify({"error": "El estado del motor no ha sido configurado aún"}), 404
    
    return jsonify({"estado_motor": estado_motor}), 200

@app.route('/api/activarServoMotor', methods=['POST'])
def activar_servo_motor():
    global estado_servo_motor
    data = request.json
    estado = data.get('estado')
    angulo = data.get('angulo')

    if not isinstance(estado, int) or not isinstance(angulo, int):
        return jsonify({"error": "Los parámetros 'estado' y 'angulo' deben ser numéricos"}), 400

    estado_servo_motor = estado
    if estado_servo_motor == 1:
        servo_motor.move(angulo)
        print(f"Motor activado a {angulo} grados")
    else:
        servo_motor.stop()
        print("Motor detenido")

    return jsonify({"mensaje": "Estado del motor actualizado correctamente"}), 200

@app.route('/api/verEstadoServoMotor', methods=['GET'])
def ver_estado_servo_motor():
    global estado_servo_motor

    if estado_servo_motor is None:
        return jsonify({"error": "El estado del motor no ha sido configurado aún"}), 404

    return jsonify({"estado_servo_motor": estado_servo_motor}), 200

#Codigo que se ejecuta solo una vez
def setup():
    #Declaracion de GPIO input o output
    GPIO.setup(LED1, GPIO.OUT)
    GPIO.setup(MOTOR, GPIO.OUT)
    GPIO.setup(PIN_IN1_STEPPER,GPIO.OUT)
    GPIO.setup(PIN_IN2_STEPPER,GPIO.OUT)
    GPIO.setup(PIN_IN3_STEPPER,GPIO.OUT)
    GPIO.setup(PIN_IN4_STEPPER,GPIO.OUT)

    #Iniciar apagados los puertos
    GPIO.output(LED1, 0)
    GPIO.output(MOTOR, 0)
    GPIO.output(PIN_IN1_STEPPER,0)
    GPIO.output(PIN_IN2_STEPPER,0)
    GPIO.output(PIN_IN3_STEPPER,0)
    GPIO.output(PIN_IN4_STEPPER,0)

try:
    while True:
        time.sleep(1)  # Mantener el hilo principal dormido

        if crear == True:
            if __name__ == '__main__':
                setup()
                crear = False
                app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
        
except KeyboardInterrupt:
        servo_motor.stop()
        running = False
        GPIO.cleanup()