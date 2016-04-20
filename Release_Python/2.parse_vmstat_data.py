#!/usr/bin/python
import argparse
import os
import re

from os.path import basename
from os.path import splitext


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


def statis_matrix(stat_matrix):
    """
    1. transpose matrix to make all the values of each vmstat's item in the single list.
    2. find the key vmstat's item, and get each number's frequence and average value in one vmstat's item.
    3. TODO: draw other items with all the values in each vmstat's item.
    """
    chart = {}
    average_dic = {}
    # transpose rows and columns in the matrix, skipped the title in the first line
    for key in [[row[i] for row in stat_matrix[1:]] for i in range(len(stat_matrix[1]))]:
        # For example: key = ['r', '3', '0', '3', '5', '0', '8', '3', '1', '1', '0', '3',...]
        if key[0] in ('r', 'b', 'us', 'sy', 'id', 'wa'):
            average_dic[key[0]] = "{0:.2f}".format(
                reduce(lambda x, y: int(x) + int(y), key[1:]) / (float(len(key)) - 1))
            # generate chart with key values' frequency
            chart[key[0]] = sorted((-key.count(w), w) for w in set(key[1:]))
        else:
            # TODO: draw 2D line to show detail
            pass
    return chart, average_dic


def read_file(filename):
    vmstat_matrix = []
    i = 2
    with open(filename, 'r') as fp:
        for line in fp:
            if len(vmstat_matrix) == 0 or not vmstat_matrix[0]:
                title = re.match(r'procs[\s\-\w]+', line)
                if title is not None:
                    vmstat_matrix.insert(0, title.group().strip())
            elif len(vmstat_matrix) == 1 or not vmstat_matrix[1]:
                subtitle = re.search(r'r\s+b[\s\w]+', line)
                if subtitle is not None:
                    vmstat_matrix.insert(1, subtitle.group().rstrip().split())
            else:
                # match to filter out raw literals
                record = re.match(r'\s*\d+[\s\d]+[\r\n]+', line)
                if record is not None:
                    vmstat_matrix.insert(i, record.group().rstrip().split())
        return vmstat_matrix


def print_file(outfile, stat_list):
    if os.path.isfile(outfile):
        os.remove(outfile)
    with open(outfile, 'w') as f:
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

    f = open(outfile, 'w')
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
