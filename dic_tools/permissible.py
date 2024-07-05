#!/usr/bin/python3
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

import sys

import dic


def main():
    # ヘッダーを出力します。
    print(';; Hiragana IME for IBus')
    print(';; Copyright (c) 2024 Esrille Inc.')
    print(';;')
    print(';;   https://github.com/esrille/ibus-hiragana')
    print(';;')
    permissible = dic.permissible()
    permissible = dic.union(permissible, dic.load(sys.argv[1]))
    dic.output(permissible)


if __name__ == '__main__':
    main()
