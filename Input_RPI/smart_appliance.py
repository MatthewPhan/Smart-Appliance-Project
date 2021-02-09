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
    import time
    import httplib
    import urllib               # for push notifications
    import logging             # for debugging
    import sys
    import Adafruit_DHT
    from gpiozero import Buzzer
    from time import sleep
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    import json
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
except RuntimeError:
    print("Error loading RPi.GPIO")


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

# Symbols
degree = u"\u00b0"

# Initialise buzzer
buzzer = Buzzer(5)

def buzzOn():
    while True:
        buzzer.on()
        return "On"

def buzzOff():
    while True:
        buzzer.off()
        return "Off"

# AWS Credentials
host = "adbw525tlam09-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "input-AmazonRootCA1.pem"
certificatePath = "input-certificate.pem.crt"
privateKeyPath = "input-private.pem.key"

# # Set the keys for the DynamoDB Tables
# washing_machine_message_keys = ["deviceid", "id", "Duration", "Status", "Timestamp"]
# weather_keys = ["deviceid", "id", "Temperature", "Humdity", "Pressure", "Timestamp"]

# AWS Configuration
my_rpi = AWSIoTMQTTClient("Smart_Appliance_RPI_Input")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Function to send push notification with pushover.net
def pushdone(bot_message):
    bot_token = '1434600515:AAEPBZLdWkF5cEbaug7QH18jWNgltUw60mQ'
    bot_chatID = '601592207'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

# Telegram Bot Token
telegram_bot = telepot.Bot('1434600515:AAEPBZLdWkF5cEbaug7QH18jWNgltUw60mQ')
print (telegram_bot.getMe())

def action(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print('Received:', command)

    # Connect to AWS DynamoDB "Smart_Appliance_Weather" Table
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    weather_table = dynamodb.Table('Smart_Appliance_Weather')
    washing_machine_table = dynamodb.Table('Smart_Appliance_Washing_Machine')

    if command == '/hi':
        telegram_bot.sendMessage (chat_id, str("Hi Tom & Jerry! What can I do for you?\n" + "/status - check status of washing machine\n" + "/weather - check weather data\n" + "/on - on the buzzer\n"
                                                + "/off - off the buzzer\n" + "/recent - the most recent time you have washed your clothes"))

    elif command == '/status':
        # retrieve weather items
        response = washing_machine_table.query(
            KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
            ScanIndexForward=False
        )
        items = response['Items']
        # Get the latest 'Status'
        n=1
        data = items[:n]
        status_values = data[0]["status"]

        string = "Your washing machine status: " + status_values
        telegram_bot.sendMessage(chat_id, string)

    elif command == '/weather':
        # retrieve weather items
        response = weather_table.query(
            KeyConditionExpression=Key('deviceid').eq('weather_id'),
            ScanIndexForward=False
        )
        items = response['Items']
        # Get the latest 'Temperature', 'Humidity', 'Pressure'.
        n = 1
        data = items[:n]
        print(data)

        Temperature_Value = data[0]['Temperature']
        Humidity_Value = data[0]['Humidity']
        Pressure_Value = data[0]['Pressure']

        global temp
        global humidity
        global pressure

        temp = "Current temperature: " + str(Temperature_Value) + degree + "C"
        humidity = "\nCurrent humidity: " + str(Humidity_Value) + "%"
        pressure = "\nCurrent pressure: " + str(Pressure_Value) + "Pa"

        if Temperature_Value == None:
            temp = "*DHT11 Sensor is unable to sense the temperature."
        if Humidity_Value == None:
            humidity = "\n*DHT11 Sensor is unable to sense the humidity."
        if Pressure_Value == None:
            pressure = "\nBMP180 Sensor is unable to sense the pressure."

        weather_values = temp + '\t' + humidity + '\t' + pressure
        telegram_bot.sendMessage(chat_id, weather_values)

    elif command == '/recent':
        # retrieve washing_machine items
        response = washing_machine_table.query(
            KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
            FilterExpression=Attr('status').eq('start'),
            ScanIndexForward=False
        )
        items = response['Items']
        # Get the latest Timestamp from washing_machine_table
        n = 1
        data = items[:n]
        recent_value = data[0]['timestamp']
        time = "You last washed your clothes on: " + recent_value
        telegram_bot.sendMessage(chat_id, time)

    elif command == '/on':
        buzzOn()

    elif command == '/off':
        buzzOff()

def main():
    # try:
    MessageLoop(telegram_bot, action).run_as_thread()

    # Connect to AWS IoT
    my_rpi.connect()

    # Configure GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(VIBRATION, GPIO.IN)
    GPIO.setup(LED, GPIO.OUT)

    # "Pull-down" resistor must be added to input.
    # push-button to avoid floating value at RPi input when button not in closed circuit.
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Start of sensing of upwards or downwards front on pin connected to vibration detector. 
    # "Bouncetime" argument ignores effect of bouncing caused by sudden state changes.
    GPIO.add_event_detect(VIBRATION, GPIO.BOTH, bouncetime=200)

    # Configure debugging journal file on RPi
    logging.basicConfig(filename='/home/pi/washer.log', 
                        level=logging.INFO, 
                        format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("****************************")
    stop = False
    logging.info("Entering main loop")

    # Retrieve the last ID from "Smart_Appliance_Washing_Machine" Table and set the current loopCount
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Washing_Machine')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
        ScanIndexForward=False
    )
    
    items = response['Items']
    n = 1 
    data = items[:n]
    data_reversed = data[::-1]

    global loopCount
    

    if len(data_reversed) == 0:
        loopCount = 0

    else:
        loopCount = data_reversed[0]['id']


    # Main loop, waits for push-button to be pressed to indicate beginning of cycle, 
    # then periodically checks vibration.
    while not stop:
        loopCount = loopCount + 1

        logging.info("Main loop iteration")

        GPIO.output(LED, True) # LED off
        GPIO.wait_for_edge(BUTTON, GPIO.RISING) # wait for signal from push-button
        logging.info(" Started")
        going = True
        GPIO.output(LED, False) # LED on

        print("The washing machine has started running...")

        washing_machine_message = {}
        washing_machine_message["deviceid"] = 'washing_machine_id'
        washing_machine_message["id"] = float(loopCount)
        washing_machine_message["duration"] = 0
        washing_machine_message["status"] = 'start'
        washing_machine_message["timestamp"] = dt_string

        my_rpi.publish("smart_appliance/washing_machine", json.dumps(washing_machine_message), 1)

        # Secondary program circuit, checks every 3 minutes for vibrations during this time. 
        # If no vibration for the last 3 minutes, cycle considered done.
        while going: 
            loopCount = loopCount + 1
            logging.info("  Inner loop iteration")
            time.sleep(DELAYINSECS)
            global TIME
            TIME = TIME+90
            print("The washing machine is operating for the past {:d} seconds".format(TIME))
            logging.info("  Just slept %ds", DELAYINSECS)
            
            washing_machine_message = {}
            washing_machine_message["deviceid"] = 'washing_machine_id'
            washing_machine_message["id"] = float(loopCount)
            washing_machine_message["duration"] = TIME
            washing_machine_message["status"] = 'running'
            washing_machine_message["timestamp"] = dt_string

            my_rpi.publish("smart_appliance/washing_machine", json.dumps(washing_machine_message), 1)

            # Manual override to stop the current cycle; 
            # keep push-button pressed during check.
            if GPIO.input(BUTTON):
                stop = True
                going = False
                
            # End of cycle if no vibration detected.
            if not GPIO.event_detected(VIBRATION):
                logging.info("  Stopped vibrating")
                print("Your laundry is done")

                mymessage = "Your laundry is done!"
                pushdone(mymessage)
                going = False

                loopCount = loopCount + 1
 
                washing_machine_message = {}
                washing_machine_message["deviceid"] = 'washing_machine_id'
                washing_machine_message["id"] = float(loopCount)
                washing_machine_message["duration"] = TIME
                washing_machine_message["status"] = 'stop'
                washing_machine_message["timestamp"] = dt_string
                my_rpi.publish("smart_appliance/washing_machine", json.dumps(washing_machine_message), 1)

        logging.debug(" End of iteration")

    # except Exception as e:
    #     print('Caught exception:' + str(e))
    #     logging.warning("Quit on exception")
    # finally:
    #     logging.info("Cleaning up")
    #     GPIO.remove_event_detect(VIBRATION)
    #     GPIO.cleanup()

       
if __name__ == '__main__': main()