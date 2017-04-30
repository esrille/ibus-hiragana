# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace With Kanji input method for IBus
#
# Copyright (c) 2017 Esrille Inc.
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

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus

keysyms = IBus

import re

_normal = {
    '1' :'１', '!' :'１', '2' :'２', '@' :'２', '3' :'３', '#' :'３', '4' :'４', '$' :'４', '5' :'５', '%' :'５',
    '6' :'６', '^' :'６', '7' :'７', '&' :'７', '8' :'８', '*' :'８', '9' :'９', '(' :'９', '0' :'０', ')' :'０',
    '-' :'ー', '_' :'ー', '=' :'＝', '+' :'＝',
    '[' :'「', '{' :'「', ']' :'」', '}' :'」',
    '\'':'　', '"' :'　', '\\':'￥', '|' :'￥',
    '`':'｀', '~' :'｀',

    'q' :'ら', 'w' :'る', 'e' :'こ', 'r' :'は', 't' :'ょ', 'y' :'き', 'u' :'の', 'i' :'く', 'o' :'あ', 'p' :'れ',
    'a' :'た', 's' :'と', 'd' :'か', 'f' :'て', 'g' :'も', 'h' :'を', 'j' :'い', 'k' :'う', 'l' :'し', ';' :'ん', ':' :'ん',
    'z' :'ま', 'x' :'り', 'c' :'に', 'v' :'さ', 'b' :'な', 'n' :'す', 'm' :'つ', ',' :'、', '<' :'、', '.' :'。', '>' :'。', '/' :'っ', '?' :'っ',
}

_shiftL = {
    '1' :'！', '!' :'！', '2' :'＠', '@' :'＠', '3' :'＃', '#' :'＃', '4' :'＄', '$' :'＄', '5' :'％', '%' :'％',
    '6' :'＾', '^' :'＾', '7' :'＆', '&' :'＆', '8' :'＊', '*' :'＊', '9' :'（', '(' :'（', '0' :'）', ')' :'）',
    '-' :'＿', '_' :'＿', '=' :'＋', '+' :'＋',
    '[' :'『', '{' :'『', ']' :'』', '}' :'』',
    '\'':'・', '"' :'・', '\\':'｜', '|' :'｜',
    '`':'…', '~' :'…',

    'q' :'ひ', 'w' :'そ', 'e' :'・', 'r' :'ゃ', 't' :'ほ', 'y' :'ぎ', 'u' :'げ', 'i' :'ぐ', 'o' :'？', 'p' :'ゐ',
    'a' :'ぬ', 's' :'ね', 'd' :'ゅ', 'f' :'よ', 'g' :'ふ', 'h' :'゛', 'j' :'ぢ', 'k' :'ゔ', 'l' :'じ', ';' :'ゑ', ':' :'ゑ',
    'z' :'ぇ', 'x' :'ぉ', 'c' :'せ', 'v' :'ゆ', 'b' :'へ', 'n' :'ず', 'm' :'づ', ',' :'，', '<' :'，', '.' :'．', '>' :'．', '/' :'ゎ', '?' :'ゎ',
}

_shiftR = {
    '1' :'！', '!' :'！', '2' :'＠', '@' :'＠', '3' :'＃', '#' :'＃', '4' :'＄', '$' :'＄', '5' :'％', '%' :'％',
    '6' :'＾', '^' :'＾', '7' :'＆', '&' :'＆', '8' :'＊', '*' :'＊', '9' :'（', '(' :'（', '0' :'）', ')' :'）',
    '-' :'＿', '_' :'＿', '=' :'＋', '+' :'＋',
    '[' :'『', '{' :'『', ']' :'』', '}' :'』',
    '\'':'・', '"' :'・', '\\':'｜', '|' :'｜',
    '`':'～', '~' :'～',

    'q' :'び', 'w' :'ぞ', 'e' :'ご', 'r' :'ば', 't' :'ぼ', 'y' :'え', 'u' :'け', 'i' :'め', 'o' :'む', 'p' :'ろ',
    'a' :'だ', 's' :'ど', 'd' :'が', 'f' :'で', 'g' :'ぶ', 'h' :'お', 'j' :'ち', 'k' :'ー', 'l' :'み', ';' :'や', ':' :'や',
    'z' :'ヵ', 'x' :'ヶ', 'c' :'ぜ', 'v' :'ざ', 'b' :'べ', 'n' :'わ', 'm' :'ぃ', ',' :'ぁ', '<' :'ぁ', '.' :'゜', '>' :'゜', '/' :'ぅ', '?' :'ぅ',
}

def to_kana(preedit, keyval, state = 0, modifiers = 0):
    yomi = ''
    if keysyms.exclam <= keyval and keyval <= keysyms.asciitilde:
        if modifiers & 1:
            yomi = _shiftL[chr(keyval).lower()]
        elif modifiers & 2:
            yomi = _shiftR[chr(keyval).lower()]
        else:
            yomi = _normal[chr(keyval).lower()]
    return yomi, preedit

#
# test
#
if __name__ == '__main__':
    yomi, preedit = to_kana('', keysyms.j, 0, 0)
    print(yomi, preedit)
    yomi, preedit = to_kana('', keysyms.j, 0, 1)
    print(yomi, preedit)
    yomi, preedit = to_kana('', keysyms.j, 0, 2)
    print(yomi, preedit)
