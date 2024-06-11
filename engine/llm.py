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

import torch
from transformers import BertForMaskedLM, BertJapaneseTokenizer

LOGGER = logging.getLogger(__name__)
MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'

tokenizer = None
model = None


def load(enabled: bool):
    global model, tokenizer
    if not enabled:
        return
    try:
        if model is None:
            model = BertForMaskedLM.from_pretrained(MODEL_NAME, local_files_only=True)
        if tokenizer is None:
            tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
    except OSError:
        LOGGER.debug(f'Local {MODEL_NAME} is not found')
    try:
        if model is None:
            model = BertForMaskedLM.from_pretrained(MODEL_NAME)
        if tokenizer is None:
            tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
    except OSError:
        LOGGER.exception(f'Could not load {MODEL_NAME}')


def pick(prefix, candidates):
    if model is None or tokenizer is None:
        return 0
    LOGGER.debug(f'pick("{prefix}", {candidates})')
    inputs = []
    for cand in candidates:
        inputs.append(prefix + cand)
    encoded_candidates = tokenizer(inputs)
    for ids in encoded_candidates.input_ids:
        LOGGER.debug(f'  {tokenizer.decode(ids)}')
    transposed = list(zip(*encoded_candidates.input_ids))
    for mask_token_index, ids in enumerate(transposed):
        if len(set(ids)) != 1:
            break
    ids = encoded_candidates.input_ids[0][:mask_token_index]
    ids += (tokenizer.mask_token_id, tokenizer.sep_token_id)
    total_ids = len(ids)

    truncated = ids
    offset = 0
    max_tokens = model.config.max_position_embeddings
    if max_tokens < total_ids + 1:
        offset = total_ids + 1 - max_tokens
        truncated = [tokenizer.cls_token_id] + ids[1 + offset:]

    encoded_input = {
        'input_ids': torch.tensor(truncated).unsqueeze(0)
    }
    token_ids = list(transposed[mask_token_index])
    probabilities = model(**encoded_input).logits[0, mask_token_index - offset]
    probabilities = torch.nn.functional.softmax(probabilities, dim=0)[token_ids]
    probabilities = probabilities.tolist()

    for i, ids in enumerate(encoded_candidates.input_ids):
        total_ids = len(ids)
        if total_ids <= mask_token_index + 2:
            continue
        next_ids = encoded_candidates.input_ids[i][:mask_token_index + 1]
        next_ids += (tokenizer.mask_token_id, tokenizer.sep_token_id)

        truncated = next_ids
        if 0 < offset:
            truncated = [tokenizer.cls_token_id] + next_ids[1 + offset:]

        encoded_input = {
            'input_ids': torch.tensor(truncated).unsqueeze(0)
        }
        p = model(**encoded_input).logits[0, mask_token_index + 1 - offset]
        p = torch.nn.functional.softmax(p, dim=0)
        probabilities[i] *= p[transposed[mask_token_index + 1][i]].item()

    index = probabilities.index(max(probabilities))
    LOGGER.debug(f'  {probabilities}')
    LOGGER.debug(f'  -> {candidates[index]}')
    return index
