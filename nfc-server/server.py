from logger import LOG
from keypad import readFromKeyboard
import pyrebase

FIFO_FILE = "nfc_fifo.tmp"
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

# Load Firebase APP
print("A")
firebase = pyrebase.initialize_app(config)
print("B")
db = firebase.database()

# Block until writer finishes...
while True:
    print("Waiting...")
    with open(FIFO_FILE, 'r') as f:
        data = f.read()


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
                    break
                else:
                    LOG.info("Authorization unsuccessful User: {}, Attempt: {}/{}".format(userDictionary["name"], \
                                                                                              i+1, \
                                                                                              NUMBER_OF_PIN_ATTEMPTS))
                    print("DISPLEJ - Autorizacia neuspesna! Pokus {} z {}".format(i+1, \
                                                                                  NUMBER_OF_PIN_ATTEMPTS))


        else:
            LOG.info("User not found in database!")
            print("DISPLEJ - Pouzivatel neexistuje!")




