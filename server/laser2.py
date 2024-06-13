import RPi.GPIO as GPIO
from time import sleep

class LightSensorController:
    def __init__(self, laser_pin=38, led_pin=36, photoresistor1_pin=11, photoresistor2_pin=21, buzzer_pin=40):
        self.laser_pin = laser_pin
        self.led_pin = led_pin
        self.photoresistor1_pin = photoresistor1_pin
        self.photoresistor2_pin = photoresistor2_pin
        self.buzzer_pin = buzzer_pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.laser_pin, GPIO.OUT)
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        GPIO.setup(self.photoresistor1_pin, GPIO.IN)
        GPIO.setup(self.photoresistor2_pin, GPIO.IN)

    def check_light_sensors(self):
        luz_recibida1 = GPIO.input(self.photoresistor1_pin)
        luz_recibida2 = GPIO.input(self.photoresistor2_pin)

        if luz_recibida1:
            print("Poca luz en FOTORESISTENCIA1: Encendiendo el láser y el LED")
            GPIO.output(self.laser_pin, GPIO.HIGH)
            GPIO.output(self.led_pin, GPIO.HIGH)

            if luz_recibida2:
                print("Poca luz en FOTORESISTENCIA2: Encendiendo el buzzer")
                GPIO.output(self.buzzer_pin, GPIO.HIGH)
            else:
                print("Mucha luz en FOTORESISTENCIA2: Apagando el buzzer")
                GPIO.output(self.buzzer_pin, GPIO.LOW)
        else:
            print("Mucha luz en FOTORESISTENCIA1: Apagando el láser y el LED")
            GPIO.output(self.laser_pin, GPIO.LOW)
            GPIO.output(self.led_pin, GPIO.LOW)

    def run(self):
        try:
            while True:
                self.check_light_sensors()
                sleep(5)  # Espera 5 segundos antes de repetir
        except KeyboardInterrupt:
            print("Programa terminado.")
        finally:
            GPIO.cleanup()
