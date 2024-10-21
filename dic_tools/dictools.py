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
import gettext
import os
import sys

import diclib


def _(text):
    return gettext.dgettext('ibus-hiragana', text)


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
    diclib.output(dic, file=file, single=args.one)


def output_dic(dic, args, unparsed, header=''):
    if args.header and 0 < len(unparsed):
        header = get_header(unparsed[0])
    if args.output is None:
        output_inner(dic, args, unparsed, header)
    else:
        with open(args.output, mode='w') as file:
            output_inner(dic, args, unparsed, header, file)


def diff(args, unparsed):
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


def hyougai(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.hyougai(diclib.load(path)))
    output_dic(dic, args, unparsed)


def hyougai_yomi(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.hyougai_yomi(diclib.load(path)))
    output_dic(dic, args, unparsed)


def intersect(args, unparsed):
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


def lookup(args, unparsed):
    if len(unparsed) < 2:
        return
    word = unparsed[0]
    dic = {}
    for path in unparsed[1:]:
        dic = diclib.union(dic, diclib.load(path))
    dic = diclib.lookup(dic, word)
    output_dic(dic, args, unparsed[1:])


def mazeyomi(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.mazeyomi(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def symbol(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.kigou(diclib.load(path)))
    output_dic(dic, args, unparsed)


# 常用漢字表にない、おくりがなをふくんだ活用しない語をとりだします
def taigen(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.okuri(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def union(args, unparsed):
    dic = {}
    op = ''
    header = '; '
    for path in unparsed:
        header += op + path
        op = ' ∪ '
        dic = diclib.union(dic, diclib.load(path))
    output_dic(dic, args, unparsed, header)


def wago(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.wago(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def yougen(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.yougen(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def yutou(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.yutou(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def zyuubako(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.zyuubako(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def katakana(args, unparsed):
    dic = {}
    for path in unparsed:
        dic = diclib.union(dic, diclib.katakana(diclib.load(path)))
    dic = diclib.difference(dic, diclib.zyouyou())
    output_dic(dic, args, unparsed)


def dispatch(args, unparsed):
    if args.command == 'diff':
        diff(args, unparsed)
    elif args.command == 'hyougai':
        hyougai(args, unparsed)
    elif args.command == 'hyougai-yomi':
        hyougai_yomi(args, unparsed)
    elif args.command == 'intersect':
        intersect(args, unparsed)
    elif args.command == 'katakana':
        katakana(args, unparsed)
    elif args.command == 'lookup':
        lookup(args, unparsed)
    elif args.command == 'mazeyomi':
        mazeyomi(args, unparsed)
    elif args.command == 'symbol':
        symbol(args, unparsed)
    elif args.command == 'taigen':
        taigen(args, unparsed)
    elif args.command == 'union':
        union(args, unparsed)
    elif args.command == 'wago':
        wago(args, unparsed)
    elif args.command == 'yougen':
        yougen(args, unparsed)
    elif args.command == 'yutou':
        yutou(args, unparsed)
    elif args.command == 'zyuubako':
        zyuubako(args, unparsed)


DESCRIPTION = _("""Hiragana IME dictionary utilities

commands:
  diff ...
    output words in the first input file that are not in other input files
  hyougai ...
    output words that use hyougai-kanji in input files
  hyougai-yomi ...
    output words that use hyougai-yomi in input files
  intersect ...
    output words that are common to all input files
  katakana ...
    output words that are in katakana in input files
  lookup WORD ...
    find WORD in the input files
  mazeyomi ...
    output yutou-yomi and zyuubako-yomi words in all input files
  symbol ...
    output words using symbol characters in all input files
  taigen ...
    output non-conjugating words with okurigana in all input files, excluding single-kanji taigen listed in zyouyou kanji table
  union ...
    output all words in input files
  wago ...
    output native Japanese words in all input files
  yougen ...
    output conjugating words in all input files, excluding single-kanji yougen listed in zyouyou kanji table
  yutou ...
    output yutou-yomi words in all input files
  zyuubako ...
    output zyuubako-yomi words in all input files
""")


def main():
    parser = argparse.ArgumentParser(prog='ibus-hiragana-tool',
                                     add_help=False,
                                     description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('command',
                        choices=[
                            'diff',
                            'hyougai',
                            'hyougai-yomi',
                            'intersect',
                            'katakana',
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
    parser.add_argument('-h', '--help',
                        action='help',
                        help=_('show help options'))
    parser.add_argument('-o', '--output',
                        help=_('write output to OUTPUT'))
    parser.add_argument('--header',
                        help=_('output the header of the first input file'),
                        action='store_true')
    parser.add_argument('--one',
                        help=_('list one word per line'),
                        action='store_true')
    parser.add_argument('--version',
                        help=_('print version information'),
                        action='store_true')
    args, unparsed = parser.parse_known_args()
    dispatch(args, unparsed)


if __name__ == '__main__':
    gettext.bindtextdomain('ibus-hiragana', os.getenv('LOCALEDIR'))
    main()
