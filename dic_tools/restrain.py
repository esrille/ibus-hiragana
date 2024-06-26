#!/usr/bin/python3
#
# Copyright (c) 2017-2024 Esrille Inc.
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

import os
import sys

import dic
from toolpath import toolpath


def main():
    path = toolpath('third_party/skk/SKK-JISYO.ML')
    if 2 <= len(sys.argv):
        path = sys.argv[1]
    skk = dic.load(path)
    skk = dic.difference(skk, dic.yougen(skk))                        # 用言を削除

    dict = dic.difference(skk, dic.load(toolpath('drop_6.dic')))
    dict = dic.union(dict, dic.load(toolpath('add_6.dic')))
    grade = 8
    if 3 <= len(sys.argv):
        grade = int(sys.argv[2])

    # 人名、地名、駅名、記号については、人名漢字の使用を許容し、例外辞書に格納しておきます。
    reigai = dic.load(toolpath('third_party/skk/SKK-JISYO.jinmei'))
    reigai = dic.union(reigai, dic.load(toolpath('third_party/skk/SKK-JISYO.geo')))
    reigai = dic.union(reigai, dic.load(toolpath('third_party/skk/SKK-JISYO.station')))
    reigai = dic.intersection(reigai, skk)
    reigai = dic.union(reigai, dic.load(toolpath('tc2.compat.dic')))
    reigai = dic.union(reigai, dic.kigou(skk))
    reigai = dic.union(dic.load(toolpath('reigai.dic')), reigai)      # 独自に追加したい熟語を追加。
    dict = dic.difference(dict, reigai)                               # 例外辞書の内容を削除
    if grade <= 6:
        reigai = dic.difference(reigai, dic.hyougai(reigai))
        reigai = dic.difference(reigai, dic.hyougai_yomi(reigai, grade))

    zyosuusi = dic.load(toolpath('zyosuusi.dic'))
    zyosuusi = dic.difference(zyosuusi, dic.hyougai_yomi(zyosuusi, grade))

    # 基本辞書をつくります。
    dict = dic.difference(dict, dic.okuri(dict))                      # おくりがなのついた熟語を削除
    dict = dic.difference(dict, dic.hyougai(dict))                    # 表外の漢字を使用している熟語を削除
    dict = dic.difference(dict, dic.hyougai_yomi(dict, grade))        # 表外のよみかたをつかっている熟語を削除
    dict = dic.difference(dict, dic.wago(dict, grade))                # 和語の熟語を削除
    dict = dic.union(dict, dic.load_huhyou(toolpath('huhyou.dic'), grade))    # 常用漢字表・付表の熟語を追加。
    dict = dic.union(dic.zyouyou(grade), dict)                        # 常用漢字を追加
    dict = dic.union(zyosuusi, dict)                                  # 助数詞を先頭に追加
    dict = dic.union(dict, reigai)                                    # 例外を追加

    if 7 <= grade:
        dict = dic.union(dict, dic.load(toolpath('add_7.dic')))
    if 8 <= grade:
        dict = dic.union(dict, dic.load(toolpath('add_8.dic')))
    if 9 <= grade:
        dict = dic.union(dict, dic.load(toolpath('add_9.dic')))
    if 6 < grade:
        dict = dic.union(dict, dic.load(toolpath('greek.dic')))       # ギリシア文字辞書を追加。

    dict = dic.difference(dict, dic.load(toolpath('drop.dic')))       # 独自に削除したい熟語を削除。

    # ヘッダーを出力します。
    print(';; Hiragana IME for IBus')
    print(';; Copyright (c) 2017-2024 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-hiragana')
    print(';;')
    print(';; この辞書は、')
    print(';;  ', os.path.basename(path))
    print(';; をもとに、ひらがなIME用にプログラムで自動生成した辞書です。')
    print(';;')
    print(';;')
    dic.copy_header(path)
    dic.output(dict)


if __name__ == '__main__':
    main()
