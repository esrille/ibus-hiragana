# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace With Kanji input method for IBus
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
import os
import re
import time

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus
from gi.repository import GLib

from dictionary import Dictionary
from event import Event

import bits
import roomazi

keysyms = IBus

_hiragana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゎゐゑ"
_katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヮヰヱ"

_non_daku = 'あいうえおかきくけこさしすせそたちつてとはひふへほやゆよアイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョゔヴ'
_daku = 'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョあいゔえおかきくけこさしすせそたちつてとはひふへほやゆよアイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨうウ'

_non_handaku = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'

_handaku = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

_re_tu = re.compile(r'[kstnhmyrwgzdbpfjv]')

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
        self.__enabled = False          # True if IME is enabled
        self.__katakana_mode = False    # True to input Katakana

        self.__layout = roomazi.layout
        self.__to_kana = self.__handle_roomazi_layout

        self.__preedit_string = ''
        self.__previous_text = ''
        self.__ignore_surrounding_text = False

        self.__lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self.__lookup_table.set_orientation(IBus.Orientation.VERTICAL)
        self.__prop_list = IBus.PropList()

        config = IBus.Bus().get_config()
        config.connect('value-changed', self.__config_value_changed_cb)

        self.__layout = self.__load_layout(config)
        self.__delay = self.__load_delay(config)

        self.__event = Event(self, self.__delay, self.__layout)
        self.__dict = Dictionary()

    def __load_layout(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'layout')
        if var == None or var.get_type_string() != 's':
            layout_path = os.path.join(os.getenv('IBUS_REPLACE_WITH_KANJI_LOCATION'), 'layouts')
            layout_path = os.path.join(layout_path, 'roomazi.json')
            print(layout_path, flush=True)
            var = GLib.Variant.new_string(layout_path)
            config.set_value('engine/replace-with-kanji-python', 'layout', var)
        print("layout:", var.get_string(), flush=True)
        try:
            with open(var.get_string()) as f:
                layout = json.loads(f.read(), "utf-8")
        except ValueError as error:
            print("JSON error:", error)
        except:
            print("Cannot open: ", var.get_string(), flush=True)
            layout = roomazi.layout
        self.__to_kana = self.__handle_roomazi_layout
        if 'Type' in layout:
            if layout['Type'] == 'Kana':
                self.__to_kana = self.__handle_kana_layout
        print(json.dumps(layout, ensure_ascii=False), flush=True)
        return layout

    def __load_delay(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'delay')
        if var == None or var.get_type_string() != 'i':
            var = GLib.Variant.new_int32(delay)
            config.set_value('engine/replace-with-kanji-python', 'delay', var)
        delay = var.get_int32()
        print("delay:", delay, flush=True)
        return delay

    def __config_value_changed_cb(self, config, section, name, value):
        print("config value changed:", name, flush=True)
        if name == "delay":
            self.__reset()
            self.__delay = self.__load_layout(config)
            self.__event = Event(self, self.__delay, self.__layout)
        elif name == "layout":
            self.__reset()
            self.__layout = self.__load_layout(config)
            self.__event = Event(self, self.__delay, self.__layout)

    def __handle_kana_layout(self, preedit, keyval, state = 0, modifiers = 0):
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
        return yomi, preedit

    def __handle_roomazi_layout(self, preedit, keyval, state = 0, modifiers = 0):
        yomi = ''
        if self.__event.is_ascii(keyval):
            preedit += self.__event.chr(keyval)
            if preedit in self.__layout['Roomazi']:
                yomi = self.__layout['Roomazi'][preedit]
                preedit = ''
            elif 2 <= len(preedit) and preedit[0] == 'n' and preedit[1] != 'y':
                yomi = 'ん'
                preedit = preedit[1:]
            elif 2 <= len(preedit) and preedit[0] == preedit[1] and _re_tu.search(preedit[1]):
                yomi = 'っ'
                preedit = preedit[1:]
        return yomi, preedit

    def __get_surrounding_text(self):
        # Note self.get_surrounding_text() may not work as expected such as in Firefox, Chrome, etc.
        if self.__ignore_surrounding_text:
            return self.__previous_text
        tuple = self.get_surrounding_text()
        text = tuple[0].get_text()
        pos = tuple[1]
        print("surrounding text: '", text, "', ", pos, ", [", self.__previous_text, "]", sep='', flush=True)
        if self.__previous_text and pos < len(self.__previous_text) or text[pos - len(self.__previous_text):pos] != self.__previous_text:
            self.__ignore_surrounding_text = True
            return self.__previous_text
        return text[:pos]

    def __delete_surrounding_text(self, size):
        self.__previous_text = self.__previous_text[:-size]
        if not self.__ignore_surrounding_text:
            self.delete_surrounding_text(-size, size)
        else:
            for i in range(size):
                self.forward_key_event(IBus.BackSpace, 14, 0)
                time.sleep(0.01)
            self.forward_key_event(IBus.BackSpace, 14, IBus.ModifierType.RELEASE_MASK)
            time.sleep(0.02)

    def is_enabled(self):
        return self.__enabled

    def enable_ime(self):
        if not self.is_enabled():
            print("enable_ime", flush=True);
            self.__preedit_string = ''
            self.__enabled = True
            self.__dict.confirm()
            self.__dict.reset()
            self.__update()
            return True
        return False

    def disable_ime(self):
        if self.is_enabled():
            print("disable_ime", flush=True);
            self.__dict.confirm()
            self.__reset()
            self.__enabled = False
            self.__update()
            return True
        return False

    def __is_roomazi_mode(self):
        return self.__to_kana == self.__handle_roomazi_layout

    def set_katakana_mode(self, enable):
        print("set_katakana_mode:", enable, flush=True)
        self.__katakana_mode = enable

    def do_process_key_event(self, keyval, keycode, state):
        return self.__event.process_key_event(keyval, keycode, state)

    def handle_key_event(self, keyval, keycode, state, modifiers):
        print("handle_key_event(%04x, %04x, %04x, %04x)" % (keyval, keycode, state, modifiers), flush=True)

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
                print("escape", flush=True)
                self.__previous_text = self.handle_escape(state)
                return True
            elif keyval == keysyms.Return:
                self.__commit()
                return True

        if self.__preedit_string and keyval == keysyms.Escape:
            self.__preedit_string = ''
            self.__update()
            return True

        # Ignore modifier keys
        if self.__event.is_modifier():
            return False
        if (state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK)) != 0:
            self.__commit()
            return False

        # Handle Japanese text
        if self.__event.is_henkan():
            self.set_katakana_mode(False)
            return self.handle_replace(keyval, state)
        if self.__event.is_shrink():
            self.set_katakana_mode(False)
            return self.handle_shrink(keyval, state)
        self.__commit()
        if self.__event.is_backspace():
            if 1 <= len(self.__preedit_string):
                self.__preedit_string = self.__preedit_string[:-1]
                self.__update()
                return True
            elif 0 < len(self.__previous_text):
                self.__previous_text = self.__previous_text[:-1]
        elif self.__event.is_ascii(keyval) or keyval == keysyms.Zenkaku_Hankaku:
            yomi, self.__preedit_string = self.__to_kana(self.__preedit_string, keyval, state, modifiers)
            if yomi:
                if self.__katakana_mode:
                    yomi = to_katakana(yomi)
                self.__commit_string(yomi)
                self.__update()
                return True
            self.__update()
            return True
        else:
            self.__previous_text = ''
        return False

    def lookup_dictionary(self, yomi):
        # Handle dangling 'n' for 'ん' here to minimize the access to the surrounding text API,
        # which could cause an unexpected behaviour occasionally at race conditions.
        adjust = 0
        if self.__preedit_string == 'n':
            yomi += 'ん'
            adjust = 1
        elif self.__preedit_string == '\\':
            yomi += '―'
            adjust = 1
        cand = self.__dict.lookup(yomi)
        size = len(self.__dict.reading())
        if 0 < size:
            size -= adjust
        self.__lookup_table.clear()
        if cand and 1 < len(self.__dict.cand()):
            for c in self.__dict.cand():
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_replace(self, keyval, state):
        if not self.__dict.current():
            text = self.__get_surrounding_text()
            (cand, size) = self.lookup_dictionary(text)
        else:
            size = len(self.__dict.current())
            if not (state & IBus.ModifierType.SHIFT_MASK):
                cand = self.__dict.next()
            else:
                cand = self.__dict.previous()
        if self.__dict.current():
            self.__preedit_string = ''
            self.__update()
            self.__delete_surrounding_text(size)
            self.__commit_string(cand)
        return True

    def handle_shrink(self, keyval, state):
        if not self.__dict.current():
            return False
        text = self.handle_escape(state)
        if 1 < len(text):
            (cand, size) = self.lookup_dictionary(text[1:])
            # Note a nap is needed here especially for applications that do not support surrounding text.
            time.sleep(0.1)
        else:
            self.__dict.reset()
            return True
        if self.__dict.current():
            self.__delete_surrounding_text(size)
            self.__commit_string(cand)
            self.__preedit_string = ''
            self.__update()
        return True

    def handle_escape(self, state):
        if not self.__dict.current():
            return
        size = len(self.__dict.current())
        self.__delete_surrounding_text(size)
        yomi = self.__dict.reading()
        preedit = ''
        if yomi[-1] == '―':
            yomi = yomi[:-1]
            preedit = '\\'
        self.__commit_string(yomi)
        self.__reset()
        if preedit:
            self.__preedit_string = preedit
        self.__update()
        return yomi

    def __commit(self):
        if self.__dict.current():
            self.__dict.confirm()
            self.__dict.reset()
            self.__lookup_table.clear()
            visible = 0 < self.__lookup_table.get_number_of_candidates()
            self.update_lookup_table(self.__lookup_table, visible)
            self.__previous_text = ''

    def __commit_string(self, text):
        if text == '゛':
            prev = self.__get_surrounding_text()
            if 0 < len(prev):
                pos = _non_daku.find(prev[-1])
                if 0 <= pos:
                    self.__delete_surrounding_text(1)
                    text = _daku[pos]
        elif text == '゜':
            prev = self.__get_surrounding_text()
            if 0 < len(prev):
                pos = _non_handaku.find(prev[-1])
                if 0 <= pos:
                    self.__delete_surrounding_text(1)
                    text = _handaku[pos]
        self.commit_text(IBus.Text.new_from_string(text))
        self.__previous_text += text

    def __update_candidate(self):
        index = self.__lookup_table.get_cursor_pos()
        candidate = self.__lookup_table.get_candidate(index)
        size = len(self.__dict.current())
        self.__dict.set_current(index)
        self.__delete_surrounding_text(size)
        self.__commit_string(candidate.text);

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
        attrs = IBus.AttrList()
        attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE,
                IBus.AttrUnderline.SINGLE, 0, preedit_len))
        text = IBus.Text.new_from_string(self.__preedit_string)
        text.set_attributes(attrs)
        self.update_preedit_text(text, preedit_len, preedit_len > 0)
        self.__update_lookup_table()

    def __update_lookup_table(self):
        if self.is_enabled():
            visible = 0 < self.__lookup_table.get_number_of_candidates()
            self.update_lookup_table(self.__lookup_table, visible)
        else:
            self.hide_lookup_table()

    def __reset(self):
        self.__dict.reset()
        self.__preedit_string = ''
        self.__lookup_table.clear()
        self.__update_lookup_table()
        self.__previous_text = ''
        self.__ignore_surrounding_text = False

    def do_focus_in(self):
        print("focus_in", flush=True)
        self.register_properties(self.__prop_list)
        # Request the initial surrounding-text in addition to the "enable" handler.
        self.get_surrounding_text()

    def do_focus_out(self):
        print("focus_out", flush=True)
        self.__reset()
        self.__dict.save_orders()

    def do_enable(self):
        print("enable", flush=True)
        # Request the initial surrounding-text when enabled as documented.
        self.get_surrounding_text()

    def do_disable(self):
        print("disable", flush=True)
        self.__reset()
        self.__enabled = False
        self.__dict.save_orders()

    def do_reset(self):
        print("reset", flush=True)
        self.__reset()
        # 'reset' seems to be sent due to an internal error, and
        # we don't switch back to the Alphabet mode here.
        # NG: self.__enabled = False
        self.__dict.save_orders()

    def do_property_activate(self, prop_name):
        print("PropertyActivate(%s)" % prop_name, flush=True)
