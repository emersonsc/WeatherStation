from dotenv import load_dotenv
from gpiozero import Button
from gpiozero import CPUTemperature
from os.path import join, dirname
from datetime import datetime
import paho.mqtt.client as mqtt
import requests
import time
import math
import bme280_sensor
import wind_direction
import statistics
#import ds18b20_therm
import database
import tenktherm
import json
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#load .env variables
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_PORT = int(os.environ.get('MQTT_PORT'))

#global vairable definition
flag_connected = 0

# constant variable definition
MQTT_STATUS_TOPIC = "raspberry/ws/status"
MQTT_SENSORS_TOPIC = "raspberry/ws/sensors"
BUCKET_SIZE = 0.011 # volume of rain required to tip rain meter one time
RAINFALL_METRIC = 0 # measure rainfall in inches or mm. 1=Metric 0=imperial

CM_IN_A_KM = 100000.0
SECS_IN_AN_HOUR = 3600

# initialize ground temp probe
#temp_probe = ds18b20_therm.DS18B20()

# define wind speed and direction lists
store_speeds = []
store_directions = []

# define variables
wind_count = 0
radius_cm = 9.0
wind_interval = 5
ADJUSTMENT = 1.18
interval = 60
rain_count = 0
cpu = CPUTemperature()
#BUCKET_SIZE = 0.011

# MQTT
def on_connect(client, userdata, flags, rc):
        print("Connected with flags [%s] rtn code [%d]"% (flags, rc) )
        global flag_connected
        flag_connected = 1

def on_disconnect(client, userdata, rc):
        print("Disconnected with rtn code [%d]"% (rc) )
        global flag_connected
        flag_connected = 0

client = mqtt.Client("WX")
client.on_connect = on_connect
client.on_disonnect = on_disconnect
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.connect(MQTT_HOST, MQTT_PORT)

# System Uptime
def uptime():
        t = os.popen('uptime -p').read()[:-1]
        uptime = t.replace('up ', '')
        return uptime

def spin():
	global wind_count
	wind_count = wind_count + 1

def calculate_speed(time_sec):
        global wind_count
        circumference_cm = (2 * math.pi) * radius_cm
        rotations = wind_count / 2.0
        
        dist_km = (circumference_cm * rotations) / CM_IN_A_KM
        
        km_per_sec = dist_km / time_sec
        km_per_hour = km_per_sec * SECS_IN_AN_HOUR
        
        mi_per_hour = km_per_hour * 0.6214

        return mi_per_hour * ADJUSTMENT
	

def bucket_tipped():
        global rain_count
        rain_count = rain_count + 1
        
def reset_rainfall():
        global rain_count
        rain_count = 0
        
def reset_wind():
        global wind_count
        wind_count = 0


        
#def reset_gust():
        #global gust
        #gust = 0

wind_speed_sensor = Button(16)
wind_speed_sensor.when_activated = spin


rain_sensor = Button(27)
rain_sensor.when_pressed = bucket_tipped
   


# Main Loop
if __name__ == '__main__':

        client.loop_start()

        # Wait to receiver the connected callback for MQTT

        while flag_connected == 0:
                print("Not connected. Waiting 1 Second.")
                time.sleep(1)

        while True:
                print("Starting Weather Sensor Read Loop...")
                store_speeds = []
                store_directions = []
                for _ in range (interval//wind_interval):
                        print("Start timed loop...")
                        reset_wind()
                        time.sleep(wind_interval)  # counter is spinning in background
                        final_speed = calculate_speed(wind_interval)
                        store_speeds.append(final_speed)

                #wind_average = wind_direction.get_average(store_directions)
                wind_gust_speed = (max(store_speeds))
                wind_speed = (statistics.mean(store_speeds))
                rainfall = rain_count * BUCKET_SIZE 
                #print("Read Ground Temp"
                #ground_temp = temp_probe.read_temp()
                print("Read Air Conditions")
                humidity, pressure, ambient_temp = bme280_sensor.read_all()
                bat_temp = tenktherm.read_all()
                dewpoint = ambient_temp - (0.36 * (100 - humidity))
                
                # Round all Values
                wind_gust_speed = round(wind_gust_speed, 2)
                wind_speed = round(wind_speed, 2)
                #wind_dir = round(wind_dir)
                humidity = round(humidity, 2)
                pressure = round(pressure, 2)
                ambient_temp = round(ambient_temp, 2)
                #ground_temp = round(ground_temp, 2)
                dewpoint = round(dewpoint, 2)
                bat_temp = round(bat_temp, 2)
                cpu_temp = round(cpu.temperature, 2)
                
                print(wind_speed, wind_gust_speed, rainfall, humidity, pressure, ambient_temp, dewpoint, bat_temp) #  ADD ground_temp BACK
                ambient_temp_str = "{0:.2f}".format(ambient_temp)
                #ground_temp_str = "{0:.2f}".format(ground_temp)
                humidity_str = "{0:.2f}".format(humidity)
                pressure_str = "{0:.2f}".format(pressure)
                wind_speed_str = "{0:.2f}".format(wind_speed)
                wind_gust_str = "{0:.2f}".format(wind_gust_speed)
                #wind_average_str = str(wind_average)
                rainfall_str = "{0:.2f}".format(rainfall)
                dewpoint_str = "{0:.2f}".format(dewpoint)
                WUurl = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"
                WU_station_id = "KMIHOWEL133" # Replace XXXX with your PWS ID
                WU_station_pwd = "trtjbtAo" # Replace YYYY with your Password
                WUcreds = "ID=" + WU_station_id + "&PASSWORD="+ WU_station_pwd
                date_str = "&dateutc=now"
                action_str = "&action=updateraw"
                r= requests.get(
                WUurl +
                WUcreds +
                date_str +
                "&humidity=" + humidity_str +
                "&baromin=" + pressure_str +
                "&windspeedmph=" + wind_speed_str +
                "&windgustmph="  + wind_gust_str +
                "&tempf=" + ambient_temp_str +
                "&rainin=" + rainfall_str +
                #"&soiltempf=" + ground_temp_str +
                #"&winddir=" + wind_average_str +
                "&dewptf=" + dewpoint_str +
                action_str)
                print("Received " + str(r.status_code) + " " + str(r.text))
                now = datetime.now()
                last_message = now.strftime("%m/%d/%Y %H:%M:%S")
                sys_uptime = uptime()

                # Create JSON dict for MQTT Transmission
                send_msg = {
                        'wind_speed': wind_speed,
                        'wind_gust_speed': wind_gust_speed,
                        'rainfall': rainfall,
                        #'wind_direction': wind_dir,
                        'humidity': humidity,
                        'pressure': pressure,
                        'ambient_temp': ambient_temp,
                        #'ground_temp': ground_temp,
                        'dewpoint': dewpoint,
                        'last_message': last_message,
                        'cpu_temp': cpu_temp,
                        'bat_temp': bat_temp,
                        'system_uptime': sys_uptime
                }

                # Convert message to json
                payload_sensors = json.dumps(send_msg)
                
                # Set status payload
                payload_status = "Online"

                # Publish Status to mqtt
                client.publish(MQTT_STATUS_TOPIC, payload_status, qos=0)

                # Publish sensor data to mqtt
                client.publish(MQTT_SENSORS_TOPIC, payload_sensors, qos=0)

                reset_rainfall()


        client.loop_stop()
        print("Loop Stopped.")
        client.disconnect()
        print("MQTT Disconnected.")
        
