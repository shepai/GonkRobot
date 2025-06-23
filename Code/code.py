from GonkController import *
import time
droid=gonk()
droid.display_face(droid.eye)

while 1:
     droid.blink()
     time.sleep(5)