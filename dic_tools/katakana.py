#!/usr/bin/python3
#
# Copyright (c) 2017-2022 Esrille Inc.
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

import codecs
import re
import sys
import dic

re_katakana = re.compile(r"[ァ-ー]{2,}")

copyright = ''


def load(path):
    global copyright
    s = set()
    try:
        file = codecs.open(path, "r", "euc_jp")
    except:
        pass
    else:
        for row in file:
            row = row.strip(" \n")
            if not row:
                continue
            if not copyright:
                pos = row.find('EDICT2')
                if 0 < pos:
                    copyright = row[pos:].strip(" \n/").split('/')
            if not re_katakana.match(row):
                continue
            row = row.split(" ", 1)
            yomi = row[0]
            yomi = yomi.strip(" \n/")
            yomi = re.split(r'[;・]', yomi)
            for i in yomi:
                found = re_katakana.match(i)
                if found:
                    s.add(found.group())
        file.close()

    # Remove typos and so on in the original file.
    try:
        s.remove('アイウエオ')
        s.remove('アアダプタ')
        s.remove('アアダプター')
        s.remove('フアン')
        s.remove('ガサ')
        s.remove('テカ')
        # any word that begins 'を' makes the normal Japanese language hard to parse.
        s.remove('ヲコト')
        s.remove('ヲタ')
        s.remove('ヲタク')
        s.remove('ヲッカ')
    except:
        pass

    return s


# EDICT2 ファイルからカタカナ辞書を生成して出力します。
def main():
    global copyright

    path = "edict2"
    if 2 <= len(sys.argv):
        path = sys.argv[1]
    gairaigo = load(path)

    print(';; Hiragana IME for IBus')
    print(';; Copyright (c) 2017-2022 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-hiragana')
    print(';;')
    print(';; This file is made available under a Creative Commons Attribution-')
    print(';; ShareAlike Licence (V3.0). The Licence Deed can be viewed,')
    print(';;   https://creativecommons.org/licenses/by-sa/3.0/')
    print(';;')
    print(';; Note this file is generated from the EDIT2 dictionary file.')
    print(';; EDIT2 is the property of the Electronic Dictionary Research and')
    print(';; Development Group, and is used in conformance with the Group\'s licence.')
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
