"""
CNC Machining Interpreter
Degrees of Freedom: 3(x, y, z)
Coolant: None
Author: Ryan Kwong
Version: v1.0.0
"""

import math

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
    return None

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
            self.x = x
            self.y = y
            self.z = z
        elif self.coord == "relative":
            xyangle = math.tanh(y/x)
    def G01(self, x1, y1, z1):
        pass

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

        
        