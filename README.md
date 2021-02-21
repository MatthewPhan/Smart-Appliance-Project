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
![alt tag](images/CA2_Assignment_Fritzing_Diagram.png)

## System Architecture Diagram:
![alt tag](images/Official_Smart_Appliance_System_Architecture.png)

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
  1. Search for IoT-core service and select it

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
    
  11. Next, we have to attach the security policy to the certificate created for the “Things”. On the left “IoT Core” dashboard, under “Secure” sub-menu, click “Certificates”.
  
![alt tag](images/image65.png)

  12. The X.509 certificate created earlier is shown as follows. Click the triple dot in the certificate and select “Attach policy”.

![alt tag](images/image69.png)

  13. Check the “Smart_Appliance_Policy” and click the “Attach” button.
 
![alt tag](images/image22.png)

  14. Next, we have to attach the “Thing” to the certificate. In the certificates page, select the triple dot beside the certificate and click “Attach thing”.
 
![alt tag](images/image34.png)
    
  15. In the “Attach things to certificate(s)” dialog box, select the check box next to the thing that was created “Smart_Appliance_RPI_Input”, and click “Attach”.
![alt tag](images/image37.png)

  16. On the left “IoT Core” dashboard under “Manage” sub-menu, click “Things”.

![alt tag](images/image45.png)
     
  17. On the next screen, select “Interact”. Copy and paste the REST API endpoint of “Smart_Appliance_RPI_Input” into a Notepad as you will need this value later.

![alt tag](images/image29.png)

### B) Register “Smart_Appliance_RPI_Output” Raspberry Pi as a Thing in AWS
The following steps are similar to Section A but with certain tweaks.
  1. Search for IoT-core service and select it.
 
  2. In the left navigation pane, click “Manage” to expand it, choose “Things”. Next, click “Create”.

  3. Select “Create a single thing”.

  4. Enter the name “Smart_Appliance_RPI_Output”. Click Next.

 ![alt tag](images/image75.png)
 
  5. Select “Create certificate”
 
  6. Download the following three files:
      a. A certificate for this thing
      b. A public key
      c. A private key
      Then, click “Download” for the root CA.
    
  7. You will be presented with the following page. Right-click “Amazon Root CA 1” and select “Save link as” to download this root certificate.

  8. Then, click the “Activate” button. You should see “Successfully activated certificate” and the Activate button changes to “Deactivate”.

  9. Click to the next page and select “Register thing”. Upon successfully registering “Smart_Appliance_RPI_Output”, you should see it appear in the table as follows.

![alt tag](images/image32.png)

  10. Next, we have to attach the security policy to the certificate created for the “Things”. On the left “IoT Core” dashboard, under “Secure” sub-menu, click “Certificates”.
 
  11. The X.509 certificate created earlier is shown as follows. Note that you should select the certificate created for “Smart_Appliance_RPI_Output”. Click the triple dot in the certificate and select “Attach policy”.
  
![alt tag](images/image39.png)
     
  12. Check the “Smart_Appliance_Policy” and click the “Attach” button.
  
![alt tag](images/image47.png)
    
  13. Next, we have to attach the Output RPI “Thing” to the certificate. In the certificates page, select the triple dot beside the Output RPI certificate and click "Attach Thing"
 
![alt tag](images/image42.png)
    
  14. In the “Attach things to certificate(s)” dialog box, select the check box next to the thing that was created “Smart_Appliance_RPI_Output”, and click “Attach”.

![alt tag](images/image41.png)
     
  15. Next, on the left “IoT Core” dashboard under “Manage” sub-menu, click “Things”.
 
  16. On the next screen, select “Interact”. Copy and paste the REST API endpoint of
“Smart_Appliance_RPI_Output” into a Notepad as you will need this value later.

![alt tag](images/image63.png)

### C) Creation of DynamoDB Tables
  1. Open the Amazon DynamoDB console and click “Create Table”.
 
![alt tag](images/image46.png)
    
  2. Create the Table “Smart_Appliance_Weather” with the following configuration:
 
![alt tag](images/image57.png)
   
  3. Create the Table “Smart_Appliance_Washing_Machine” with the following configuration:
 
![alt tag](images/image76.png)
    
  4. Create the Table “Smart_Appliance_Accounts” with the following configuration:
  
![alt tag](images/image3.png)
     
### D) Creation of DynamoDB Rules and Roles for each Tables
  1. On the left “IoT Core” dashboard, under “Act” sub-menu, click “Rules”.
  
![alt tag](images/image26.png)
     
  2. First, create the “DynamoDB_Weather_Rule” with the following configurations:
  
