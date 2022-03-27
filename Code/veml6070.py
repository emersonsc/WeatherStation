import time
import board
import adafruit_veml6070

with board.I2C() as i2c:
    uv = adafruit_veml6070.VEML6070(i2c)

    for j in range(10):
        uv_raw = uv.uv_raw
        risk_level = uv.get_index(uv_raw)
        print("Reading: {0} | Risk Level: {1}".format(uv_raw, risk_level))
        time.sleep(1)
