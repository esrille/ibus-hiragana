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

import package

LOGGER = logging.getLogger(__name__)
MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'
MAX_CANDIDATES = 10

tokenizer = None
model = None
yougen_tokens = {}


def loaded() -> bool:
    if model is None or tokenizer is None:
        return False
    return True


def load(enabled: bool):
    global model, tokenizer, torch, yougen_tokens
    if not enabled:
        return
    try:
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer
    except ImportError as e:
        LOGGER.debug(f'{e}')
        return
    try:
        if model is None:
            model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME, local_files_only=True)
        if tokenizer is None:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
    except OSError:
        LOGGER.debug(f'Local {MODEL_NAME} is not found')

    if loaded() and not yougen_tokens:
        try:
            vocab = tokenizer.get_vocab()
            with open(os.path.join(package.get_datadir(), 'dic', 'yougen_token.dic'), 'r') as f:
                for line in f:
                    line = line.strip('')
                    if not line or line[0] == ';':
                        continue
                    words = line.split(' ', 1)
                    yomi = words[0]
                    words = words[1].strip(' \n/').split('/')
                    yougen_tokens[yomi] = [vocab[word] for word in words]
        except OSError:
            LOGGER.exception('Could not load "yougen_vocab.dic"')


# yougen_cand → yougen_yomi
def pick(prefix, candidates, yougen=-1, yougen_shrunk='', yougen_yomi='') -> dict[int, str]:
    if not loaded():
        return 0
    LOGGER.debug(f"pick('{prefix}', {candidates}, {yougen}, '{yougen_shrunk}', '{yougen_yomi}')")

    if MAX_CANDIDATES < len(candidates):
        candidates = candidates[:MAX_CANDIDATES]
    else:
        candidates = candidates[:]
    pos_yougen = yougen
    if 0 <= yougen:
        if yougen < MAX_CANDIDATES:
            candidates[yougen] = yougen_shrunk + '[UNK]'
        else:
            candidates.append(yougen_shrunk + '[UNK]')
            pos_yougen = MAX_CANDIDATES

    inputs = []
    for cand in candidates:
        inputs.append(prefix + cand)
    encoded_candidates = tokenizer(inputs, padding=True)
    transposed = list(zip(*encoded_candidates.input_ids))
    for mask_token_index, ids in enumerate(transposed):
        if len(set(ids)) != 1:
            break
    ids = encoded_candidates.input_ids[0][:mask_token_index]
    ids += (tokenizer.mask_token_id, tokenizer.sep_token_id)

    truncated = ids
    offset = 0
    if model.config.max_position_embeddings < len(ids) + 1:
        offset = len(ids) + 1 - model.config.max_position_embeddings
        truncated = [tokenizer.cls_token_id] + ids[1 + offset:]
    encoded_input = {
        'input_ids': torch.tensor(truncated).unsqueeze(0)
    }
    token_ids = list(transposed[mask_token_index])
    with torch.no_grad():
        probabilities = model(**encoded_input).logits[0, mask_token_index - offset]
    probabilities = torch.nn.functional.softmax(probabilities, dim=0)

    if 0 <= yougen and encoded_candidates.input_ids[pos_yougen][mask_token_index] == tokenizer.unk_token_id:
        if yougen_yomi in yougen_tokens:
            yp = sum(probabilities[yougen_tokens[yougen_yomi]].tolist())
        else:
            yp = 0.0
        probabilities = probabilities[token_ids].tolist()
        probabilities[pos_yougen] = yp
    else:
        probabilities = probabilities[token_ids].tolist()

    for i, ids in enumerate(encoded_candidates.input_ids):
        if ids[mask_token_index + 1] in (tokenizer.sep_token_id, tokenizer.pad_token_id):
            continue

        next_ids = ids[:mask_token_index + 1]
        next_ids += (tokenizer.mask_token_id, tokenizer.sep_token_id)

        truncated = next_ids
        if 0 < offset:
            truncated = [tokenizer.cls_token_id] + next_ids[1 + offset:]
        encoded_input = {
            'input_ids': torch.tensor(truncated).unsqueeze(0)
        }
        with torch.no_grad():
            p = model(**encoded_input).logits[0, mask_token_index + 1 - offset]
        p = torch.nn.functional.softmax(p, dim=0)

        if 0 <= yougen and i == pos_yougen and ids[mask_token_index + 1] == tokenizer.unk_token_id:
            if yougen_yomi in yougen_tokens:
                probabilities[i] *= sum(p[yougen_tokens[yougen_yomi]].tolist())
            else:
                probabilities[i] = 0.0
        else:
            probabilities[i] *= p[transposed[mask_token_index + 1][i]].item()

    for i, ids in enumerate(encoded_candidates.input_ids):
        LOGGER.debug(f'  {tokenizer.decode(ids)} ({len(ids)}) {probabilities[i]}')

    if pos_yougen == MAX_CANDIDATES:
        p_yougen = probabilities.pop()
        p_dict = {index: value for index, value in enumerate(probabilities)}
        p_dict[yougen] = p_yougen
    else:
        p_dict = { index: value for index, value in enumerate(probabilities) }
    return p_dict
