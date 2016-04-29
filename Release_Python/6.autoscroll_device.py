#!/usr/bin/python

import subprocess
import time
from subprocess import check_output
from time import gmtime, strftime

UP_KEYEVENT = "adb shell input touchscreen swipe 471 1440 471 753"
DOWN_KEYEVENT = "adb shell input touchscreen swipe 471 753 471 1440"

timeout = time.time() + 60 * 30  # 30 minutes from now
print "current time:", strftime("%H:%M:%S", gmtime())

while True:
    if time.time() > timeout:
        break
    try:
        for _ in range(15):
            check_output(UP_KEYEVENT, shell=True)
            print "input touchscreen swipe 471 1440 471 753"
            time.sleep(1)
        for _ in range(15):
            check_output(DOWN_KEYEVENT, shell=True)
            print "input touchscreen swipe 471 753 471 1440"
            time.sleep(1)
    except subprocess.CalledProcessError:
        print "*** Error: please check your device state.\n"
        raise SystemError(0)

print "Finished at:", strftime("%H:%M:%S", gmtime())
