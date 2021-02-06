#!/usr/bin/python
from __future__ import print_function
try:
    # Import necessary libraries
    import datetime
    import telepot
    from telepot.loop import MessageLoop
    import RPi.GPIO as GPIO
    import requests
    from datetime import date, datetime, timedelta
    import mysql.connector
    import time
    import httplib
    import urllib               # for push notifications
    import logging             # for debugging
    import Adafruit_BMP.BMP085 as BMP085
    import sys
    import Adafruit_DHT
    from rpi_lcd import LCD
    from gpiozero import Buzzer
    from time import sleep
except RuntimeError:
    print("Error loading RPi.GPIO")


# Connect to db
cnx = mysql.connector.connect(user='iotuser', password='dmitiot', database='iotdatabase')
cursor = cnx.cursor()

# Set datetime string
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# Set global variables
DELAYINSECS = 90 # Time in seconds before declaring end of cycle (1 min 30s)
TIME = 0


# Define RPi input/output pins
BUTTON = 13
LED = 18
VIBRATION = 17
pin = 19

# Initialise buzzer
buzzer = Buzzer(5)

# define variables for weather station
# bmp180Sensor = BMP085.BMP085()

# Grab weather values
temp = ''
humidity = ''
pressure = ''
weather_values = ''
degree = u"\u00b0"

sql_select_Query = "select convert(temperature, char(50)) as temperature from weather order by id desc limit 1;"
cursor.execute(sql_select_Query)
records = cursor.fetchall()

for record in records:
    temp = "Current temperature: " + record[0] + degree + "C"
    temp_2 = record[0]


sql_select_Query = "select convert(humidity, char(50)) as humidity from weather order by id desc limit 1;"
cursor.execute(sql_select_Query)
records = cursor.fetchall()

for record in records:
    humidity = "\nCurrent humidity: " + record[0] + "%"
    humidity_2 = record[0]


sql_select_Query = "select convert(pressure, char(50)) as pressure from weather order by id desc limit 1;"
cursor.execute(sql_select_Query)
records = cursor.fetchall()

for record in records:
    pressure = "\nCurrent atmospheric pressure: " + record[0] + "hPa"
    pressure_2 = record[0]

weather_values = temp + '\t' + humidity + '\t' + pressure
lcd_values = temp_2 + '/' + humidity_2 + '/' + pressure_2

# # LCD screen output
# lcd = LCD()
# lcd.text('Temp Hum Pres', 1)
# lcd.text(lcd_values, 2)

def buzzOn():
    while True:
        buzzer.on()
        return "On"

def buzzOff():
    while True:
        buzzer.off()
        return "Off"





def main():
    try:

        # MessageLoop(telegram_bot, action).run_as_thread()

        # Configure GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(VIBRATION, GPIO.IN)
        GPIO.setup(LED, GPIO.OUT)

        # "Pull-down" resistor must be added to input 
        # push-button to avoid floating value at 
        # RPi input when button not in closed circuit.
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Start of sensing of upwards or downwards front on
        # pin connected to vibration detector. 
        # "Bouncetime" argument ignores effect of bouncing caused by
        # sudden state changes.
        GPIO.add_event_detect(VIBRATION, GPIO.BOTH, bouncetime=200)

        # Configure debugging journal file on RPi
        logging.basicConfig(filename='/home/pi/washer.log', 
                            level=logging.INFO, 
                            format='%(asctime)s %(levelname)s:%(message)s')
        logging.info("****************************")
        stop = False
        logging.info("Entering main loop")

        # Main loop, waits for push-button to be 
        # pressed to indicate beginning of cycle, then 
        # periodically checks vibration.
        while not stop:
            logging.info("Main loop iteration")

            GPIO.output(LED, True) # LED off
            GPIO.wait_for_edge(BUTTON, GPIO.RISING) # wait for signal 
                                                    # from push-button
            logging.info(" Started")
            going = True
            GPIO.output(LED, False) # LED on

            global dt_string
            global cursor 
            global cnx

            # Call function to read weather values from sensors
            # weather()

            print("The washing machine has started running...")

            start = ('NULL', '0', 'start', dt_string)
            cursor.execute('INSERT INTO vibration (id, duration, status, timestamp) VALUES (%s,%s,%s,%s)', start)
            cnx.commit()

            # Secondary program circuit, checks every 3 
            # minutes for vibrations during this time. 
            # If no vibration for the last 3 
            # minutes, cycle considered done.
            while going: 
                
                logging.info("  Inner loop iteration")
                time.sleep(DELAYINSECS)
                global TIME
                TIME = TIME+90
                print("The washing machine is operating for the past {:d} seconds".format(TIME))
                logging.info("  Just slept %ds", DELAYINSECS)
                
                running = ('NULL', TIME, 'running', dt_string)
                cursor.execute('INSERT INTO vibration (id, duration, status, timestamp) VALUES (%s,%s,%s,%s)', running)
                cnx.commit()

                # Manual override to stop the current cycle; 
                # keep push-button
                # pressed during check.
                if GPIO.input(BUTTON):
                    stop = True
                    going = False
                    

                # End of cycle if no vibration detected.
                if not GPIO.event_detected(VIBRATION):
                    logging.info("  Stopped vibrating")
                    print("Your laundry is done")

                    #pushdone()
                    mymessage = "Your laundry is done!"
                    pushdone(mymessage)
                    going = False

                    end = ('NULL', '0', 'stopped', dt_string)
                    cursor.execute('INSERT INTO vibration (id, duration, status, timestamp) VALUES (%s,%s,%s,%s)', end)
                    cnx.commit()
                    
            logging.debug(" End of iteration")

    except Exception as e:
        print('Caught exception:' + str(e))
        logging.warning("Quit on exception")
    finally:
        logging.info("Cleaning up")
        GPIO.remove_event_detect(VIBRATION)
        GPIO.cleanup()

       
if __name__ == '__main__': main()