# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
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
import logging
import re

logger = logging.getLogger(__name__)

_re_not_yomi = re.compile(r'[^ぁ-ゖァ-ー―]')
_re_yomi = re.compile(r'^[ぁ-ゖァ-ー―]+[、。，．]?$')

_dic_ver = "v0.4.0"

class Dictionary:

    def __init__(self, path):
        logger.info("Dictionary(%s)", path)

        self.__dict_base = {}
        self.__dict = {}

        self.__yomi = ''
        self.__no = 0
        self.__cand = []
        self.__dirty = False

        self.__orders_path = ''

        # Load Katakana dictionary first so that Katakana words come after Kanji words.
        katakana_path = os.path.join(os.getenv('IBUS_REPLACE_WITH_KANJI_LOCATION'), 'katakana.dic')
        self.__load_dict(self.__dict_base, katakana_path)

        # Load system dictionary
        self.__load_dict(self.__dict_base, path)

        # Load private dictionary
        self.__dict = self.__dict_base.copy()

        my_path = os.path.expanduser('~/.local/share/ibus-replace-with-kanji/my.dic')
        self.__load_dict(self.__dict, my_path, 'a+')

        base = os.path.basename(path)
        if base:
            self.__orders_path = os.path.expanduser('~/.local/share/ibus-replace-with-kanji')
            self.__orders_path = os.path.join(self.__orders_path, base)
            self.__load_dict(self.__dict, self.__orders_path, 'a+', version_checked=False)

    def __load_dict(self, dict, path, mode='r', version_checked = True):
        with open(path, mode) as file:
            file.seek(0, 0)   # in case opened in the 'a+' mode
            for line in file:
                line = line.strip(' \n/')
                if line[0] == ';':
                    if line == "; " + _dic_ver:
                        version_checked = True
                    continue
                if not line:
                    continue
                if not version_checked:
                    continue
                p = line.split(' ', 1)
                yomi = p[0]
                cand = p[1].strip(' \n/').split('/')
                if not yomi in dict:
                    dict[yomi] = cand
                else:
                    update = list(dict[yomi])
                    for i in reversed(cand):
                        if i in update:
                            update.remove(i)
                        update.insert(0, i)
                    dict[yomi] = update
            logger.info("Loaded %s", path)

    def __str(self, s):
        if s[-1] == '―':
            return s[:-1]
        return s

    def reset(self):
        self.__yomi = ''

    def next(self):
        if self.__no + 1 < len(self.__cand):
            self.__no += 1
        return self.__str(self.__cand[self.__no])

    def previous(self):
        if 0 < self.__no:
            self.__no -= 1
        return self.__str(self.__cand[self.__no])

    def current(self):
        if self.__yomi:
            return self.__str(self.__cand[self.__no])
        return ''

    def set_current(self, index):
        index = int(index)
        if self.__yomi and 0 <= index and index < len(self.__cand):
            self.__no = index

    def reading(self):
        return self.__yomi

    def cand(self):
        if self.__yomi:
            return self.__cand
        return []

    def __match(self, okuri, yomi):
        if okuri and 0 <= "iIkKgsStnbmrw".find(okuri[-1]):
            suffix = okuri[-1]
            okuri = okuri[:-1]
        else:
            suffix = ''
        l = min(len(okuri), len(yomi))
        if not yomi.startswith(okuri[:l]):
            return False
        okuri = okuri[l:]
        if okuri:
            return True
        yomi = yomi[l:]
        if not suffix or not yomi:
            return True
        if suffix == 'i' or suffix == 'I':
            if 2 <= len(yomi):
                if yomi.startswith("かろ"):
                    return True
                if yomi.startswith("かっ"):
                    return True
                if yomi.startswith("けれ"):
                    return True
                if yomi.startswith("かれ"):
                    return True
            if 0 <= "けういさかく".find(yomi[0]):
                return True
            if suffix == 'I':   # 連体詞「大きな」、「小さな」。
                if yomi[0] == 'な':
                    return True
            return False
        if suffix == 'k':
            return 0 <= "かきくけこい".find(yomi[0])
        if suffix == 'K':   # 「いく」のみ
            return 0 <= "かきくけこっ".find(yomi[0])
        if suffix == 'g':
            return 0 <= "がぎぐげごい".find(yomi[0])
        if suffix == 's':
            return 0 <= "さしすせそ".find(yomi[0])
        if suffix == 'S':   # サ行変格活用
            # see http://ci.nii.ac.jp/naid/40005174758, http://ci.nii.ac.jp/naid/40016557492
            return 0 <= "しすせ".find(yomi[0])
        if suffix == 't':
            return 0 <= "たちつてとっ".find(yomi[0])
        if suffix == 'n':
            return 0 <= "なにぬねのん".find(yomi[0])
        if suffix == 'b':
            return 0 <= "ばびぶべぼん".find(yomi[0])
        if suffix == 'm':
            return 0 <= "まみむめもん".find(yomi[0])
        if suffix == 'r':
            return 0 <= "らりるれろっ".find(yomi[0])
        if suffix == 'w':
            return 0 <= "わいうえおっ".find(yomi[0])
        return False

    def lookup(self, yomi, pos):
        self.reset()
        # Look for the nearest hyphen.
        suffix = yomi[:pos].rfind('―')
        if 0 <= suffix and not _re_yomi.match(yomi[suffix:pos]):
            suffix = -1
        if suffix <= 0:
            size = pos
            for i in range(size - 1, -1, -1):
                if _re_not_yomi.match(yomi[i]):
                    break
                y = yomi[i:size]
                if y in self.__dict:
                    self.__yomi = y
                    self.__cand = self.__dict[y]
                    self.__no = 0
                    self.__order = list()
            return self.current()

        # Process suffix
        size = suffix + 1
        y = yomi
        for i in range(len(yomi[size:])):
            if _re_not_yomi.match(yomi[size + i]):
                y = y[:size + i]
                break
        for i in range(size - 2, -1, -1):
            if _re_not_yomi.match(y[i]):
                break
            if y[i:size] in self.__dict:
                cand = list()
                order = list()
                n = 0
                for c in self.__dict[y[i:size]]:
                    p = self.__match(c[1:], y[size:])
                    logger.debug("lookup: %s %s => %d", c, y[size:], p)
                    c = c[0] + yomi[size:pos]
                    if p and not c in cand:
                        cand.append(c)
                        order.append(n)
                    n += 1
                if cand:
                    self.__yomi = yomi[i:pos]
                    self.__cand = cand
                    self.__no = 0
                    self.__order = order
        return self.current()

    def confirm(self):
        if not self.__yomi or self.__no == 0:
            return

        # Get a copy of the original candidate list
        yomi = self.__yomi
        no = self.__no
        if self.__order:
            yomi = yomi[:yomi.find('―') + 1]
            no = self.__order[no]
            cand = self.__dict[yomi][:]
        else:
            cand = self.__cand[:]

        # Update the order of the candidates.
        first = cand[no]
        cand.remove(first)
        cand.insert(0, first)
        self.__dict[yomi] = cand
        self.__dirty = True

    def save_orders(self):
        if not self.__dirty:
            return
        with open(self.__orders_path, 'w') as file:
            file.write("; " + _dic_ver + "\n")
            for yomi, cand in self.__dict.items():
                if not yomi in self.__dict_base or cand != self.__dict_base[yomi]:
                    file.write(yomi + " /" + '/'.join(cand) + "/\n")
        self.__dirty = False

    def dump(self):
        print('\'', self.__yomi, '\' ', self.__no, ' ', self.__cand, sep='')
