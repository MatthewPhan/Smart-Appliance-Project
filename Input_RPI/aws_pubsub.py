# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from gpiozero import MCP3008

adc = MCP3008(channel=0)

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
	
host = "a8uqd9rftusd1-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "input-AmazonRootCA1.pem"
certificatePath = "input-certificate.pem.crt"
privateKeyPath = "input-private.pem.key"

my_rpi = AWSIoTMQTTClient("Smart_Appliance_RPI_Input")   # need to use unique client name
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
loopCount = 0
while True:
    """
        The following code is tweaked to generate random number instead of connecting to raspberrypi LDR.
    """
    # light = round(1024-(adc.value*1024))
    import random
    light = random.randint(1, 1024)

    # sending light data to "sensors/light" topic
    my_rpi.publish("smart_appliance/weather", str(light), 1)  
sleep(5)