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

import os
import re

_re_not_yomi = re.compile(r'[^ぁ-んァ-ヶー]')

class Dictionary:

    __dict = {}

    __yomi = ''
    __no = 0
    __cand = []

    def __init__(self):
        pathname = os.path.join(os.getenv('IBUS_REPLACE_WITH_KANJI_LOCATION'), 'restrained.dic')
        print(pathname, flush=True)
        file = open(pathname, 'r')
        for line in file:
            if line[0] == ';':
                continue;
            p = line.strip(' \n/').split(' ', 1)
            yomi = p[0]
            cand = p[1].strip(' \n/').split('/')
            self.__dict[yomi] = cand

    def reset(self):
        self.__yomi = ''

    def next(self):
        if self.__no + 1 < len(self.__cand):
            self.__no += 1
        return self.__cand[self.__no];

    def previous(self):
        if 0 < self.__no:
            self.__no -= 1
        return self.__cand[self.__no];

    def current(self):
        if self.__yomi:
            return self.__cand[self.__no];
        return ''

    def set_current(self, index):
        index = int(index)
        if self.__yomi and 0 <= index and index < len(self.__cand):
            self.__no = index;

    def reading(self):
        return self.__yomi

    def cand(self):
        if self.__yomi:
            return self.__cand;
        return []

    def lookup(self, yomi):
        self.reset()
        size = len(yomi)
        for i in range(size - 1, -1, -1):
            y = yomi[i:size]
            if _re_not_yomi.search(y):
                break;
            if y in self.__dict:
                self.__yomi = y
                self.__cand = self.__dict[y]
                self.__no = 0
        return self.current()

    def confirm(self):
        if not self.__yomi or self.__no == 0:
            return
        # Update the order of the candidates.
        last = self.__cand[self.__no]
        self.__cand.remove(last)
        self.__cand.insert(0, last)
        self.__dict[self.__yomi] = self.__cand

    def dump(self):
        print('\'', self.__yomi, '\' ', self.__no, ' ', self.__cand, sep='', flush=True)

#
# test
#
if __name__ == '__main__':
    dic = Dictionary()
    yomi = 'かんじ'
    cand = dic.lookup(yomi)
    print(yomi, cand)
    cand = dic.next()
    print(yomi, cand)
    cand = dic.next()
    print(yomi, cand)
    dic.confirm()
    cand = dic.lookup(yomi)
    print(yomi, cand)
