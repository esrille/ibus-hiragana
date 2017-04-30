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
    '-' :'、', '_' :'、', '=' :'゛', '+' :'゛',
    '[' :'「', '{' :'「', ']' :'」', '}' :'」',
    '\'':'　', '"' :'　', '\\':'￥', '|' :'￥',
    '`':'｀', '~' :'｀',

    'q' :'。', 'w' :'か', 'e' :'た', 'r' :'こ', 't' :'さ', 'y' :'ら', 'u' :'ち', 'i' :'く', 'o' :'つ', 'p' :'，',
    'a' :'う', 's' :'し', 'd' :'て', 'f' :'け', 'g' :'せ', 'h' :'は', 'j' :'と', 'k' :'き', 'l' :'い', ';' :'ん', ':' :'ん',
    'z' :'．', 'x' :'ひ', 'c' :'す', 'v' :'ふ', 'b' :'へ', 'n' :'め', 'm' :'そ', ',' :'ね', '<' :'ね', '.' :'ほ', '>' :'ほ', '/' :'・', '?' :'・',
}

_shiftL = {
    '1' :'？', '!' :'？', '2' :'／', '@' :'／', '3' :'～', '#' :'～', '4' :'「', '$' :'「', '5' :'」', '%' :'」',
    '6' :'［ ', '^' :'［ ', '7' :'］', '&' :'］', '8' :'（', '*' :'（', '9' :'）', '(' :'）', '0' :'＿', ')' :'＿',
    '-' :'、', '_' :'、', '=' :'゜', '+' :'゜',
    '[' :'『', '{' :'『', ']' :'』', '}' :'』',
    '\'':'・', '"' :'・', '\\':'｜', '|' :'｜',
    '`':'…', '~' :'…',

    'q' :'ぁ', 'w' :'え', 'e' :'り', 'r' :'ゃ', 't' :'れ', 'y' :'ぱ', 'u' :'ぢ', 'i' :'ぐ', 'o' :'づ', 'p' :'ぴ',
    'a' :'を', 's' :'あ', 'd' :'な', 'f' :'ゅ', 'g' :'も', 'h' :'ば', 'j' :'ど', 'k' :'ぎ', 'l' :'ぽ', ';' :'ん', ':' :'ん',
    'z' :'ぅ', 'x' :'ー', 'c' :'ろ', 'v' :'や', 'b' :'ぃ', 'n' :'ぷ', 'm' :'ぞ', ',' :'ぺ', '<' :'ぺ', '.' :'ぼ', '>' :'ぼ', '/' :'・', '?' :'・',
}

_shiftR = {
    '1' :'？', '!' :'？', '2' :'／', '@' :'／', '3' :'～', '#' :'～', '4' :'「', '$' :'「', '5' :'」', '%' :'」',
    '6' :'［ ', '^' :'［ ', '7' :'］', '&' :'］', '8' :'（', '*' :'（', '9' :'）', '(' :'）', '0' :'＿', ')' :'＿',
    '-' :'、', '_' :'、', '=' :'゜', '+' :'゜',
    '[' :'『', '{' :'『', ']' :'』', '}' :'』',
    '\'':'・', '"' :'・', '\\':'｜', '|' :'｜',
    '`':'～', '~' :'～',

    'q' :'。', 'w' :'が', 'e' :'だ', 'r' :'ご', 't' :'ざ', 'y' :'よ', 'u' :'に', 'i' :'る', 'o' :'ま', 'p' :'ぇ',
    'a' :'ゔ', 's' :'じ', 'd' :'で', 'f' :'げ', 'g' :'ぜ', 'h' :'み', 'j' :'お', 'k' :'の', 'l' :'ょ', ';' :'っ', ':' :'っ',
    'z' :'．', 'x' :'び', 'c' :'ず', 'v' :'ぶ', 'b' :'べ', 'n' :'ぬ', 'm' :'ゆ', ',' :'む', '<' :'む', '.' :'わ', '>' :'わ', '/' :'ぉ', '?' :'ぉ',
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
