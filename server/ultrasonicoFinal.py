import RPi.GPIO as GPIO
import time

# Configurar los pines GPIO para los bits binarios
bit0 = 14  # Pin 11 en la Raspberry Pi
bit1 = 12  # Pin 12 en la Raspberry Pi
bit2 = 4   # Pin 13 en la Raspberry Pi
bit3 = 15  # Pin 15 en la Raspberry Pi

# Configurar los pines GPIO para el sensor ultrasónico
TRIG = 27  # Pin 16 en la Raspberry Pi
ECHO = 22  # Pin 18 en la Raspberry Pi

# Configurar el modo de numeración de pines
GPIO.setmode(GPIO.BCM)

# Configurar los pines como salidas
GPIO.setup([bit0, bit1, bit2, bit3], GPIO.OUT)

# Configurar los pines para el sensor ultrasónico
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Inicializar el pin TRIG en bajo
GPIO.output(TRIG, False)
time.sleep(2)

# Variable para almacenar el número actual
number = 0

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

try:
    while True:
        # Obtener la distancia medida por el sensor ultrasónico
        distance = get_distance()
        print('persona detectada')
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

except KeyboardInterrupt:
    # Limpiar la configuración de los pines GPIO al salir
    GPIO.cleanup()
