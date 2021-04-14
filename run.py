#!/usr/bin/env python3
########################################################################
# Filename    : UltrasonicRanging.py
# Description : Get distance via UltrasonicRanging sensor
# auther      : www.freenove.com
# modification: 2019/12/28
########################################################################
import RPi.GPIO as GPIO
import time
import subprocess


# config
DISTANCE_IN_CM = 30

from enum import Enum
class State(Enum):
    LOOKING = 1
    PLAYING = 2


# define the pins connected to L293D 
motoRPin1 = 13
motoRPin2 = 11
enablePin = 15
#adc = ADCDevice() # Define an ADCDevice class object
process = None


state = State.LOOKING

def setupMotor():
    # global adc
    # if(adc.detectI2C(0x48)): # Detect the pcf8591.
    #     adc = PCF8591()
    # elif(adc.detectI2C(0x4b)): # Detect the ads7830
    #     adc = ADS7830()
    # else:
    #     print("No correct I2C address found, \n"
    #     "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
    #     "Program Exit. \n");
    #     exit(-1)
    global p
    GPIO.setmode(GPIO.BOARD)   
    GPIO.setup(motoRPin1,GPIO.OUT)   # set pins to OUTPUT mode
    GPIO.setup(motoRPin2,GPIO.OUT)
    GPIO.setup(enablePin,GPIO.OUT)
        
    p = GPIO.PWM(enablePin,1000) # creat PWM and set Frequence to 1KHz
    p.start(0)

# mapNUM function: map the value from a range of mapping to another range.
def mapNUM(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
	
# motor function: determine the direction and speed of the motor according to the input ADC value input
def motor(ADC):
    value = ADC -128
    if (value > 0):  # make motor turn forward
        GPIO.output(motoRPin1,GPIO.HIGH)  # motoRPin1 output HIHG level
        GPIO.output(motoRPin2,GPIO.LOW)   # motoRPin2 output LOW level
        print ('Turn Forward...')
    elif (value < 0): # make motor turn backward
        GPIO.output(motoRPin1,GPIO.LOW)
        GPIO.output(motoRPin2,GPIO.HIGH)
        print ('Turn Backward...')
    else :
        GPIO.output(motoRPin1,GPIO.LOW)
        GPIO.output(motoRPin2,GPIO.LOW)
        print ('Motor Stop...')
    p.start(mapNUM(abs(value),0,128,0,100))
    print ('The PWM duty cycle is %d%%\n'%(abs(value)*100/127))   # print PMW duty cycle.

def loop():
    while True:
        # value = adc.analogRead(0) # read ADC value of channel 0
        # print ('ADC Value : %d'%(value))
        value = 255
        motor(value)
        time.sleep(0.2)

def destroyMotor():
    p.stop()  # stop PWM






trigPin = 16
echoPin = 18
MAX_DISTANCE = 220          # define the maximum measuring distance, unit: cm
timeOut = MAX_DISTANCE*60   # calculate timeout according to the maximum measuring distance

def pulseIn(pin,level,timeOut): # obtain pulse time of a pin under timeOut
    t0 = time.time()
    while(GPIO.input(pin) != level):
        if((time.time() - t0) > timeOut*0.000001):
            return 0;
    t0 = time.time()
    while(GPIO.input(pin) == level):
        if((time.time() - t0) > timeOut*0.000001):
            return 0;
    pulseTime = (time.time() - t0)*1000000
    return pulseTime
    
def getSonar():     # get the measurement results of ultrasonic module,with unit: cm
    GPIO.output(trigPin,GPIO.HIGH)      # make trigPin output 10us HIGH level 
    time.sleep(0.00001)     # 10us
    GPIO.output(trigPin,GPIO.LOW) # make trigPin output LOW level 
    pingTime = pulseIn(echoPin,GPIO.HIGH,timeOut)   # read plus time of echoPin
    distance = pingTime * 340.0 / 2.0 / 10000.0     # calculate distance with sound speed 340m/s 
    return distance
    
def setup():
    GPIO.setmode(GPIO.BOARD)      # use PHYSICAL GPIO Numbering
    GPIO.setup(trigPin, GPIO.OUT)   # set trigPin to OUTPUT mode
    GPIO.setup(echoPin, GPIO.IN)    # set echoPin to INPUT mode


def startPlaying():
    global state
    global process
    print("$$ starting playing")
    state = State.PLAYING
    motor(255)
    process = subprocess.Popen(['cvlc', 'disco.m4a', 'vlc://quit'])
    print("$$ STARTED playing")

def stopPlaying():    
    global state
    state = State.LOOKING
    print("$$ stopping playing")
    motor(128)

def findSomeone():
    distance = getSonar() # get distance
    print ("The distance is : %.2f cm"%(distance))
    if (distance < DISTANCE_IN_CM):
        startPlaying();

def checkForEndOfSong():
    global process
    if(process == None):
        stopPlaying();
    else:
        result = process.poll();
        print(f'@@ poll returned {result}')
        if (process.poll() != None):
            stopPlaying();

def loop():
    global state
    while(True):
        if(state == State.LOOKING):
            findSomeone();
        elif state == State.PLAYING:
            checkForEndOfSong();

        time.sleep(.2)
        

def destroy():
    destroyMotor()
    GPIO.cleanup()

if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    setup()
    setupMotor()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()


    
