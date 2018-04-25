#!/usr/bin/python
# coding=utf-8

import os
import sys

UTDID = 'utdid'
CODE = 'code'
OFFLINE = 'offline'
TIME = 'time'
VERSION = 'version'
MODEL = 'model'

TITLE = (UTDID, CODE, OFFLINE, TIME, VERSION, MODEL)


def read_file(filename):
    with open(filename, 'r') as fp:
        return fp.read()


def prepare_dic(file_str):
    result_dic = {}
    matrix = []
    for line in file_str.split('\n'):
        items = line.split(',')
        matrix.append(items)
    # 转置矩阵
    item_list = [[row[i] if i < len(row) else "" for row in matrix] for i in range(len(matrix[0]))]

    title_index = 0
    for idx, val in enumerate(item_list):  # 返回list的index
        # FIXME: 这里根据数据查询结果提取TITLE里的数据
        if idx == 0 or idx == 1 or idx == 3 or idx == 4 or idx == 5 or idx == 7:
            result_dic.update({TITLE[title_index]: val})
            title_index += 1

    # print_dic(result_dic)
    return result_dic


def split_dict_by_offline(raw_dic):
    offline_dic = {}
    online_dic = {}
    invalid_dic = {}
    for key, val in raw_dic.items():
        offline_values = []
        online_values = []
        invalid_values = []
        for index in range(len(raw_dic.get(OFFLINE))):
            if raw_dic.get(OFFLINE)[index] == 'true':
                offline_values.append(val[index])
            elif raw_dic.get(OFFLINE)[index] == 'false':
                online_values.append(val[index])
            else:
                invalid_values.append(val[index])
        offline_dic.update({key: offline_values})
        online_dic.update({key: online_values})
        invalid_dic.update({key: invalid_values})
    # print '### offline_dic:'
    # print print_dic(offline_dic)
    # print '### online_dic:'
    # print print_dic(online_dic)
    # print '### invalid_dic:'
    # print print_dic(invalid_dic)
    return offline_dic, online_dic


def parse_code(code_list):
    # How can I count the occurrences of a list item in Python?
    # https://stackoverflow.com/a/23909767/4710864
    return dict((x, code_list.count(x)) for x in set(code_list))


def print_dic(content):
    for key, val in content.items():
        print key, len(val), '  ', val


def write_content(outfile, content):
    with open(outfile, 'a') as f:
        f.write(content)


def write_to_file(output_dict, outfile):
    with open(outfile, 'a') as f:
        for key, val in output_dict.items():
            if isinstance(val, dict):
                f.write("{0}:\n".format(key))
                for k, v in dict(output_dict.get('code_table')).items():
                    f.write("\t{0} {1}\n".format(k, v))
            else:
                f.write("{0} {1}\n".format(key, val))


def silent_remove(outfile):
    if os.path.isfile(outfile):
        os.remove(outfile)


def create_data(request_value_dic):
    online_table = {}
    code_count = len(request_value_dic.get(CODE))
    utdid_count = len(set(request_value_dic.get(UTDID)))
    online_table['code_count'] = code_count
    online_table['utdid_count'] = utdid_count
    online_table['code_table'] = parse_code(request_value_dic.get(CODE))
    print '*****************'
    print online_table
    return online_table


def main(filename, outfile):
    offline_dic, online_dic = split_dict_by_offline(prepare_dic(read_file(filename)))
    offline_data = create_data(offline_dic)
    online_data = create_data(online_dic)

    silent_remove(outfile)
    write_content(outfile, str('\n *** OFFLINE ****:\n'))
    write_to_file(offline_data, outfile)
    write_content(outfile, str('\n *** ONLINE ***:\n'))
    write_to_file(online_data, outfile)


if __name__ == '__main__':
    # 检查参数合法性
    if len(sys.argv) == 3:
        request_file = sys.argv[1]
        if not os.path.isfile(request_file):
            print '[-] ' + request_file + 'does not exist.'
            exit(0)
        if not os.access(request_file, os.R_OK):
            print '[-] ' + request_file + 'access denied.'
            exit(0)
    else:
        print '[-] Usage: ' + str(sys.argv[0]) + '<filename>' + ' <outfilename>'
        exit(0)
    main(sys.argv[1], sys.argv[2])
