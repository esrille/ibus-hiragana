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

import time

from dictionary import Dictionary

keysyms = IBus

import roomazi

class EngineReplaceWithKanji(IBus.Engine):
    __gtype_name__ = 'EngineReplaceWithKanji'

    __state = 0   # 0: Alphabet mode, 1: Kana mode

    def __init__(self):
        super(EngineReplaceWithKanji, self).__init__()
        self.__preedit_string = ''
        self.__lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self.__prop_list = IBus.PropList()

        self.__lookup_table.set_orientation(IBus.Orientation.HORIZONTAL)

        # Initialize the dictionary
        self.__dict = Dictionary()

    def do_process_key_event(self, keyval, keycode, state):
        print("process_key_event(%04x, %04x, %04x)" % (keyval, keycode, state), flush=True)

        # Ignore key release events
        is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
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
                self.reset()
                self.__state = 0
                self.__update()
                return True
            if 0 < self.__lookup_table.get_number_of_candidates():
                if keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                    return self.do_page_up()
                elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                    return self.do_page_down()
                elif keyval == keysyms.Left or keyval == keysyms.space and (state & IBus.ModifierType.SHIFT_MASK):
                    return self.do_cursor_left()
                elif (keyval == keysyms.Right or keyval == keysyms.space) and not (state & IBus.ModifierType.SHIFT_MASK):
                    return self.do_cursor_right()
                elif keyval == keysyms.Return:
                    self.__commit()
                    return True
            return self.handle_romaji(keyval, state)
        return False

    def handle_romaji(self, keyval, state):
        if (state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK)) != 0:
            self.__commit()
            return False

        if keyval == keysyms.space or keyval == keysyms.Right:
            return self.handle_replace(keyval, state)
        if keysyms.Shift_L <= keyval and keyval <= keysyms.Hyper_R:
            return False

        self.__commit()
        if keyval == keysyms.BackSpace:
            if 1 <= len(self.__preedit_string):
                self.__preedit_string = self.__preedit_string[:-1]
                self.__update()
                return True
        elif keysyms.exclam <= keyval and keyval <= keysyms.asciitilde:
            yomi, self.__preedit_string = roomazi.to_kana(self.__preedit_string, keyval, state)
            if yomi:
                self.__commit_string(yomi)
                self.__update()
                return True
            self.__update()
            return True
        return False

    def lookup_dictionary(self, yomi):
        cand = self.__dict.lookup(yomi)
        size = len(self.__dict.reading())
        self.__lookup_table.clear()
        if cand and 1 < len(self.__dict.cand()):
            for c in self.__dict.cand():
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_replace(self, keyval, state):
        if not self.__dict.current():
            print("replace", flush=True)
            if keyval != keysyms.space:
                return False
            tuple = self.get_surrounding_text()
            text = tuple[0].get_text()
            pos = tuple[1]
            print("surrounding_text: '", text, "', ", pos, sep='', flush=True)
            if pos == 0:
                return False
            (cand, size) = self.lookup_dictionary(text[0:pos])
        elif keyval == keysyms.Right:
            text = self.handle_escape(state)
            if 1 < len(text):
                (cand, size) = self.lookup_dictionary(text[1:])
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
            self.delete_surrounding_text(-size, size)
            self.__commit_string(cand)
            self.__preedit_string = ''
            self.__update()

        return True

    def handle_escape(self, state):
        if not self.__dict.current():
            return
        size = len(self.__dict.current())
        self.delete_surrounding_text(-size, size)
        yomi = self.__dict.reading()
        time.sleep(0.02)
        self.__commit_string(yomi)
        self.reset()
        self.__update()
        return yomi

    def __commit(self):
        self.__dict.confirm()
        self.__dict.reset()
        self.__lookup_table.clear()
        visible = 0 < self.__lookup_table.get_number_of_candidates()
        self.update_lookup_table(self.__lookup_table, visible)

    def __commit_string(self, text):
        self.commit_text(IBus.Text.new_from_string(text))
        self.__update()

    def __update_candidate(self):
        index = self.__lookup_table.get_cursor_pos()
        candidate = self.__lookup_table.get_candidate(index)
        size = len(self.__dict.current())
        self.__dict.set_current(index)
        self.delete_surrounding_text(-size, size)
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

    def do_cursor_left(self):
        if self.__lookup_table.cursor_up():
            self.__update_lookup_table()
            self.__update_candidate()
        return True

    def do_cursor_right(self):
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

    def reset(self):
        self.__dict.reset()
        self.__preedit_string = ''
        self.__lookup_table.clear()
        self.__update_lookup_table()

    def do_focus_in(self):
        print("focus_in", flush=True)
        self.register_properties(self.__prop_list)

    def do_focus_out(self):
        print("focus_out", flush=True)
        self.reset()

    def do_enable(self):
        print("enable", flush=True)
        # Request the initial surrounding-text when enabled as documented.
        self.get_surrounding_text()

    def do_disable(self):
        print("disable", flush=True)
        self.reset()

    def do_reset(self):
        print("reset", flush=True)
        self.reset()

    def do_property_activate(self, prop_name):
        print("PropertyActivate(%s)" % prop_name, flush=True)
