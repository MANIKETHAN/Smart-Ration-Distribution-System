import RPi.GPIO as GPIO
import time

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(0) # Initialization






def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(servoPIN , True)
    p.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servoPIN, False)
    p.ChangeDutyCycle(0)
    
SetAngle(90)    
p.stop()
GPIO.cleanup()