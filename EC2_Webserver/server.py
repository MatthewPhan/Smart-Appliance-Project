import flask
from flask import Flask, render_template, jsonify, request, Response, redirect, url_for, session
# from gpiozero import Buzzer
from time import sleep

import telepot
from telepot.loop import MessageLoop

import sys
import re
# import picamera 
import socket 
import io 
from importlib import import_module
import os
import json
import numpy
import datetime
import decimal

import time
import httplib
import urllib             
import logging
# import RPi.GPIO as GPIO
import requests
import datetime

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

# import jsonconverter as jsonc
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3
from boto3.dynamodb.conditions import Key, Attr

gevent.monkey.patch_all()  

# # import camera driver
# if os.environ.get('CAMERA'):
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
#     from camera import Camera

app = Flask(__name__)

app.secret_key = '112'

stopped_status_id = ''

# RPI AWS configuration 
host = "adbw525tlam09-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "input-AmazonRootCA1.pem"
certificatePath = "input-certificate.pem.crt"
privateKeyPath = "input-private.pem.key"

my_rpi = AWSIoTMQTTClient("Smart_Appliance_Server")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

my_rpi.connect()


def buzzOn():
    while True:
        buzzer.on()
        return "On"

def buzzOff():
    while True:
        buzzer.off()
        return "Off"        

@app.route("/")
def index():
    return render_template('login.html')

@app.route("/readWeatherValuesAPI", methods = ['POST', 'GET'])
def readWeatherValuesAPI():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Weather')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('weather_id'),
                                
        ScanIndexForward=False
    )

    items = response['Items']
    n=1
    data = items[:n]
    current_dict = {}

    current_temp = data[0]["Temperature"]
    current_hum = data[0]["Humidity"]
    current_press = data[0]["Pressure"]

    current_dict = {'Temperature': str(current_temp), 'Humidity': str(current_hum), 'Pressure': str(current_press)}

    return(jsonify(current_dict))


# Update values in temperature graph
@app.route("/updateTempGraphAPI", methods = ['POST','GET'])
def updateTempGraphAPI():
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Weather')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('weather_id'),
                                
        ScanIndexForward=False
    )

    items = response['Items']
    n=5
    data = items[:n]
    data_reversed = data[::-1]
    labels = list()
    labels_2 = list()

    for i in range(5):
        current_time = data_reversed[i]['Timestamp']
        labels.append(current_time)

    for i in range(5):
        current_temp = data_reversed[i]['Temperature']
        if current_temp == None:
            current_temp = 0
        cast_temp = str(current_temp)
        labels_2.append(cast_temp)

    data_dict = {'labels': labels, 'labels_2': labels_2}
    return(jsonify(data_dict))

# Uppdate values in humidity graph
@app.route("/updateHumidityGraphAPI", methods = ['POST','GET'])
def updateHumidityGraphAPI():

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Weather')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('weather_id'),
                                
        ScanIndexForward=False
    )

    items = response['Items']
    n=5
    data = items[:n]
    data_reversed = data[::-1]
    labels = list()
    labels_3 = list()

    for i in range(5):
        current_time = data_reversed[i]['Timestamp']
        labels.append(current_time)

    for i in range(5):
        current_hum = data_reversed[i]['Humidity']
        if current_hum == None:
            current_hum = 0
        cast_hum = str(current_hum)
        labels_3.append(cast_hum)
    

    data_dict = {'labels': labels, 'labels_3': labels_3}
    return(jsonify(data_dict))


# Update values in pressure graph
@app.route("/updatePressureGraphAPI", methods = ['POST','GET'])
def updatePressureGraphAPI():

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Weather')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('weather_id'),
                                
        ScanIndexForward=False
    )

    items = response['Items']
    n=5
    data = items[:n]
    data_reversed = data[::-1]
    labels = list()
    labels_4 = list()

    for i in range(5):
        current_time = data_reversed[i]['Timestamp']
        labels.append(current_time)

    for i in range(5):
        current_press = data_reversed[i]['Pressure']
        if current_press == None:
            current_press = 0
        cast_press = str(current_press)
        labels_4.append(cast_press)

    data_dict = {'labels': labels, 'labels_4': labels_4}
    return(jsonify(data_dict))


@app.route('/index.html', methods = ['POST', 'GET'])
def reindex():
    # User is loggedin show them the home page

    # Retrieve weather values
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Weather')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('weather_id'),   
        ScanIndexForward=False
    )

    # retrieve latest weather values
    items = response['Items']
    n=1
    data = items[:n]
    values=data[0]

    # Data_2 retrieve 5 of the latest timestamp
    n=5
    data_2 = items[:n]
    data_2_reversed = data_2[::-1]

    labels = list()
    labels.append(data_2_reversed[0]["Timestamp"])
    labels.append(data_2_reversed[1]["Timestamp"])
    labels.append(data_2_reversed[2]["Timestamp"])
    labels.append(data_2_reversed[3]["Timestamp"])
    labels.append(data_2_reversed[4]["Timestamp"])

    # Data_3 is to retrieve tempp, humidity and pressure values 
    data_3 = items[:n]
    data_3_reversed = data_3[::-1]

    labels_2 = list()

    for i in range(5):
        temp = data_3_reversed[i]["Temperature"]
        if temp == None:
            temp = 0
        cast_temp = str(temp)
        labels_2.append(cast_temp)

    labels_3 = list()
    for i in range(5):
        humidity = data_3_reversed[i]["Humidity"]
        if humidity == None:
            humidity = 0
        cast_hum = str(humidity)
        labels_3.append(cast_hum)

    labels_4 = list()
    for i in range(5):
        pressure = data_3_reversed[i]["Pressure"]
        if pressure == None:
            pressure = 0
        cast_press = str(pressure)
        labels_4.append(cast_press)

    return render_template('index.html', values=values, labels=labels, labels_2=labels_2, labels_3=labels_3, labels_4=labels_4)


