# Smart-Appliance-Project

Quick-Start Guide:
1)	First configure the various AWS services and roles (Refer to Section 3 - Software setup instructions) 
2)	Update the credentials file on both the input and output RPi as well as the EC2 webserver
3)	Run weather.py and smart_appliance.py on the input RPI
4)	Run output.py on output RPI
5)	Run populate_s3.py to populate baseline images to the S3 bucket (Note: Baseline images should be in the same folder as well)
6)	Run the ‘sudo -s’ command on the EC2 server before running the server.py file

Hardware checklist:
-	1 DHT11 sensor
-	1 LED
-	1 LCD screen
-	1 SW-420 Vibration Sensor
-	1 BMP 180 Pressure Sensor
-	1 Buzzer
-	3 Buttons
-	1 Picamera

Hardware setup instructions:
1)	The SW-420 vibration sensor has 3 pins namely the digital output, GND and VCC pin. The data pin can be used to connect with any GPIO pin and the voltage suitable for the sensor is 3.3V to 5V however it is recommended to use 3.3V. 
2)	The BMP-180 pressure sensor has 4 pins namely the SDA, SCL, GND and VCC pins. Connect the jumper wires accordingly and connect it to the SDA, SCL and GND pins on the breadboard. As for the VCC pin it is also recommended to use 3.3V.

Fritzing Diagram:


Software Checklist:
EC2 Server Configuration 

```bash
sudo yum check-update
sudo yum install -y amazon-linux-extras
sudo amazon-linus-extras enable python3.8
sudo yum clean metadata
sudo yum install python38 -y

EC2 Server and RPIs
-	pip install gpiozero
-	pip install telepot
-	pip install picamera
-	Pip install flask
-	Pip install numpy
-	Pip install boto3
-	Pip install AWSIoTPPythonSDK
-	Pip install paho-mqtt


Software setup instructions:

