#!/usr/bin/python3
#
# Copyright (c) 2017-2023 Esrille Inc.
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

import re
import sys

import dic

RE_KATAKANA = re.compile(r'[ァ-ー]{2,}')

copyright = ''


def load(path):
    global copyright
    s = set()
    with open(path, encoding='euc_jp') as f:
        for row in f:
            row = row.strip(' \n')
            if not row:
                continue
            if not copyright:
                pos = row.find('EDICT2')
                if 0 < pos:
                    copyright = row[pos:].strip(' \n/').split('/')
            if not RE_KATAKANA.match(row):
                continue
            row = row.split(' ', 1)
            yomi = row[0]
            yomi = yomi.strip(' \n/')
            yomi = re.split(r'[;・]', yomi)
            for i in yomi:
                found = RE_KATAKANA.match(i)
                if found:
                    s.add(found.group())
    return s


# EDICT2 ファイルからカタカナ辞書を生成して出力します。
def main():
    global copyright

    path = 'edict2'
    if 2 <= len(sys.argv):
        path = sys.argv[1]
    gairaigo = load(path)

    if 3 <= len(sys.argv):
        with open(sys.argv[2]) as f:
            for line in f:
                if line[0] == ';':
                    continue
                gairaigo.discard(line.strip())

    print(';; Hiragana IME for IBus')
    print(';; Copyright (c) 2017-2024 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-hiragana')
    print(';;')
    print(';; This file is made available under a Creative Commons Attribution-')
    print(';; ShareAlike Licence (V3.0). The Licence Deed can be viewed,')
    print(';;   https://creativecommons.org/licenses/by-sa/3.0/')
    print(';;')
    print(';; Note this file is generated from the EDIT2 dictionary file.')
    print(';; EDIT2 is the property of the Electronic Dictionary Research and')
    print(";; Development Group, and is used in conformance with the Group's licence.")
    print(';;')
    for i in copyright:
        print(';;  ', i)
    print(';;')
    print(';;   https://www.edrdg.org/jmdict/edict.html')
    print(';;')

    for i in sorted(gairaigo):
        print(dic.to_hirakana(i), ' /', i, '/', sep='')


if __name__ == '__main__':
    main()
