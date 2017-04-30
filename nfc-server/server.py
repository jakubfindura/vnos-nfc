from logger import LOG
from keypad import readFromKeyboard
import pyrebase
import json
import time
import datetime

import RPi.GPIO as GPIO
from time import sleep
from multiprocessing import Process

FIFO_FILE = "nfc_fifo.tmp"
AUDIT_FILE = "arrays.json"
NUMBER_OF_PIN_ATTEMPTS = 3

LED_WHITE = 19
LED_RED = 21
LED_GREEN = 23

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_GREEN,GPIO.OUT)
GPIO.setup(LED_RED,GPIO.OUT)
GPIO.setup(LED_WHITE,GPIO.OUT)

def led_coroutine(LED_GPIO, delay, count):
  print("CORO {}".format(LED_GPIO))
  if count > 0 :
    for x in range(1,count+1):
      GPIO.output(LED_GPIO,True)
      sleep(delay/1000/2)
      GPIO.output(LED_GPIO,False)
      sleep(delay/1000/2)
  else:
    while True:
      GPIO.output(LED_GPIO,True)
      sleep(delay/1000/2)
      GPIO.output(LED_GPIO,False)
      sleep(delay/1000/2)

  GPIO.output(LED_GPIO,False)

def blink(led,delay=200,count=5):
  t = Process(target=led_coroutine, daemon=True, args=(led,delay,count))
  t.start()

config = {
  "apiKey": "AIzaSyDOHduR778EpMt98zEVyg42vjKKhIkhPas",
  "authDomain": "vnos-nfc.firebaseapp.com",
  "databaseURL": "https://vnos-nfc.firebaseio.com/",
  "storageBucket": "vnos-nfc.appspot.com"
}

class NfcRecord:
    def __init__(self, preamble, msgType, postamble, nID, timestamp):
         self.preamble = preamble
         self.msgTyoe = msgType
         self.postamble = postamble
         self.nID = nID
         self.timestamp = timestamp


def appendAuditJson(jsonAudit):
  with open(AUDIT_FILE, mode='r', encoding='utf-8') as feedsjson:
    feeds = json.load(feedsjson)
  with open(AUDIT_FILE, mode='w', encoding='utf-8') as feedsjson:
    feeds['data'].append(jsonAudit)
    json.dump(feeds, feedsjson)

# Load Firebase APP
firebase = pyrebase.initialize_app(config)
db = firebase.database()
LOG.debug("Firebase loaded")

# Block until writer finishes...
while True:
    white = Process(target=led_coroutine, daemon=True, args=(LED_WHITE,300,0))

    LOG.debug("Waiting for communication...")
    with open(FIFO_FILE, 'r') as f:
        data = f.read()

    white.start()
    LOG.debug("Loaded string from NFC:{}".format(data))
    LOG.debug("Spliting loaded string to array")

    # Split data into an array
    array = [x for x in data.split()]

    
    nfcRecord = NfcRecord(''.join(array[:2]), \
                          ''.join(array[-2:]), \
                          ''.join(array[2]), \
                          ''.join(array[3:-6]), \
                          int(''.join(array[19:-2]),16))

    LOG.debug("NID received: {}".format(nfcRecord.nID))

    user = db.child("users").order_by_child("nid").equal_to(nfcRecord.nID).get()
    if(user.each() == []):
        print("DISPLEJ - Pouzivatel neexistuje!")
        LOG.debug("User not found in database!")
    else:
      userValues = user.each()[0].val()

      outputJson = {'Timestamp': datetime.datetime.now().isoformat(),
                    'Username': userValues['name'],
                    'E-Mail': userValues['email'],
                    'FirebaseID': user.each()[0].key(),
                    'Action':'False'}

      print("DISPLEJ - Zadaj PIN")
      LOG.debug("ID is in database.")
      LOG.debug("Waiting for keyboard INPUT...")
      for i in range(NUMBER_OF_PIN_ATTEMPTS):
        loadedPin = readFromKeyboard()
        LOG.debug("Loaded PIN:{}".format(loadedPin))

        if(userValues["pin"] == loadedPin):
          outputJson["Action"] = "True"
          appendAuditJson(outputJson)
          LOG.debug("Authorization successful, User:{}".format(userValues["name"]))
          print("DISPLEJ - Autorizacia uspesna!")
          blink(LED_GREEN,300,5)
          break
        else:
          appendAuditJson(outputJson)
          LOG.debug("Authorization unsuccessful User: {}, Attempt: {}/{}".format(userValues["name"], \
                                                                                    i+1, \
                                                                                    NUMBER_OF_PIN_ATTEMPTS))
          print("DISPLEJ - Autorizacia neuspesna! Pokus {} z {}".format(i+1, \
                                                                      NUMBER_OF_PIN_ATTEMPTS))
          blink(LED_RED,200,3)

    white.terminate()
    GPIO.output(LED_WHITE,False)

    LOG.debug("Authorization finished. User not logged in!!!")
    blink(LED_RED,300,5)

