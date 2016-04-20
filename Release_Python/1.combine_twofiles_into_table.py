#!/usr/bin/python
import argparse
import ntpath
import operator
import re
from datetime import datetime
from itertools import groupby

FMT = '%H:%M:%S'
file1 = ""
file2 = ""
outfile = ""


def main():
    global file1, file2, outfile

    # command line optinos
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', nargs=2)
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    file1 = args.file[0]
    file2 = args.file[1]
    outfile = args.output

    dic1 = filter_file_by_stat(file1)
    dic2 = filter_file_by_stat(file2)

    compared_dicts = dicts_compared(dic1, dic2)
    print_stats(compared_dicts[0], compared_dicts[1], dic1, dic2)

    # python -O xx.py   --without this print info
    # python xx.py      -- print this info
    if __debug__:
        for k, v in sort_dic(compared_dicts[0]):
            print ('{0}:  {1}'.format(k, v))
        print "********************"
        for k, v in sort_dic(compared_dicts[1]):
            print ('{0}:  {1}'.format(k, v))


def dicts_compared(d1, d2):
    """
    compare two dictionary and find out the the different value of the same key
    if it's the same key and value, output: {key, value}
    if it's the different key and value, output: {key, (value_d1, value_d2)}
    if there are extra items in the one of the dicts, save in the non_intersection dict for searching in the future.
    """
    non_intersection = {}
    result = {}
    # make sure dics_sort[0] is bigger than dics_sort[1]
    dics_sort = (d1, d2) if len(d1.keys()) - len(d2.keys()) >= 0 else (d2, d1)

    for key in dics_sort[0].keys():
        if key not in dics_sort[1]:
            result[key] = dics_sort[0][key]
            non_intersection[key] = dics_sort[0][key]
        elif d1[key] != d2[key]:
            # we need order of the result in the tuple, so using original dictionary
            result[key] = (d1[key], d2[key])
        else:
            result[key] = d1[key]
    return result, non_intersection


def sort_dic(dic):
    return sorted(dic.items(), key=operator.itemgetter(0))


def filter_file_by_stat(file_path):
    """
    filter file's content into dictionary: {adb command: its value}
    The special keys is "time", "version", "/proc/swaps", "battery", "/proc/zoneinfo"(ignore)

    The file's original content is:
      adb -s 24f8fc02 shell cat /sys/module/lowmemorykiller/parameters/adj :
      0,58,117,176,529,1000

    Special one:
      adb -s 24f8fc02 shell cat /proc/swaps :
      Filename				Type		Size	Used	Priority
      /dev/block/zram0                        partition	524284	521080	-1
    """
    file_stats = {}
    # For match time & version, so we start from the begin of the file
    regx = re.compile('.+?(?=adb.*?shell|\Z)', re.MULTILINE | re.DOTALL)
    with open(file_path, 'r') as fp:
        # combine every adb command & its result into one line, and find keywords with regex in each line
        for stat in [mat.group().replace('\n', ' ').replace('\r', '') + '\n' for mat in regx.finditer(fp.read())]:
            sys_infos = re.match(r".+? (\d\d:\d\d:\d\d).+?(\b\w+\b)[ ]*\n", stat)
            if sys_infos is not None:
                if sys_infos.group(1): file_stats.update({"time": sys_infos.group(1)})
                if sys_infos.group(2): file_stats.update({"version": sys_infos.group(2)})
            else:
                try:
                    m = re.search('.* ([^ ]+)[ ]+:[ ]+(.+?)\n', stat)
                    if m.group(1) == '/proc/swaps':
                        index = 0
                        # split "/proc/swaps" by '/dev/block/ and find the keywords in each group
                        for block in re.split('/dev/block/', m.group()):
                            z = re.match(r"(zram\d).+?(\b\d+).+?(\b\d+)", block)
                            if z is not None:
                                file_stats.update({"{0}({1})".format(m.group(1), index):
                                                       "{0}: {1}/{2}".format(z.group(1), z.group(3), z.group(2))})
                                index += 1
                    elif m.group(1) == 'battery':
                        ba_stats = re.compile(r".+?level: (\d+\b).+?temperature: (\d+)").match(m.group()).groups()
                        if ba_stats[0]: file_stats.update({"{0} level".format(m.group(1)): ba_stats[0]})
                        if ba_stats[1]: file_stats.update({"{0} temperature".format(m.group(1)): ba_stats[1]})
                    elif m.group(1) == '/proc/zoneinfo':
                        continue
                    else:
                        file_stats.update({m.group(1): m.group(2)})
                except AttributeError:
                    print "Error Attribute: stat= " + stat

    if __debug__:
        for k, v in file_stats.items():
            print (k, v)
        print "size=" + str(len(file_stats))

    return file_stats


