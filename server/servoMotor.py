import RPi.GPIO as GPIO
import time

class ServoMotor:
    def __init__(self, pin, frequency=50):
        self.pin = pin
        self.frequency = frequency
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)
    
    def move(self, angle):
        duty_cycle = angle / 18.0 + 2.5
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)
        self.pwm.ChangeDutyCycle(0)  # Detener el pulso para no mantener el servo en movimiento
    
    def stop(self):
        self.pwm.ChangeDutyCycle(0)