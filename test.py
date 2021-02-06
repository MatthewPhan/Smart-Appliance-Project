import Adafruit_BMP.BMP085 as BMP085
import sys
import Adafruit_DHT
import datetime
from datetime import date, datetime, timedelta
import time
from time import sleep
import mysql.connector
from rpi_lcd import LCD

bmp180Sensor = BMP085.BMP085()
pin = 19

# Grab weather values
degree = u"\u00b0"

# Set datetime string
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

def main():
    
    while True:
      humidity, temperature = Adafruit_DHT.read_retry(11, pin)
      presBMP = bmp180Sensor.read_pressure() # absolute pressure in hPa
      print('DHT11 Sensor Readings:')
      print('\tTemp: {} C'.format(temperature))
      print('\tHumidity: {}'.format(humidity))
      print('BMP Pressure Sensor Readings:')
      print('\tPressure = {} hPa [or mbar]'.format(presBMP))
      print('Recorded on: {}'.format(dt_string))

if __name__ == '__main__': main()
