import Adafruit_BMP.BMP085 as BMP085
import sys
import Adafruit_DHT
import datetime
from datetime import date, datetime, timedelta
import time
from time import sleep
import mysql.connector
from rpi_lcd import LCD

# Connect to db
cnx = mysql.connector.connect(user='iotuser', password='dmitiot', database='iotdatabase')
cursor = cnx.cursor()

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

      weatherValues = ('NULL', temperature, humidity, presBMP, dt_string)
      cursor.execute('INSERT INTO weather (id, temperature, humidity, pressure, timestamp) VALUES (%s,%s,%s,%s,%s)', weatherValues)
      cnx.commit()

      sql_select_Query = "select convert(temperature, char(50)) as temperature from weather order by id desc limit 1;"
      cursor.execute(sql_select_Query)
      records = cursor.fetchall()

      for record in records:
          # temp = "Current temperature: " + record[0] + degree + "C"
          temp_2 = record[0]


      sql_select_Query = "select convert(humidity, char(50)) as humidity from weather order by id desc limit 1;"
      cursor.execute(sql_select_Query)
      records = cursor.fetchall()

      for record in records:
          # humidity = "\nCurrent humidity: " + record[0] + "%"
          humidity_2 = record[0]


      sql_select_Query = "select convert(pressure, char(50)) as pressure from weather order by id desc limit 1;"
      cursor.execute(sql_select_Query)
      records = cursor.fetchall()

      for record in records:
          # pressure = "\nCurrent atmospheric pressure: " + record[0] + "hPa"
          pressure_2 = record[0]

      lcd_values = temp_2 + '/' + humidity_2 + '/' + pressure_2

      # LCD screen output
      lcd = LCD()
      lcd.text('Temp Hum Pres', 1)
      lcd.text(lcd_values, 2)
      sleep(10)

if __name__ == '__main__': main()
