from gpiozero import MCP3008
from time import sleep
import math
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan6 = AnalogIn(mcp, MCP.P6)

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Thermistor.git"


class Thermistor:
    
    def __init__(
        self,
        pin,
        series_resistor,
        nominal_resistance,
        nominal_temperature,
        b_coefficient,
        *,
        high_side=True
    ):
        # pylint: disable=too-many-arguments
        self.pin = chan6
        self.series_resistor = series_resistor
        self.nominal_resistance = nominal_resistance
        self.nominal_temperature = nominal_temperature
        self.b_coefficient = b_coefficient
        self.high_side = high_side

    @property
    def resistance(self):
        """The resistance of the thermistor in Ohms"""
        if self.high_side:
            # Thermistor connected from analog input to high logic level.
            reading = self.pin.value / 64
            reading = (1023 * self.series_resistor) / reading
            reading -= self.series_resistor
        else:
            # Thermistor connected from analog input to ground.
            reading = self.series_resistor / (65535.0 / self.pin.value - 1.0)
        return reading

    @property
    def temperature(self):
        """The temperature of the thermistor in Celsius"""
        steinhart = self.resistance / self.nominal_resistance  # (R/Ro)
        steinhart = math.log(steinhart)  # ln(R/Ro)
        steinhart /= self.b_coefficient  # 1/B * ln(R/Ro)
        steinhart += 1.0 / (self.nominal_temperature + 273.15)  # + (1/To)
        steinhart = 1.0 / steinhart  # Invert
        steinhart -= 273.15  # convert to C

        return steinhart
