#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Esrille Inc.
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
    base = dic.load(path)

    # 人名、地名、駅名、記号については、人名漢字の使用を許容し、例外辞書に格納しておきます。
    zinmei = dic.load('/usr/share/skk/SKK-JISYO.jinmei')
    reigai_zinmei = dic.intersection(base, zinmei)
    geo = dic.load('/usr/share/skk/SKK-JISYO.geo')
    reigai_geo = dic.intersection(base, geo)
    station = dic.load('/usr/share/skk/SKK-JISYO.station')
    reigai_station = dic.intersection(base, station)
    reigai_kigou = dic.kigou(base)
    reigai = dic.union(reigai_zinmei, reigai_geo)
    reigai = dic.union(reigai, reigai_station)
    reigai = dic.union(reigai, reigai_kigou)

    # 基本辞書をつくります。
    base = dic.difference(base, reigai)                     # 例外辞書の内容を削除
    base  = dic.difference(base, dic.hyougai(base))         # 表外の漢字を使用している熟語を削除
    base = dic.difference(base, dic.zinmei(base))           # 人名漢字を使用している熟語を削除
    base = dic.difference(base, dic.okuri(base))            # おくりがなのついた熟語を削除
    base = dic.difference(base, dic.hyougai_yomi(base))     # 表外のよみかたをつかっている熟語を削除
    base = dic.difference(base, dic.wago(base))             # 和語の熟語を削除

    # 実際に使用する辞書をつくります。
    dict = dic.union(base, dic.taigen_wago())               # 和語の名詞を追加
    yougen = dic.yougen()
    # yougen = dic.kyouiku(yougen)                            # 和語の用言の漢字を教育用漢字に限定します。
    dict = dic.union(dict, yougen)                          # 和語の用言を追加
    dict = dic.union(dict, reigai)                          # 例外を追加
    dict = dic.union(dict, dic.load('fuhyou.dic'))          # 常用漢字表・付表の熟語を追加。
    dict = dic.union(dict, dic.load('greece.dic'))          # ギリシア文字辞書を追加。
    dict = dic.union(dict, dic.load('tc2.compat.dic'))      # tc2のmazegaki.dic辞書から選択した単語を追加。
    dict = dic.union(dict, dic.load('my.dic'))              # 独自に追加したい熟語を追加。

    # ヘッダーを出力します。
    print(';; 日本語漢字置換インプット メソッド')
    print(';; Copyright (c) 2017 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-replace-with-kanji')
    print(';;')
    print(';; この辞書は、')
    print(';;  ', path)
    print(';; をもとに、日本語漢字置換インプット メソッド用にプログラムで')
    print(';; 自動生成した辞書です。')
    print(';;')
    print(';;')
    dic.copy_header(path)
    dic.output(dict)
