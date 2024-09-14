#!/usr/bin/env python
#
# Copyright (c) 2024 Esrille Inc.
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

from transformers import AutoTokenizer

import diclib
from vocablib import KATUYOU, RE_HIRAGANA
from vocablib import build_yougen_dic, load_vocab, load_yougen

MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'

DAKUON = 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'
SEION = 'かきくけこさしすせそたちつてとはひふへほ'


# Compare okuri and yomi ignoring the Dakuten of the last character
def strdcmp(okuri, yomi):
    assert 0 < len(yomi)
    last = len(yomi) - 1
    pos = DAKUON.find(okuri[last])
    if 0 <= pos:
        okuri = okuri[:last] + SEION[pos]
        if okuri == yomi:
            return True
    return False


def opt_len(x):
    return 0 if x is None else len(x)


# -1: yomi is not valid
# 0: yomi can be valid; still missing a few letters
# 1: yomi is valid
def dictionary_match(okuri, yomi):
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
        elif strdcmp(okuri, yomi):
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
    conj_len = len(max(katuyou, key=opt_len))
    for i in range(min(len(yomi), conj_len), 0, -1):
        for k in katuyou:
            if k is None or len(k) <= i:
                continue
            if len(yomi) < len(k) and (k[:i] == yomi[:i] or strdcmp(k[:i], yomi[:i])):
                return 0
        for k in katuyou:
            if k is None or len(k) != i:
                continue
            if k == yomi[:i]:
                return 1 if i < len(yomi) else 0
            elif len(yomi) == len(k) and strdcmp(k, yomi[:i]):
                return 0

    # cf. 食べ
    if '' in katuyou:
        return 1 if 0 < len(yomi) else 0

    return -1


# (venv) $ ./katuyou_token.py > katuyou_token.dic
def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    yougen = load_yougen()
    vocab = load_vocab(tokenizer)
    yougen_dic = build_yougen_dic(yougen, vocab)

    katuyou_dic = {}
    for kanji, words in sorted(yougen.items()):
        for yomi in sorted(words):
            pos = yomi.find('―')            # yomi: のぼ―r
            assert 0 < pos
            stem = kanji + yomi[pos + 1:]   # stem: 上r

            okuri = yomi[pos + 1:]
            yomi = yomi[:pos + 1]
            gokan = stem[:-1] if stem[-1] in '1iIkKgsStnbmrwW235' else stem
            # Note vocab.txt uses '叱' instead of '𠮟'.
            if gokan[0] == '𠮟':
                gokan = '叱' + gokan[1:]

            # _match するか確認する
            tokens = []
            for token in yougen_dic[yomi]:
                yomi = token
                m = RE_HIRAGANA.match(yomi)
                if m:
                    yomi = token[len(m.group()):]
                m = RE_HIRAGANA.search(yomi)
                if m:
                    yomi = yomi[m.start():]
                else:
                    yomi = ''
                if token.startswith(gokan) and 0 <= dictionary_match(okuri, yomi):
                    tokens.append(token)
            if not tokens:
                tokens.append(kanji[0])
            katuyou_dic[stem] = sorted(tokens)

    diclib.output(katuyou_dic)


if __name__ == '__main__':
    main()