def print_stats(data, non_intersection, dic1, dic2):
    """
    print the result dictionary into the file with the html format
    """
    with open(outfile, 'a') as the_file:
        # write the title code
        the_file.write('<table border="1">\n')
        the_file.write('<tr>\n')
        the_file.write("<th>Items</th> <th>{0}</th> <th>{1}</th> <th>result</th>\n".format(ntpath.basename(file1),
                                                                                           ntpath.basename(file2)))
        the_file.write('</tr>\n')

        # write time and version first.
        the_file.write('<tr>\n')
        the_file.write(
            "<td>{0}</td> <td>{1}</td> <td>{2}</td> <td>{3}</td>\n".format("time", data['time'][0], data['time'][1],
                                     'Duration: {0}'.format(datetime.strptime(data['time'][1], FMT)
                                                            - datetime.strptime(data['time'][0], FMT))))
        the_file.write('</tr>\n')
        the_file.write('<tr>\n')
        the_file.write("<td>{0}</td> <td></td> <td></td> <td>{1}</td>\n".format("version", data['version']))
        the_file.write('</tr>\n')

        # remove time & version item in data dictionary
        del data['time']
        del data['version']

        for key, value in sort_dic(data):
            # <td>January</td> <td>$100</td>
            the_file.write('<tr>\n')
            if key in non_intersection:
                # if it's unique item, find out which dic it belong to.
                if key in dic1:
                    the_file.write("<td>{0}</td> <td>{1}</td> <td></td> <td>{2}</td>\n".format(key, value, value))
                elif key in dic2:
                    the_file.write("<td>{0}</td> <td></td> <td>{1}</td> <td>{2}</td>\n".format(key, value, value))
                else:
                    raise AttributeError
            elif isinstance(value, tuple):
                # Here is the different values between item in the two files
                zram1 = re.match(r"(zram\d): (\d+)/(\d+)", value[0])
                zram2 = re.match(r"(zram\d): (\d+)/(\d+)", value[1])
                if zram1 is not None or zram2 is not None:
                    the_file.write(
                        "<td>{0}</td> <td>{1}</td> <td>{2}</td> <td>{3}</td>\n".format(key, value[0], value[1],
                                "{0}: {1}/{2}".format(zram1.group(1),int(zram1.group(2)) - int(zram2.group(2)),
                                                                     int(zram1.group(3)) - int(zram2.group(3)))))
                else:
                    the_file.write(
                        "<td>{0}</td> <td>{1}</td> <td>{2}</td> <td>{3}</td>\n"
                            .format(key, value[0], value[1], int(value[0]) - int(value[1])))
            else:
                # If you want to only remove whitespace from the beginning and end you can use strip()
                the_file.write("<td>{0}</td> <td></td> <td></td> <td>{1}</td>\n".format(key, value.strip()))
            the_file.write('</tr>\n')
        the_file.write('</table>\n')


def group_special_lines_into_one(filename, out_file):
    """use empty line as the delimiter to group lines into one"""
    with open(filename, 'r') as f, open(out_file, 'w') as g:
        # group lines without empty line, use empty line as delimiter
        groups = groupby(f, key=lambda v: not str.isspace(v))
        # if it is the empty line, key is false
        g.writelines(''.join(group).replace('\n', '') + '\n' for key, group in groups if key)
        for key, group in groupby(f, lambda v: not str.isspace(v)):
            for thing in group:
                print "The key is %s, The group is %s" % (key, str(thing).replace('\n', ''))
            print " "


if __name__ == '__main__':
    main()
