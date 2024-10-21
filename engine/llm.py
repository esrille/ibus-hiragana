# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2024 Esrille Inc.
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
MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'
MAX_CANDIDATES = 10

HIRAGANA = ('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわゐゑをん'
            'ゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっゎぱぴぷぺぽ・ーゝゞ')
RE_HIRAGANA = re.compile(f'[{HIRAGANA}]+')
RE_PREFIX = re.compile(f'[{HIRAGANA}]+')
RE_SUFFIX = re.compile(f'[{HIRAGANA}]*[1iIkKgsStnbmrwW235]?$')

model = None


class LanguageModel:

    def __init__(self, device_type: str = 'cpu'):
        global torch
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer

        if device_type == 'cuda' and torch.cuda.is_available():
            LOGGER.debug(f'torch.cuda.is_available: {torch.cuda.is_available()}')
            self._device = torch.device('cuda')
        else:
            self._device = torch.device('cpu')
        self._model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME, local_files_only=True)
        self._model.to(self._device)
        self._tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
        self._yougen_tokens = {}
        self._katuyou_tokens = {}
        vocab = self._tokenizer.get_vocab()
        with open(os.path.join(package.get_datadir(), 'dic', 'yougen_token.dic'), 'r') as f:
            for line in f:
                line = line.strip('')
                if not line or line[0] == ';':
                    continue
                words = line.split(' ', 1)
                yomi = words[0]
                words = words[1].strip(' \n/').split('/')
                self._yougen_tokens[yomi] = [vocab[word] for word in words]
        with open(os.path.join(package.get_datadir(), 'dic', 'katuyou_token.dic'), 'r') as f:
            for line in f:
                line = line.strip('')
                if not line or line[0] == ';':
                    continue
                words = line.split(' ', 1)
                stem = words[0]
                words = words[1].strip(' \n/').split('/')
                self._katuyou_tokens[stem] = words

    def __del__(self):
        del self._model
        del self._tokenizer
        torch.cuda.empty_cache()

    def device_type(self) -> str:
        return self._device.type

    def get_info(self) -> str:
        if torch.cuda.is_available():
            if self.device_type() == 'cuda':
                return f'LLM/CUDA ({torch.cuda.get_device_name(self._device).replace("NVIDIA ", "")})'
        return 'LLM'

    @staticmethod
    def _match(token, word, conj) -> bool:
        if word == token:
            return True
        if word.startswith(token):
            if conj[-1] in 'sS' and (word.endswith('しい') or word.endswith('しく')):
                return False
            return True
        if token.startswith(word):
            return True
        return False

    def assist_yougen(self, prefix, yomi, stem_list) -> dict[int, float]:
        assert '―' in yomi
        LOGGER.debug(f"_assist_yougen('{prefix}', '{yomi}', {stem_list})")
        if len(stem_list) == 1:
            return {0: 1.0}

        vocab = self._tokenizer.get_vocab()

        yougen_list = []
        yomi_list = []
        shrink_list = []

        shrink_index = []

        pos = yomi.rfind('―')
        for i in range(0, pos, 1):
            if yomi[i:pos + 1] in self._yougen_tokens:
                yougen_list.append(yomi[:i] + '[UNK]')
                yomi_list.append(yomi[i:pos])
                shrink_list.append(i)
        assert yougen_list

        for stem in stem_list:
            m = RE_PREFIX.match(stem)
            if not m:
                shrink_index.append(0)
            else:
                shrink = len(m.group())
                assert shrink in shrink_list
                shrink_index.append(shrink_list.index(shrink))

        inputs = [prefix + yougen for yougen in yougen_list]

        encoded_inputs = self._tokenizer(inputs, padding=True)
        transposed = list(zip(*encoded_inputs.input_ids))
        for mask_token_index, ids in enumerate(transposed):
            if len(set(ids)) != 1:
                break
        if mask_token_index == len(transposed) - 1:
            mask_token_index = len(transposed) - 2

        ids = encoded_inputs.input_ids[0][:mask_token_index]
        ids += (self._tokenizer.mask_token_id, self._tokenizer.sep_token_id)
        truncated = ids
        offset = 0
        if self._model.config.max_position_embeddings < len(ids) + 1:
            offset = len(ids) + 1 - self._model.config.max_position_embeddings
            truncated = [self._tokenizer.cls_token_id] + ids[1 + offset:]
        encoded_input = {
            'input_ids': torch.tensor(truncated).unsqueeze(0).to(self._device)
        }
        with torch.no_grad():
            probabilities = self._model(**encoded_input).logits[0, mask_token_index - offset]
        probabilities = torch.nn.functional.softmax(probabilities, dim=0)

        prefix_p = [1.0] * len(yougen_list)
        yougen_p = [0.0] * len(stem_list)
        for i in range(len(yougen_list)):
            if encoded_inputs.input_ids[i][mask_token_index] == self._tokenizer.unk_token_id:
                for j, stem in enumerate(stem_list):
                    if shrink_index[j] == i:
                        stem = stem[shrink_list[i]:]
                        assert stem in self._katuyou_tokens
                        v = []
                        for token in self._katuyou_tokens[stem]:
                            suffix = RE_SUFFIX.search(stem)
                            assert suffix
                            word = stem[:suffix.start()] + yomi[pos + 1:]
                            if self._match(token, word, stem[suffix.start():]):
                                v.append(vocab[token])
                        if v:
                            yougen_p[j] = sum(probabilities[v].tolist())
            else:
                prefix_p[i] = probabilities[transposed[mask_token_index][i]].item()

        for i in range(mask_token_index + 1, len(transposed) - 1):
            for j, ids in enumerate(encoded_inputs.input_ids):
                if ids[i] in (self._tokenizer.sep_token_id, self._tokenizer.pad_token_id):
                    continue
                next_ids = ids[:i]
                next_ids += (self._tokenizer.mask_token_id, self._tokenizer.sep_token_id)
                truncated = next_ids
                if 0 < offset:
                    truncated = [self._tokenizer.cls_token_id] + next_ids[1 + offset:]
                encoded_input = {
                    'input_ids': torch.tensor(truncated).unsqueeze(0).to(self._device)
                }
                with torch.no_grad():
                    p = self._model(**encoded_input).logits[0, i - offset]
                p = torch.nn.functional.softmax(p, dim=0)
                if ids[i] == self._tokenizer.unk_token_id:
                    for k, stem in enumerate(stem_list):
                        if shrink_index[k] == j:
                            stem = stem[shrink_list[j]:]
                            assert stem in self._katuyou_tokens
                            v = []
                            for token in self._katuyou_tokens[stem]:
                                suffix = RE_SUFFIX.search(stem)
                                assert suffix
                                word = stem[:suffix.start()] + yomi[pos + 1:]
                                if self._match(token, word, stem[suffix.start():]):
                                    v.append(vocab[token])
                            if v:
                                yougen_p[k] = sum(probabilities[v].tolist())
                else:
                    prefix_p[j] *= p[transposed[i][j]].item()

        p_list = []
        for i in range(len(stem_list)):
            p_list.append(prefix_p[shrink_index[i]] * yougen_p[i])

        for i, p in enumerate(p_list):
            LOGGER.debug(f'{stem_list[i]} {p * 100:.8f}%')

        p_dict = {index: value for index, value in enumerate(p_list)}
        return p_dict

    def assist(self, prefix, yomi, words) -> dict[int, float]:
        LOGGER.debug(f"assist('{prefix}', '{yomi}', {words})")
        yougen_yomi = []
        yougen_list = []
        pos_yougen = -1
        if '―' not in yomi:
            # Check that yougen exists in candidates.
            for i, word in enumerate(words):
                if word[-1] != '―':
                    continue
                assert yomi + '―' == word
                pos_yougen = i
                for j in range(0, len(word) - 1, 1):
                    if word[j:] in self._yougen_tokens:
                        yougen_list.append(word[:j] + '[UNK]')
                        yougen_yomi.append(word[j:])
                break

        if MAX_CANDIDATES < len(words):
            words = words[:MAX_CANDIDATES]
        else:
            words = words[:]
        pos_cand = len(words)
        if 0 <= pos_yougen:
            if pos_yougen < pos_cand:
                words[pos_yougen] = '[UNK]'
            words.extend(yougen_list)

        inputs = []
        for word in words:
            inputs.append(prefix + word)

        encoded_inputs = self._tokenizer(inputs, padding=True)
        transposed = list(zip(*encoded_inputs.input_ids))
        for mask_token_index, ids in enumerate(transposed):
            if len(set(ids)) != 1:
                break
        if mask_token_index == len(transposed) - 1:
            mask_token_index = len(transposed) - 2

        ids = encoded_inputs.input_ids[0][:mask_token_index]
        ids += (self._tokenizer.mask_token_id, self._tokenizer.sep_token_id)
        truncated = ids
        offset = 0
        if self._model.config.max_position_embeddings < len(ids) + 1:
            offset = len(ids) + 1 - self._model.config.max_position_embeddings
            truncated = [self._tokenizer.cls_token_id] + ids[1 + offset:]
        encoded_input = {
            'input_ids': torch.tensor(truncated).unsqueeze(0).to(self._device)
        }
        token_ids = list(transposed[mask_token_index])
        with torch.no_grad():
            probabilities = self._model(**encoded_input).logits[0, mask_token_index - offset]
        probabilities = torch.nn.functional.softmax(probabilities, dim=0)

        yougen_p = []
        for i in range(pos_cand, len(words)):
            if encoded_inputs.input_ids[i][mask_token_index] == self._tokenizer.unk_token_id:
                if yougen_yomi[i - pos_cand] in self._yougen_tokens:
                    LOGGER.debug(f'assist: {yougen_yomi[i - pos_cand]} '
                                 f'{self._tokenizer.decode(self._yougen_tokens[yougen_yomi[i - pos_cand]])}')
                    p = torch.sum(probabilities[self._yougen_tokens[yougen_yomi[i - pos_cand]]])
                else:
                    p = 0.0
            else:
                p = probabilities[transposed[mask_token_index][i]].item()
            yougen_p.append(p)
        probabilities = probabilities[token_ids].tolist()
        probabilities = probabilities[:pos_cand] + yougen_p

        p_max = 0.0
        for i in range(mask_token_index + 1, len(transposed) - 1):
            calculated = set()
            for j, ids in enumerate(encoded_inputs.input_ids):
                if j in calculated:
                    continue
                if ids[i] in (self._tokenizer.sep_token_id, self._tokenizer.pad_token_id):
                    if j != pos_yougen:
                        p_max = max(p_max, probabilities[j])
                    continue
                if probabilities[j] <= p_max:
                    continue
                next_ids = ids[:i]
                next_ids += (self._tokenizer.mask_token_id, self._tokenizer.sep_token_id)
                truncated = next_ids
                if 0 < offset:
                    truncated = [self._tokenizer.cls_token_id] + next_ids[1 + offset:]
                encoded_input = {
                    'input_ids': torch.tensor(truncated).unsqueeze(0).to(self._device)
                }
                with torch.no_grad():
                    p = self._model(**encoded_input).logits[0, i - offset]
                p = torch.nn.functional.softmax(p, dim=0)

                if pos_cand <= j and ids[i] == self._tokenizer.unk_token_id:
                    if yougen_yomi[j - pos_cand] in self._yougen_tokens:
                        LOGGER.debug(f'assist: {yougen_yomi[j - pos_cand]} '
                                     f'{self._tokenizer.decode(self._yougen_tokens[yougen_yomi[j - pos_cand]])}')
                        probabilities[j] *= torch.sum(p[self._yougen_tokens[yougen_yomi[j - pos_cand]]])
                    else:
                        probabilities[j] = 0.0
                else:
                    probabilities[j] *= p[transposed[i][j]].item()
                    for k in range(j + 1, len(inputs)):
                        if ids[mask_token_index:i] == encoded_inputs.input_ids[k][mask_token_index:i]:
                            probabilities[k] *= p[transposed[i][k]].item()
                            calculated.add(k)

        for i, ids in enumerate(encoded_inputs.input_ids):
            LOGGER.debug(f'{self._tokenizer.decode(ids)} ({len(ids)}) {probabilities[i] * 100:.8f}%')

        if pos_yougen < 0:
            p_dict = {index: value for index, value in enumerate(probabilities)}
        else:
            p_dict = {index: value for index, value in enumerate(probabilities[:pos_cand])}
            p_dict[pos_yougen] = sum(probabilities[pos_cand:])
        return p_dict


def load(enable: bool, device_type: str = 'cpu'):
    global model

    if not enable:
        model = None
        return None
    if model and model.device_type() == device_type:
        return model
    model = None
    try:
        model = LanguageModel(device_type)
    except ImportError:
        LOGGER.exception('Could not import transformers')
    except OSError:
        LOGGER.exception(f'Could not load {MODEL_NAME}')
    return model


def get_info() -> str:
    if not model:
        return ''
    return model.get_info()
