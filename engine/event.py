# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
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

import logging

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus
from gi.repository import GLib

import bits

keysyms = IBus

logger = logging.getLogger(__name__)

class Event:
    def __init__(self, engine, delay, layout):
        self.__engine = engine
        self.__delay = delay    # Delay for non-shift keys in milliseconds (mainly for Nicola layout)

        # Set to the default values
        self.__SandS = False                    # True if SandS is used
        self.__Henkan = keysyms.space           # or keysyms.Henkan
        self.__Muhenkan = keysyms.VoidSymbol    # or keysyms.Muhenkan
        self.__Katakana = keysyms.Shift_R       # or keysyms.Hiragana_Katakana, keysyms.Control_R
        self.__CapsIME = True                   # or False
        self.__Eisuu = keysyms.F14              # or keysyms.VoidSymbol
        self.__Kana = keysyms.F13               # or keysyms.VoidSymbol
        self.__Space = keysyms.F13              # Extra space key in Kana mode
        self.__Thumb = False                    # or True for using Muhenkan/Henkan
        self.__Yen = False

        if "Keyboard" in layout:
            keyboard = layout["Keyboard"]
            if keyboard == "109":
                self.__Henkan = keysyms.Henkan
                self.__Muhenkan = keysyms.Muhenkan
                self.__Katakana = keysyms.Hiragana_Katakana
                self.__Yen = True
            if keyboard == "NISSE":
                self.__CapsIME = False
                self.__Katakana = keysyms.Control_R

        if "SandS" in layout:
            self.__SandS = True

        # Current event
        self.__keyval = keysyms.VoidSymbol
        self.__keycode = 0
        self.__state = 0
        self.__modifiers = 0                 # See bits.py

    def is_space(self):
        return self.__keyval == keysyms.space

    def is_backspace(self):
        return self.__keyval == keysyms.BackSpace

    def is_ascii(self, keyval):
        # keysyms.yen is treated as '¥' for Japanese 109 keyboard.
        return keysyms.exclam <= keyval and keyval <= keysyms.asciitilde or keyval == keysyms.yen or keyval == self.__Space

    def is_modifier(self):
        return keysyms.Shift_L <= self.__keyval and self.__keyval <= keysyms.Hyper_R

    def is_henkan(self):
        if self.__Henkan == keysyms.space:
            return self.__keyval == keysyms.space and not (self.__state & IBus.ModifierType.SHIFT_MASK)
        return self.__keyval == self.__Henkan

    def is_muhenkan(self):
        if self.__Henkan == keysyms.space:
            return self.__keyval == keysyms.space and (self.__state & IBus.ModifierType.SHIFT_MASK)
        return self.__keyval == self.__Muhenkan

    def is_shrink(self):
        return self.__keyval == keysyms.Right and (self.__state & IBus.ModifierType.SHIFT_MASK)

    def is_shift(self):
        if self.__state & IBus.ModifierType.SHIFT_MASK:
            return True
        if self.__SandS and (self.__modifiers & bits.Space_Bit):
            return True
        return False

    def is_katakana(self):
        if self.__Katakana == keysyms.Shift_R and (self.__modifiers & bits.Dual_ShiftR_Bit):
            return True
        if self.__Katakana == keysyms.Control_R and (self.__modifiers & bits.Dual_ControlR_Bit):
            return True
        return False

    def process_key_event(self, keyval, keycode, state):
        self.__modifiers &= ~(bits.Dual_Space_Bit | bits.Dual_ShiftR_Bit | bits.Dual_ControlR_Bit)
        is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
        if is_press:
            if keyval == keysyms.space:
                self.__modifiers |= bits.Space_Bit
                self.__modifiers &= ~bits.Not_Dual_Space_Bit
            elif keyval == keysyms.Shift_L:
                self.__modifiers |= bits.ShiftL_Bit
            elif keyval == keysyms.Control_L:
                self.__modifiers |= bits.ControlL_Bit
            elif keyval == keysyms.Shift_R:
                self.__modifiers |= bits.ShiftR_Bit
                self.__modifiers &= ~bits.Not_Dual_ShiftR_Bit
            elif keyval == keysyms.Control_R:
                self.__modifiers |= bits.ControlR_Bit
                self.__modifiers &= ~bits.Not_Dual_ControlR_Bit
            if (self.__modifiers & bits.Space_Bit) and keyval != keysyms.space:
                self.__modifiers |= bits.Not_Dual_Space_Bit
            if (self.__modifiers & bits.ShiftR_Bit) and keyval != keysyms.Shift_R:
                self.__modifiers |= bits.Not_Dual_ShiftR_Bit
            if (self.__modifiers & bits.ControlR_Bit) and keyval != keysyms.Control_R:
                self.__modifiers |= bits.Not_Dual_ControlR_Bit

            # Check CAPS LOCK for IME on/off
            if self.__CapsIME:
                if keyval == keysyms.Caps_Lock:
                    # Note CAPS LOCK LED is turned off after the key release event.
                    if state & IBus.ModifierType.LOCK_MASK:
                        self.__engine.disable_ime()
                    else:
                        self.__engine.enable_ime()
                else:
                    if state & IBus.ModifierType.LOCK_MASK:
                        self.__engine.enable_ime()
                    else:
                        self.__engine.disable_ime()

        else:
            if keyval == keysyms.space:
                if not (self.__modifiers & bits.Not_Dual_Space_Bit):
                    self.__modifiers |= bits.Dual_Space_Bit
                self.__modifiers &= ~bits.Space_Bit
            elif keyval == keysyms.Shift_L:
                self.__modifiers &= ~bits.ShiftL_Bit
            elif keyval == keysyms.Control_L:
                self.__modifiers &= ~bits.ControlL_Bit
            elif keyval == keysyms.Shift_R:
                if not (self.__modifiers & bits.Not_Dual_ShiftR_Bit):
                    self.__modifiers |= bits.Dual_ShiftR_Bit
                self.__modifiers &= ~bits.ShiftR_Bit
            elif keyval == keysyms.Control_R:
                if not (self.__modifiers & bits.Not_Dual_ControlR_Bit):
                    self.__modifiers |= bits.Dual_ControlR_Bit
                self.__modifiers &= ~bits.ControlR_Bit

        if self.__SandS and self.__engine.is_enabled():
            if (self.__modifiers & bits.Space_Bit) and keyval == keysyms.space:
                return True
            if self.__modifiers & bits.Dual_Space_Bit:
                is_press = True

        if self.is_katakana():
            self.__engine.set_katakana_mode(True)

        logger.debug("process_key_event(%s, %04x, %04x) %02x" % (IBus.keyval_name(keyval), keycode, state, self.__modifiers))

        # Ignore key release events
        if not is_press:
            return False

        # Take over XF86Tools (F13) and XF86Launch5 (F14) as well.
        if keyval == self.__Kana or keyval == 0x1008ff81:
            if self.__engine.enable_ime():
                return True
        elif keyval == self.__Eisuu or keyval == 0x1008ff45:
            if self.__engine.disable_ime():
                return True

        if self.__engine.is_enabled():
            if 0 < self.__delay:
                GLib.timeout_add(self.__delay, self.handle_key_event_timeout, keyval, keycode, state)
                return True
            return self.handle_key_event(keyval, keycode, state)

        # Prevent an extra action for F13 and F14 taken by other software.
        if keysyms.F13 <= keyval and keyval <= keysyms.F14:
            return True

        return False

    def handle_key_event_timeout(self, keyval, keycode, state):
        if not self.handle_key_event(keyval, keycode, state):
            self.forward_key_event(keyval, keycode, state)
        # Stop timer by returning False
        return False

    def handle_key_event(self, keyval, keycode, state):
        if keyval == keysyms.backslash and keycode == 0x7c:
            # Treat Yen key separately for Japanese 109 keyboard.
            keyval = keysyms.yen
        self.__keyval = keyval
        self.__keycode = keycode
        self.__state = state
        if not self.is_modifier():
            if self.__Katakana == keyval:
                self.__engine.set_katakana_mode(True)
                return True

        return self.__engine.handle_key_event(keyval, keycode, state, self.__modifiers)

    def chr(self, keyval):
        c = ''
        if self.is_ascii(keyval):
            if keyval == keysyms.yen:
                c = '¥'
            elif keyval == self.__Space:
                c = ' '
            else:
                c = chr(keyval).lower()
        return c

#
# test
#
if __name__ == '__main__':

    class EngineMock:
        def __init__(self):
            self.__enabled = False
            self.__katakana_mode = False    # True to input Katakana
        def enable_ime(self):
            self.__enabled = True
        def disable_ime(self):
            self.__enabled = False
        def is_enabled(self):
            return self.__enabled
        def set_katakana_mode(self, enable):
            self.__katakana_mode = enable
        def handle_key_event(self, keyval, keycode, state, modifiers):
            print("handle_key_event(%04x, %04x, %04x, %04x)" % (keyval, keycode, state, modifiers))

    engine = EngineMock();
    event = Event(engine, 0, True)
    event.process_key_event(keysyms.Shift_R, 0x0036, 0)
    event.process_key_event(keysyms.Shift_R, 0x0036, IBus.ModifierType.RELEASE_MASK | IBus.ModifierType.SHIFT_MASK)
    print(event.is_katakana(), "%04x" % event._Event__modifiers);
    event.process_key_event(keysyms.Control_R, 0x0061, 0)
    event.process_key_event(keysyms.Control_R, 0x0061, IBus.ModifierType.RELEASE_MASK | IBus.ModifierType.CONTROL_MASK)
    print(event.is_katakana(), "%04x" % event._Event__modifiers);
