#!/usr/bin/python3
#
# Copyright (c) 2017-2021 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain base copy of the License at:
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

from signal import signal, SIGPIPE, SIG_DFL

import dic

if __name__ == '__main__':
    signal(SIGPIPE, SIG_DFL)

    path = '/usr/share/skk/SKK-JISYO.ML'
    if 2 <= len(sys.argv):
        path = sys.argv[1]
    dict = dic.load(path)
    dict = dic.difference(dict, dic.yougen(dict))                   # 用言を削除
    dict = dic.union(dict, dic.load('my.dic'))                      # 独自に追加したい熟語を追加。

    grade = 8
    if 3 <= len(sys.argv):
        grade = int(sys.argv[2])

    # 人名、地名、駅名、記号については、人名漢字の使用を許容し、例外辞書に格納しておきます。
    zinmei = dic.load('/usr/share/skk/SKK-JISYO.jinmei')
    reigai_zinmei = dic.intersection(dict, zinmei)
    geo = dic.load('/usr/share/skk/SKK-JISYO.geo')
    reigai_geo = dic.intersection(dict, geo)
    station = dic.load('/usr/share/skk/SKK-JISYO.station')
    reigai_station = dic.intersection(dict, station)
    reigai_kigou = dic.kigou(dict)
    reigai = dic.union(reigai_zinmei, reigai_geo)
    reigai = dic.union(reigai, reigai_station)
    reigai = dic.union(reigai, reigai_kigou)
    dict = dic.difference(dict, reigai)                             # 例外辞書の内容を削除
    if grade <= 6:
        reigai = dic.difference(reigai, dic.hyougai(reigai))
        reigai = dic.difference(reigai, dic.hyougai_yomi(reigai, grade))

    zyosuusi = dic.load('zyosuusi.dic')
    zyosuusi = dic.difference(zyosuusi, dic.hyougai_yomi(zyosuusi, grade))

    # 基本辞書をつくります。
    dict = dic.difference(dict, dic.okuri(dict))                    # おくりがなのついた熟語を削除
    dict = dic.difference(dict, dic.hyougai(dict))                  # 表外の漢字を使用している熟語を削除
    dict = dic.difference(dict, dic.hyougai_yomi(dict, grade))      # 表外のよみかたをつかっている熟語を削除
    dict = dic.difference(dict, dic.wago(dict, grade))              # 和語の熟語を削除
    dict = dic.union(dict, dic.load_huhyou('huhyou.dic', grade))    # 常用漢字表・付表の熟語を追加。
    dict = dic.union(dic.zyouyou(grade), dict)                      # 常用漢字を追加
    dict = dic.union(zyosuusi, dict)                                # 助数詞を先頭に追加
    dict = dic.union(dict, reigai)                                  # 例外を追加
    if 8 <= grade:
        dict = dic.union(dict, dic.load('tc2.compat.dic'))          # tc2のmazegaki.dic辞書から選択した単語を追加。
    if 6 < grade:
        dict = dic.union(dict, dic.load('greek.dic'))               # ギリシア文字辞書を追加。

    dict = dic.difference(dict, dic.load('drop.dic'))               # 独自に削除したい熟語を削除。
    dict = dic.union(dict, dic.load('basic.dic'))                   # 「にほん」を追加。

    # ヘッダーを出力します。
    print(';; Hiragana IME for IBus')
    print(';; Copyright (c) 2017-2021 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-hiragana')
    print(';;')
    print(';; この辞書は、')
    print(';;  ', path)
    print(';; をもとに、ひらがなIME用にプログラムで自動生成した辞書です。')
    print(';;')
    print(';;')
    dic.copy_header(path)
    dic.output(dict)
