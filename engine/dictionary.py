# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2017-2024 Esrille Inc.
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

from __future__ import annotations

import logging
import os
import re

import package

LOGGER = logging.getLogger(__name__)

DICTIONARY_VERSION = 'v1.0.0'

# Constants used for Hiragana - Katakana conversion
HIRAGANA = ('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわゐゑをん'
            'ゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっゎぱぴぷぺぽ・ーゝゞ')
KATAKANA = ('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヰヱヲン'
            'ヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッヮパピプペポ・ーヽヾ')
TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)
TO_HIRAGANA = str.maketrans(KATAKANA, HIRAGANA)

YOMI = re.compile(f'^#?[{HIRAGANA}]+―?$')
OKURI = re.compile(f'―[{HIRAGANA}]*')       # for match()
SUFFIX = re.compile(f'[{HIRAGANA}]*[1iIkKgsStnbmrwW235]?$')

KATUYOU = {
    '1': ('', 'る', 'れば', 'ろ', 'よう', 'て', 'た', 'な', 'た', 'ま', 'ず', None, None),
    'i': ('く', 'い', 'ければ', None, 'かろう', 'くて', 'かった', None, None, None, None, None, None, '',
          'さ', 'み', 'げ', 'そう'),
    'I': ('く', 'い', 'ければ', None, 'かろう', 'くて', 'かった', None, None, None, None, None, None, '',
          'さ', 'み', 'げ', 'そう', 'な'),   # 小さい, 大きい
    'k': ('き', 'く', 'けば', 'け', 'こう', 'いて', 'いた', 'かな', 'きた', 'きま', 'かず', 'かせ', 'かれ'),
    'K': ('き', 'く', 'けば', 'け', 'こう', 'って', 'った', 'かな', 'きた', 'きま', 'かず', 'かせ', 'かれ'),  # 行く
    'g': ('ぎ', 'ぐ', 'げば', 'げ', 'ごう', 'いで', 'いだ', 'がな', 'ぎた', 'ぎま', 'がず', 'がせ', 'がれ'),
    's': ('し', 'す', 'せば', 'せ', 'そう', 'して', 'した', 'さな', 'した', 'しま', 'さず', 'させ', 'され'),
    'S': ('し', 'する', 'すれば', 'しろ', 'しよう', 'して', 'した', 'しな', 'した', 'しま', 'せず', 'させ', 'され'),  # 欲S
    't': ('ち', 'つ', 'てば', 'て', 'とう', 'って', 'った', 'たな', 'ちた', 'ちま', 'たず', 'たせ', 'たれ'),
    'n': ('に', 'ぬ', 'ねば', 'ね', 'のう', 'んで', 'んだ', 'なな', 'にた', 'にま', 'なず', 'なせ', 'なれ'),
    'b': ('び', 'ぶ', 'べば', 'べ', 'ぼう', 'んで', 'んだ', 'ばな', 'びた', 'びま', 'ばず', 'ばせ', 'ばれ'),
    'm': ('み', 'む', 'めば', 'め', 'もう', 'んで', 'んだ', 'まな', 'みた', 'みま', 'まず', 'ませ', 'まれ'),
    'r': ('り', 'る', 'れば', 'れ', 'ろう', 'って', 'った', 'らな', 'りた', 'りま', 'らず', 'らせ', 'られ'),
    'w': ('い', 'う', 'えば', 'え', 'おう', 'って', 'った', 'わな', 'いた', 'いま', 'わず', 'わせ', 'われ'),
    'W': ('い', 'う', 'えば', 'え', 'おう', 'うて', 'うた', 'わな', 'いた', 'いま', 'わず', 'わせ', 'われ'),  # 問う, 請う, 乞う, etc.
    '2': ('', None, None, None, None, 'て', 'た', None, 'た', 'ま', None, None, None),  # きて
    '3': (None, 'る', 'れば', None, None, None, None, None, None, None, None, None, None),  # くる
    '5': (None, None, None, 'い', 'よう', None, None, 'な', None, None, 'ず', 'させ', 'られ'),  # こい
}
DAKUON = 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'
SEION = 'かきくけこさしすせそたちつてとはひふへほ'
RE_PREFIX = re.compile(f'^[{HIRAGANA}]+')


