import RPi.GPIO as GPIO
import time

# Configurar la librería RPi.GPIO para usar el número de pin físico
GPIO.setmode(GPIO.BOARD)

# Definir los pines de salida (ajusta los números según tu configuración)
PIN_A = 18  # Pin físico 11 (GPIO 17)
PIN_B = 22  # Pin físico 13 (GPIO 27)
PIN_C = 23  # Pin físico 15 (GPIO 22)

# Configurar los pines como salida
GPIO.setup(PIN_A, GPIO.OUT)
GPIO.setup(PIN_B, GPIO.OUT)
GPIO.setup(PIN_C, GPIO.OUT)

def decimal_to_binary(decimal):
    binary = format(decimal, '03b')
    return [int(bit) for bit in binary]

def set_demultiplexer(value):
    binary_value = decimal_to_binary(value)
    GPIO.output(PIN_A, binary_value[0])
    GPIO.output(PIN_B, binary_value[1])
    GPIO.output(PIN_C, binary_value[2])

try:
    while True:
        decimal_input = input("Ingrese un número decimal (0-7): ")
        if decimal_input.isdigit():
            decimal_value = int(decimal_input)
            if 0 <= decimal_value <= 7:
                set_demultiplexer(decimal_value)
            else:
                print("Por favor, ingrese un número entre 0 y 7.")
        else:
            print("Entrada inválida. Por favor, ingrese un número decimal.")
except KeyboardInterrupt:
    print("Programa terminado.")
finally:
    GPIO.cleanup()
