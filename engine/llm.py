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
        LOGGER.info(f'Local {MODEL_NAME} is not found')
    try:
        if model is None:
            model = BertForMaskedLM.from_pretrained(MODEL_NAME)
        if tokenizer is None:
            tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
    except OSError:
        LOGGER.exception(f'Could not load {MODEL_NAME}')


def pick(candidates):
    if model is None or tokenizer is None:
        return 0
    LOGGER.debug(f'pick({candidates})')
    encoded_candidates = tokenizer(candidates)
    transposed = list(zip(*encoded_candidates.input_ids))
    for mask_token_index, ids in enumerate(transposed):
        if len(set(ids)) != 1:
            break
    ids = encoded_candidates.input_ids[0][:mask_token_index]
    ids += (tokenizer.mask_token_id, tokenizer.sep_token_id)
    inputs = {
        'input_ids': torch.tensor(ids).unsqueeze(0)
    }
    logits = model(**inputs).logits
    token_ids = list(transposed[mask_token_index])
    topk = torch.topk(logits[0, mask_token_index][token_ids], k=len(candidates))
    LOGGER.debug(f'  {topk.values.tolist()}')
    LOGGER.debug(f'  {topk.indices.tolist()}')
    LOGGER.debug(f'  A: {candidates[topk.indices[0]]}')
    return topk.indices[0]
