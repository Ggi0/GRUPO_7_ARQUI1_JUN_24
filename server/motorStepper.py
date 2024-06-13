import RPi.GPIO as GPIO
import sys
import time
import threading

# * Clase para controlar el motor stepper
class StepperMotor:
    def __init__(self, step_pins, seq, wait_time=10):
        self.step_pins = step_pins
        self.seq = seq
        self.step_count = len(seq)
        self.step_dir = 1
        self.step_counter = 0
        self.wait_time = wait_time / float(1000)
        self.running = False
        self.pause = threading.Event()
        self.pause.set()

        for pin in step_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def run(self):
        while self.running:
            self.pause.wait()  # Pausar el hilo si se desactiva el evento

            for pin in range(0, 4):
                xpin = self.step_pins[pin]
                GPIO.output(xpin, self.seq[self.step_counter][pin])

            self.step_counter += self.step_dir

            # Si llegamos al final de la secuencia, empezar de nuevo
            if self.step_counter >= self.step_count:
                self.step_counter = 0
            if self.step_counter < 0:
                self.step_counter = self.step_count + self.step_dir

            time.sleep(self.wait_time)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run, daemon=True).start()
            print("Motor iniciado")

    def stop(self):
        self.running = False
        print("Motor detenido")

    def pause_motor(self):
        self.pause.clear()
        print("Motor pausado")

    def resume_motor(self):
        self.pause.set()
        print("Motor reanudado")