![alt tag](images/image56.png)
![alt tag](images/image20.png)

  3. Select “Add action”.
 
![alt tag](images/image55.png)
     
  4. Select “Split message into multiple columns of a DynamoDB table (DynamoDBv2)”.

![alt tag](images/image73.png)
     
  5. Select the “Configure Action” button, and choose the Table Name “Smart_Appliance_Weather” for this rule. Click “Add action”.
 
![alt tag](images/image62.png)

  6. Next, click “Create Rule”. Upon successful creation, you can see the rule created as follows.

![alt tag](images/image61.png)

  7. Next, create the rule for the Smart_Appliance_Accounts table. Create the “DynamoDB_Weather_Rule” with the following configurations:

![alt tag](images/image7.png)
![alt tag](images/image81.png)

  8. Select “Add action” and choose “Split message into multiple columns of a DynamoDB table (DynamoDBv2)” (refer to Step 4).

  9. Select the “Configure Action” button, and choose the Table Name “Smart_Appliance_Accounts” for this rule. Click “Add action”.
 
![alt tag](images/image15.png)
     
  10. Next, click “Create Rule”. Upon successful creation, you can see the rule created as follows.
  
![alt tag](images/image14.png)
     
  11. Lastly, create the rule for the Smart_Appliance_Washing_Machine table. Create the “DynamoDB_Weather_Rule” with the following configurations:
 
![alt tag](images/image59.png)

![alt tag](images/image12.png)

  12. Select “Add action” and choose “Split message into multiple columns of a DynamoDB table (DynamoDBv2)” (refer to Step 4).

  13. Select the “Configure Action” button, and choose the Table Name “Smart_Appliance_Washing_Machine” for this rule. Click “Add action”.
 
![alt tag](images/image18.png)
     
  14. Next, click “Create Rule”. Upon successful creation, you can see the rule created as follows.
  
![alt tag](images/image83.png)

### E) EC2 Set-Up
  1. Navigate to EC2 service in the AWS console

![alt tag](images/image24.png)

  2. Find the Launch Instance section in the EC2 dashboard and clock on the orange button to “Launch Instance”.

![alt tag](images/image52.png)

  3. Select ‘Amazon Linux 2 AMI (HVM)’ and choose the option for 64-bit (x86)

![alt tag](images/image58.png)

  4. For the next step, select ‘t2.micro’ for the instance type. Then click the button ‘Next: Configure Instance Details’ below.

![alt tag](images/image36.png)

  5. For configuring instance details, enable the “Auto-assign Public IP” option. Then scroll down to find the “Advanced Details” section and enter the following commands in the “User data” text box. Once done, click the “Next: Add storage” button below the webpage.

![alt tag](images/image54.png)
![alt tag](images/image1.png)

  6. In “Step 4: Add Storage”, do not make any changes and leave everything as default. Click the “Next: Add Tags” button below.

![alt tag](images/image53.png)

  7. In “Step 5: Add Tags”, click the “Add Tag” button. Input the key and value according to the table shown below. Once done, click the “Next: Configure Security Group” button.

![alt tag](images/image79.png)

  8. In “Step 6: Configure Security Group”. Enable the option “Create a new security group” and input the “Security group name” and “description” text box with the following values:

![alt tag](images/image21.png)

  9. Add a rule on top of the default rule. Specify its “Type”, “Protocol”, “Port Range” and “Source” as follows:

![alt tag](images/image77.png)

  10. Finally, click the “Review and Launch” button where you will brought to a page that displays a summary of your configurations for your instance. Lastly, click the “Launch” button.

![alt tag](images/image80.png)

  11. You will be asked to select an existing key pair or create a new one. Choose the option “Create a new key pair” and specify the key pair name as “Key pair for python web server”. Click the button “Download the key pair” and save the file in a known folder. The key will be used to SSH into the web server. Once downloaded, click “Launch Instances”.

![alt tag](images/image49.png)

  12. The instance will then be launched and you will be able to view the instance in the EC2 dashboard.

![alt tag](images/image67.png)

  13. Connecting to EC2 via WinSCP
  14. Download the needed dependencies
  15. Steps to run which python program

### F) Creation of S3 bucket
  1. Open the S3 service in AWS console and click on “Create bucket”

![alt tag](images/image2.png)

  2. Type “Smart-Appliance-Bucket” as name and select AWS region as “US East 1 (North Virginia)”. Use the default values for the rest of the option. FInally, click the “Create Bucket” button.

![alt tag](images/image68.png)

  3. The bucket is then created on the S3 console as shown below

