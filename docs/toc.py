#!/usr/bin/env python3
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

import sys


IAA = '\uFFF9'  # IAA (INTERLINEAR ANNOTATION ANCHOR)
IAS = '\uFFFA'  # IAS (INTERLINEAR ANNOTATION SEPARATOR)
IAT = '\uFFFB'  # IAT (INTERLINEAR ANNOTATION TERMINATOR)


def main():
    tr = str.maketrans({
        IAA: '<ruby>',
        IAS: '<rp>(</rp><rt>',
        IAT: '</rt><rp>)</rp></ruby>'
    })

    level = 0
    for path in sys.argv[1:]:
        with open(path) as file:
            url = path[:-2] + 'html'
            for line in file:
                line = line.translate(tr)
                if line.startswith('# '):
                    print('<li><details><summary>'
                          f"<a href='{url}'>{line[2:].strip()}</a></summary>")
                    continue
                if line.startswith('## '):
                    ref = url
                    left = line.rfind('{: #')
                    if 0 <= left:
                        right = line.rfind('}')
                        if 0 <= right:
                            ref += line[left + 3:right]
                            line = line[:left]
                    if level == 0:
                        print('<ul>')
                        level = 1
                    if url == ref:
                        print(f"  <li>{line[3:].strip()}")
                    else:
                        print(f"  <li><a href='{ref}'>{line[3:].strip()}</a>")
        if 0 < level:
            print('</ul>')
            level = 0
        print('</details>')


if __name__ == '__main__':
    main()
