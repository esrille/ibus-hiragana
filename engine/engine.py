# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2017-2020 Esrille Inc.
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

import json
import logging
import os
import re
import sys
import time

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus

from dictionary import Dictionary
from event import Event

import bits
import roomazi

keysyms = IBus

logger = logging.getLogger(__name__)

_hiragana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゎゐゑ・ーゝゞ"
_katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヮヰヱ・ーヽヾ"

_to_katakana = str.maketrans(_hiragana, _katakana)

_non_daku = 'あいうえおかきくけこさしすせそたちつてとはひふへほやゆよアイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョゔヴゝヽゞヾ'
_daku = 'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョあいゔえおかきくけこさしすせそたちつてとはひふへほやゆよアイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨうウゞヾゝヽ'

_non_handaku = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'
_handaku = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

_zenkaku = ''.join(chr(i) for i in range(0xff01, 0xff5f)) + '　￥'
_hankaku = ''.join(chr(i) for i in range(0x21, 0x7f)) + ' ¥'

_to_hankaku = str.maketrans(_zenkaku, _hankaku)
_to_zenkaku = str.maketrans(_hankaku, _zenkaku)

_re_tu = re.compile(r'[kstnhmyrwgzdbpfjv]')

_name_to_logging_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

_input_mode_names = set(['A', 'あ', 'ア', 'Ａ', 'ｱ'])

IAA = '\uFFF9'  # IAA (INTERLINEAR ANNOTATION ANCHOR)
IAS = '\uFFFA'  # IAS (INTERLINEAR ANNOTATION SEPARATOR)
IAT = '\uFFFB'  # IAT (INTERLINEAR ANNOTATION TERMINATOR)


def to_katakana(kana):
    return kana.translate(_to_katakana)


def to_hankaku(kana):
    str = ''
    for c in kana:
        c = c.translate(_to_hankaku)
        str += {
            '。': '｡', '「': '｢', '」': '｣', '、': '､', '・': '･',
            'ヲ': 'ｦ',
            'ァ': 'ｧ', 'ィ': 'ｨ', 'ゥ': 'ｩ', 'ェ': 'ｪ', 'ォ': 'ｫ',
            'ャ': 'ｬ', 'ュ': 'ｭ', 'ョ': 'ｮ',
            'ッ': 'ｯ', 'ー': 'ｰ',
            'ア': 'ｱ', 'イ': 'ｲ', 'ウ': 'ｳ', 'エ': 'ｴ', 'オ': 'ｵ',
            'カ': 'ｶ', 'キ': 'ｷ', 'ク': 'ｸ', 'ケ': 'ｹ', 'コ': 'ｺ',
            'サ': 'ｻ', 'シ': 'ｼ', 'ス': 'ｽ', 'セ': 'ｾ', 'ソ': 'ｿ',
            'タ': 'ﾀ', 'チ': 'ﾁ', 'ツ': 'ﾂ', 'テ': 'ﾃ', 'ト': 'ﾄ',
            'ナ': 'ﾅ', 'ニ': 'ﾆ', 'ヌ': 'ﾇ', 'ネ': 'ﾈ', 'ノ': 'ﾉ',
            'ハ': 'ﾊ', 'ヒ': 'ﾋ', 'フ': 'ﾌ', 'ヘ': 'ﾍ', 'ホ': 'ﾎ',
            'マ': 'ﾏ', 'ミ': 'ﾐ', 'ム': 'ﾑ', 'メ': 'ﾒ', 'モ': 'ﾓ',
            'ヤ': 'ﾔ', 'ユ': 'ﾕ', 'ヨ': 'ﾖ',
            'ラ': 'ﾗ', 'リ': 'ﾘ', 'ル': 'ﾙ', 'レ': 'ﾚ', 'ロ': 'ﾛ',
            'ワ': 'ﾜ', 'ン': 'ﾝ', '゙': 'ﾞ', '゚': 'ﾟ',
            'ガ': 'ｶﾞ', 'ギ': 'ｷﾞ', 'グ': 'ｸﾞ', 'ゲ': 'ｹﾞ', 'ゴ': 'ｺﾞ',
            'ザ': 'ｻﾞ', 'ジ': 'ｼﾞ', 'ズ': 'ｽﾞ', 'ゼ': 'ｾﾞ', 'ゾ': 'ｿﾞ',
            'ダ': 'ﾀﾞ', 'ヂ': 'ﾁﾞ', 'ヅ': 'ﾂﾞ', 'デ': 'ﾃﾞ', 'ド': 'ﾄﾞ',
            'バ': 'ﾊﾞ', 'ビ': 'ﾋﾞ', 'ブ': 'ﾌﾞ', 'ベ': 'ﾍﾞ', 'ボ': 'ﾎﾞ',
            'パ': 'ﾊﾟ', 'ピ': 'ﾋﾟ', 'プ': 'ﾌﾟ', 'ペ': 'ﾍﾟ', 'ポ': 'ﾎﾟ',
            'ヴ': 'ｳﾞ'
        }.get(c, c)
    return str


