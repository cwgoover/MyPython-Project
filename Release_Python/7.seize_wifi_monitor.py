#!/usr/bin/python
import argparse
import subprocess
import time
from subprocess import check_output
from time import gmtime, strftime

BROWSER_WEBSITE = "shell am start -a android.intent.action.VIEW -n com.android.chrome/com.google.android.apps.chrome.Main -d http://www.stackoverflow.com"

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--time', nargs='?', help="duration time")
parser.add_argument('-s', '--device', nargs='?', help="target device")
parser.add_argument('-x', '--index', nargs=2, help="The tap's coordinate")
args = parser.parse_args()
duration = args.time
device = args.device
_x = args.index[0]
_y = args.index[1]

print "\n*** Please turn off wifi first. We assume that the wifi is enable after first tapping...\n"
timeout = 0
if duration is not None:
    timeout = time.time() + duration
    print "current time:", strftime("%H:%M:%S", gmtime())

if device is None:
    cmd = "adb shell input tap {0} {1}".format(_x, _y)
    browser = "adb", BROWSER_WEBSITE
else:
    cmd = "adb -s {0} shell input tap {1} {2}".format(device, _x, _y)
    browser = "adb -s {0} {1}".format(device, BROWSER_WEBSITE)
print "The command:", cmd

i = 0
while True:
    if duration is not None and time.time() > timeout:
        print "Time out so quit!"
        break
    try:
        if i % 2 == 0:
            print strftime("%H:%M:%S", gmtime()), "/Turn on wifi"
            check_output(cmd, shell=True)
            time.sleep(10)
            print strftime("%H:%M:%S", gmtime()), "/browser website"
            check_output(browser, shell=True)
            time.sleep(30)
        else:
            print strftime("%H:%M:%S", gmtime()), "/Turn off wifi"
            check_output(cmd, shell=True)
            time.sleep(10)
        i += 1
    except subprocess.CalledProcessError:
        print "*** Error: please check your device state.\n"
        raise SystemError(0)


# Launching random web browsers on Android
# http://wrla.ch/blog/2012/05/launching-random-web-browsers-on-android-via-adb/
# *** am start -a android.intent.action.VIEW -n <application/intent> -d <url>
