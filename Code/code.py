#import demo


#import demo
from gonkController import *
import time
from sinBot import sinBot
droid=gonk()
droid.display_face(droid.eye)
droid.reset()
print(droid.getGyro())
print("Temperature:",droid.temp)

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
bot=sinBot()
demo_geno=np.array([-0.04198164,  0.90918552, -4.65281121, -2.22457433, -0.22812124,  3.07819192,
                        -0.21745877, -0.47165101,  2.15240473, -1.02080081])
bot.set_genotype(demo_geno)
for i in range(1000):
    motors=bot.get_positions(0)*50
    time.sleep(0.1)
    if i%300==0: droid.blink()
    print(motors)
    droid.move(0,motors[0])
    droid.move(1,motors[1])
    droid.move(2,motors[2])
    droid.move(3,motors[3])
    time.sleep(0.5)

for i in range(1000):
    print(droid.getFeet())
    time.sleep(0.1)
