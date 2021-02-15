from time import sleep
from rpi_lcd import LCD
import RPi.GPIO as GPIO
from gpiozero import Buzzer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Set the keys for the DynamoDB Tables & Global Variables
lcd_dict = {}
wm_dict = {}
rc_dict = {}
degree = u"\u00b0"
buzzer = Buzzer(5)

# AWS Credentials
host = "adbw525tlam09-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "output-AmazonRootCA1.pem"
certificatePath = "output-certificate.pem.crt"
privateKeyPath = "output-private.pem.key"

# AWS Configuration
my_rpi = AWSIoTMQTTClient("Smart_Appliance_RPI_Output")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec


# Custom MQTT message callback and populate data
def customCallback(client, userdata, message):
    print("Received a new message from 'smart_appliance/+': ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

    # Handle weather values
    try:
        data = json.loads(message.payload)
        if data['Temperature'] == None:
            lcd_dict['Temperature'] = 0
        else:
            lcd_dict['Temperature'] = int(data['Temperature'])
    
        if data['Humidity'] == None:
            lcd_dict['Humidity'] = 0
        else:
            lcd_dict['Humidity'] = int(data['Humidity'])
            
        if data['Pressure'] == None:
            lcd_dict['Pressure'] = 0
        else:
            lcd_dict['Pressure'] = int(data['Pressure'])
        print(lcd_dict)
    except KeyError:
        lcd_dict['Temperature'] = 0
        lcd_dict['Humidity'] = 0
        lcd_dict['Pressure'] = 0
        print(lcd_dict)
    
    # Handle washing_machine values
    try:
        data = json.loads(message.payload)
        wm_dict['id'] = data['id']
        wm_dict['status'] = data['status']
        print(wm_dict)
    except KeyError:
        pass

    # Handle remote_control values
    try:
        data = json.loads(message.payload)
        status_value = data['buzzerControl']
        if status_value == "On":
            buzzOn()
        elif status_value == "Off":
            buzzOff()
    except KeyError:
        pass

# Buzzer function
def buzzOn():
    buzzer.on()

def buzzOff():
    buzzer.off()

# retrieve data from DynamoDB and display it in LCD Screen
def retrieveWeatherValues():
    # retrieve lcd_dict values to print in LCD
    try:
        temp = lcd_dict['Temperature']
        humidity = lcd_dict['Humidity']
        pressure = lcd_dict['Pressure'] 
    except KeyError:
        # if no data is published, output all 0
        temp = 0
        humidity = 0
        pressure = 0
    lcd_values = str(temp) + '/' + str(humidity) + '/' + str(pressure)

    # LCD screen output
    lcd = LCD()
    lcd.text('Temp Hum Pres', 1)
    lcd.text(lcd_values, 2)

# alert the buzzer when washing machine program stopped  
def processWashingMachineStatus():
    try:
        status_value = wm_dict["status"]        
        if status_value == "stop":
            buzzOn()
            wm_dict["status"] = ""
    except KeyError:
        pass

# retrieve buzzerControl and control buzzer accordingly
def remoteControlBuzzer():
    try:
        status_value = rc_dict["buzzerControl"]
        print(status_value)
        if status_value == "On":
            buzzOn()
        elif status_value == "Off":
            buzzOff()
    except KeyError:
        pass

# allow us to manually off the buzzer with push-button
def buzzerButton():
    buzzerGPIO = 5
    pushButton = 13

    #GPIO SETUP
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pushButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(buzzerGPIO, GPIO.OUT)
    def button_callback(pushButton):
        print("Button was pushed!")
        GPIO.output(buzzerGPIO,GPIO.LOW)
    try:
        GPIO.add_event_detect(pushButton,GPIO.RISING,callback=button_callback)
    except KeyboardInterrupt: 
        GPIO.cleanup()

def main():
    print("Smart_Appliance_RPI_Output running...")
    my_rpi.connect()
    my_rpi.subscribe("smart_appliance/+", 1, customCallback)
    buzzerButton()
    while True:
        remoteControlBuzzer()
        retrieveWeatherValues()
        processWashingMachineStatus()
        sleep(2) 

if __name__ == "__main__": main()