import time
import board
from adafruit_bme280 import basic as adafruit_bme280
from time import sleep
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#bme280.sea_level_pressure = 980.00

#temperature_offset = 0

#while True:
def read_all():
    humidity = bme280.relative_humidity
    pressure = (bme280.pressure * 0.02953)
    ambient_temp = (bme280.temperature * (9/5.0) + 32)
    #altitude = (bme680.altitude * 3.28084)
    return humidity, pressure, ambient_temp
    #print(ambient_temp, humidity, pressure)
    #time.sleep(2)
    
