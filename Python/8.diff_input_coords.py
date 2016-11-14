#!/usr/bin/python
import argparse

import re

MOTION_EVENT_REG = '\s*[A-Z]+\s*0=[\s?([\d\.]+),\s([\d\.]+),\s+(\d+)]'
GETEVENT_REG = '\s*[\s*([\d\.]+)].*(ABS_MT_POSITION_\w)\s+(\w+).*'


def read_motion_file(file):
    with open(file, 'r') as ins:
        array = []
        for line in ins:
            info = re.search(MOTION_EVENT_REG, line)
            if info is not None:
                array.append(line)
    return array


def main():
    """
    1. Make sure getevent & MotionEvent start at the same time.
    2. Deal with the simple gesture, such as vertical slip, horizontal slip
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--getevent')
    parser.add_argument('-m', '--motion')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()
    getevent_file = args.getevent
    motion_file = args.motion
    output_file = args.output


if __name__ == '__main__':
    main()
