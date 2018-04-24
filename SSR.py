import time
import RPi.GPIO as GPIO
GPIO.cleanup() #release pins
GPIO.setmode(GPIO.BOARD) #defines pin numbers according to physical layout as opposed to "BCM"
SSR = 11
button = 12
pwm_frequency = 0.5
running = False
GPIO.setup(SSR,GPIO.OUT) #define "SSR" pin as output
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP) #define "button" pin as input and set up internal pullup resistor
pwm = GPIO.PWM(SSR,pwm_frequency) #allows pwm.start(DutyCycle) followed by pwm.ChangeDutyCycle(DutyCycle) and pwm.ChangeFrequency(pwm_frequency)

def start_stop_pwm(channel):  
	if running == True:
		pwm.stop()
		running = False
	else:
		pwm.start(50)
		running = True 
 
GPIO.add_event_detect(button, GPIO.FALLING, callback=start_stop_pwm, bouncetime=200) #will hopefully interrupt while(1)
try:  
	while(1): #main loop does nothing for now...PID can go here?
		time.sleep(1)
except KeyboardInterrupt:  
	GPIO.cleanup() # clean up GPIO on CTRL+C exit
GPIO.cleanup() #release pins

######### STUFF FOR TESTING ##########

# GPIO.output(SSR,True) #set the SSR pin high (3.3 V) GPIO.output(SSR,1) also works
# time.sleep(1) #pause for one second
# GPIO.output(SSR,0)