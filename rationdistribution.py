import requests
import RPi.GPIO as GPIO
import time
import math
import time
import sys
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
import os
import RPi.GPIO as GPIO
from RPLCD import CharLCD

os.system("sudo python3 /home/pi/smartration/servooperation/dalservoclose.py")
os.system("sudo python3 /home/pi/smartration/servooperation/riceservoclose.py")

url ='http://raspberrypi.microembeddedtech.com/queryconnect.php'


########### WEIGHT SENSOR INTILIZATION #######

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(393)
hx.reset()
hx.tare()
print("Tare done! Add weight now...")

##################### PIN NUMBERS #############3
ricebuttonpin=23
dalbuttonpin=24
endbuttonpin=27
#################### GPIO INITILIZAION ##################
GPIO.setmode(GPIO.BCM)
GPIO.setup(ricebuttonpin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(dalbuttonpin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(endbuttonpin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

#lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23],numbering_mode = GPIO.BOARD)
lcd = CharLCD(cols=16, rows=2, pin_rs=26, pin_e=19, pins_data=[13, 16, 20, 21],numbering_mode = GPIO.BCM)


lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string('  SMART RATION')
lcd.cursor_pos = (1, 0)
lcd.write_string('DISTRIBUTION SYS')
time.sleep(2)

######## VARIABLES ######
useridno=999
cudal=0
curice=0
nedal=0
nerice=0
startration=0
ricepressed=0
dalpressed=0
riceservo=0
dalservo=0


################################### Tries to initialize the Finger Print Sensor########
try:
    f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))



################################### DATABASE FUNCTIONS ###############

def dalupdatedb(uid):
    struid=str(uid)
    dalupdate="UPDATE `smartrationdistribution` SET `cudal`= 0  WHERE uid='"+struid+"'"
    upobj = {'query':dalupdate ,'key': 'querykey',}
    upz = requests.post(url, data = upobj)
    
    
def riceupdatedb(uid):
    struid=str(uid)
    dalupdate="UPDATE `smartrationdistribution` SET `curice`= 0  WHERE uid='"+struid+"'"
    upobj = {'query':dalupdate ,'key': 'querykey',}
    upz = requests.post(url, data = upobj)
    


def getdatafromdb(uid):
    global cudal
    global curice
    global nedal
    global nerice
    global useridno
    struid=str(uid)
    selectsqlquery="SELECT `uid`, `cudal`, `curice`, `nedal`, `nerice` FROM `smartrationdistribution` WHERE uid='"+struid+"'"
    myobj = {'query':selectsqlquery ,'key': 'querykey',}
    z = requests.post(url, data = myobj)
    #print(z.text)  #<class 'str'>
    #print(type(z.text))
    stringtext=z.text
    #print(stringtext)
    #print("\n")
    splittext = stringtext.split("\n")
    #print(splittext)
    del splittext[0]
    del splittext[-1]
    #print(splittext)
    opercmd=splittext[0]
    #print(type(opercmd))
    #print("RECEIVED COMMAND:",opercmd)
    #print("\n")
    commasplit=opercmd.split(",")
    useridno=commasplit[0]
    cudal=commasplit[1]
    curice=commasplit[2]
    nedal=commasplit[3]
    nerice=commasplit[4]
    #print("USER ID:",useridno)
    #print("Current Month Dal:",cudal)
    #print("Current Month Dal:",curice)
    #print("Next Month Dal:",nedal)
    #print("Next Month Dal:",nerice)
    
def getweightvalue():
    val = max(0, int(hx.get_weight(5)))
    print(int(val))
    hx.power_down()
    hx.power_up()
    time.sleep(0.1)
    return val


def resetallvar():
        startration=0
        useridno=999
        cudal=0
        curice=0
        nedal=0
        nerice=0
        startration=0
        ricepressed=0
        dalpressed=0
    
    
    
    
#### WHILE LOOP ############
    
while True:
    if startration==0:
        ## Tries to search the finger and calculate hash
        try:
            print('Waiting for finger...')
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string('PLACE FINGER..')
            

            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Searchs template
            result = f.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if ( positionNumber == -1 ):
                print('No match found!')
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string('NO MATCH FOUND')
                time.sleep(2)
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string('PLACE FINGER..')
                
                
            else:
                print('Found template at position #' + str(positionNumber))
                #print('The accuracy score is: ' + str(accuracyScore))
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string('FOUND USER ID:')
                lcd.write_string(str(positionNumber))
                lcd.cursor_pos = (1, 0)
                lcd.write_string('Getting Details')
                time.sleep(2)
                getdatafromdb(positionNumber)
                print("USER ID:",useridno)
                print("Current Month Dal:",cudal)
                print("Current Month RICE:",curice)
                print("Next Month Dal:",nedal)
                print("Next Month RICE:",nerice)
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string(' AVL RICE:')
                lcd.write_string(str(curice))
                lcd.write_string(" g")
                lcd.cursor_pos = (1, 0)
                lcd.write_string(' AVL DAL:')
                lcd.write_string(str(cudal))
                lcd.write_string(" g")
                time.sleep(4)
                cuuserid=int(useridno)
                riceintval=int(curice)
                dalintval=int(cudal)
                if riceintval > 100 or dalintval > 100:
                    startration=1
                else:
                    print("MINIMUM REQUIRED 100 GRAMS")
                    lcd.clear()
                    lcd.cursor_pos = (0, 0)
                    lcd.write_string('MIN REQURED 100 G')
                    lcd.cursor_pos=(1,0)
                    lcd.write_string(" RESET/EXIT ")
                    time.sleep(2)
                    resetallvar()

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)
        
        
    if startration==1:
        print("SELECT BUTTON FOR RICE OR DAL")
        if ricepressed==0 and dalpressed==0:
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(' SELECT BUTTON ')
            lcd.cursor_pos = (1, 0)
            lcd.write_string('1.RICE  2.DAL')
        
        ricebtnread=GPIO.input(ricebuttonpin)
        dalbtnread=GPIO.input(dalbuttonpin)
        print("RICE BUTTON VALUE:",ricebtnread)
        print("DAL BUTTON VALUE:",dalbtnread)
        if ricebtnread==0:
            ricepressed=1
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(' RICE SELECTED ')
            lcd.cursor_pos = (1, 0)
            lcd.write_string('PLACE CONTAINER')
            time.sleep(5)
            
        elif dalbtnread==0:
            dalpressed=1
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(' DAL SELECTED ')
            lcd.cursor_pos = (1, 0)
            lcd.write_string('PLACE CONTAINER')
            time.sleep(5)
            
        if ricepressed==1: 
            cuuserid=int(useridno)
            ricedispatchval=int(curice)
            if riceservo==0:
                riceservo=1
                os.system("sudo python3 /home/pi/smartration/servooperation/riceservoopen.py")
            riceweightvalue=getweightvalue()
            print(riceweightvalue)
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string('Weight: ')
            lcd.write_string(str(riceweightvalue))
            
            if riceweightvalue > ricedispatchval:
                print("END WEIGHT");
                if riceservo==1:
                    os.system("sudo python3 /home/pi/smartration/servooperation/riceservoclose.py")
                    riceservo=0
                riceupdatedb(cuuserid)
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string('DISPATCH COMPLETED')
                #lcd.cursor_pos = (1, 0)
                #lcd.write_string('PRESS END BUTTON')
                ricepressed=0
                time.sleep(3)
                    
        
                
        elif dalpressed==1:
            cuuserid=int(useridno)
            daldispatchval=int(cudal)
            if dalservo==0:
                dalservo=1
                os.system("sudo python3 /home/pi/smartration/servooperation/dalservoopen.py")
            
            dalweightvalue=getweightvalue()
            print(dalweightvalue)
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string('Weight: ')
            lcd.write_string(str(dalweightvalue))
           
            if dalweightvalue > daldispatchval:
                print("DAL WEIGHT END")
                if dalservo==1:
                    os.system("sudo python3 /home/pi/smartration/servooperation/dalservoclose.py")
                    dalservo=0
                dalupdatedb(cuuserid)
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string('DISPATCH COMPLETED')
                #lcd.cursor_pos = (1, 0)
                #lcd.write_string('PRESS END BUTTON')
                dalpressed=0
                time.sleep(3)
                
        time.sleep(0.5)
        
    endbtnead=GPIO.input(endbuttonpin)
    print("END BUTTON:",endbtnead)

    if endbtnead==0:
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string('OPERATION DONE')
        time.sleep(2)
        #lcd.clear()
        #lcd.cursor_pos = (0, 0)
        #lcd.write_string('PLACE FINGER..')
        startration=0
        useridno=999
        cudal=0
        curice=0
        nedal=0
        nerice=0
        startration=0
        ricepressed=0
        dalpressed=0
       
        

    
    time.sleep(0.5)

cleanAndExit()