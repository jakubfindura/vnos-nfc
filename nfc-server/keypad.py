import RPi.GPIO as GPIO
from logger import LOG

GPIO.setmode(GPIO.BOARD)

ENDING_CHARACTER = "#"

MATRIX = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']]

ROW = [7,11,13,15]
COL = [12,16,18,22]

LED = [31,33,35,37]

for j in range(4):
    GPIO.setup(LED[j], GPIO.OUT)

for j in range(4):
    GPIO.setup(COL[j], GPIO.OUT)
    GPIO.output(COL[j],1)

for i in range(4):
    GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

def readFromKeyboard():
    stringList = []
    try:
        while(True):
            for j in range(4):
                GPIO.output(COL[j], 0)
                for i in range(4):
                    if GPIO.input(ROW[i]) == 0:
                        GPIO.output(LED[i],True)        
                        loadedCharacter = MATRIX[i][j]
                        if(loadedCharacter == "#"):
                            #print MATRIX[i][j]
                            return ''.join(stringList)
                        stringList.append(loadedCharacter)
                        while(GPIO.input(ROW[i]) == 0):
                            pass
                        GPIO.output(LED[i],False)       
                GPIO.output(COL[j], 1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        return None