![alt tag](images/image5.png)

### G) Configure AWS Rekognition and S3
  1. Configure AWS rekognition to allow us manage collection containers (which is stores the
face feature vectors)
  ```bash
  aws rekognition create-collection --collection-id family_collection --region us-east-1
  ```
  2.  Create a DynamoDB Table to maintain a reference of the FaceID returned from Rekognition and the full name of the person.
  ```bash
     aws dynamodb create-table --table-name family_collection \
    attribute-definitions
    AttributeName=RekognitionId,AttributeType=S \ --key-schema
    AttributeName=RekognitionId,KeyType=HASH \
    --provisioned-throughput
    ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --region us-east-1
  ```
  
  3. Create a bucket to store the images
  ```
    aws s3 mb s3://smart-appliance-bucket --region us-east-1
  ```
  4. Create a trust and access policy. Note that you should replace aws-region, account-id, and the actual name of the resources (e.g., bucket-name and family_collection) with the name of the resources in your environment.
  - These two policies allows the AWS Lambda Role (created in step 5) to
    a) to access the objects from Amazon S3,
    b) initiate the IndexFaces function of Amazon Rekognition,
    c) create multiple entries within our Amazon DynamoDB key-value store for a mapping between the FaceId and the person’s full name.
  - trust-policy.json

![alt tag](images/image4.png)

  - access-policy.json

![alt tag](images/image25.png)
  
  5. Create an IAM service role for AWS Lambda, by the following two commands:
```
    aws iam create-role --role-name LambdaRekognitionRole --
    assume-role-policy-document trust-policy.json

    aws iam put-role-policy --role-name LambdaRekognitionRole --
    policy-name LambdaPermissions --policy-document accesspolicy.json
```

### H) Configure AWS Lambda for Face-Mapping Detection
  Create the Lambda function that is triggered every time a new picture is uploaded to Amazon S3. Create the function using the Author from scratch option.
  1. Search for “Lambda” in the AWS console and select it.
  2. Enter the following field:

![alt tag](images/image43.png)

  3. As seen below, the Lambda function role is created.

![alt tag](images/image31.png)

  4. Select “Add trigger”.

![alt tag](images/image82.png)

  5. On the configure triggers page, select S3, and the name of your bucket as the trigger. Then configure the Event type and Prefix as shown in the following example. This ensures that your Lambda function is triggered only when new objects that start with a key matching the index/pattern are created within the bucket. Remember to check the “I acknowledge..”.

![alt tag](images/image70.png)

  6. Copy and Paste the Lambda_Facemapping.py from into the Function Code.
  7. Select “Deploy”. Upon successful deployment, “Changes deployed” would be listed.

![alt tag](images/image11.png)

  8. Select the “Permission” tab, and click “Edit”.

![alt tag](images/image40.png)

  9. Change the “Existing role”, with the Role we created earlier (LambdaRekognitionRole). Click “Save”.

![alt tag](images/image50.png)

 ### I) Create an AWS SNS Topic, Subscribe and Create SNS Rule
  1. Search the Amazon AWS console for the SNS service, choose “Topics” at the sidebar and select “Create Topic”.

![alt tag](images/image44.png)

  2. Choose “Standard” and enter the topic name and display name.

![alt tag](images/image66.png)

  3. Take note of the ARN of the topic that is just created.

![alt tag](images/image60.png)

  4. On the same page, select the button “Create subscription”

![alt tag](images/image33.png)

  5. Under “Create subscription”, select “email” as the option under Protocol. Type in the email account in the endpoint as follows (Note: The email account can be your personal email however our group decided to create a new email for this assignment):

![alt tag](images/image19.png)

  6. Head over to the Gmail account and confirm the subscription. Successful confirmation would look like the following picture

![alt tag](images/image48.png)

  7. In the AWS IoT console, in the left navigation pane, choose “Act”, then “Create a rule”
  8. On the Create a rule page, enter the following:

![alt tag](images/image10.png)
![alt tag](images/image23.png)

  9. In ‘Set one or more actions’, choose Add action.
  10. On the Select an action page, select ‘Send a message as an SNS push notification’, and then click ‘Configure action’.

![alt tag](images/image72.png)

  11. On the Configure action page, from the SNS target drop-down list, choose the Amazon SNS topic created earlier ‘forgotpassword’.

![alt tag](images/image8.png)

  12. On the Configure action page, create a new role for this rule

![alt tag](images/image35.png)

  13. Choose Add action.
  14. Choose Create rule.
  15. On the Overview page for the rule, choose the left arrow to return to the AWS IoT dashboard.
  















  














     
 







