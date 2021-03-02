import cv2
import os
import paho.mqtt.client as paho
import os
import socket
import ssl
import random
import string
import json
from time import sleep
from random import uniform
 
connflag = False
 
def on_connect(client, userdata, flags, rc):               
    global connflag
    print ("Conectado a AWS")
    connflag = True
    print("Resultado Retornado da Conexão: " + str(rc) )
 
def on_message(client, userdata, msg):                      
    print(msg.topic+" "+str(msg.payload))
    
    
mqttc = paho.Client()                                       
mqttc.on_connect = on_connect                               
mqttc.on_message = on_message                               
#### Dados para conexao com a AWS #### 
awshost = "a2xkvczx6vsoxz-ats.iot.us-east-1.amazonaws.com"      
awsport = 8883                                                      
clientId = "raspiberry_Client"                                     
thingName = "raspiberry_Client"                                    
caPath = "/home/pi/certs/AmazonRootCA1.pem"                        
certPath = "/home/pi/certs/certificate.pem.crt"                    
keyPath = "/home/pi/certs/private.pem.key"                         
 
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)  # pass parameters
 
mqttc.connect(awshost, awsport, keepalive=60)              
 
mqttc.loop_start()                                    

cam = cv2.VideoCapture(0)
cam.set(3, 640) 
cam.set(4, 480) 

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


face_id = input('\n Informe um Número de ID para o usuário e pressione <ENTER> ==> ')
face_name = input('\n Informe um Nome para o usuário e pressione <ENTER> ==> ')


paylodmsg0="{"
paylodmsg1 = "\"face_id\":\""
paylodmsg2 = "\",\"face_name\":\""
paylodmsg3="\"}"
paylodmsg = "{}{}{}{}{}{}".format(paylodmsg0, paylodmsg1, face_id, paylodmsg2, face_name, paylodmsg3)
paylodmsg = json.dumps(paylodmsg)
print(paylodmsg)
paylodmsg_json = json.loads(paylodmsg)       
mqttc.publish("ElectronicsInnovation", paylodmsg_json , qos=1)       
print("Menssagem enviada para AWS" )
print(paylodmsg_json)

print("\n [INFO] Iniciando a captura de imagens. Olhe para câmera e espere ...")

count = 0

while(True):
    ret, img = cam.read()
    img = cv2.flip(img, -1) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        
        cv2.imwrite("dataset/User." + str(face_id) + '.'+ str(count) + ".jpg", gray[y:y+h,x:x+w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff
    if k == 27:
        break
    elif count >= 60: 
         break

# Do a bit of cleanup
print("\n [INFO] Fechando o Programa")
cam.release()
cv2.destroyAllWindows()
