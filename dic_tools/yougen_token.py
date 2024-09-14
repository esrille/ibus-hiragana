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
from vocablib import build_yougen_dic, load_vocab, load_yougen

MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'


# (venv) $ ./yougen_token.py > yougen_token.dic
def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    yougen = load_yougen()
    vocab = load_vocab(tokenizer)
    dic = build_yougen_dic(yougen, vocab)
    diclib.output(dic)


if __name__ == '__main__':
    main()
