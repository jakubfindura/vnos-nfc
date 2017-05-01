from logger import LOG
from keypad import readFromKeyboard
from time import sleep
from RPLCD.i2c import CharLCD


from multiprocessing import Process
import datetime
import RPi.GPIO as GPIO
import threading
import pyrebase
import json
import time

FIFO_FILE = "nfc_fifo.tmp"
AUDIT_FILE = "arrays.json"
NUMBER_OF_PIN_ATTEMPTS = 3

LED_WHITE = 19
LED_RED = 21
LED_GREEN = 23


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

def lcd_init():
  print("LCD INIT")
  lcd = CharLCD(0x3f)
  lcd.clear()
  return lcd

def lcd_print(string, row=0, col=0):
  lcd.cursor_pos = (row,col)
  if( len(string) > 16 ):
    raise Exception("To many characters")
  lcd.write_string(string)

lcd = None
lcd = lcd_init()
# Block until writer finishes...
while True:
    #LOG.debug("Waiting for communication...")
    white = Process(target=led_coroutine, daemon=True, args=(LED_WHITE,300,0))
    lcd.clear()
    lcd_print("Prilozte kartu", 0, 0)
    LOG.debug("Waiting for communication...")
    with open(FIFO_FILE, 'r') as f:
        data = f.read()

    white.start()
    lcd_print("Autentifikujem", 0, 0)
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
    authenticated = False

    if(user.each() == []):
      lcd_print("Pouzivatel      ", 0, 0)
      lcd_print(" neexistuje!    ", 1, 0)
      print("DISPLEJ - Pouzivatel neexistuje!")
      LOG.debug("User not found in database!")
    else:
      userValues = user.each()[0].val()

      outputJson = [datetime.datetime.now().isoformat(),
                    userValues['name'],
                    userValues['email'],
                    user.each()[0].key(),
                    "False"]

      print("DISPLEJ - Zadaj PIN")
      LOG.debug("ID is in database.")
      LOG.debug("Waiting for keyboard INPUT...")

      for i in range(NUMBER_OF_PIN_ATTEMPTS):
        lcd_print("Zadaj PIN({}/3): ".format(i+1), 1, 0)
        loadedPin = readFromKeyboard()
        LOG.debug("Loaded PIN:{}".format(loadedPin))


        if(userValues["pin"] == loadedPin):
          outputJson[4] = "True"
          appendAuditJson(outputJson)
          LOG.debug("Authorization successful, User:{}".format(userValues["name"]))
          print("DISPLEJ - Autorizacia uspesna!")
          
          authenticated = True
          break
        else:
          appendAuditJson(outputJson)
          LOG.debug("Authorization unsuccessful User: {}, Attempt: {}/{}".format(userValues["name"], \
                                                                                    i+1, \
                                                                                    NUMBER_OF_PIN_ATTEMPTS))
          print("DISPLEJ - Autorizacia neuspesna! Pokus {} z {}".format(i+1, \
                                                                        NUMBER_OF_PIN_ATTEMPTS))
          lcd_print("Zly PIN         ", 1, 0)
          sleep(1)
          blink(LED_RED,200,3)
      else:
        authenticated = False                                                          

    white.terminate()

    if authenticated:
      blink(LED_GREEN,300,5)
      lcd_print("Autorizacia     ", 0, 0)
      lcd_print(" uspesna!       ", 1, 0)
      sleep(2)
      lcd_print("Otvaram dvere   ", 0, 0)
      lcd_print("                ", 1, 0)
      sleep(1)
    else:
      blink(LED_RED,300,5)
      lcd_print("Autorizacia     ")
      lcd_print(" neuspesna!!!   ", 1, 0)
      sleep(2)
      
    GPIO.output(LED_WHITE,False)