def to_zenkaku(asc):
    return asc.translate(_to_zenkaku)


class EngineReplaceWithKanji(IBus.Engine):
    __gtype_name__ = 'EngineReplaceWithKanji'

    def __init__(self):
        super(EngineReplaceWithKanji, self).__init__()
        self.__mode = 'A'     # __mode must be one of _input_mode_names
        self.__override = False

        self.__layout = roomazi.layout
        self.__to_kana = self.__handle_roomazi_layout

        self.__preedit_string = ''
        self.__previous_text = ''
        self.__ignore_surrounding_text = False

        self.__lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self.__lookup_table.set_orientation(IBus.Orientation.VERTICAL)

        self.__init_props()

        self.__config = IBus.Bus().get_config()
        self.__config.connect('value-changed', self.__config_value_changed_cb)

        self.__logging_level = self.__load_logging_level(self.__config)
        self.__dict = self.__load_dictionary(self.__config)
        self.__layout = self.__load_layout(self.__config)
        self.__delay = self.__load_delay(self.__config)
        self.__event = Event(self, self.__delay, self.__layout)

        self.set_mode(self.__load_input_mode(self.__config))
        self.__set_x4063_mode(self.__load_x4063_mode(self.__config))

        self.__shrunk = ''

        self.__committed = ''
        self.__acked = True
        self.connect('set-surrounding-text', self.set_surrounding_text_cb)

        self.connect('set-cursor-location', self.set_cursor_location_cb)

    def __init_props(self):
        self.__prop_list = IBus.PropList()
        self.__input_mode_prop = IBus.Property(
            key='InputMode',
            prop_type=IBus.PropType.NORMAL,
            symbol=IBus.Text.new_from_string(self.__mode),
            label=IBus.Text.new_from_string('Input mode (%s)' % self.__mode),
            icon=None,
            tooltip=None,
            sensitive=False,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self.__prop_list.append(self.__input_mode_prop)

    def __update_input_mode(self):
        self.__input_mode_prop.set_symbol(IBus.Text.new_from_string(self.__mode))
        self.__input_mode_prop.set_label(IBus.Text.new_from_string('Input mode (%s)' % self.__mode))
        self.update_property(self.__input_mode_prop)

    def __load_input_mode(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'mode')
        if var is None or var.get_type_string() != 's' or not var.get_string() in _input_mode_names:
            mode = 'A'
            if var:
                config.unset('engine/replace-with-kanji-python', 'mode')
        else:
            mode = var.get_string()
        logger.info("input mode: %s", mode)
        return mode

    def __load_logging_level(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'logging_level')
        if var is None or var.get_type_string() != 's' or not var.get_string() in _name_to_logging_level:
            level = 'WARNING'
            if var:
                config.unset('engine/replace-with-kanji-python', 'logging_level')
        else:
            level = var.get_string()
        logger.info("logging_level: %s", level)
        logging.getLogger().setLevel(_name_to_logging_level[level])
        return level

    def __load_dictionary(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'dictionary')
        if var is None or var.get_type_string() != 's':
            path = os.path.join(os.getenv('IBUS_REPLACE_WITH_KANJI_LOCATION'), 'restrained.dic')
            if var:
                config.unset('engine/replace-with-kanji-python', 'dictionary')
        else:
            path = var.get_string()
        return Dictionary(path)

    def __load_layout(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'layout')
        if var is None or var.get_type_string() != 's':
            path = os.path.join(os.getenv('IBUS_REPLACE_WITH_KANJI_LOCATION'), 'layouts')
            path = os.path.join(path, 'roomazi.json')
            if var:
                config.unset('engine/replace-with-kanji-python', 'layout')
        else:
            path = var.get_string()
        logger.info("layout: %s", path)
        layout = roomazi.layout     # Use 'roomazi' as default
        try:
            with open(path) as f:
                layout = json.load(f)
        except ValueError as error:
            logger.error("JSON error: %s", error)
        except OSError as error:
            logger.error("Error: %s", error)
        except:
            logger.error("Unexpected error: %s %s", sys.exc_info()[0], sys.exc_info()[1])
        self.__to_kana = self.__handle_roomazi_layout
        if 'Type' in layout:
            if layout['Type'] == 'Kana':
                self.__to_kana = self.__handle_kana_layout
        return layout

    def __load_delay(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'delay')
        if var is None or var.get_type_string() != 'i':
            delay = 0
            if var:
                config.unset('engine/replace-with-kanji-python', 'delay')
        else:
            delay = var.get_int32()
        logger.info("delay: %d", delay)
        return delay

    def __load_x4063_mode(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'nn_as_jis_x_4063')
        if var is None or var.get_type_string() != 'b':
            mode = True
            if var:
                config.unset('engine/replace-with-kanji-python', 'nn_as_jis_x_4063')
        else:
            mode = var.get_boolean()
        logger.info("nn_as_jis_x_4063 mode: {}".format(mode))
        return mode

    def __config_value_changed_cb(self, config, section, name, value):
        section = section.replace('_', '-')
        if section != 'engine/replace-with-kanji-python':
            return
        logger.debug("config_value_changed({}, {}, {})".format(section, name, value))
        if name == "logging_level":
            self.__logging_level = self.__load_logging_level(config)
        elif name == "delay":
            self.__reset()
            self.__delay = self.__load_delay(config)
            self.__event = Event(self, self.__delay, self.__layout)
        elif name == "layout":
            self.__reset()
            self.__layout = self.__load_layout(config)
            self.__event = Event(self, self.__delay, self.__layout)
        elif name == "dictionary":
            self.__reset()
            self.__dict = self.__load_dictionary(config)
        elif name == "mode":
            self.set_mode(self.__load_input_mode(self.__config))
            self.__override = True
        elif name == "nn_as_jis_x_4063":
            self.__set_x4063_mode(self.__load_x4063_mode(self.__config))

    def __handle_kana_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        c = self.__event.chr().lower()
        if preedit == '\\':
            preedit = ''
            if self.__event.is_shift():
                if 'Shift' in self.__layout:
                    yomi = self.__layout['\\Shift'][c]
                elif modifiers & bits.ShiftL_Bit:
                    yomi = self.__layout['\\ShiftL'][c]
                elif modifiers & bits.ShiftR_Bit:
                    yomi = self.__layout['\\ShiftR'][c]
            else:
                yomi = self.__layout['\\Normal'][c]
        else:
            if self.__event.is_shift():
                if 'Shift' in self.__layout:
                    yomi = self.__layout['Shift'][c]
                elif modifiers & bits.ShiftL_Bit:
                    yomi = self.__layout['ShiftL'][c]
                elif modifiers & bits.ShiftR_Bit:
                    yomi = self.__layout['ShiftR'][c]
            else:
                yomi = self.__layout['Normal'][c]
            if yomi == '\\':
                preedit += yomi
                yomi = ''
        return yomi, preedit

    def __set_x4063_mode(self, on):
        if on:
            self.character_after_n = "aiueo\'wyn"
        else:
            self.character_after_n = "aiueo\'wy"
        logger.debug("set_x4063_mode({})".format(on))

    def __handle_roomazi_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        c = self.__event.chr().lower()
        if preedit == 'n' and self.character_after_n.find(c) < 0:
            yomi = 'ん'
            preedit = preedit[1:]
        preedit += c
        if preedit in self.__layout['Roomazi']:
            yomi += self.__layout['Roomazi'][preedit]
            preedit = ''
            if yomi == '\\':
                preedit = yomi
                yomi = ''
        elif 2 <= len(preedit) and preedit[0] == preedit[1] and _re_tu.search(preedit[1]):
            yomi += 'っ'
            preedit = preedit[1:]
        return yomi, preedit

    def __get_surrounding_text(self):
        if not (self.client_capabilities & IBus.Capabilite.SURROUNDING_TEXT):
            self.__ignore_surrounding_text = True
        if self.__ignore_surrounding_text or not self.__acked:
            logger.debug("surrounding text: [%s]" % (self.__previous_text))
            return self.__previous_text, len(self.__previous_text)

        tuple = self.get_surrounding_text()
        text = tuple[0].get_text()
        pos = tuple[1]

        # Qt reports pos as if text is in UTF-16 while GTK reports pos in sane manner.
        # If you're using primarily Qt, use the following code to amend the issue
        # when a character in Unicode supplementary planes is included in text.
        #
        # Deal with surrogate pair manually. (Qt bug?)
        # for i in range(len(text)):
        #     if pos <= i:
        #         break
        #     if 0x10000 <= ord(text[i]):
        #         pos -= 1

        # Qt seems to insert self.__preedit_string to the text, while GTK doesn't.
        # We mimic GTK's behavior here.
        preedit_len = len(self.__preedit_string)
        if 0 < preedit_len and preedit_len <= pos and text[pos - preedit_len:pos] == self.__preedit_string:
            text = text[:-preedit_len]
            pos -= preedit_len
        logger.debug("surrounding text: '%s', %d, [%s]", text, pos, self.__previous_text)
        return text, pos

    def __delete_surrounding_text(self, size):
        self.__previous_text = self.__previous_text[:-size]
        if not self.__ignore_surrounding_text and self.__acked:
            self.delete_surrounding_text(-size, size)
        else:
            # Note a short delay after each BackSpace is necessary for the target application to catch up.
            for i in range(size):
                self.forward_key_event(IBus.BackSpace, 14, 0)
                time.sleep(0.02)
            self.forward_key_event(IBus.BackSpace, 14, IBus.ModifierType.RELEASE_MASK)

    def is_overridden(self):
        return self.__override

    def is_enabled(self):
        return self.get_mode() != 'A'

    def enable_ime(self):
        if not self.is_enabled():
            self.set_mode('あ')
            return True
        return False

    def disable_ime(self):
        if self.is_enabled():
            self.set_mode('A')
            return True
        return False

    def switch_zenkaku_hankaku(self):
        mode = self.get_mode()
        mode = {
            'A': 'Ａ',
            'Ａ': 'A',
            'ア': 'ｱ',
            'ｱ': 'ア',
            'あ': 'あ'
        }.get(mode, 'A')
        return self.set_mode(mode)

    def switch_katakana(self):
        mode = self.get_mode()
        mode = {
            'A': 'ｱ',
            'Ａ': 'ア',
            'ア': 'あ',
            'ｱ': 'あ',
            'あ': 'ア'
        }.get(mode, 'ア')
        return self.set_mode(mode)

    def get_mode(self):
        return self.__mode

    def set_mode(self, mode):
        self.__override = False
        if self.__mode == mode:
            return False
        logger.debug("set_mode(%s)" % (mode))
        self.__preedit_string = ''
        self.__commit()
        self.__mode = mode
        self.__update()
        self.__update_input_mode()
        return True

    def __is_roomazi_mode(self):
        return self.__to_kana == self.__handle_roomazi_layout

    def do_process_key_event(self, keyval, keycode, state):
        return self.__event.process_key_event(keyval, keycode, state)

    def handle_key_event(self, keyval, keycode, state, modifiers):
        logger.debug("handle_key_event(%s, %04x, %04x, %04x)" % (IBus.keyval_name(keyval), keycode, state, modifiers))

        if self.__event.is_dual_role():
            pass
        elif self.__event.is_modifier():
            # Ignore modifier keys
            return False
        elif state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK):
            self.__commit()
            return False

        # Handle Candidate window
        if 0 < self.__lookup_table.get_number_of_candidates():
            if keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                return self.do_page_up()
            elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                return self.do_page_down()
            elif keyval == keysyms.Up or self.__event.is_muhenkan():
                return self.do_cursor_up()
            elif keyval == keysyms.Down or self.__event.is_henkan():
                return self.do_cursor_down()
            elif keyval == keysyms.Escape:
                self.handle_escape(state)
                return True
            elif keyval == keysyms.Return:
                self.__commit()
                return True

        if self.__preedit_string:
            if keyval == keysyms.Return:
                if self.__preedit_string == 'n':
                    self.__preedit_string = 'ん'
                self.__commit_string(self.__preedit_string)
                self.__preedit_string = ''
                self.__update()
                return True
            if keyval == keysyms.Escape:
                self.__preedit_string = ''
                self.__update()
                return True

        # Handle Japanese text
        if self.__event.is_henkan():
            return self.handle_replace(keyval, state)
        if self.__event.is_shrink():
            return self.handle_shrink(keyval, state)
        self.__commit()
        yomi = ''
        if self.__event.is_katakana():
            if self.__event.is_shift():
                self.switch_katakana()
            else:
                self.handle_katakana()
            return True
        if self.__event.is_backspace():
            if 1 <= len(self.__preedit_string):
                self.__preedit_string = self.__preedit_string[:-1]
                self.__update()
                return True
            elif 0 < len(self.__previous_text):
                self.__previous_text = self.__previous_text[:-1]
            return False
        if self.__event.is_ascii():
            if self.get_mode() == 'Ａ':
                yomi = to_zenkaku(self.__event.chr())
            else:
                yomi, self.__preedit_string = self.__to_kana(self.__preedit_string, keyval, state, modifiers)
        elif keyval == keysyms.hyphen:
            yomi = '―'
        else:
            self.__previous_text = ''
            return False
        if yomi:
            if self.get_mode() == 'ア':
                yomi = to_katakana(yomi)
            elif self.get_mode() == 'ｱ':
                yomi = to_hankaku(to_katakana(yomi))
            self.__commit_string(yomi)
        self.__update()
        return True

    def lookup_dictionary(self, yomi, pos):
        if self.__preedit_string == 'n':
            yomi = yomi[:pos] + 'ん'
            pos += 1
        self.__lookup_table.clear()
        cand = self.__dict.lookup(yomi, pos)
        size = len(self.__dict.reading())
        if 0 < size:
            if self.__preedit_string == 'n':
                if self.__acked:
                    # For furiganapad, yomi has to be committed anyway.
                    # However, 'ん' will be acked by set_cursor_location_cb()
                    # only after the converted text is committed later.
                    # So we pretend that 'ん' is acked here.
                    self.__commit_string('ん')
                    self.__acked = True
                    self.__committed = ''
                else:
                    size = size - 1
            self.__preedit_string = ''
            if 1 < len(self.__dict.cand()):
                for c in self.__dict.cand():
                    self.__lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_katakana(self):
        text, pos = self.__get_surrounding_text()
        for i in reversed(range(pos)):
            if 0 <= _katakana.find(text[i]):
                continue
            found = _hiragana.find(text[i])
            if 0 <= found:
                self.__delete_surrounding_text(pos - i)
                self.__commit_string(_katakana[found] + text[i + 1:pos])
            break
        return True

    def handle_replace(self, keyval, state):
        if not self.__dict.current():
            text, pos = self.__get_surrounding_text()
            (cand, size) = self.lookup_dictionary(text, pos)
            self.__shrunk = ''
        else:
            size = len(self.__shrunk) + len(self.__dict.current())
            if not self.__event.is_shift():
                cand = self.__dict.next()
            else:
                cand = self.__dict.previous()
        if self.__dict.current():
            self.__update()
            self.__delete_surrounding_text(size)
            self.__commit_string(self.__shrunk + cand)
        return True

    def handle_shrink(self, keyval, state):
        logger.debug("handle_shrink: '%s'", self.__dict.current())
        if not self.__dict.current():
            return False
        yomi = self.__dict.reading()
        if len(yomi) <= 1:
            self.handle_escape(state)
            return True
        current_size = len(self.__shrunk) + len(self.__dict.current())
        text, pos = self.__get_surrounding_text()
        (cand, size) = self.lookup_dictionary(yomi[1:] + text[pos:], len(yomi) - 1)
        kana = yomi
        if 0 < size:
            kana = kana[:-size]
        self.__shrunk += kana
        self.__delete_surrounding_text(current_size)
        self.__commit_string(self.__shrunk + cand)
        # Update preedit *after* committing the string to append preedit.
        self.__update()
        return True

    def handle_escape(self, state):
        if not self.__dict.current():
            return
        size = len(self.__dict.current())
        yomi = self.__dict.reading()
        self.__delete_surrounding_text(size)
        self.__commit_string(yomi)
        self.__reset(False)
        self.__update()

    def __commit(self):
        if self.__dict.current():
            self.__dict.confirm(self.__shrunk)
            self.__dict.reset()
            self.__lookup_table.clear()
            visible = 0 < self.__lookup_table.get_number_of_candidates()
            self.update_lookup_table(self.__lookup_table, visible)
            self.__previous_text = ''

    def __commit_string(self, text):
        if text == '゛':
            prev, pos = self.__get_surrounding_text()
            if 0 < pos:
                found = _non_daku.find(prev[pos - 1])
                if 0 <= found:
                    self.__delete_surrounding_text(1)
                    text = _daku[found]
        elif text == '゜':
            prev, pos = self.__get_surrounding_text()
            if 0 < pos:
                found = _non_handaku.find(prev[pos - 1])
                if 0 <= found:
                    self.__delete_surrounding_text(1)
                    text = _handaku[found]
        self.__committed = text
        self.__acked = False
        self.__previous_text += text
        self.commit_text(IBus.Text.new_from_string(text))

    def __reset(self, full=True):
        self.__dict.reset()
        self.__lookup_table.clear()
        self.__update_lookup_table()
        if full:
            self.__committed = ''
            self.__acked = True
            self.__previous_text = ''
            self.__preedit_string = ''
            self.__ignore_surrounding_text = False

    def __update_candidate(self):
        index = self.__lookup_table.get_cursor_pos()
        size = len(self.__shrunk) + len(self.__dict.current())
        self.__dict.set_current(index)
        self.__delete_surrounding_text(size)
        self.__commit_string(self.__shrunk + self.__dict.current())

    def do_page_up(self):
        if self.__lookup_table.page_up():
            self.__update_lookup_table()
            self.__update_candidate()
        return True

    def do_page_down(self):
        if self.__lookup_table.page_down():
            self.__update_lookup_table()
            self.__update_candidate()
        return True

    def do_cursor_up(self):
        if self.__lookup_table.cursor_up():
            self.__update_lookup_table()
            self.__update_candidate()
        return True

    def do_cursor_down(self):
        if self.__lookup_table.cursor_down():
            self.__update_lookup_table()
            self.__update_candidate()
        return True

    def __update(self):
        preedit_len = len(self.__preedit_string)
        text = IBus.Text.new_from_string(self.__preedit_string)
        if 0 < preedit_len:
            attrs = IBus.AttrList()
            attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE, IBus.AttrUnderline.SINGLE, 0, preedit_len))
            text.set_attributes(attrs)
        # Note self.hide_preedit_text() does not seem to work as expected with Kate.
        # cf. "Qt5 IBus input context does not implement hide_preedit_text()",
        #     https://bugreports.qt.io/browse/QTBUG-48412
        self.update_preedit_text(text, preedit_len, 0 < preedit_len)
        self.__update_lookup_table()

    def __update_lookup_table(self):
        if self.is_enabled():
            visible = 0 < self.__lookup_table.get_number_of_candidates()
            self.update_lookup_table(self.__lookup_table, visible)

    def do_focus_in(self):
        logger.info("focus_in")
        self.__event.reset()
        self.register_properties(self.__prop_list)
        # Request the initial surrounding-text in addition to the "enable" handler.
        self.get_surrounding_text()

    def do_focus_out(self):
        logger.info("focus_out")
        self.__reset()
        self.__dict.save_orders()

    def do_enable(self):
        logger.info("enable")
        # Request the initial surrounding-text when enabled as documented.
        self.get_surrounding_text()

    def do_disable(self):
        logger.info("disable")
        self.__reset()
        self.__mode = 'A'
        self.__dict.save_orders()

    def do_reset(self):
        logger.info("reset")
        self.__reset()
        # Do not switch back to the Alphabet mode here; 'reset' should be
        # called when the text cursor is moved by a mouse click, etc.

    def do_property_activate(self, prop_name, state):
        logger.info("property_activate(%s, %d)" % (prop_name, state))

    def set_surrounding_text_cb(self, engine, text, cursor_pos, anchor_pos):
        text = self.get_plain_text(text.get_text()[:cursor_pos])
        if self.__committed:
            pos = text.rfind(self.__committed)
            if 0 <= pos and pos + len(self.__committed) == len(text):
                self.__acked = True
                self.__committed = ''
        logger.debug("set_surrounding_text_cb(%s, %d, %d) => %d" % (text, cursor_pos, anchor_pos, self.__acked))

    def get_plain_text(self, text):
        plain = ''
        in_ruby = False
        for c in text:
            if c == IAA:
                in_ruby = False
            elif c == IAS:
                in_ruby = True
            elif c == IAT:
                in_ruby = False
            elif not in_ruby:
                plain += c
        return plain

    def set_cursor_location_cb(self, engine, x, y, w, h):
        # On Raspbian, at least till Buster, the candidate window does not
        # always follow the cursor position. The following code is not
        # necessary on Ubuntu 18.04 or Fedora 30.
        logger.debug("set_cursor_location_cb(%d, %d, %d, %d)" % (x, y, w, h))
        self.__update_lookup_table()