@app.route('/forms.html', methods=['GET', 'POST'])
# function for adding another user or signing up
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        # Check if account exists 
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Smart_Appliance_Accounts')
        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('accounts_id'),
            ScanIndexForward=False
        )
        items = response['Items']
        n=20
        data = items[:n]
        data_reversed = data[::-1]
        current_id = data_reversed[0]["id"]
        
        for i in range(len(data)):
            email_db = data[i]["email"]

            if email == email_db:
                msg = 'Account already exists!'

            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'

            elif not email or not password:
                msg = 'Please fill out the form!'

            else:
                id = current_id + 1
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                message = {}
                message["deviceid"] = "accounts_id"
                message["id"] = float(id)
                message["email"] = email
                message["password"] = password
                my_rpi.publish("smart_appliance/accounts", json.dumps(message), 1)
                msg = 'You have successfully registered!' 

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('forms.html', msg=msg)

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    msg = '' 
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Smart_Appliance_Accounts')
        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('accounts_id'),
            FilterExpression=Attr('email').eq(email) & Attr('password').eq(password),
            ScanIndexForward=False
        )

        items = response['Items']
        n=1
        data = items[:n]

        # If account exists in accounts table in out database
        if len(data) > 0:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = float(data[0]['id'])
            session['email'] = data[0]['email']
            # Redirect to home page
            return redirect(url_for('reindex'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
            return render_template('login.html', msg=msg)

@app.route('/content_2.html')
def washing_machine():

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Washing_Machine')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
                                
        ScanIndexForward=False
    )

    items = response['Items']
    n=1
    data = items[:n]
    status = data[0]
    
    current_duration = data[0]["duration"]
    minutes = 0
    seconds = 0

    if current_duration < 60:
        seconds = current_duration
    else: 
        minutes = int(current_duration / 60)
        seconds =  current_duration % 60

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Washing_Machine')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
        FilterExpression=Attr('status').eq('start'),                        
        ScanIndexForward=False
    )

    items = response['Items']

    # Get the latest Timestamp from washing_machine_table
    n = 1
    data_2 = items[:n]
    last_run = data_2[0]

    # # store "stopped" id as initial value for comparison with readWashingValuesAPI
    # global stopped_status_id 
    # stopped_status_id = data[0]["id"]
    # print(stopped_status_id)

    return render_template('content_2.html', status=status, last_run=last_run, minutes=minutes, seconds=seconds)

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/readWashingValuesAPI", methods=['GET', 'POST'])
def readWashingValuesAPI():

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Washing_Machine')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
                                
        ScanIndexForward=False
    )

    items = response['Items']
    n=1
    data = items[:n]
    status_value = data[0]["status"]

    current_duration = data[0]["duration"]
    minutes = 0
    seconds = 0

    if current_duration < 60:
        seconds = current_duration
    else: 
        minutes = int(current_duration / 60)
        seconds =  current_duration % 60

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Smart_Appliance_Washing_Machine')
    response = table.query(
        KeyConditionExpression=Key('deviceid').eq('washing_machine_id'),
        FilterExpression=Attr('status').eq('start'),                        
        ScanIndexForward=False
    )

    items = response['Items']
    # Get the latest Timestamp from washing_machine_table
    n = 1
    data_2 = items[:n]
    last_run_values = data_2[0]["timestamp"]

    # # check if washing status is stopped, if so sound the buzzer
    # if status_value == "stopped":
    #     global stopped_status_id
    #     print(stopped_status_id)

    #     # compare ID
    #     current_id = status_value[0]["id"]
    #     print(current_id)

    #     if current_id == stopped_status_id:
    #         buzzOff()

    #     else:
    #         buzzOn()
    #         stopped_status_id = current_id
            

    data_dict = {"status": status_value, "minutes": str(minutes), "seconds":str(seconds), "last_run": last_run_values}
    return(jsonify(data_dict))

@app.route("/controlAlertAPI/<status>", methods = ['POST', 'GET'])
def controlAlertAPI(status):
    if status == 'On':
        message = {}
        message['buzzerControl'] = "On"
        my_rpi.publish("smart_appliance/remotecontrol", json.dumps(message), 1)
        return status
    else:
        message = {}
        message['buzzerControl'] = "Off"
        my_rpi.publish("smart_appliance/remotecontrol", json.dumps(message), 1)
        return status

    


# @app.route('/video_feed')
# def video_feed(): 
#     return Response(gen(Camera()),
#         mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
   try:
        print('Server waiting for requests')
        http_server = WSGIServer(('0.0.0.0', 8001), app)
        app.debug = True
        http_server.serve_forever()
        

   except:
        print("Exception")
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
