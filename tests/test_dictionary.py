#!/usr/bin/env python
#
# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2017-2024 Esrille Inc.
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

import logging
import unittest

import gi
gi.require_version('IBus', '1.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gio

import dictionary
import llm
from dictionary import Dictionary


# To run tests, execute the following command within venv:
#  $ PYTHONPATH=/usr/share/ibus-hiragana/engine python -m unittest -v
class TestDictionary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings = Gio.Settings.new('org.freedesktop.ibus.engine.hiragana')
        path = settings.get_string('dictionary')
        user = settings.get_string('user-dictionary')
        cls.dict = Dictionary(path, user, True)
        cls.model = llm.load(True)

    def test__match(self):
        self.dict.use_romazi(False)

        result = self.dict._match('', 'る')
        self.assertEqual(result, -1)

        result = self.dict._match('k', 'く')
        self.assertEqual(result, 0)
        result = self.dict._match('k', 'くと')
        self.assertEqual(result, 1)
        result = self.dict._match('k', 'い')
        self.assertEqual(result, 0)
        result = self.dict._match('k', 'いて')
        self.assertEqual(result, 0)
        result = self.dict._match('k', 'いてと')
        self.assertEqual(result, 1)
        result = self.dict._match('k', 'いで')
        self.assertEqual(result, -1)
        result = self.dict._match('k', 'ぐ')
        self.assertEqual(result, -1)
        result = self.dict._match('k', 'けは')
        self.assertEqual(result, 0)
        result = self.dict._match('k', 'けば')
        self.assertEqual(result, 0)
        result = self.dict._match('k', 'けばと')
        self.assertEqual(result, 1)
        result = self.dict._match('k', 'す')
        self.assertEqual(result, -1)

        result = self.dict._match('g', 'く')
        self.assertEqual(result, 0)
        result = self.dict._match('g', 'いて')
        self.assertEqual(result, 0)
        result = self.dict._match('g', 'いで')
        self.assertEqual(result, 0)
        result = self.dict._match('g', 'いてい')
        self.assertEqual(result, -1)
        result = self.dict._match('g', 'ぎの')
        self.assertEqual(result, 1)

        result = self.dict._match('b', 'は')
        self.assertEqual(result, 0)

        # 食べ
        result = self.dict._match('べ1', '')
        self.assertEqual(result, 0)
        result = self.dict._match('べ1', 'へ')
        self.assertEqual(result, 0)
        result = self.dict._match('べ1', 'べ')
        self.assertEqual(result, 0)
        result = self.dict._match('べ1', 'べれ')
        self.assertEqual(result, 0)
        result = self.dict._match('べ1', 'べあ')
        self.assertEqual(result, 1)
        result = self.dict._match('べ1', 'え')
        self.assertEqual(result, -1)

        # 速さ，早さ
        result = self.dict._match('i', 'さ')
        self.assertEqual(result, 0)

        # 美しみ
        result = self.dict._match('しi', 'しみ')
        self.assertEqual(result, 0)

        result = self.dict._match('いに', 'いにね')
        self.assertEqual(result, 1)
        result = self.dict._match('いに', 'いに')
        self.assertEqual(result, 0)
        result = self.dict._match('いに', 'い')
        self.assertEqual(result, 0)
        result = self.dict._match('いに', '')
        self.assertEqual(result, 0)

        # 涙ぐましい
        result = self.dict._match('ぐましi', 'く')
        self.assertEqual(result, 0)

        # 行っは (誤変換)
        # result = self.dict._match('w', 'っは')
        # self.assertEqual(result, 0)

    def test_zyosuusi(self):
        if not self.model:
            self.skipTest('LLM not loaded')
            return
        text = '2かげつ'
        cand, suggested = self.dict.assisted_lookup(self.model, text, len(text), 0)
        self.dict.confirm('')
        self.assertEqual(cand, 'か月')

    def test_conj_max(self):
        for katuyou in dictionary.KATUYOU.values():
            result = len(max(katuyou, key=self.dict.opt_len))
            self.assertTrue(0 < result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
