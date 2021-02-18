import os
import RPi.GPIO as GPIO
import boto3
import botocore
from picamera import PiCamera
from time import sleep
import json
import io
from PIL import Image

BUTTON = 5

# Function for taking picture
def takePhoto(file_path,file_name):
    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        full_path = file_path + "/" + file_name
        camera.capture(full_path)
        sleep(3)

def faceMap(image_path):
    rekognition = boto3.client('rekognition', region_name='us-east-1')
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
    image = Image.open(image_path)
    stream = io.BytesIO()
    image.save(stream,format="JPEG")
    image_binary = stream.getvalue()
    response = rekognition.search_faces_by_image(
        CollectionId='family_collection',
        Image={'Bytes':image_binary}                                       
        )

    for match in response['FaceMatches']:
        print (match['Face']['FaceId'],match['Face']['Confidence'])
            
        face = dynamodb.get_item(
            TableName='family_collection',  
            Key={'RekognitionId': {'S': match['Face']['FaceId']}}
            )
        
        if 'Item' in face:
            print (face['Item']['FullName']['S'])
            # send telegram msg withh the user name
        else:
            print ('no match found in person lookup')

def faceDetectionButton():
    #GPIO SETUP
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def button_callback(BUTTON):
        # Set the filename and bucket name
        BUCKET = 'smart-appliance-bucket'
        location = {'LocationConstraint': 'us-east-1'}
        file_path = os.getcwd()
        file_name = "/image.jpeg"
        # print(file_path + file_name)
        print("Taking picture and uploading to Rekognition...SAY CHEESE!")
        takePhoto(file_path, file_name)
        faceMap(file_path + file_name)
        os.remove(file_path + file_name)
    try:
        # check if button is pushed, if so run the button_callback function
        GPIO.add_event_detect(BUTTON,GPIO.RISING,callback=button_callback)
    except KeyboardInterrupt: 
        GPIO.cleanup()

def main():
    print("main function running")
    faceDetectionButton()
    while True:
        sleep(1)
        
    
if __name__ == '__main__': main()
