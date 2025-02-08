#!/usr/bin/env python
#
# Copyright (c) 2024, 2025 Esrille Inc.
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

import json

from transformers import AutoTokenizer

import diclib
from toolpath import toolpath
from vocablib import RE_SUFFIX
from vocablib import build_yougen_dic, load_vocab

MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'


def load_kango_verbs():
    dic = {}
    with open(toolpath('kango_verb.dic'), 'r') as f:
        for row in f:
            row = row.strip()
            if not row or row[0] == ';':
                continue
            row = row.split(maxsplit=2)
            yomi = row[0]
            if yomi[-1] != '―':
                continue
            words = row[1].strip(' \n/').split('/')
            for word in words:
                suffix = RE_SUFFIX.search(word)
                kanji = word[:suffix.start()]
                diclib.add_word(dic, kanji, yomi + suffix.group())
    return dic


# (venv) $ ./kango_token.py > kango_token.json
def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    kango_verbs = load_kango_verbs()
    vocab = load_vocab(tokenizer)
    kango_tokens = build_yougen_dic(kango_verbs, vocab)

    dic = {}
    for stem, tokens in kango_tokens.items():
        assert stem[-1] == '―'
        yomi = stem[:-1]
        sub = {}
        for token in tokens:
            suffix = RE_SUFFIX.search(token)
            kanji = token[:suffix.start()]
            diclib.add_word(sub, kanji, kanji)
            diclib.add_word(sub, kanji, token)
        dic[yomi] = sub
    print(json.dumps(dic, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
