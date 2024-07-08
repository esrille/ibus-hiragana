#!/usr/bin/env python3
#
# Copyright (c) 2024 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

import diclib


def get_header(filename):
    header = ''
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith(';'):
                header += line
            else:
                break
    return header.strip()


def output_inner(dic, args, unparsed, header='', file=sys.stdout):
    if header:
        print(header, file=file)
    diclib.output(dic, file=file, single=args.single)


def output_dic(dic, args, unparsed, header=''):
    if args.header and 0 < len(unparsed):
        header = get_header(unparsed[0])
    if args.output is None:
        output_inner(dic, args, unparsed, header)
    else:
        with open(args.output, mode='w') as file:
            output_inner(dic, args, unparsed, header, file)


def diff(args, unparsed, output):
    dic = {}
    op = ''
    header = '; '
    for path in unparsed:
        header += op + path
        if op == '':
            dic = diclib.load(path)
            op = ' - '
        else:
            dic = diclib.difference(dic, diclib.load(path))
    output_dic(dic, args, unparsed, header)


def hyougai(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.hyougai(diclib.load(path)))
    output_dic(dic, args, unparsed)


def intersect(args, unparsed, output):
    dic = {}
    op = ''
    header = '; '
    for path in unparsed:
        header += op + path
        if op == '':
            dic = diclib.load(path)
            op = ' ∩ '
        else:
            dic = diclib.intersection(dic, diclib.load(path))
    output_dic(dic, args, unparsed, header)


def lookup(args, unparsed, output):
    if len(unparsed) < 2:
        return
    word = unparsed[0]
    dic = {}
    for path in unparsed[1:]:
        dic = diclib.union(dic, diclib.load(path))
    dic = diclib.lookup(dic, word)
    output_dic(dic, args, unparsed[1:])


def mazeyomi(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.mazeyomi(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def symbol(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.kigou(diclib.load(path)))
    output_dic(dic, args, unparsed)


# 常用漢字表にない、おくりがなをふくんだ活用しない語をとりだします
def taigen(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.okuri(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def union(args, unparsed, output):
    dic = {}
    op = ''
    header = '; '
    for path in unparsed:
        header += op + path
        op = ' ∪ '
        dic = diclib.union(dic, diclib.load(path))
    output_dic(dic, args, unparsed, header)


def wago(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.wago(diclib.load(path), okuri=False))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def yougen(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.yougen(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def yutou(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.yutou(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def zyuubako(args, unparsed, output):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.zyuubako(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def dispatch(args, unparsed, output):
    if args.command == 'diff':
        diff(args, unparsed, output)
    elif args.command == 'hyougai':
        hyougai(args, unparsed, output)
    elif args.command == 'intersect':
        intersect(args, unparsed, output)
    elif args.command == 'lookup':
        lookup(args, unparsed, output)
    elif args.command == 'mazeyomi':
        mazeyomi(args, unparsed, output)
    elif args.command == 'symbol':
        symbol(args, unparsed, output)
    elif args.command == 'taigen':
        taigen(args, unparsed, output)
    elif args.command == 'union':
        union(args, unparsed, output)
    elif args.command == 'wago':
        wago(args, unparsed, output)
    elif args.command == 'yougen':
        yougen(args, unparsed, output)
    elif args.command == 'yutou':
        yutou(args, unparsed, output)
    elif args.command == 'zyuubako':
        zyuubako(args, unparsed, output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=[
        'diff',
        'hyougai',
        'intersect',
        'lookup',
        'mazeyomi',
        'symbol',
        'taigen',
        'union',
        'wago',
        'yougen',
        'yutou',
        'zyuubako',
    ])
    parser.add_argument('-o', '--output')
    parser.add_argument('--header', action='store_true')
    parser.add_argument('--single', action='store_true')
    args, unparsed = parser.parse_known_args()
    dispatch(args, unparsed, sys.stdout)


if __name__ == '__main__':
    main()
