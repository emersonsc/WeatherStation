from gpiozero import MCP3008
import math
import time

adc = MCP3008(channel=7)

volts = {2.9: 0.0,
         2.8: 0.0,
         1.9: 22.5,
         2.0: 22.5,
         2.1: 45.0,
         0.5: 67.5,
         0.6: 90.0,
         0.4: 112.5,
         1.1: 135.0,
         1.0: 135.0,
         0.8: 157.5,
         1.5: 180.0,
         1.3: 202.5,
         2.6: 225.0,
         2.5: 247.5,
         3.2: 270.0,
         3.3: 270.0
         3.0: 292.5,
         3.1: 315.0,
         2.7: 337.5}

count = 0

def get_average(angles):
    sin_sum = 0.0
    cos_sum = 0.0
    
    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)
        
    flen = float(len(angles))
    s = sin_sum / flen
    c = cos_sum / flen
    arc = math.degrees(math.atan(s / c))
    average = 0.0
    
    if s > 0 and c > 0:
        average = arc
    elif c < 0:
        average = arc + 180
    elif s < 0 and c > 0:
        average = arc + 360
        
        
    return 0.0 if average == 360 else average


def get_value(length=5):
    data = []
    #print("Measuring wind direction for %d seconds..." % length)
    start_time = time.time()
    
    while time.time() - start_time <= length:
        wind = round(adc.value * 3.3,1)
        
        if wind in volts:
            data.append(volts[wind])
            
    return get_average(data)

if __name__ == "__main__":
    while True:
        wind = round(adc.value * 3.2,1)
        direction = volts.get(wind)
        if direction:
            print("Found " + str(wind) + " " + str(volts[wind]))
        else:
            print("unknown value: " + str(wind))

        time.sleep(1)
