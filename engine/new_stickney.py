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

    'q' :'つ', 'w' :'と', 'e' :'こ', 'r' :'く', 't' :'け', 'y' :'や', 'u' :'ゆ', 'i' :'よ', 'o' :'な', 'p' :'に',
    'a' :'た', 's' :'は', 'd' :'し', 'f' :'か', 'g' :'て', 'h' :'ん', 'j' :'う', 'k' :'い', 'l' :'゛', ';' :'の', ':' :'の',
    'z' :'そ', 'x' :'せ', 'c' :'す', 'v' :'き', 'b' :'さ', 'n' :'っ', 'm' :'れ', ',' :'、', '<' :'、', '.' :'。', '>' :'。', '/' :'を', '?' :'を',
}

_shift = {
    '1' :'！', '!' :'！', '2' :'＠', '@' :'＠', '3' :'＃', '#' :'＃', '4' :'＄', '$' :'＄', '5' :'％', '%' :'％',
    '6' :'＾', '^' :'＾', '7' :'＆', '&' :'＆', '8' :'＊', '*' :'＊', '9' :'（', '(' :'（', '0' :'）', ')' :'）',
    '-' :'＿', '_' :'＿', '=' :'＋', '+' :'＋',
    '[' :'『', '{' :'『', ']' :'』', '}' :'』',
    '\'':'・', '"' :'・', '\\':'｜', '|' :'｜',

    'q' :'', 'w' :'ち', 'e' :'ぬ', 'r' :'ね', 't' :'', 'y' :'む', 'u' :'め', 'i' :'お', 'o' :'ま', 'p' :'み',
    'a' :'゜', 's' :'ひ', 'd' :'ふ', 'f' :'へ', 'g' :'ほ', 'h' :'わ', 'j' :'る', 'k' :'り', 'l' :'あ', ';' :'も', ':' :'も',
    'z' :'', 'x' :'', 'c' :'', 'v' :'', 'b' :'', 'n' :'ろ', 'm' :'ら', ',' :'え', '<' :'え', '.' :'ー', '>' :'ー', '/' :'？', '?' :'？',
}

def to_kana(preedit, keyval, state = 0):
    yomi = ''
    if keysyms.exclam <= keyval and keyval <= keysyms.asciitilde:
        if (state & IBus.ModifierType.SHIFT_MASK):
            yomi = _shift[chr(keyval).lower()]
        else:
            yomi = _normal[chr(keyval).lower()]
    return yomi, preedit

#
# test
#
if __name__ == '__main__':
    yomi, preedit = to_kana('', keysyms.j)
    print(yomi, preedit)
    yomi, preedit = to_kana('', keysyms.j, IBus.ModifierType.SHIFT_MASK)
    print(yomi, preedit)
