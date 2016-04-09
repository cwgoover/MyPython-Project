#!/usr/bin/python
import argparse
import os
import re
from os.path import basename
from os.path import splitext

import pylab as pl

rx = re.compile(r"""
    (?P<title>proc.*cpu[-]+[\n\r])              # Title at the beginning of a line
    [\n\r]*                                     # empty newline
    (?P<subtitle>\s?r\s+b\s+swpd.*wa[\n\r])     # Subtitle
    [\n\r]*
    (?P<record>^(\s?\b[0-9]+\b\s+)+[\n\r])      # record
    """, re.MULTILINE | re.VERBOSE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()
    infile = args.file
    outfile = args.output
    # recombine file name: xx.txt -> xx_table.txt
    out_table = "{0}_table.txt".format(splitext(basename(outfile))[0])

    vmstat_matrix = read_file(infile)

    # print the table in the file
    print_file(outfile, vmstat_matrix)

    # calculate special value in the table
    chart, average_dic = statis_matrix(vmstat_matrix)
    print_table(out_table, chart, average_dic)

    # press [enter] to close all the figures in the show module
    # otherwise, all the figures will be closed after finished this script
    # _ = raw_input("Press [enter] to exit.")


def statis_matrix(stat_matrix):
    """
    1. transpose matrix to make all the values of each vmstat's item in the single list.
    2. find the key vmstat's item, and get each number's frequence and average value in one vmstat's item.
    3. draw other items with all the values in each vmstat's item.
    """
    chart = {}
    average_dic = {}
    # Can I generate and show a different image during each loop with Matplotlib?
    # http://stackoverflow.com/a/11129869/4710864
    # pl.ion()    # turn on interactive mode, non-blocking `show`, otherwise only show one figure

    # transpose rows and columns in the matrix, skipped the title in the first line
    for key in [[row[i] for row in stat_matrix[1:]] for i in range(len(stat_matrix[1]))]:
        # For example: key = ['r', '3', '0', '3', '5', '0', '8', '3', '1', '1', '0', '3',...]
        if key[0] in ('r', 'b', 'us', 'sy', 'id', 'wa'):
            # Limiting floats to two decimal points
            # http://stackoverflow.com/a/455634/4710864  or  http://stackoverflow.com/a/6539677/4710864
            #
            # finding average of a list: http://stackoverflow.com/a/9039992/4710864
            # or 'reduce(lambda x,y:x+y, [float(x) for x in distance])'
            #
            # reduce function: https://docs.python.org/2/library/functions.html#reduce
            average_dic[key[0]] = "{0:.2f}".format(
                reduce(lambda x, y: int(x) + int(y), key[1:]) / (float(len(key)) - 1))
            # generate chart with key values' frequency
            # based on: Build an ASCII chart of the most commonly used words in a given text
            # http://stackoverflow.com/a/3170549/4710864 (mypython #3)
            chart[key[0]] = sorted((-key.count(w), w) for w in set(key[1:]))
        else:
            pl.figure()
            pl.title(key[0])    # show title
            pl.xlabel('time')
            pl.ylabel('value')
            # Convert all strings in a list to int:
            # http://stackoverflow.com/questions/7368789/convert-all-strings-in-a-list-to-int
            # results = map(int, results)
            #
            # Create a range of numbers with a given increment
            # http://stackoverflow.com/a/18325904/4710864
            # In Python, range(start, stop + 1, step) can be used like Matlab's start:step:stop command.
            #
            pl.plot(range(len(key[1:])), map(int, key[1:]), linewidth=2)
            # pl.show()
            # Save plot to image file instead of displaying it using Matplotlib
            # http://stackoverflow.com/a/9890599/4710864
            pl.savefig("{0}.png".format(key[0]))
            # time.sleep(1) # wait 1 second to show next one.

    return chart, average_dic


def read_file(filename):
    vmstat_matrix = []
    first_line = True
    with open(filename, 'r') as fp:
        for match in rx.finditer(fp.read()):
            if first_line:
                first_line = False
                vmstat_matrix.append(match.group('title'))
                vmstat_matrix.append(match.group('subtitle').split())
                vmstat_matrix.append(match.group('record').rstrip().split())
            else:
                # Python's rstrip method strips all kinds of trailing whitespace
                #  by default, not just newlines
                #
                # use split()) to directly create matrix here
                vmstat_matrix.append(match.group('record').rstrip().split())
    return vmstat_matrix


def print_file(outfile, stat_list):
    if os.path.isfile(outfile):
        os.remove(outfile)
    with open(outfile, 'a') as f:
        for item in stat_list:
            if 'procs' not in item:
                f.write("{0}\n".format(' '.join(item)))
            else:
                f.write('{0}\n'.format(item))


def draw_cylinder(f, stat_dic):
    # Make sure these bars (plus space-word-space, estimate length) always fit:
    #  bar + [space] + ['] + word + ['] + [:] should be always <= 80 characters
    h = min(9 * value[0] / (74 - len(value[1])) for value in stat_dic)
    f.write("\n {0}\n".format(9 * stat_dic[0][0] / h * '_'))
    for l, w in stat_dic[:20]:
        f.write("{0} '{1}':{2}\n".format('|' + 9 * l / h * '_' + '|', w, -l))


def print_table(outfile, stat_map, average_dic):
    if os.path.isfile(outfile):
        os.remove(outfile)

    f = open(outfile, 'a')
    # print procs info
    f.write("The vmstat monitor:\n")
    f.write("\n--------procs--------:\nr: {0}".format(average_dic['r']))
    draw_cylinder(f, stat_map['r'])
    f.write("\n\nb: {0}".format(average_dic['b']))
    draw_cylinder(f, stat_map['b'])

    # print cpu info
    f.write("\n\n\n--------cpu--------:\nus: {0}".format(average_dic['us']))
    draw_cylinder(f, stat_map['us'])
    f.write("\n\nsy: {0}".format(average_dic['sy']))
    draw_cylinder(f, stat_map['sy'])
    f.write("\n\nid: {0}".format(average_dic['id']))
    draw_cylinder(f, stat_map['id'])
    f.write("\n\nwa: {0}".format(average_dic['wa']))
    draw_cylinder(f, stat_map['wa'])
    f.close()

if __name__ == '__main__':
    main()
