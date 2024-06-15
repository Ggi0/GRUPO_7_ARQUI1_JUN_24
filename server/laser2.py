import RPi.GPIO as GPIO
from time import sleep

# Configura el modo de los pines
GPIO.setmode(GPIO.BOARD)

# Selecciona el número de puerto (pin 38, GPIO 20) para el láser
LASER = 38

# Selecciona el número de puerto (pin 36, GPIO 16) para el LED
LED = 36

# Selecciona el número de puerto (pin 11, GPIO 17) para la fotoresistencia1
FOTORESISTENCIA1 = 11

# Selecciona el número de puerto (pin 21, GPIO 9) para la fotoresistencia2
FOTORESISTENCIA2 = 21

# Selecciona el número de puerto (pin 40, GPIO 21) para el buzzer
BUZZER = 40

# Configura el pin del láser como salida
GPIO.setup(LASER, GPIO.OUT)

# Configura el pin del LED como salida
GPIO.setup(LED, GPIO.OUT)

# Configura el pin del buzzer como salida
GPIO.setup(BUZZER, GPIO.OUT)

# Configura el pin de la fotoresistencia1 como entrada
GPIO.setup(FOTORESISTENCIA1, GPIO.IN)

# Configura el pin de la fotoresistencia2 como entrada
GPIO.setup(FOTORESISTENCIA2, GPIO.IN)

try:
    while True:
        luz_recibida1 = GPIO.input(FOTORESISTENCIA1)
        luz_recibida2 = GPIO.input(FOTORESISTENCIA2)
        if luz_recibida1:
            print("Poca luz en FOTORESISTENCIA1: Encendiendo el láser y el LED")
            GPIO.output(LASER, GPIO.HIGH)
            GPIO.output(LED, GPIO.HIGH)

            if luz_recibida2:
                print("Poca luz en FOTORESISTENCIA2: Encendiendo el buzzer")
                GPIO.output(BUZZER, GPIO.HIGH)
            else:
                print("Mucha luz en FOTORESISTENCIA2: Apagando el buzzer")
                GPIO.output(BUZZER, GPIO.LOW)

        else:
            print("Mucha luz en FOTORESISTENCIA1: Apagando el láser y el LED")
            GPIO.output(LASER, GPIO.LOW)
            GPIO.output(LED, GPIO.LOW)


        sleep(5)  # Espera 5 segundos antes de repetir

except KeyboardInterrupt:
    GPIO.cleanup()
