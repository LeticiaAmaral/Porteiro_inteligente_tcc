import cv2
import numpy as np
import os
import paho.mqtt.client as paho
import boto3
from boto3.dynamodb.conditions import Key
import pandas as pd
from pandasql import sqldf
import ssl
import mysql.connector

 
def on_connect(client, userdata, flags, rc):               
    print("Resultado Retornado da Conexão: " + str(rc) )
    client.subscribe("#" , 1 )                              
 
def on_message(client, userdata, msg):                      
    print("topic: "+msg.topic)
    print("payload: "+str(msg.payload))

client = boto3.client('dynamodb', region_name='us-east-2')
 
mqttc = paho.Client()                                   
mqttc.on_connect = on_connect                              
mqttc.on_message = on_message                               
awshost = "<xxxxxxxxx-ats.iot.region.amazonaws.com>"      
awsport = 8883                                                      
clientId = "<thingName>"                                     
thingName = "<thingName>"                               
caPath = "/home/pi/certs/AmazonRootCA1.pem"                      
certPath = "/home/pi/certs/certificate.pem.crt"                   
keyPath = "/home/pi/certs/private.pem.key"                         
 
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)      
 
mqttc.connect(awshost, awsport, keepalive=60)              
 
mqttc.loop_start()

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id='aws_access_key_id',
                          aws_secret_access_key='aws_secret_access_key',
                          region_name='region'
)

table = dynamodb.Table('<Table_Name>')S
response = table.scan()
data = response['Items']
df = pd.DataFrame(data)


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX

id = 0

cam = cv2.VideoCapture(0)
cam.set(3, 640) 
cam.set(4, 480) 

minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)
while True:
    ret, img =cam.read()
    img = cv2.flip(img, -1) 
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
        )
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        
        if (confidence < 55):
             id = df.loc[(df.face_id == str(id)),['face_name']].values[0]
             confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "Pessoa Desconhecida"
            confidence = "  {0}%".format(round(100 - confidence))
    
        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
    cv2.imshow('Camera',img) 
    k = cv2.waitKey(10) & 0xff 
    if k == 27:
         break

print("\n [INFO] Fechando o Programa")
cam.release()
cv2.destroyAllWindows()
