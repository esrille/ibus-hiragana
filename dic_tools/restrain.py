#!/usr/bin/python3
#
# Copyright (c) 2017-2025 Esrille Inc.
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

import diclib
from toolpath import toolpath


def main():
    path = toolpath('third_party/skk/SKK-JISYO.ML')
    if 2 <= len(sys.argv):
        path = sys.argv[1]
    grade = 9
    if 3 <= len(sys.argv):
        grade = int(sys.argv[2])

    # もとにするSKK辞書をよみこむ
    skk = diclib.load(path)
    skk = diclib.difference(skk, diclib.yougen(skk))                    # 用言を削除

    # 人名、地名、駅名、記号をふくむ例外辞書をつくります。
    # 小学生用の辞書をのぞき、漢字制限はかけません。
    reigai = diclib.load(toolpath('third_party/skk/SKK-JISYO.jinmei'))
    reigai = diclib.union(reigai, diclib.load(toolpath('third_party/skk/SKK-JISYO.geo')))
    reigai = diclib.union(reigai, diclib.load(toolpath('third_party/skk/SKK-JISYO.station')))
    reigai = diclib.intersection(reigai, skk)
    reigai = diclib.union(reigai, diclib.load(toolpath('tc2.compat.dic')))
    reigai = diclib.union(reigai, diclib.kigou(skk))
    reigai = diclib.union(diclib.load(toolpath('reigai.dic')), reigai)  # 独自に追加したい語を追加
    if grade <= 6:
        reigai = diclib.difference(reigai, diclib.hyougai(reigai))
        reigai = diclib.difference(reigai, diclib.hyougai_yomi(reigai, grade))

    # 基本辞書をつくります。
    dict = diclib.difference(skk, diclib.load(toolpath('drop_6.dic')))
    dict = diclib.difference(dict, diclib.zyouyou(9))                  # 常用漢字をいったん削除
    dict = diclib.union(dict, diclib.load(toolpath('add_6.dic')))
    if 7 <= grade:
        dict = diclib.union(dict, diclib.load(toolpath('add_7.dic')))
    if 8 <= grade:
        dict = diclib.union(dict, diclib.load(toolpath('add_8.dic')))
    dict = diclib.difference(dict, reigai)                              # 例外辞書の内容を削除
    dict = diclib.difference(dict, diclib.okuri(dict))                  # おくりがなのついた語を削除
    dict = diclib.difference(dict, diclib.hyougai_yomi(dict, grade))    # 表外のよみかたをつかっている語を削除
    dict = diclib.difference(dict, diclib.wago(dict, grade))            # 和語の語を削除
    dict = diclib.difference(dict, diclib.mazeyomi(dict, grade))        # 重箱よみと湯桶よみの語を削除
    if 9 <= grade:
        dict = diclib.union(dict, diclib.load(toolpath('add_9.dic')))
    dict = diclib.difference(dict, diclib.hyougai(dict))                # 表外の漢字を使用している語を削除
    huhyou = diclib.load_huhyou(toolpath('huhyou.dic'), grade)
    dict = diclib.union(diclib.zyouyou(grade, exclude_special=True), dict)  # 常用漢字を追加
    dict = diclib.union(huhyou, dict)                                   # 常用漢字表・付表の語を追加
    dict = diclib.difference(dict, diclib.permissible())                # 許容されているおくりがなを削除
    zyosuusi = diclib.load(toolpath('zyosuusi.dic'))
    zyosuusi = diclib.difference(zyosuusi, diclib.hyougai_yomi(zyosuusi, grade))
    dict = diclib.union(zyosuusi, dict)                                 # 助数詞を先頭に追加

    # 例外辞書をマージします。
    dict = diclib.union(dict, reigai)
    if 6 < grade:
        dict = diclib.union(dict, diclib.load(toolpath('greek.dic')))   # ギリシア文字を追加。
    dict = diclib.difference(dict, diclib.load(toolpath('drop.dic')))   # 独自に削除したい語を削除。

    # ヘッダーを出力します。
    print(';; Hiragana IME for IBus')
    print(';; Copyright (c) 2017-2025 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-hiragana')
    print(';;')
    print(';; この辞書は、')
    print(';;  ', os.path.basename(path))
    print(';; をもとに、ひらがなIME用にプログラムで生成した辞書です。')
    print(';;')
    print(';;')
    diclib.copy_header(path)
    diclib.output(dict)


if __name__ == '__main__':
    main()
