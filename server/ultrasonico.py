import RPi.GPIO as GPIO
import time

# Configurar los pines del sensor ultrasónico y los LEDs
GPIO.setmode(GPIO.BOARD)
TRIG = 11
ECHO = 13
LED_PINS = [15, 16, 18, 22]  # Pines GPIO de los LEDs
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)

# Inicializar contador global
contador = 0

# Función para medir la distancia
def medir_distancia():
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    inicio_tiempo = time.time()
    fin_tiempo = time.time()

    while GPIO.input(ECHO) == 0:
        inicio_tiempo = time.time()

    while GPIO.input(ECHO) == 1:
        fin_tiempo = time.time()

    duracion = fin_tiempo - inicio_tiempo
    distancia = (duracion * 34300) / 2

    return distancia

# Función para encender los LEDs según el contador
def encender_leds():
    global contador
    binario = bin(contador)[2:].zfill(4)  # Convertir el contador a binario de 4 bits
    for i, bit in enumerate(binario):
        GPIO.output(LED_PINS[i], int(bit))

try:
    while True:
        distancia = medir_distancia()
        if distancia <= 4:
            contador += 1
            print("Movimiento detectado. Contador:", contador)
            encender_leds()
        time.sleep(0.5)  # Puedes ajustar este tiempo según tus necesidades

except KeyboardInterrupt:
    print("Deteniendo el programa")
    GPIO.cleanup()
