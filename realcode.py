import RPi.GPIO as GPIO
from threading import Lock
from time import sleep, time
import Adafruit_MCP9808.MCP9808 as MCP9808
from PID import PID
from TempDisp import TempDisp
import ws_broadcast as ws
import json

# GPIO Ports
Enc_A = 27              # Encoder input A: input GPIO 4 
Enc_B = 17                   # Encoder input B: input GPIO 14 
button = 18
SSR = 26

# encoder
Rotary_counter = 0           # Start counting from 0
Current_A = 1               # Assume that rotary switch is not 
Current_B = 1               # moving while we init software
LockRotary = Lock()      # create lock for rotary switch

#SSR control
running = False
pwm_frequency = 100

#temp sensor
t0 = time()
tsens = MCP9808.MCP9808()

#PID
P = 20
I = 0
D = 0
pid = PID(P,I,D)
pid.SetPoint = 0
pid.setSampleTime = 0.2
disp = TempDisp()

#send data
PORT = 8082
myws = ws.broadcast(PORT)
 
def start_stop_pwm(channel):  
	global pwm, running, pidOut 
	if running == True:
		pwm.stop()
		running = False
	else:
		pwm.start(pidOut)
		running = True 
  
# initialize interrupt handlers
def init():
	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BCM)              # I used BOARD (not BCM) mode, but that was causing problems with the oled library
                                # define the Encoder switch inputs
	GPIO.setup(SSR,GPIO.OUT)
	GPIO.setup(Enc_A, GPIO.IN, pull_up_down = GPIO.PUD_UP)             
	GPIO.setup(Enc_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP) #define "button" pin as input and set up internal pullup resis$
     
                    # setup callback thread for the A and B encoder 
                    # use interrupts for all inputs
	GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt)             # NO bouncetime 
	GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt)             # NO bouncetime
	GPIO.add_event_detect(button, GPIO.FALLING, callback=start_stop_pwm, bouncetime=200)
	tsens.begin()
	return
 
 
 
# Rotarty encoder interrupt:
# this one is called for both inputs from rotary switch (A and B)
def rotary_interrupt(A_or_B):
	global Rotary_counter, Current_A, Current_B, LockRotary
                                       # read both of the switches
	Switch_A = GPIO.input(Enc_A)
	Switch_B = GPIO.input(Enc_B)
                                       # now check if state of A or B has changed
                                       # if not that means that bouncing caused it
	if Current_A == Switch_A and Current_B == Switch_B:      # Same interrupt as before (Bouncing)?
		return                              # ignore interrupt!
 
	Current_A = Switch_A                        # remember new state
	Current_B = Switch_B                        # for next bouncing check
 
 
	if (Switch_A and Switch_B):                  # Both one active? Yes -> end of sequence
		LockRotary.acquire()                  # get lock 
		if A_or_B == Enc_B:                     # Turning direction depends on 
			Rotary_counter += 1                  # which input gave last interrupt
		else:                              # so depending on direction either
			Rotary_counter -= 1                  # increase or decrease counter
			LockRotary.release()                  # and release lock
	return                                 # THAT'S IT
 

 

def update_data(x,y1,y2):
	myws.send(json.dumps({'x':x,'y1':y1,'y2':y2}))


# Main loop. Demonstrate reading, direction and speed of turning left/rignt
def main():
	global tarTemp, pwm, Rotary_counter, LockRotary, SSR, pwm_frequency, t0, tsens, pid, pidOut
	pidOut = 0  
	tarTemp = 0                           # Current tarTemp   
	NewCounter = 0                        # for faster reading with locks
     
	init()                              # Init interrupts, GPIO, ...
	pwm = GPIO.PWM(SSR,pwm_frequency) #allows pwm.start(DutyCycle) followed by pwm.ChangeDutyCycle(DutyCycle) and pwm.ChangeFrequency(pwm_frequency)
	try:
		while True :                        # start test 
			sleep(0.2)                        # sleep 200 msec
 
                                    # because of threading make sure no thread
                                    # changes value until we get them
                                    # and reset them
 
			LockRotary.acquire()               # get lock for rotary switch
			NewCounter = Rotary_counter         # get counter value
			Rotary_counter = 0                  # RESET IT TO 0
			LockRotary.release()               # and release lock
                
			if (NewCounter !=0):               # Counter has CHANGED
				tarTemp = tarTemp + NewCounter*abs(NewCounter)   # Decrease or increase tarTemp 
				if tarTemp < 0:                  # limit tarTemp to 0...100
					tarTemp = 0
				elif tarTemp > 100:               # limit tarTemp to 0...100
					tarTemp = 100
				pid.SetPoint = tarTemp
				pidOut=pid.output   # !!! MAPPING NEEDS FIXING !!!
				if pidOut > 100:
					pidOut = 100
				elif pidOut < 0:
					pidOut = 0
				print(pid.output,pidOut)
				pwm.ChangeDutyCycle(pidOut)
             
			newT = tsens.readTempC()
			newTemp = round(newT,1)
			disp.Display(tarTemp,newTemp)
			pid.update(newTemp)
			update_data(x=time()-t0, y1=tarTemp, y2=newTemp)
          
	except KeyboardInterrupt:
		print('interrupted with keyboard')
	except:
		print('unspecified error')
	finally:
		GPIO.cleanup()
        
        
if __name__ == "__main__":
	main()