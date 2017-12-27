# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
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

_hiragana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゎゐゑ・ー"
_katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヮヰヱ・ー"

_non_daku = 'あいうえおかきくけこさしすせそたちつてとはひふへほやゆよアイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョゔヴ'
_daku = 'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョあいゔえおかきくけこさしすせそたちつてとはひふへほやゆよアイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨうウ'

_non_handaku = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'

_handaku = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

_re_tu = re.compile(r'[kstnhmyrwgzdbpfjv]')

_name_to_logging_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

_input_mode_names = set(['A', 'あ', 'ア'])


def to_katakana(kana):
    result = ''
    for c in kana:
        pos = _hiragana.find(c)
        if pos < 0:
            result += c
        else:
            result += _katakana[pos]
    return result


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

        self.__shrunk = ''

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

    def __config_value_changed_cb(self, config, section, name, value):
        section = section.replace('_', '-')
        if section != 'engine/replace-with-kanji-python':
            return
        logger.debug("config_value_changed(%s, %s, %s): %s" % (section, name, value, self.__mode))
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

    def __handle_kana_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        if self.__event.is_ascii(keyval):
            c = self.__event.chr(keyval)
            if preedit == '\\':
                preedit = ''
                if 'Shift' in self.__layout and self.__event.is_shift():
                    yomi = self.__layout['\\Shift'][c]
                elif modifiers & bits.ShiftL_Bit:
                    yomi = self.__layout['\\ShiftL'][c]
                elif modifiers & bits.ShiftR_Bit:
                    yomi = self.__layout['\\ShiftR'][c]
                else:
                    yomi = self.__layout['\\Normal'][c]
            else:
                if 'Shift' in self.__layout and self.__event.is_shift():
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
        elif keyval == keysyms.Zenkaku_Hankaku:
            if preedit == '\\':
                yomi = '￥'
                preedit = ''
            else:
                preedit += '\\'
        elif keyval == keysyms.hyphen:
            yomi = '―'
        return yomi, preedit

    def __handle_roomazi_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        if self.__event.is_ascii(keyval):
            c = self.__event.chr(keyval)
            if preedit == 'n' and "aiueon\'wy".find(c) < 0:
                yomi = 'ん'
                preedit = preedit[1:]
            preedit += c
            if preedit in self.__layout['Roomazi']:
                yomi += self.__layout['Roomazi'][preedit]
                preedit = ''
            elif 2 <= len(preedit) and preedit[0] == preedit[1] and _re_tu.search(preedit[1]):
                yomi += 'っ'
                preedit = preedit[1:]
        elif keyval == keysyms.hyphen:
            yomi = '―'
        return yomi, preedit

    def __get_surrounding_text(self):
        if not (self.client_capabilities & IBus.Capabilite.SURROUNDING_TEXT):
            self.__ignore_surrounding_text = True
        if self.__ignore_surrounding_text:
            logger.debug("surrounding text: [%s]", self.__previous_text)
            return self.__previous_text, len(self.__previous_text)
        tuple = self.get_surrounding_text()
        text = tuple[0].get_text()
        pos = tuple[1]
        # Deal with surrogate pair manually. (iBus bug?)
        for i in range(len(text)):
            if pos <= i:
                break
            if 0x10000 <= ord(text[i]):
                pos -= 1
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
        if not self.__ignore_surrounding_text:
            self.delete_surrounding_text(-size, size)
        else:
            # Note a short delay after each BackSpace is necessary for the target application to catch up.
            for i in range(size):
                self.forward_key_event(IBus.BackSpace, 14, 0)
                time.sleep(0.01)
            self.forward_key_event(IBus.BackSpace, 14, IBus.ModifierType.RELEASE_MASK)

    def is_overridden(self):
        return self.__override

    def is_enabled(self):
        return self.get_mode() != 'A'

    def enable_ime(self):
        if not self.is_enabled():
            self.set_mode('あ')

    def disable_ime(self):
        self.set_mode('A')

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

        if self.__event.is_katakana() or self.__event.is_space() or self.__event.is_suffix():
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

        if self.__preedit_string and keyval == keysyms.Escape:
            self.__preedit_string = ''
            self.__update()
            return True

        # Handle Japanese text
        if self.__event.is_katakana():
            if state & IBus.ModifierType.MOD1_MASK:
                self.set_mode('あ' if self.get_mode() == 'ア' else 'ア')
            else:
                self.handle_katakana()
            return True
        if self.__event.is_henkan():
            return self.handle_replace(keyval, state)
        if self.__event.is_shrink():
            return self.handle_shrink(keyval, state)
        self.__commit()
        if self.__event.is_backspace():
            if 1 <= len(self.__preedit_string):
                self.__preedit_string = self.__preedit_string[:-1]
                self.__update()
                return True
            elif 0 < len(self.__previous_text):
                self.__previous_text = self.__previous_text[:-1]
        elif self.__event.is_ascii(keyval) or keyval == keysyms.Zenkaku_Hankaku or keyval == keysyms.hyphen:
            yomi, self.__preedit_string = self.__to_kana(self.__preedit_string, keyval, state, modifiers)
            if yomi:
                if self.get_mode() == 'ア':
                    yomi = to_katakana(yomi)
                self.__commit_string(yomi)
                self.__update()
                return True
            self.__update()
            return True
        else:
            self.__previous_text = ''
        return False

    def lookup_dictionary(self, yomi, pos):
        # Handle dangling 'n' for 'ん' here to minimize the access to the surrounding text API,
        # which could cause an unexpected behaviour occasionally at race conditions.
        adjust = 0
        if self.__preedit_string == 'n':
            yomi = yomi[:pos] + 'ん'
            pos += 1
            adjust = 1
        self.__lookup_table.clear()
        cand = self.__dict.lookup(yomi, pos)
        size = len(self.__dict.reading())
        if 0 < size:
            self.__preedit_string = ''
            size -= adjust
            if 1 < len(self.__dict.cand()):
                for c in self.__dict.cand():
                    self.__lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_katakana(self):
        if self.__dict.current():
            return True
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
            size = len(self.__dict.current())
            if not (state & IBus.ModifierType.SHIFT_MASK):
                cand = self.__dict.next()
            else:
                cand = self.__dict.previous()
        if self.__dict.current():
            self.__update()
            self.__delete_surrounding_text(size)
            self.__commit_string(cand)
        return True

    def handle_shrink(self, keyval, state):
        logger.debug("handle_shrink: '%s'", self.__dict.current())
        if not self.__dict.current():
            return False
        yomi = self.__dict.reading()
        if yomi == 1:
            self.handle_escape(state)
            return True
        current_size = len(self.__dict.current())
        text, pos = self.__get_surrounding_text()
        (cand, size) = self.lookup_dictionary(yomi[1:] + text[pos:], len(yomi) - 1)
        kana = yomi
        if 0 < size:
            kana = kana[:-size]
            self.__shrunk += kana
        elif kana[-1] == '―':
            kana = kana[:-1]
        self.__delete_surrounding_text(current_size)
        self.__commit_string(kana + cand)
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
        self.commit_text(IBus.Text.new_from_string(text))
        self.__previous_text += text

    def __reset(self, full=True):
        self.__dict.reset()
        self.__lookup_table.clear()
        self.__update_lookup_table()
        if full:
            self.__previous_text = ''
            self.__preedit_string = ''
            self.__ignore_surrounding_text = False

    def __update_candidate(self):
        index = self.__lookup_table.get_cursor_pos()
        size = len(self.__dict.current())
        self.__dict.set_current(index)
        self.__delete_surrounding_text(size)
        self.__commit_string(self.__dict.current())

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
