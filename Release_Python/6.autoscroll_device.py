#!/usr/bin/python
import argparse
import subprocess
import time
from subprocess import check_output
from time import gmtime, strftime

UP_KEYEVENT = "adb shell input touchscreen swipe 471 1440 471 753"
DOWN_KEYEVENT = "adb shell input touchscreen swipe 471 753 471 1440"

MULTI_DEV_UP_KEYEVENT = "shell input touchscreen swipe 471 1440 471 753"
MULTI_DEV_DOWN_KEYEVENT = "shell input touchscreen swipe 471 753 471 1440"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', nargs=1, help="0:Slow vertical swipe; 1:Slide in circle")
    parser.add_argument('-t', '--time', nargs='?', help="Mode:0 customized time")
    parser.add_argument('-c', '--coordinates', nargs=2, help="x/y coordinates")
    parser.add_argument('-s', '--device', nargs='?', help="target device")
    args = parser.parse_args()
    mode = int(args.mode[0])
    slide_time = args.time
    mode0_coords = args.coordinates
    mode1_device = args.device

    if slide_time is None:
        m_time = 60 * 30  # 30 minutes from now
    else:
        m_time = int(slide_time) * 60

    if mode == 0:
        x_coord = int(mode0_coords[0])
        y_coord = int(mode0_coords[1])
        do_vertical_swipe(x_coord, y_coord, m_time)
    else:
        if mode1_device is None:
            up_cmd = UP_KEYEVENT
            down_cmd = DOWN_KEYEVENT
        else:
            up_cmd = "adb -s {} {}".format(mode1_device, MULTI_DEV_UP_KEYEVENT)
            down_cmd = "adb -s {} {}".format(mode1_device, MULTI_DEV_DOWN_KEYEVENT)
        slide_loop(up_cmd, down_cmd, m_time)


def slide_loop(up_cmd, down_cmd, m_time):
    # timeout = time.time() + 60 * 30  # 30 minutes from now
    timeout = time.time() + m_time
    print "current time:", strftime("%H:%M:%S", gmtime())

    while True:
        if time.time() > timeout:
            break
        try:
            for _ in range(15):
                check_output(up_cmd, shell=True)
                print "input touchscreen swipe 471 1440 471 753"
                time.sleep(1)
            for _ in range(15):
                check_output(down_cmd, shell=True)
                print "input touchscreen swipe 471 753 471 1440"
                time.sleep(1)
        except subprocess.CalledProcessError:
            print "*** Error: please check your device state.\n"
            raise SystemError(0)

    print "Finished at:", strftime("%H:%M:%S", gmtime())


def do_vertical_swipe(x_coord, y_coord, m_time):
    timeout = time.time() + m_time
    print "current time:", strftime("%H:%M:%S", gmtime())
    while True:
        if time.time() > timeout:
            break
        try:
            # swipe <x1> <y1> <x2> <y2> [duration(ms)] (Default: touchscreen)
            cmd = "adb shell input touchscreen swipe {} {} {} {} 12000".format(x_coord, y_coord, x_coord, y_coord + 500)
            check_output(cmd, shell=True)
            # x_coord += 10
            y_coord += 10
        except subprocess.CalledProcessError:
            print "*** Error: please check your device state.\n"
            raise SystemError(0)


if __name__ == '__main__':
    main()
