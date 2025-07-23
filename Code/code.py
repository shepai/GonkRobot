#import demo


#import demo
from gonkController import *
import time
from sinBot import sinBot
droid=gonk()
droid.display_face(droid.eye)
droid.reset()
print(droid.getGyro())

bot=sinBot()
demo_geno=np.array([0.2540666270398062, 3.3034403579674625, -0.22961708446935794, 3.3551562168512503, -0.5982119772821328, -1.049603120934403, -0.5806661302844076, -0.48036117705384485, -0.5454412746191527, -2.237367193631852])
bot.set_genotype(demo_geno)
for i in range(1000):
    motors=bot.get_positions(0)
    time.sleep(0.1)
    if i%300==0: droid.blink()
    print(droid.sim)
    droid.move_simulated_angle(0,motors[0])
    droid.move_simulated_angle(1,motors[1])
    droid.move_simulated_angle(2,motors[2])
    droid.move_simulated_angle(3,motors[3])
    time.sleep(0.5)

for i in range(1000):
    print(droid.getFeet())
    time.sleep(0.1)
