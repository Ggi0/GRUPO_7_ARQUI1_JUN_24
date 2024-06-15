import RPi.GPIO as GPIO
import time

class LedController:
    def _init_(self, pin_a=18, pin_b=22, pin_c=23):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_c = pin_c

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_a, GPIO.OUT)
        GPIO.setup(self.pin_b, GPIO.OUT)
        GPIO.setup(self.pin_c, GPIO.OUT)

    @staticmethod
    def decimal_to_binary(decimal):
        binary = format(decimal, '03b')
        return [int(bit) for bit in binary]

    def set_demultiplexer(self, value):
        binary_value = self.decimal_to_binary(value)
        GPIO.output(self.pin_a, binary_value[0])
        GPIO.output(self.pin_b, binary_value[1])
        GPIO.output(self.pin_c, binary_value[2])

    def run(self):
        try:
            while True:
                decimal_input = input("Ingrese un n�mero decimal (0-7): ")
                if decimal_input.isdigit():
                    decimal_value = int(decimal_input)
                    if 0 <= decimal_value <= 7:
                        self.set_demultiplexer(decimal_value)
                    else:
                        print("Por favor, ingrese un n�mero entre 0 y 7.")
                else:
                    print("Entrada inv�lida. Por favor, ingrese un n�mero decimal.")
        except KeyboardInterrupt:
            print("Programa terminado.")
        finally:
            GPIO.cleanup()