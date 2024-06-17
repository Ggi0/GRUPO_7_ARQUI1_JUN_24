import RPi.GPIO as GPIO
from time import sleep

# Configura el modo de los pines
GPIO.setmode(GPIO.BOARD)

# Selecciona el número de puerto (pin 40, GPIO 21) para el buzzer
BUZZER = 40

# Configura el pin del buzzer como salida
GPIO.setup(BUZZER, GPIO.OUT)

try:
    while True:
        # Enciende el buzzer
        GPIO.output(BUZZER, GPIO.HIGH)
        print("El buzzer está encendido.")
        sleep(5)  # Espera 5 segundos

        # Apaga el buzzer
        GPIO.output(BUZZER, GPIO.LOW)
        print("El buzzer está apagado.")
        sleep(5)  # Espera 5 segundos

except KeyboardInterrupt:
    # Limpia la configuración de los pines al salir
    GPIO.cleanup()

print("hola")