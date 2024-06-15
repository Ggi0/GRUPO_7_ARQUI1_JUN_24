import RPi.GPIO as GPIO
import time

def init_servo(pin, frequency=50):
    """
    Inicializa el servo motor en el pin especificado con la frecuencia dada.
    """
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
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)  # Detener el pulso para no mantener el servo en movimiento

def stop_servo(pwm):
    """
    Detiene el servo motor.
    """
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    GPIO.cleanup()

# Ejemplo de uso
pin = 12  # Reemplaza esto con el pin GPIO que est�s utilizando
pwm = init_servo(pin)

try:
    while True:
        angle = float(input("Ingresa el �ngulo al que deseas mover el servo (0-180): "))
        move_servo(pwm, angle)
except KeyboardInterrupt:
    print("Programa interrumpido por el usuario")
finally:
    stop_servo(pwm)
