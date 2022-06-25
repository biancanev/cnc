#!/usr/bin/env python3
"""
CNC Machining Interpreter
Degrees of Freedom: 3(x, y, z)
Coolant: None
Author: Ryan Kwong
Version: v1.0.0
"""

import math
import RPi.GPIO as GPIO
import time
import threading

#Define pins on RPi
xin1 = 17
xin2 = 18
xin3 = 27
xin4 = 22
yin1 = 6
yin2 = 13
yin3 = 19
yin4 = 26

#Define variables for X motor
xstep_sleep = 0.002
xstep_count = 4096
xdirection = False #True for CW, False for CCW
xstep_sequence = [[1,0,0,1],
				[1,0,0,0],
				[1,1,0,0],
				[0,1,0,0],
				[0,1,1,0],
				[0,0,1,0],
				[0,0,1,1],
				[0,0,0,1]]

#Define variables for Y motor
ystep_sleep = 0.002
ystep_count = 4096
ydirection = False #True for CW, False for CCW
ystep_sequence = [[1,0,0,1],
				[1,0,0,0],
				[1,1,0,0],
				[0,1,0,0],
				[0,1,1,0],
				[0,0,1,0],
				[0,0,1,1],
				[0,0,0,1]]

#Set up pin directions
GPIO.setmode(GPIO.BCM)
GPIO.setup(xin1, GPIO.OUT)
GPIO.setup(xin2,GPIO.OUT)
GPIO.setup(xin3,GPIO.OUT)
GPIO.setup(xin4,GPIO.OUT)
GPIO.setup(yin1, GPIO.OUT)
GPIO.setup(yin2,GPIO.OUT)
GPIO.setup(yin3,GPIO.OUT)
GPIO.setup(yin4,GPIO.OUT)

#Default pin outputs
GPIO.output(xin1, GPIO.LOW)
GPIO.output(xin2,GPIO.LOW)
GPIO.output(xin3,GPIO.LOW)
GPIO.output(xin4,GPIO.LOW)
GPIO.output(yin1, GPIO.LOW)
GPIO.output(yin2,GPIO.LOW)
GPIO.output(yin3,GPIO.LOW)
GPIO.output(yin4,GPIO.LOW)

#Define motors as an array of pins
xmotor_pins = [xin1,xin2,xin3,xin4]
ymotor_pins =[yin1,yin2,yin3,yin4]

#Define stepper motor reset
def cleanup():
    GPIO.output(xin1, GPIO.LOW)
    GPIO.output(xin2,GPIO.LOW)
    GPIO.output(xin3,GPIO.LOW)
    GPIO.output(xin4,GPIO.LOW)
    GPIO.output(yin1, GPIO.LOW)
    GPIO.output(yin2,GPIO.LOW)
    GPIO.output(yin3,GPIO.LOW)
    GPIO.output(yin4,GPIO.LOW)
    GPIO.cleanup()

#Run X motor
def runXMotor():
    try:
        xmotor_step_counter = 0
        i = 0
        for i in range(xstep_count):
            for pin in range(0, len(xmotor_pins)):
                GPIO.output(xmotor_pins[pin], xstep_sequence[xmotor_step_counter][pin])
            if xdirection == True:
                xmotor_step_counter = (xmotor_step_counter - 1) % 8
            elif xdirection == False:
                xmotor_step_counter = (xmotor_step_counter + 1) % 8
            else:
                print("Unrecognized direction")
                cleanup()
            time.sleep(xstep_sleep)
    except KeyboardInterrupt:
        cleanup()
        exit(1)

#Run Y motor
def runYMotor():
    try:
        ymotor_step_counter = 0
        i = 0
        for i in range(ystep_count):
            for pin in range(0, len(ymotor_pins)):
                GPIO.output(ymotor_pins[pin], ystep_sequence[ymotor_step_counter][pin])
            if ydirection == True:
                ymotor_step_counter = (ymotor_step_counter - 1) % 8
            elif ydirection == False:
                ymotor_step_counter = (ymotor_step_counter + 1) % 8
            else:
                print("Unrecognized direction")
                cleanup()
            time.sleep(ystep_sleep)
    except KeyboardInterrupt:
        cleanup()
        exit(1)

#Define global positioning and machining variables
x = 0
y = 0
z = 0
i = 0
j = 0
r = 0
tool = 1
spindle = 0
feed = 0

