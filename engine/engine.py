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

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus
from gi.repository import GLib

import time

from dictionary import Dictionary

import roomazi
import new_stickney
import tron

keysyms = IBus

_hiragana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゎゐゑ"
_katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヮヰヱ"

_non_daku = 'あいうえおかきくけこさしすせそたちつてとはひふへほやゆよアイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョゔヴ'
_daku = 'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョあいゔえおかきくけこさしすせそたちつてとはひふへほやゆよアイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨうウ'

_non_handaku = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'

_handaku = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

def to_katakana(kana, lock):
    if not lock:
        return kana
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

    # self.__modifiers bits
    ShiftL_Bit = 1 << 0
    ShiftR_Bit = 1 << 1

    def __init__(self):
        super(EngineReplaceWithKanji, self).__init__()
        self.__state = 0        # 0: Alphabet mode, 1: Kana mode
        self.__modifiers = 0

        self.__preedit_string = ''
        self.__previous_text = ''
        self.__ignore_surrounding_text = False

        self.__lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self.__lookup_table.set_orientation(IBus.Orientation.VERTICAL)
        self.__prop_list = IBus.PropList()

        self.__dict = Dictionary()

        config = IBus.Bus().get_config()
        var = config.get_value('engine/replace-with-kanji-python', 'layout')
        if not var:
            var = GLib.Variant.new_string('roomazi')
            config.set_value('engine/replace-with-kanji-python', 'layout', GLib.Variant.new_string('roomazi'))
        layout = var.get_string()
        print("layout:", layout, flush=True)
        if layout == 'new_stickney':
            self.__to_kana = new_stickney.to_kana
        elif layout == 'tron':
            self.__to_kana = tron.to_kana
        else:
            self.__to_kana = roomazi.to_kana

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

    def do_process_key_event(self, keyval, keycode, state):
        is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
        if is_press:
            if keyval == keysyms.Shift_L:
                self.__modifiers |= self.ShiftL_Bit
            elif keyval == keysyms.Shift_R:
                self.__modifiers |= self.ShiftR_Bit
        else:
            if keyval == keysyms.Shift_L:
                self.__modifiers &= ~self.ShiftL_Bit
            elif keyval == keysyms.Shift_R:
                self.__modifiers &= ~self.ShiftR_Bit
        print("process_key_event(%04x, %04x, %04x) %02x" % (keyval, keycode, state, self.__modifiers), flush=True)
        # Ignore key release events
        if not is_press:
            return False

        if self.__state == 0:
            if keyval == keysyms.Henkan_Mode or keyval == 0x1008ff81:   # Enable IME
                self.__preedit_string = ''
                self.__state = 1
                self.__dict.confirm()
                self.__dict.reset()
                self.__update()
                return True
            return False
        elif self.__state == 1:
            if keyval == keysyms.Muhenkan or keyval == 0x1008ff45:      # Disable IME
                self.__dict.confirm()
                self.__reset()
                self.__state = 0
                self.__update()
                return True
            if 0 < self.__lookup_table.get_number_of_candidates():
                if keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                    return self.do_page_up()
                elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                    return self.do_page_down()
                elif keyval == keysyms.Up or keyval == keysyms.space and (state & IBus.ModifierType.SHIFT_MASK):
                    return self.do_cursor_up()
                elif keyval == keysyms.Down or keyval == keysyms.space and not (state & IBus.ModifierType.SHIFT_MASK):
                    return self.do_cursor_down()
                elif keyval == keysyms.Escape:
                    print("escape", flush=True)
                    self.__previous_text = self.handle_escape(state)
                    return True
                elif keyval == keysyms.Return:
                    self.__commit()
                    return True
            return self.handle_roomazi(keyval, state)
        return False

    def handle_roomazi(self, keyval, state):
        if (state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK)) != 0:
            self.__commit()
            return False

        if keyval == keysyms.space:
            return self.handle_replace(keyval, state)
        if keyval == keysyms.Right and (state & IBus.ModifierType.SHIFT_MASK):
            return self.handle_replace(keyval, state)
        if keysyms.Shift_L <= keyval and keyval <= keysyms.Hyper_R:
            return False

        self.__commit()
        if keyval == keysyms.BackSpace:
            if 1 <= len(self.__preedit_string):
                self.__preedit_string = self.__preedit_string[:-1]
                self.__update()
                return True
            elif 0 < len(self.__previous_text):
                self.__previous_text = self.__previous_text[:-1]
        elif keysyms.exclam <= keyval and keyval <= keysyms.asciitilde:
            yomi, self.__preedit_string = self.__to_kana(self.__preedit_string, keyval, state, self.__modifiers)
            if yomi:
                yomi = to_katakana(yomi, state & IBus.ModifierType.LOCK_MASK)
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
        if self.__preedit_string == 'n':
            yomi += 'ん'
        cand = self.__dict.lookup(yomi)
        size = len(self.__dict.reading())
        if 0 < size and self.__preedit_string == 'n':
            size -= 1
        self.__lookup_table.clear()
        if cand and 1 < len(self.__dict.cand()):
            for c in self.__dict.cand():
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_replace(self, keyval, state):
        if not self.__dict.current():
            if keyval != keysyms.space:
                return False
            text = self.__get_surrounding_text()
            (cand, size) = self.lookup_dictionary(text)
        elif keyval == keysyms.Right:
            text = self.handle_escape(state)
            if 1 < len(text):
                (cand, size) = self.lookup_dictionary(text[1:])
                # Note a nap is needed here especially for applications that do not support surrounding text.
                time.sleep(0.1)
            else:
                self.__dict.reset()
                return True
        else:
            size = len(self.__dict.current())
            if not (state & IBus.ModifierType.SHIFT_MASK):
                cand = self.__dict.next()
            else:
                cand = self.__dict.previous()
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
        self.__commit_string(yomi)
        self.__reset()
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
        if self.__state == 1:
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
        self.__state = 0
        self.__dict.save_orders()

    def do_reset(self):
        print("reset", flush=True)
        self.__reset()
        self.__state = 0
        self.__dict.save_orders()

    def do_property_activate(self, prop_name):
        print("PropertyActivate(%s)" % prop_name, flush=True)
