#!/usr/bin/python3
#
# Copyright (c) 2017 Esrille Inc.
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

import codecs
import re
import sys

from signal import signal, SIGPIPE, SIG_DFL

import dic

if __name__ == '__main__':
    signal(SIGPIPE, SIG_DFL)
    path = 'restrained.dic'
    if 2 <= len(sys.argv):
        path = sys.argv[1]
    dict = dic.load(path)
    okuri = dic.okuri(dict)
    dic.output(okuri)
