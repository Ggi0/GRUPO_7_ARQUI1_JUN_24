import time
import smbus2
from RPLCD.i2c import CharLCD



class LCDController:
    def __init__(self, i2c_addr=0x27):
        """
        Constructor de la clase LCDController.
        
        Configura la pantalla LCD con la dirección I2C proporcionada.
        
        Args:
        - i2c_addr: Dirección I2C de la pantalla LCD.
        """
        self.lcd = CharLCD('PCF8574', i2c_addr, auto_linebreaks=True)
    
    def display_message(self, message, duration=2):
        """
        Muestra un mensaje en la pantalla LCD durante un tiempo determinado.
        
        Args:
        - message: Mensaje a mostrar en la pantalla LCD.
        - duration: Tiempo en segundos que se mostrará el mensaje (default: 2 segundos).
        """
        self.lcd.clear()
        self.lcd.write_string(message)
        time.sleep(duration)
    
    def run(self):
        """
        Función principal que ejecuta el ciclo de mostrar mensajes en la pantalla LCD.
        """
        try:
            self.display_message("Hola, Mundo!")
            self.display_message("LCD con I2C")
            self.display_message("Raspberry Pi 4")
        except KeyboardInterrupt:
            pass
        finally:
            self.lcd.close()

