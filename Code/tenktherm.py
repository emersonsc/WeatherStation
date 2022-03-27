from time import sleep
import math as mt
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import board
import adathermistor

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan6 = AnalogIn(mcp, MCP.P6)
A = 0.001129148
B = 0.000234125
C = 0.0000000876741

def read_all():
#while True:
    R = 10000 / (65535/chan6.value - 1)
    TempK = 1 / (A + (B * mt.log(R)) + C * mt.pow(mt.log(R),3))
    # Convert from Kelvin to Celsius
    TempC = TempK - 273.15
    TempF = ((TempC * 1.8) + 32)
    return TempF
    #print(TempF)
