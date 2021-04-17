import RPi.GPIO as GPIO

MOTOR_SPEED = .6


# Pin Assignments
motoRPin1 = 13
motoRPin2 = 11
enablePin = 15
#adc = ADCDevice() # Define an ADCDevice class object


def mapNUM(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

class DiscoBall:

    def init(self):
        GPIO.setmode(GPIO.BOARD)   
        GPIO.setup(motoRPin1,GPIO.OUT)   # set pins to OUTPUT mode
        GPIO.setup(motoRPin2,GPIO.OUT)
        GPIO.setup(enablePin,GPIO.OUT)

        self.p = GPIO.PWM(enablePin,1000) # creat PWM and set Frequence to 1KHz
        self.p.start(0)

    def spin(self):
        self.motor(128 + 128 * MOTOR_SPEED)

    def stop(self):
        self.motor(128)

    # motor function: determine the direction and speed of the motor according to the input ADC value input
    def motor(self,ADC):
        value = ADC -128
        if (value > 0):  # make motor turn forward
            GPIO.output(motoRPin1,GPIO.HIGH)  # motoRPin1 output HIHG level
            GPIO.output(motoRPin2,GPIO.LOW)   # motoRPin2 output LOW level
        elif (value < 0): # make motor turn backward
            GPIO.output(motoRPin1,GPIO.LOW)
            GPIO.output(motoRPin2,GPIO.HIGH)
        else :
            GPIO.output(motoRPin1,GPIO.LOW)
            GPIO.output(motoRPin2,GPIO.LOW)
        self.p.start(mapNUM(abs(value),0,128,0,100))
    #    print ('The PWM duty cycle is %d%%\n'%(abs(value)*100/127))   # print PMW duty cycle.

    def shutdown(self):
        self.p.stop()  # stop PWM    