# Smart-Appliance-Project

## Quick-Start Guide:
1)	First configure the various AWS services and roles (Refer to Section 3 - Software setup instructions) 
2)	Update the credentials file on both the input and output RPi as well as the EC2 webserver
3)	Run weather.py and smart_appliance.py on the input RPI
4)	Run output.py on output RPI
5)	Run populate_s3.py to populate baseline images to the S3 bucket (Note: Baseline images should be in the same folder as well)
6)	Run the ‘sudo -s’ command on the EC2 server before running the server.py file

## Hardware checklist:
-	1 DHT11 sensor
-	1 LED
-	1 LCD screen
-	1 SW-420 Vibration Sensor
-	1 BMP 180 Pressure Sensor
-	1 Buzzer
-	3 Buttons
-	1 Picamera

## Hardware setup instructions:
1)	The SW-420 vibration sensor has 3 pins namely the digital output, GND and VCC pin. The data pin can be used to connect with any GPIO pin and the voltage suitable for the sensor is 3.3V to 5V however it is recommended to use 3.3V. 
2)	The BMP-180 pressure sensor has 4 pins namely the SDA, SCL, GND and VCC pins. Connect the jumper wires accordingly and connect it to the SDA, SCL and GND pins on the breadboard. As for the VCC pin it is also recommended to use 3.3V.

## Fritzing Diagram:


## Software Checklist:
### EC2 Server Configuration 

```bash
sudo yum check-update
sudo yum install -y amazon-linux-extras
sudo amazon-linus-extras enable python3.8
sudo yum clean metadata
sudo yum install python38 -y
```

### EC2 Server and RPIs
```bash
pip install gpiozero
pip install telepot
pip install picamera
Pip install flask
Pip install numpy
Pip install boto3
Pip install AWSIoTPPythonSDK
Pip install paho-mqtt
```

## Software setup instructions:
### A) Register “Smart_Appliance_RPI_Input” Raspberry Pi as a Thing in AWS
  1. Search for IoT-core service and select it.<br />
     ![alt tag](images/image38.png)
  2. In the left navigation pane, click “Manage” to expand it, choose “Things”. Next, click “Create”.
     ![alt tag](images/image9.png)
  3. Select “Create a single thing”.
     ![alt tag](images/image64.png)
  4. Enter the name “Smart_Appliance_RPI_Input”. Click Next.
     ![alt tag](images/image74.png)
  5. Select “Create certificate”.
     ![alt tag](images/image6.png)
  6. Download the following three files:
    • A certificate for this thing
    • A public key
    • A private key
     Then, click “Download” for the root CA.
     ![alt tag](images/image13.png)
  7. You will be presented with the following page. Right-click “Amazon Root CA 1” and select “Save link as” to download this root certificate.
     ![alt tag](images/image27.png)
  8. Then, click the “Activate” button. You should see “Successfully activated certificate” and the Activate button changes to “Deactivate”.
     ![alt tag](images/image71.png)
  9. Click to the next page and select “Register thing”. Upon successfully registering “Smart_Appliance_RPI_Input”, you should see it appear in the table as follows.
     ![alt tag](images/image51.png)
  10. On the left “IoT Core” dashboard, under the “Secure” sub-menu, select “Policies”.


     ![alt tag](images/image78.png)
  11. Select “Create a policy”.
     ![alt tag](images/image16.png)
  12. Create a new Security Policy for our RPIs with the following configurations.
     ![alt tag](images/image28.png)
  13. Click “Create”. The policy would be successfully created.
     ![alt tag](images/image30.png)
  14. Next, we have to attach the security policy to the certificate created for the “Things”. On the left “IoT Core” dashboard, under “Secure” sub-menu, click “Certificates”.
     ![alt tag](images/image65.png)
  15. The X.509 certificate created earlier is shown as follows. Click the triple dot in the certificate and select “Attach policy”.
     ![alt tag](images/image69.png)
  16. Check the “Smart_Appliance_Policy” and click the “Attach” button.
     ![alt tag](images/image22.png)
  17. Next, we have to attach the “Thing” to the certificate. In the certificates page, select the triple dot beside the certificate and click “Attach thing”.
     ![alt tag](images/image34.png)
  18. In the “Attach things to certificate(s)” dialog box, select the check box next to the thing that was created “Smart_Appliance_RPI_Input”, and click “Attach”.
     ![alt tag](images/image37.png)
  19. On the left “IoT Core” dashboard under “Manage” sub-menu, click “Things”.
     ![alt tag](images/image45.png)
  20. On the next screen, select “Interact”. Copy and paste the REST API endpoint of “Smart_Appliance_RPI_Input” into a Notepad as you will need this value later.
     ![alt tag](images/image29.png)

### B) Register “Smart_Appliance_RPI_Output” Raspberry Pi as a Thing in AWS





