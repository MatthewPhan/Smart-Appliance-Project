import Adafruit_BMP.BMP085 as BMP085
import sys
import Adafruit_DHT
import datetime
from datetime import date, datetime, timedelta
import time
from time import sleep
from rpi_lcd import LCD
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import boto3
from boto3.dynamodb.conditions import Key, Attr


# Set global variable
last_id = ''

bmp180Sensor = BMP085.BMP085()
pin = 19

# Grab weather values
degree = u"\u00b0"

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

def main():

    try:

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Smart_Appliance_Weather')

        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('weather_id'),
                                
            ScanIndexForward=False
        )

        items = response['Items']

        n=1 # limit to last 10 items
        data = items[:n]
        data_reversed = data[::-1]
        
        global last_id

        if len(data_reversed) == 0:
            last_id = 0
        else:
            last_id = data_reversed[0]["id"]

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

    
    host = "adbw525tlam09-ats.iot.us-east-1.amazonaws.com"
    rootCAPath = "input-AmazonRootCA1.pem"
    certificatePath = "input-certificate.pem.crt"
    privateKeyPath = "input-private.pem.key"

    my_rpi = AWSIoTMQTTClient("Matthew_1828328")   # need to use unique client name
    my_rpi.configureEndpoint(host, 8883)
    my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
    my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
    my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    my_rpi.connect()
    my_rpi.subscribe("smart_appliance/weather", 1, customCallback)    # retrieving light data from AWS broker's "smart_appliance/weather" topic to subscriber
    sleep(2)

    # Publish to the same topic in a loop forever
    if last_id == 0:
        loopCount = 0

    else:
        loopCount = last_id

    while True:
        # Set datetime string
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        humidity, temperature = Adafruit_DHT.read_retry(11, pin)
        presBMP = bmp180Sensor.read_pressure() # absolute pressure in hPa
        print('DHT11 Sensor Readings:')
        print('\tTemp: {} C'.format(temperature))
        print('\tHumidity: {}'.format(humidity))
        print('BMP Pressure Sensor Readings:')
        print('\tPressure = {} hPa [or mbar]'.format(presBMP))
        print('Recorded on: {}'.format(dt_string))

        loopCount = float(loopCount) + 1

        message = {}
        message["deviceid"] = "weather_id"
        message["id"] = float(loopCount)   
        message["Temperature"] = temperature
        message["Humidity"] = humidity
        message["Pressure"] = presBMP
        message["Timestamp"] = dt_string  

        my_rpi.publish("smart_appliance/weather", json.dumps(message), 1)

        sleep(5)

if __name__ == '__main__': main()
