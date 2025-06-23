"""
CircuitPython variant of gonk robot

Uses SD card to store data and four motors to locomote. Makes use of the tactile PCB sensor
"""

import board
import busio
import busio as io
import sdcardio
import storage
import adafruit_mpu6050
import adafruit_ht16k33.matrix
import digitalio
import analogio
from audiomp3 import MP3Decoder
try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!
import pwmio
from adafruit_motor import servo
import time
import ulab.numpy as np

class gonk:
    def __init__(self):
        self.DELAY=0.0001
        self.i2c = io.I2C(board.GP1, board.GP0)
        self.i2c.try_lock()
        print("devices",self.i2c.scan())
        self.i2c.unlock()
        #setup sd card
        spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
        cs = board.GP15
        self.sd=1
        try:
            sd = sdcardio.SDCard(spi, cs)
            vfs = storage.VfsFat(sd)
            storage.mount(vfs, '/sd')
            with open("/sd/test.csv", "w") as f:
                f.write("")
        except:
            print("No Sd card")
            self.sd=0
        self.audio = AudioOut(board.GP18)
        #setup eye
        self.timer=time.time()
        self.eye=[
                [0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
                [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
                [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
                [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
                [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0]
            ]
        self.eyes=1
        self.display=None
        try:
            self.display = adafruit_ht16k33.matrix.Matrix16x8(self.i2c)
            self.display.brightness=0.4
        except:
            print("No eyes detected")
            self.eyes=0.0
        #setup MPU sensor
            self.temp=0
        self.mpu=1
        try:
            self.mpu_ = adafruit_mpu6050.MPU6050(self.i2c, address=0x69)
        except:
            print("No mpu6050 detected")
            self.mpu=0
        #setup servos
        pins=[board.GP17,board.GP20,board.GP21,board.GP22]
        self.servos=[servo.Servo(pwmio.PWMOut(pins[i], frequency=50),min_pulse=750, max_pulse=2250) for i in range(len(pins))]
        #setup feet
        self.LF=[digitalio.DigitalInOut(board.GP2),digitalio.DigitalInOut(board.GP3),digitalio.DigitalInOut(board.GP4),digitalio.DigitalInOut(board.GP5)]
        for i in range(len(self.LF)): #set mode
            self.LF[i].direction = digitalio.Direction.OUTPUT
        self.RF=[digitalio.DigitalInOut(board.GP8),digitalio.DigitalInOut(board.GP9),digitalio.DigitalInOut(board.GP14),digitalio.DigitalInOut(board.GP16)]
        for i in range(len(self.RF)): #set mode
            self.RF[i].direction = digitalio.Direction.OUTPUT
        self.Lpin = analogio.AnalogIn(board.GP27)
        self.Rpin = analogio.AnalogIn(board.GP26)
        self.openPinL=digitalio.DigitalInOut(board.GP7)
        self.openPinR=digitalio.DigitalInOut(board.GP6)
        self.openPinL.direction = digitalio.Direction.OUTPUT
        self.openPinR.direction = digitalio.Direction.OUTPUT
        self.openPinL.value=0
        self.openPinR.value=0
        #bandpass filter
        self.LP=self.getFeet()
        self.HP=self.getFeet()
        self.time=time.monotonic()
    def reset(self):
        """
        reset all motors
        """
        angles=[100,50,170,100]
        for i in range(len(self.servos)):
            self.servos[i].angle=angles[i]
    def move(self,servo,angle,step=2):
        """
        move the servo in a slower way
        @param servo
        @param angle
        @param step (step size to move) larger step means quicker motor
        """
        assert servo>=0 and servo<len(self.servos),"Incorrect index"
        if angle<self.servos[servo].angle:
            for i in reversed(range(angle,int(self.servos[servo].angle),step)):
                self.servos[servo].angle-=step
                time.sleep(0.01)
        else:
            for i in range(int(self.servos[servo].angle),angle,step):
                self.servos[servo].angle+=step
                time.sleep(0.01)
        self.servos[servo].angle=angle
    def getFeet(self,ignore=[]): #get the readings from both feet
        def select_channel(channel,foot): #select a channel
            channel=f'{channel:04b}'
            foot[0].value=int(channel[3])
            foot[1].value=int(channel[2])
            foot[2].value=int(channel[1])
            foot[3].value=int(channel[0])
        a=np.zeros((32,))
        for i in range(16): #loop through sensors on each foot
            select_channel(i,self.LF)
            a[i]=self.Lpin.value
        for i in range(16):
            select_channel(i,self.RF)
            a[16+i]=self.Rpin.value
        return np.array(a)
    def filter(self,array,alpha=0.3):
        """
        Apply a bandpass filter to the array of analogue values
        @param array
        @param alpha
        """
        low_pass=(1-alpha)*self.LP +(alpha*array)
        highpass=alpha*self.HP + alpha*(low_pass-self.LP)
        self.LP=low_pass.copy()
        self.HP=highpass.copy()
        return highpass
    def move(self,servo,angle):
        """
        Move the servo to the set angle
        @param servo is the index of the servo
        @param angle is the angle to move to
        """
        assert servo>=0 and servo<len(self.servos),"Incorrect index"
        self.servos[servo].angle=angle
    def display_face(self,motion):
        #display the eye
        if self.eyes:
            for i in range(8):
                for j in range(16):
                    self.display[j, i] = motion[i][j]
                    self.display.show()

                    time.sleep(self.DELAY)
    def writeData(self,name,gyro=None,pressure=None,servos=False):
        #pressure to string
        if type(gyro)==type(None):
            gyro=self.getGyro()
        if type(pressure)==type(None):
            pressure=self.filter(self.getFeet())
        s=""
        for i in range(len(pressure)):
            s+=str(pressure[i])+","
        if self.mpu and self.sd: #check all the needed sensors are active
            with open("/sd/"+str(name), "a") as f:
                if not servos:
                    f.write(str(time.monotonic()-self.time)+","+str(gyro[0])+","+str(gyro[1])+","+str(gyro[2])+","+s[:-1]+"\n")
                if servos:
                    f.write(str(time.monotonic()-self.time)+","+str(gyro[0])+","+str(gyro[1])+","+str(gyro[2])+","+s[:-1]+","+str(self.servos[0].angle)+","+str(self.servos[1].angle)+","+str(self.servos[2].angle)+","+str(self.servos[3].angle)+"\n")
        else: print("Cannot save as sensor or storage device missing")
    def blink(self):
        #blink the eye
        test=self.eye.copy()
        if self.eyes:
            for k in range(3):
                for i in range(len(test)):
                    for j in range(len(test[0])):
                        self.display[j, i] = test[i][j]
                self.display.show()
                test.pop(k+1)
                test.pop(len(test)-k-1)
                test.insert(k,[0 for i in range(16)])
                test.insert(len(test)-k,[0 for i in range(16)])
            for i in range(8):
                for j in range(16):
                    self.display[j, i] = 0
                    self.display[j,3]=1
                    self.display[j,4]=1
            time.sleep(0.1)
            self.display_face(self.eye)
    def getGyro(self,mode=1):
        """
        Record either gyro or acc depending on the mode
        """
        if self.mpu:
            c=0
            found=False
            while c<50 and not found: #attempt to validate the mpu incase of disconnetion bug
                try:
                    acc=None
                    if mode==0:acc=self.mpu_.gyro
                    if mode==1:acc=self.mpu_.acceleration
                    self.temp=self.mpu_.temperature #not used
                    found=True
                except OSError:
                    print("attempt reading again")
                    pass
                c+=1
            if not found: #if it is still not found try reconnect
                try:
                    self.i2c.try_lock()
                    print("devices",self.i2c.scan())
                    self.i2c.unlock()
                    print("attempt reconnection")
                    self.mpu_ = adafruit_mpu6050.MPU6050(self.i2c)
                    return self.getGyro(mode=mode)
                except:
                    raise ValueError("MPU disconnected")
            return acc
    def playSound(self):
        """
        Play the gonk droid sound
        """
        mp3 = open("gonk-droid-sound.mp3", "rb")
        decoder = MP3Decoder(mp3)
        decoder.file = open("gonk-droid-sound.mp3", "rb")
        self.audio.play(decoder)
        t = time.monotonic()
        while time.monotonic() - t < 3:
            pass
    def createFile(self,name,keys):
        """
        creates a file on the sd card 
        @param name is the name of the csv
        @param gets is an array of names to be the column names
        """
        if ".csv" not in name: name+=".csv"
        self.time=time.monotonic()
        with open("/sd/"+str(name), "w") as f:
            for j in range(len(keys)-1):
                f.write(keys[j]+",")
            f.write(keys[-1]+"\n")




