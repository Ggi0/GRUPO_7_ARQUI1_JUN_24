import smbus2
from RPLCD.i2c import CharLCD

# Direcci�n I2C del dispositivo LCD, aseg�rate de que esta es la direcci�n correcta
i2c_address = 0x27  # Reemplaza con la direcci�n detectada

# Inicializa el LCD
lcd = CharLCD(i2c_expander='PCF8574', address=i2c_address, port=1,
              cols=16, rows=2, charmap='A00', auto_linebreaks=True)

# Escribe un mensaje en el LCD
lcd.write_string('Hello, world!')
