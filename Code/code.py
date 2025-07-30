#import demo


#import demo
from gonkController import *
import time
from sinBot import sinBot
from CTRNN import CTRNN
from simple import simple
droid=gonk()
droid.display_face(droid.eye)
droid.reset()
print(droid.getGyro())
#print("Temperature:",droid.temp)

"""
droid=gk.gonk()
droid.display_face(droid.eye)
print("Recording")
droid.reset()
name="movementRightFoot1.csv"
droid.createFile(name,["x","y","z","s1","s2","s3","s4","s5","s6"])

"""
#while 1:
     #droid.blink()
     #time.sleep(5)

bot=simple()
demo_geno=np.array([-30, 30, 0, 0, -20, 20, 20, 20, 30, 30, 20, 20, 20, 20, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0] )
bot.set_genotype(demo_geno)
bot.dt=0.1

for i in range(1000):
    motors=bot.get_positions()
    if i%300==0: droid.blink()
    print(motors)
    droid.move_simulated_angle(0,motors[0])
    droid.move_simulated_angle(1,motors[1])
    droid.move_simulated_angle(2,motors[2])
    droid.move_simulated_angle(3,motors[3])
    time.sleep(0.01)

for i in range(1000):
    print(droid.getFeet())
    time.sleep(0.1)

