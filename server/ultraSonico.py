import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin, led_pins):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.led_pins = led_pins
        self.contador = 0

        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        for pin in self.led_pins:
            GPIO.setup(pin, GPIO.OUT)

    def medir_distancia(self):
        GPIO.output(self.trig_pin, False)
        time.sleep(0.1)

        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        inicio_tiempo = time.time()
        fin_tiempo = time.time()

        while GPIO.input(self.echo_pin) == 0:
            inicio_tiempo = time.time()

        while GPIO.input(self.echo_pin) == 1:
            fin_tiempo = time.time()

        duracion = fin_tiempo - inicio_tiempo
        distancia = (duracion * 34300) / 2

        return distancia

    def encender_leds(self):
        binario = bin(self.contador)[2:].zfill(4)  # Convertir el contador a binario de 4 bits
        for i, bit in enumerate(binario):
            GPIO.output(self.led_pins[i], int(bit))

    def sensor_thread(self):
        try:
            while True:
                distancia = self.medir_distancia()
                if distancia <= 4:
                    self.contador += 1
                    print("Movimiento detectado. Contador:", self.contador)
                    self.encender_leds()
                time.sleep(0.5)  # Puedes ajustar este tiempo según tus necesidades
        except KeyboardInterrupt:
            print("Deteniendo el programa del sensor")
            GPIO.cleanup()