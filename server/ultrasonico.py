import RPi.GPIO as GPIO
import time

class UltrasonicSensorController:
    def __init__(self, trig_pin=11, echo_pin=13, led_a=15, led_b=16, led_c=18, led_d=22):
        """
        Constructor de la clase UltrasonicSensorController.
        
        Configura los pines GPIO y otros parámetros iniciales.
        
        Args:
        - trig_pin: Número del pin GPIO conectado al pin de trigger del sensor ultrasónico.
        - echo_pin: Número del pin GPIO conectado al pin de echo del sensor ultrasónico.
        - led_a, led_b, led_c, led_d: Números de pines GPIO conectados a los LEDs.
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.led_a = led_a
        self.led_b = led_b
        self.led_c = led_c
        self.led_d = led_d
        self.counter = 0

        # Configuración de los pines GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.setup(self.led_a, GPIO.OUT)
        GPIO.setup(self.led_b, GPIO.OUT)
        GPIO.setup(self.led_c, GPIO.OUT)
        GPIO.setup(self.led_d, GPIO.OUT)

    def measure_distance(self):
        """
        Mide la distancia utilizando el sensor ultrasónico.
        
        Returns:
        - distance: Distancia medida en centímetros.
        """
        GPIO.output(self.trig_pin, False)
        time.sleep(0.1)

        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        duration = stop_time - start_time
        distance = (duration * 34300) / 2

        return distance

    def update_leds(self):
        """
        Actualiza los LEDs según el contador binario.
        """
        binary_counter = bin(self.counter)[2:].zfill(4)
        GPIO.output(self.led_a, int(binary_counter[0]))
        GPIO.output(self.led_b, int(binary_counter[1]))
        GPIO.output(self.led_c, int(binary_counter[2]))
        GPIO.output(self.led_d, int(binary_counter[3]))

    def run(self):
        """
        Función principal que ejecuta el programa.
        """
        try:
            while True:
                distance = self.measure_distance()
                if distance <= 4:
                    self.counter += 1
                    print("Movement detected. Counter:", self.counter)
                    self.update_leds()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopping program")
            GPIO.cleanup()
