from logger import LOG
from keypad import readFromKeyboard
import RPi.GPIO as GPIO
from time import sleep
import threading
from multiprocessing import Process
import pyrebase

FIFO_FILE = "nfc_fifo.tmp"
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

# Load Firebase APP
print("A")
firebase = pyrebase.initialize_app(config)
print("B")
db = firebase.database()

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
  

# Block until writer finishes...
while True:
    white = Process(target=led_coroutine, daemon=True, args=(LED_WHITE,300,0))
    print("Waiting...")
    with open(FIFO_FILE, 'r') as f:
        data = f.read()

    white.start()

    LOG.info("Loaded string from NFC:{}".format(data))
    LOG.debug("Spliting loaded string to array")
    print(data)

    # Split data into an array
    array = [x for x in data.split()]
    print(array)
    
    nfcRecord = NfcRecord(''.join(array[:2]), \
                          ''.join(array[-2:]), \
                          ''.join(array[2]), \
                          ''.join(array[3:-6]), \
                          int(''.join(array[19:-2]),16))

    users = db.child("users").get()
    user = db.child("users").order_by_child("nid").equal_to(nfcRecord.nID).get().val()

    for x in users.val():
        print(users.val()[x]["nid"])
        print(nfcRecord.nID)
        if(users.val()[x]["nid"] == nfcRecord.nID):
            userDictionary = users.val()[x]
            print("DISPLEJ - Zadaj PIN")
            LOG.info("ID is in database.")
            LOG.info("Waiting for keyboard INPUT from keyboard")

            for i in range(NUMBER_OF_PIN_ATTEMPTS):
                LOG.info("Loaded PIN")
                if(userDictionary["pin"] == readFromKeyboard()):
                    LOG.info("Authorization successful, User:{}".format(userDictionary["name"]))
                    print("DISPLEJ - Autorizacia uspesna!")
                    blink(LED_GREEN,300,5)
                    break
                else:
                    LOG.info("Authorization unsuccessful User: {}, Attempt: {}/{}".format(userDictionary["name"], \
                                                                                              i+1, \
                                                                                              NUMBER_OF_PIN_ATTEMPTS))
                    print("DISPLEJ - Autorizacia neuspesna! Pokus {} z {}".format(i+1, \
                                                                                  NUMBER_OF_PIN_ATTEMPTS))
                    blink(LED_RED,200,3)


        else:
            LOG.info("User not found in database!")
            print("DISPLEJ - Pouzivatel neexistuje!")

    white.terminate()
    GPIO.output(LED_WHITE,False)



