import flask
from flask import Flask, render_template, jsonify, request, Response, redirect, url_for, session
from gpiozero import Buzzer
from time import sleep

from flask_mysqldb import MySQL
from flask import Markup
import MySQLdb.cursors

import telepot
from telepot.loop import MessageLoop

import mysql.connector
import sys
import re
import picamera 
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
import RPi.GPIO as GPIO
import requests
import datetime

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()  

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

app = Flask(__name__)

app.secret_key = '112'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'iotuser'
app.config['MYSQL_PASSWORD'] = 'dmitiot'
app.config['MYSQL_DB'] = 'iotdatabase'

# Intialize MySQL
mysql = MySQL(app)

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

@app.route("/")
def index():
    
    return render_template('login.html')

@app.route('/index.html', methods = ['POST', 'GET'])
def reindex():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # Retrieve weather values
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM weather ORDER BY id DESC LIMIT 1')
        values = cursor.fetchone()
        print(values)

        cursor.execute('SELECT timestamp FROM weather ORDER BY id DESC LIMIT 5')
        rows = cursor.fetchall()
        rows_values = [iter_item for iter_item in map(lambda item: ([item[key]
                                          for key in item.keys()]), rows)]

        labels = list()
        labels.append(rows_values[0])
        labels.append(rows_values[1])
        labels.append(rows_values[2])
        labels.append(rows_values[3])
        labels.append(rows_values[4])

        cursor.execute('select convert(temperature, char(50)) as temperature from weather order by id desc limit 5;')
        temp = cursor.fetchall()
        temp_values = [iter_item for iter_item in map(lambda item: ([item[key]
                                          for key in item.keys()]), temp)]
        labels_2 = list()
        labels_2.append(temp_values[0])
        labels_2.append(temp_values[1])
        labels_2.append(temp_values[2])
        labels_2.append(temp_values[3])
        labels_2.append(temp_values[4])
      
        print(labels_2)

        cursor.execute('select convert(humidity, char(50)) as humidity from weather order by id desc limit 5;')
        hum = cursor.fetchall()
        hum_values = [iter_item for iter_item in map(lambda item: ([item[key]
                                          for key in item.keys()]), hum)]
        labels_3 = list()
        labels_3.append(hum_values[0])
        labels_3.append(hum_values[1])
        labels_3.append(hum_values[2])
        labels_3.append(hum_values[3])
        labels_3.append(hum_values[4])
        print(labels_3)

        cursor.execute('select convert(pressure, char(50)) as pressure from weather order by id desc limit 5;')
        press = cursor.fetchall()
        press_values = [iter_item for iter_item in map(lambda item: ([item[key]
                                          for key in item.keys()]), press)]
        labels_4 = list()
        labels_4.append(press_values[0])
        labels_4.append(press_values[1])
        labels_4.append(press_values[2])
        labels_4.append(press_values[3])
        labels_4.append(press_values[4])
        print(labels_4)

        return render_template('index.html', email=session['email'], values=values, labels=labels, labels_2=labels_2, labels_3=labels_3, labels_4=labels_4)

    # User is not loggedin redirect to login page
    return redirect(url_for('login.html'))
    


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
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not email or not password:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s)', (email, password,))
            mysql.connection.commit()
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
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            # Redirect to home page
            return redirect(url_for('reindex'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
            return render_template('login.html', msg=msg)

@app.route('/content_2.html')
def washing_machine():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM vibration ORDER BY id DESC LIMIT 1')
    status = cursor.fetchone()
    print(status)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT duration FROM vibration ORDER BY id DESC LIMIT 1')
    columns = cursor.fetchone()
    integer = columns.values()
    number = integer[0]
    minutes = 0
    seconds = 0

    if number < 60:
        seconds = number
    else: 
        minutes = number / 60
        seconds =  number % 60

    cursor.execute("select * from vibration where status = 'start' order by id desc limit 1;")
    last_run = cursor.fetchone()
    print(last_run)

    return render_template('content_2.html', status=status, last_run=last_run, minutes=minutes, seconds=seconds)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/writeLED/<status>")
def writePin(status):

   if status == 'On':
     response = buzzOn()
   else:
     response = buzzOff()

   return response


@app.route('/video_feed')
def video_feed(): 
    return Response(gen(Camera()),
        mimetype='multipart/x-mixed-replace; boundary=frame')


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