def calibrate():
    xdirection = True
    runXMotor()
    xdirection = False
    runXMotor()
    ydirection = True
    runYMotor()
    Ydirection = False
    runYMotor()
    xdirection = True
    ydirection = True
    xMove = threading.Thread(target=runXMotor, args = ())
    yMove = threading.Thread(target=runYMotor, args = ())
    xMove.start()
    yMove.start()
    xMove.join()
    yMove.join()
    xdirection = False
    ydirection = False
    xMove = threading.Thread(target=runXMotor, args = ())
    yMove = threading.Thread(target=runYMotor, args = ())
    xMove.start()
    yMove.start()
    xMove.join()
    yMove.join()

class Feed:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.limit_x = 5
        self.linit_y = 5
        self.linit_z = 3
        self.coord = "absolute"
        self.unit = "in"
        self.spindle = 0
        self.feed = 0
        self.vice = False
        self.tool = 1
        self.lock = False
    
    def toggleVice(self):
        if self.vice == False:
            self.vice = True
        else:
            self.vice = False

    def home(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def unlock(self):
        self.lock = False

    def override(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.spindle = 0
        self.feed = 0
        self.lock = True

    #G Codes
    def G00(self):
        #Absolute
        if self.coord == "absolute":
            print("Traveling to", x, y, z)
            if self.x < int(x):
                xdirection = True
            elif self.x > int(x):
                xdirection = False
            if self.y < int(y):
                ydirection = True
            elif self.y > int(y):
                ydirection = False
            xMove = threading.Thread(target=runXMotor, args = ())
            yMove = threading.Thread(target=runYMotor, args = ())
            xMove.start()
            yMove.start()
            xMove.join()
            yMove.join()
            self.x = x
            self.y = y
            self.z = z
            self.x = x
            self.y = y
            self.z = z
        elif self.coord == "relative":
            xyangle = math.tanh(y/x)
    def G01(self):
        if self.coord == "absolute":
            print("Traveling to", x, y, z)
            if int(self.x) < int(x):
                xdirection = True
            elif int(self.x) > int(x):
                xdirection = False
            if int(self.y) < int(y):
                ydirection = True
            elif int(self.y) > int(y):
                ydirection = False
            xMove = threading.Thread(target=runXMotor, args = ())
            yMove = threading.Thread(target=runYMotor, args = ())
            xMove.start()
            yMove.start()
            xMove.join()
            yMove.join()
            self.x = x
            self.y = y
            self.z = z
        elif self.coord == "relative":
            xyangle = math.tanh(y/x)

    def G20(self):
        self.unit = "in"

    def G21(self):
        self.unit = "mm"

    def G70(self):
        self.unit = "in"

    def G71(self):
        self.unit = "mm"

    #M Codes
    def M00(self):
        print("Programmed Stop")

    def M01(self):
        ans = input("Would you like to continue? Y/n")
        if ans == "Y":
            print("Programmed Stop")
        elif ans == "N":
            pass
        else:
            print("Unrecognized command:", ans, "Terminating process.")

    def M02(self):
        print("Program End")

    def M03(self):
        self.spindle = spindle
        print('Spindle speed set to', spindle)

    def M04(self):
        self.spindle = -1 * spindle

    def M05(self):
        self.spindle = 0

    def M06(self,):
        self.spindle = 0
        self.tool = tool
        print("Changed tool to ", self.tool)

    #Currently no support for Coolant(M08 or M09)


def run(filename: str):
    with open(filename, 'r') as f:
        for line in f:
            decode = line.split(" ")
            for command in range(len(decode)):
                if decode[command][0] == "N":
                    pass
                else:
                    cmd = getattr(Feed, decode[command])
                    try: 
                        cmd()
                    except:
                        print("Command", command, "not found")
                        return "Error"

#Debugging
calibrate()
feeder = Feed()
f = open('test.nc')
for line in f:
    decode = line.split(" ")
    for command in range(len(decode)):
        #Disregard line numbers
        if decode[command][0] == "N":
            pass
        #Variable setup
        elif decode[command][0] == "X":
            x = decode[command][1:len(decode[command])]
            print(x)
        elif decode[command][0] == "Y":
            y = decode[command][1:len(decode[command])]
        elif decode[command][0] == "Z":
            z = decode[command][1:len(decode[command])]
        elif decode[command][0] == "I":
            i = decode[command][1:len(decode[command])]
        elif decode[command][0] == "J":
            j = decode[command][1:len(decode[command])]
        elif decode[command][0] == "R":
            r = decode[command][1:len(decode[command])]
        elif decode[command][0] == "T":
            tool = decode[command][1:len(decode[command])]
        elif decode[command][0] == "S":
            spindle = decode[command][1:len(decode[command])]
        elif decode[command][0] == "F":
            feed = decode[command][1:len(decode[command])]
    for command in range(len(decode)):
        if decode[command][0] == "G" or decode[command][0] == "M":
            print(decode[command])
            cmd = getattr(Feed, str(decode[command]))
            cmd(feeder)
