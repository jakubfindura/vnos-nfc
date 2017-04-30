from logger import LOG
from keypad import readFromKeyboard
import pyrebase
import json
import time

FIFO_FILE = "nfc_fifo.tmp"
AUDIT_FILE = "arrays.json"
NUMBER_OF_PIN_ATTEMPTS = 3


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
    LOG.debug("Waiting for communication...")
    with open(FIFO_FILE, 'r') as f:
        data = f.read()


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
          break
        else:
          appendAuditJson(outputJson)
          LOG.debug("Authorization unsuccessful User: {}, Attempt: {}/{}".format(userValues["name"], \
                                                                                    i+1, \
                                                                                    NUMBER_OF_PIN_ATTEMPTS))
          print("DISPLEJ - Autorizacia neuspesna! Pokus {} z {}".format(i+1, \
                                                                      NUMBER_OF_PIN_ATTEMPTS))

    LOG.debug("Authorization finished. User not logged in!!!")






