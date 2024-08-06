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

import os
import re

from transformers import AutoTokenizer

import diclib
from toolpath import toolpath


MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'
RE_YOUGEN = re.compile(f'([{diclib.ZYOUYOU}]+)[{diclib.HIRAGANA}]+')

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


def load_yougen():
    dic = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as f:
        for row in f:
            row = row.strip().split(',')
            kanji = row[0]
            kun = set()
            for yomi in row[1:]:
                if 8 < int(yomi[-1]):
                    continue
                yomi = yomi[:-2]
                yomi = yomi.strip('（）')
                pos = yomi.find('―')
                if 0 < pos:
                    kun.add(yomi)
            if kun:
                dic[kanji] = list(kun)

    diclib.add_word(dic, '知', 'し―らs')
    diclib.add_word(dic, '聞', 'き―かs')

    # reigai.dic にある語
    diclib.add_word(dic, '演', 'えん―じ1')
    diclib.add_word(dic, '応', 'おう―じ1')
    diclib.add_word(dic, '感', 'かん―じ1')
    diclib.add_word(dic, '禁', 'きん―じ1')
    diclib.add_word(dic, '準', 'じゅん―じ1')
    diclib.add_word(dic, '乗', 'じょう―じ1')
    diclib.add_word(dic, '生', 'しょう―じ1')
    diclib.add_word(dic, '信', 'しん―じ1')
    diclib.add_word(dic, '通', 'つう―じ1')
    diclib.add_word(dic, '転', 'てん―じ1')
    diclib.add_word(dic, '投', 'とう―じ1')
    diclib.add_word(dic, '任', 'にん―じ1')
    diclib.add_word(dic, '封', 'ふう―じ1')
    diclib.add_word(dic, '報', 'ほう―じ1')
    diclib.add_word(dic, '命', 'めい―じ1')
    diclib.add_word(dic, '論', 'ろん―じ1')

    # huhyou.dic にある語
    diclib.add_word(dic, '浮', 'うわ―つk')
    diclib.add_word(dic, '支', 'つか―え1')
    diclib.add_word(dic, '退', 'の―k')
    diclib.add_word(dic, '手伝', 'てつだ―w')
    diclib.add_word(dic, '巡', 'まわ―りさん')
    diclib.add_word(dic, '母', 'かあ―さん')
    diclib.add_word(dic, '父', 'とう―さん')
    diclib.add_word(dic, '兄', 'にい―さん')
    diclib.add_word(dic, '姉', 'ねえ―さん')
    diclib.add_word(dic, '最寄', 'もよ―り')

    return dic


def load_vocab(tokenizer):
    vocab = {}
    tokens = tokenizer.get_vocab().keys()
    for token in tokens:
        m = RE_YOUGEN.match(token)
        if m:
            assert token[0] in diclib.ZYOUYOU
            assert token[0] in tokens
            diclib.add_word(vocab, m.group(1), token)
    return vocab


def match(conj, word):
    pos = conj.find('―')
    assert 0 <= pos
    if '1iIkKgsStnbmrwW235'.find(conj[-1]) < 0:
        return (conj[:pos + 1] + word[1:]).startswith(conj)
    for x in KATUYOU[conj[-1]]:
        if x is None:
            continue
        cand = conj[:-1] + x
        m = RE_YOUGEN.match(word)
        assert m
        cand = m.group(1) + cand[pos + 1:]
        if len(cand) == 1:
            continue
        if word == cand:
            return True
        if word.startswith(cand):
            if conj[-1] in 'sS' and (word.endswith('しい') or word.endswith('しく')):
                return False
            return True
        if cand.startswith(word):
            return True
    return False


def main():
    """bert-base-japanese-v3に登録されている用言を辞書形式でとりだす。"""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    yougen = load_yougen()
    vocab = load_vocab(tokenizer)

    rev = {}
    dic = {}
    for kanji, words in sorted(vocab.items()):
        if kanji not in yougen:
            continue
        for conj in yougen[kanji]:
            # ex.
            # kanji: 信
            # words: ['信じ', '信じる']
            # conj: 'しん―じ1'
            pos = conj.find('―')
            yomi = conj[:pos + 1]
            stem = kanji + conj[pos + 1:]
            if stem[-1] in '1iIkKgsStnbmrwW235':
                stem = stem[:-1]
            if stem not in words:
                diclib.add_word(dic, yomi, kanji)
            for word in sorted(words):
                if match(conj, word):
                    diclib.add_word(dic, yomi, word)
                    diclib.add_word(rev, word, yomi)

    for kanji, words in sorted(yougen.items()):
        # Note vocab.txt uses '叱' instead of '𠮟'.
        if kanji == '𠮟':
            kanji = '叱'
        for yomi in sorted(words):
            pos = yomi.find('―')
            assert 0 < pos
            yomi = yomi[:pos + 1]
            if yomi not in dic:
                diclib.add_word(dic, yomi, kanji)

    for yomi, words in dic.items():
        dic[yomi] = sorted(dic[yomi])

    if 0:
        for word, cand in sorted(rev.items()):
            if len(cand) == 1:
                continue
            for yomi in cand:
                print(f'{word} /{yomi}/')
    else:
        diclib.output(dic)

if __name__ == '__main__':
    main()