class Dictionary:

    @staticmethod
    def opt_len(x):
        return 0 if x is None else len(x)

    # Compare okuri and yomi ignoring the Dakuten of the last character
    @staticmethod
    def strdcmp(okuri, yomi):
        assert 0 < len(yomi)
        last = len(yomi) - 1
        pos = DAKUON.find(okuri[last])
        if 0 <= pos:
            okuri = okuri[:last] + SEION[pos]
            if okuri == yomi:
                return True
        return False

    @staticmethod
    def strcmp(okuri, yomi):
        return okuri == yomi

    def __init__(self, system: str, user: str,
                 clear_history: bool = False,
                 permissible: bool = False):
        LOGGER.debug(f'Dictionary("{system}", "{user}", {clear_history}, {permissible})')

        self._dict_base = {}
        self._dict = {}
        self._max_len = 0   # maximum length of a reading

        self._yomi = ''
        self._no = 0
        self._cand = []
        self._order = []
        self._completed = []
        self._numeric = ''
        self._dirty = False
        self._strdcmp = self.strcmp

        self._shrunk = ''   # shrunk word by using LLM
        self._rejected = {}  # ignored shrunk words

        self._orders_path = ''

        dir_path = os.path.join(package.get_datadir(), 'dic')

        try:
            # Load Katakana dictionary first so that Katakana words come after Kanji words.
            path = os.path.join(dir_path, 'katakana.dic')
            self._load_dict(self._dict_base, path)
        except OSError:
            LOGGER.exception('Could not load "katakana.dic"')

        if permissible and system == 'restrained.9.dic':
            try:
                path = os.path.join(dir_path, 'permissible.dic')
                self._load_dict(self._dict_base, path)
            except OSError:
                LOGGER.exception('Could not load "permissible.dic"')

        try:
            # Load system dictionary
            path = os.path.join(dir_path, system)
            self._load_dict(self._dict_base, path)
        except OSError:
            LOGGER.exception(f'Could not load "{path}"')

        # Load user dictionary
        if user:
            path = os.path.join(package.get_user_datadir(), user)
            if os.path.abspath(path) == path:
                try:
                    self._load_dict(self._dict_base, path)
                except OSError:
                    LOGGER.exception(f'Could not load "{path}"')

        # Create the working dictionary
        self._dict = self._dict_base.copy()

        # Load input history
        self._orders_path = os.path.join(package.get_user_datadir(), 'dic', system)
        try:
            if clear_history:
                LOGGER.debug('clear_history')
                with open(self._orders_path, 'w') as f:
                    f.write(f'; {DICTIONARY_VERSION}\n')
            else:
                self._load_dict(self._dict, self._orders_path, 'a+', version_checked=False)
        except OSError:
            LOGGER.exception(f'Could not load "{self._orders_path}"')

    def remove_entry(self, yomi: str, word: str):
        cand = self._dict.get(yomi)
        if cand and word in cand:
            cand.remove(word)
            if not cand:
                del self._dict[yomi]

    def _load_dict(self, dic: dict[str, list[str]], path: str, mode='r', version_checked=True):
        reorder_only = not version_checked
        try:
            with open(path, mode) as f:
                f.seek(0, 0)   # in case opened in the 'a+' mode
                for line in f:
                    line = line.strip(' \n/')
                    if not line:
                        continue
                    if line[0] == ';':
                        if line == f'; {DICTIONARY_VERSION}':
                            version_checked = True
                        continue
                    if not version_checked:
                        continue
                    words = line.split(' ', 1)
                    if len(words) < 2:
                        continue
                    yomi = words[0]
                    words = words[1].strip(' \n/').split('/')
                    if yomi.startswith('-'):
                        self._remove_entries(dic, yomi[1:], words)
                    else:
                        self._merge_entry(dic, yomi, words, reorder_only)
                        if yomi.endswith('―'):
                            self._merge_entry(dic, yomi[:-1], [yomi], reorder_only)
                LOGGER.debug(f'Loaded {path}')
        except OSError:
            LOGGER.warning(f'could not load "{path}"')

    def _merge_entry(self, dic: dict[str, list[str]], yomi: str, words: list[str], reorder_only: bool):
        if not YOMI.match(yomi):
            LOGGER.warning(f'invalid candidate: "{yomi}" / {words}')
            return
        if yomi in words or '' in words:
            LOGGER.warning(f'unexpected candidate: "{yomi}" / {words}')
        words_dict = dict.fromkeys(words)
        words_dict.pop('', None)
        words_dict.pop(yomi, None)
        words = list(words_dict)
        if not words:
            return

        katakana = ''
        if yomi[-1] != '―':
            katakana = yomi.translate(TO_KATAKANA)
            if katakana not in words:
                katakana = ''

        if yomi not in dic:
            if not reorder_only:
                dic[yomi] = words
            elif katakana:
                dic[yomi] = [katakana]
            else:
                self._dirty = True

            size = len(yomi)
            if yomi[-1] == '―':
                size -= 1
            self._max_len = max(size, self._max_len)

        else:
            update = dic[yomi][:]
            yougen = []
            for word in reversed(words):
                if word in update:
                    update.remove(word)
                    update.insert(0, word)
                elif not reorder_only or word[0] in HIRAGANA or word[0] == '#' or word == katakana:
                    if word[-1] == '―':
                        yougen.insert(0, word)
                    else:
                        update.insert(0, word)
                else:
                    self._dirty = True
            update.extend(yougen)
            dic[yomi] = update

    def _remove_entries(self, dic: dict[str, list[str]], yomi: str, cand: list[str]):
        if yomi not in dic:
            return
        update = [x for x in dic[yomi] if x not in cand]
        LOGGER.debug(f'_remove_entry: {dic[yomi]}→{update}')
        if update:
            dic[yomi] = update
        else:
            del dic[yomi]

    def add_katakana(self, word):
        LOGGER.debug(f'add_katakana("{word}")')
        yomi = word.translate(TO_HIRAGANA)
        words = self._dict.get(yomi, [])
        if word in words:
            words.remove(word)
        words.insert(0, word)
        self._dict[yomi] = words
        self._dirty = True

    def reset(self):
        if self._shrunk:
            cand = self._dict.get(self._yomi)
            if cand and self._shrunk in cand:
                cand.remove(self._shrunk)
            self._shrunk = ''
        self._yomi = ''
        self._numeric = ''

    def set_current_to_next(self):
        if self._no + 1 < len(self._cand):
            self._no += 1
        return self._cand[self._no]

    def set_current_to_previous(self):
        if 0 < self._no:
            self._no -= 1
        return self._cand[self._no]

    def current(self):
        if self._yomi:
            return self._cand[self._no]
        return ''

    def set_current(self, index):
        index = int(index)
        if self._yomi and 0 <= index < len(self._cand):
            self._no = index

    def reading(self):
        return self._yomi

    def cand(self):
        if self._yomi:
            return self._cand
        return []

    # -1: yomi is not valid
    # 0: yomi can be valid; still missing a few letters
    # 1: yomi is valid
    def _match(self, okuri, yomi):
        if okuri and 0 <= '1iIkKgsStnbmrwW235'.find(okuri[-1]):
            suffix = okuri[-1]
            okuri = okuri[:-1]
        else:
            suffix = ''
        pos = min(len(okuri), len(yomi))

        # Check the fixed part of Okurigana
        if okuri:
            if yomi[:pos] == okuri[:pos]:
                if pos == len(okuri):
                    if not suffix:
                        return 1 if len(okuri) < len(yomi) else 0
                else:
                    return 0
            elif len(okuri) < len(yomi):
                return -1
            elif self._strdcmp(okuri, yomi):
                return 0
            else:
                return -1

        if not suffix or suffix not in KATUYOU:
            return -1

        # Check conjugations
        assert pos == len(okuri)
        yomi = yomi[pos:]
        if not yomi:
            return 0
        katuyou = KATUYOU[suffix]
        conj_len = len(max(katuyou, key=self.opt_len))
        for i in range(min(len(yomi), conj_len), 0, -1):
            for k in katuyou:
                if k is None or len(k) <= i:
                    continue
                if len(yomi) < len(k) and (k[:i] == yomi[:i] or self._strdcmp(k[:i], yomi[:i])):
                    return 0
            for k in katuyou:
                if k is None or len(k) != i:
                    continue
                if k == yomi[:i]:
                    return 1 if i < len(yomi) else 0
                elif len(yomi) == len(k) and self._strdcmp(k, yomi[:i]):
                    return 0

        # cf. 食べ
        if '' in katuyou:
            return 1 if 0 < len(yomi) else 0

        return -1

    def lookup_yougen(self) -> (int, str, str):
        if not self._yomi:
            return -1, '', ''
        if '―' in self._yomi:
            return -1, '', ''
        for i, word in enumerate(self._dict[self._yomi]):
            if word[-1] == '―':
                yomi = word
                shrunk = ''
                while yomi not in self._dict:
                    LOGGER.debug(f'lookup_yougen: {yomi}')
                    shrunk += yomi[0]
                    yomi = yomi[1:]
                # Check shrunken entries that look like,
                # にし― / ['に知r']
                m = RE_PREFIX.search(self._dict[yomi][0])
                if m and yomi.startswith(m.group()):
                    LOGGER.debug(f'lookup_yougen: "{shrunk}" {yomi}')
                    shrunk += m.group()
                    yomi = yomi[m.end():]
                return i, shrunk, yomi
        return -1, '', ''

    def lookup_next_taigen(self, text, start, pos) -> bool:
        # Return False if no more lookup is necessary.
        if text[start] not in HIRAGANA:
            return False
        yomi = text[start:pos]
        if yomi in self._dict:
            self._yomi = yomi
            self._cand = self._dict[yomi]
            self._no = 0
            self._order = []
            self._completed = []
            self._numeric = ''
            LOGGER.debug(f'lookup_next_taigen: yomi: "{self._yomi}", cand: {self._cand}')
        return True

    def lookup_numeric(self, text, start, pos, numeric):
        LOGGER.debug(f'lookup_numeric("{text}", {start}, {pos}, "{numeric}")')
        assert text[start:].startswith(numeric)
        yomi = text[start:pos].replace(numeric, '#')
        if yomi in self._dict:
            if yomi[1:] == self._yomi:
                cand = self._cand[:]
            else:
                self._yomi = yomi[1:]
                cand = []
            for word in reversed(self._dict[yomi]):
                word = word[1:]
                if word in cand:
                    cand.remove(word)
                cand.insert(0, word)
            self._cand = cand
            self._no = 0
            self._order = []
            self._completed = []
            self._numeric = numeric

    def lookup_next_yougen(self, text, start, pos, suffix) -> bool:
        # Return False if no more lookup is necessary.
        LOGGER.debug(f'lookup_next_yougen("{text}", {start}, {pos}, {suffix})')
        end = suffix + 1
        if text[start] not in HIRAGANA:
            return False
        if text[start:end] in self._dict:
            cand = ([], [])
            order = ([], [])
            for n, word in enumerate(self._dict[text[start:end]]):
                pattern = SUFFIX.search(word)
                if pattern:
                    pos_okuri = pattern.start()
                else:
                    pos_okuri = len(word)
                okuri = word[pos_okuri:]
                p = self._match(okuri, text[end:])
                LOGGER.debug(f'lookup_next_yougen: {word} {text[end:]} => {p}')
                word = word[:pos_okuri] + text[end:pos]
                if 0 <= p:
                    assert p in (0, 1)
                    if word not in cand[p]:
                        cand[p].append(word)
                        order[p].append(n)
            if cand[0] or cand[1]:
                for word in cand[0]:
                    if word in cand[1]:
                        at = cand[1].index(word)
                        del cand[1][at]
                        del order[1][at]
                self._yomi = text[start:pos]
                self._cand = cand[0] + cand[1]
                self._no = 0
                self._order = order[0] + order[1]
                self._completed = [0] * len(cand[0]) + [1] * len(cand[1])
                LOGGER.debug(f'lookup_next_yougen: {self._cand}, {self._order}, {self._completed}')
                self._numeric = ''
        return True

    def lookup(self, text, pos, anchor=0):
        LOGGER.debug(f'lookup("{text}", {pos}, {anchor})')
        if anchor + self._max_len < pos:
            anchor = pos - self._max_len
        self.reset()
        suffix = text[anchor:pos].rfind('―')
        if 0 <= suffix:
            suffix += anchor
            okuri = OKURI.match(text[suffix:])
            if okuri:
                text = text[:suffix + okuri.end()]
            else:
                suffix = -1
        if suffix <= 0:
            numeric = ''
            for i in range(pos - 1, anchor - 1, -1):
                if text[i].isnumeric():
                    numeric = text[i] + numeric
                    if anchor < i and text[i - 1].isnumeric():
                        continue
                    self.lookup_numeric(text, i, pos, numeric)
                    break
                else:
                    if not self.lookup_next_taigen(text, i, pos):
                        break
        else:
            for i in range(suffix - 1, anchor - 1, -1):
                if not self.lookup_next_yougen(text, i, pos, suffix):
                    break
        return self.current()

    # Get stem list from self._cand
    def _get_stem_list(self):
        stem_list = []
        for i in range(len(self._cand)):
            yomi, stem = self.get_stem(i)
            stem_list.append(stem)
        return stem_list

    def assisted_lookup(self, model, text, pos, anchor=0):
        LOGGER.debug(f'assisted_lookup("{text}", {pos}, {anchor})')
        if anchor + self._max_len < pos:
            anchor = pos - self._max_len
        self.reset()
        suggested = 0
        word_assisted = ''
        shrunk = ''
        yomi = ''
        suffix = text[anchor:pos].rfind('―')
        if 0 <= suffix:
            suffix += anchor
            okuri = OKURI.match(text[suffix:])
            if okuri:
                text = text[:suffix + okuri.end()]
            else:
                suffix = -1
        if suffix <= 0:
            numeric = ''
            for i in range(pos - 1, anchor - 1, -1):
                if text[i].isnumeric():
                    numeric = text[i] + numeric
                    if anchor < i and text[i - 1].isnumeric():
                        continue
                    self.lookup_numeric(text, i, pos, numeric)
                    if self._numeric:
                        p_dict = model.assist(text[:pos - len(self._yomi)], self._yomi, self._cand)
                        shrunk = ''
                        suggested = max(p_dict, key=p_dict.get)
                    break
                else:
                    cont = self.lookup_next_taigen(text, i, pos)
                    if yomi != self._yomi:
                        if word_assisted:
                            word_assisted = self._yomi[:-len(yomi)] + word_assisted
                            if word_assisted not in self._cand:
                                cand = self._cand[:]
                                cand.insert(0, word_assisted)
                                self._cand = cand
                                shrunk = word_assisted
                            else:
                                shrunk = ''
                        yomi = self._yomi
                        p_dict = model.assist(text[:pos - len(self._yomi)], self._yomi, self._cand)
                        suggested = max(p_dict, key=p_dict.get)
                        word_assisted = self._cand[suggested]
                        if shrunk and (p_dict[0] < suggested or self.is_rejected(yomi, shrunk)):
                            del self._cand[0]
                            shrunk = ''
                            suggested -= 1
                        LOGGER.debug(f'assisted_lookup: {self._yomi} /{word_assisted}/ ; /{shrunk}/')
                    if not cont:
                        break
            if shrunk:
                # Temporarily register shrunk in the working dictionary
                cand = self._dict.get(yomi)
                assert cand
                assert shrunk not in cand
                cand = cand[:]
                cand.insert(0, shrunk)
                self._dict[yomi] = cand
                self._shrunk = shrunk
        else:
            cand = []
            stem = ''
            for i in range(suffix - 1, anchor - 1, -1):
                if text[i] not in HIRAGANA:
                    break
                if stem:
                    cand = self._dict.get(text[i:suffix + 1])
                    if not cand:
                        continue
                    if shrunk:
                        # Remove shrunk found in the previous lookup.
                        assert shrunk in cand
                        cand.remove(shrunk)
                    shrunk = text[i] + stem
                    if shrunk not in cand:
                        # Temporarily register shrunk in the working dictionary
                        cand = cand[:]
                        cand.insert(0, shrunk)
                        self._dict[text[i:suffix + 1]] = cand
                    else:
                        shrunk = ''
                    LOGGER.debug(f'assisted_lookup: {text[i:suffix + 1]}, {shrunk}')
                cont = self.lookup_next_yougen(text, i, pos, suffix)
                if yomi != self._yomi:
                    yomi = self._yomi
                    stem_list = self._get_stem_list()
                    p_dict = model.assist_yougen(text[:pos - len(yomi)], yomi, stem_list)
                    suggested = max(p_dict, key=p_dict.get)
                    # Look for shrunk word in _cand
                    yy, stem = self.get_stem(suggested)
                    if shrunk and (stem != shrunk or self.is_rejected(yy, shrunk)):
                        for i, word in enumerate(self._cand):
                            yy, st = self.get_stem(i)
                            if st == shrunk:
                                del self._cand[i]
                                del self._order[i]
                                del self._completed[i]
                                suggested -= 1
                                break
                        # DO NOT clear shrunk as it is still in self._dict.
                        # shrunk = ''
                if not cont:
                    break
            if 0 <= suggested:
                LOGGER.debug(f'assisted_lookup: {self._yomi} "{shrunk}-{self._cand[suggested]}"')
            self._shrunk = shrunk

        return self.current(), suggested

    def is_complete(self):
        """Return True if the current yougen conversion is completed."""
        current = self.current()
        if not current:
            return False
        if '―' in current:
            return False
        if '―' not in self._yomi:
            return False
        return False if 0 in self._completed else True

    def get_stem(self, no):
        yomi = self._yomi
        if not yomi:
            return '', ''
        if self._order:
            yomi = yomi[:yomi.find('―') + 1]
            no = self._order[no]
            return yomi, self._dict[yomi][no]
        if self._numeric:
            yomi = '#' + yomi
            cand = self._dict[yomi]
            if len(cand) <= no:
                return yomi, '#' + self._cand[no]
            return yomi, cand[no]
        return yomi, self._cand[no]

    def confirm(self, shrunk) -> int:
        if not self._yomi:
            return 0

        no_orig = self._no
        yomi = self._yomi
        no = self._no

        if self._order:
            yomi = yomi[:yomi.find('―') + 1]
            no = self._order[no]
            cand = self._dict[yomi][:]
        elif self._numeric:
            yomi = '#' + yomi
            cand = self._dict[yomi][:]
            if len(cand) <= no:
                cand.append('#' + self._cand[no])
                no = len(cand) - 1
        else:
            cand = self._cand

        # Update the order of the candidates.
        first = cand[no]
        if first == yomi:
            # Ignore pseudo candidates
            return 0
        if 0 < no:
            cand.remove(first)
            cand.insert(0, first)
            self._dict[yomi] = cand
            self._dirty = True

        if self._shrunk:
            assert self._shrunk in cand
            if first == self._shrunk:
                self._dirty = True
                self._accept(yomi, self._shrunk)
            else:
                cand.remove(self._shrunk)
                self._reject(yomi, self._shrunk)
            self._dict[yomi] = cand
            self._shrunk = ''

        # Personalize the dictionary if the candidate has been selected by shrinking the reading.
        if shrunk and not self._numeric:
            yomi = shrunk + yomi
            cand = self._dict.get(yomi)
            if cand:
                first = shrunk + first
                cand = cand[:]
                try:
                    cand.remove(first)
                except ValueError:
                    pass
                cand.insert(0, first)
                self._dict[yomi] = cand
                self._dirty = True
                no = 0
            elif yomi[-1] == '―':
                cand = self._dict.get(yomi[:-1])
                if cand:
                    first = shrunk + first
                    self._dict[yomi] = [first]
                    self._dirty = True
                    no = 0

        return no_orig

    def create_pseudo_candidate(self, text):
        LOGGER.debug(f'create_pseudo_candidate("{text}")')
        assert '―' in text
        self._yomi = text
        self._cand = [text]
        self._order = [0]
        self._completed = [0]
        self._no = 0
        self._numeric = ''

    def is_pseudo_candidate(self):
        return self._yomi and self._yomi in self._cand

    def _write_orders(self, filename):
        with open(filename, 'w') as f:
            f.write(f'; {DICTIONARY_VERSION}\n')
            for yomi, words in sorted(self._dict.items()):
                if yomi not in self._dict_base or words != self._dict_base[yomi]:
                    f.write(f'{yomi} /{"/".join(words)}/\n')

    def save_orders(self):
        if not self._dirty:
            return
        try:
            if not os.path.exists(self._orders_path):
                self._write_orders(self._orders_path)
            else:
                bakfile = self._orders_path + '.bak'
                tmpfile = self._orders_path + '.tmp'
                self._write_orders(tmpfile)
                if os.path.exists(bakfile):
                    os.remove(bakfile)
                os.rename(self._orders_path, bakfile)
                os.rename(tmpfile, self._orders_path)
        except OSError:
            LOGGER.exception(f'could not save the orders in "{self._orders_path}"')
        self._dirty = False

    def use_romazi(self, romazi):
        if romazi:
            self._strdcmp = self.strcmp
        else:
            self._strdcmp = self.strdcmp

    #
    # self._rejected methods
    #
    def is_rejected(self, yomi, word) -> bool:
        LOGGER.debug(f'is_rejected({yomi}, {word})')
        return word in self._rejected.get(yomi, set())

    def _reject(self, yomi, word) -> None:
        LOGGER.debug(f'_rejected({yomi}, {word})')
        if yomi in self._rejected:
            self._rejected[yomi].add(word)
        else:
            self._rejected[yomi] = {word}

    def _accept(self, yomi, word) -> None:
        LOGGER.debug(f'_accept({yomi}, {word})')
        if yomi in self._rejected:
            self._rejected[yomi].discard(word)
