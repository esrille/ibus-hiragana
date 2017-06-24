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
        self.__Prefix = False                   # True if Shift is to be prefixed
        self.__DualBits = bits.Dual_ShiftR_Bit

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
                self.__DualBits = bits.Dual_ControlR_Bit

        if "SandS" in layout:
            self.__SandS = True
            self.__DualBits |= bits.Dual_Space_Bit
        elif "Prefix" in layout:
            self.__Prefix = True
            self.__Henkan = keysyms.apostrophe
            self.__Space = keysyms.Alt_R
            self.__DualBits |= bits.Dual_Space_Bit | bits.Dual_AltR_Bit

        if "Henkan" in layout:
            self.__Henkan = IBus.keyval_from_name(layout["Henkan"])

        # Current event
        self.__keyval = keysyms.VoidSymbol
        self.__keycode = 0
        self.__state = 0
        self.__modifiers = 0                 # See bits.py

    def is_space(self):
        if self.__Space == keysyms.Alt_R and (self.__modifiers & bits.Dual_AltR_Bit):
            return True
        return self.__keyval == keysyms.space

    def is_backspace(self):
        return self.__keyval == keysyms.BackSpace

    def is_ascii(self, keyval):
        # keysyms.yen is treated as '¥' for Japanese 109 keyboard.
        return keysyms.exclam <= keyval and keyval <= keysyms.asciitilde or keyval == keysyms.yen or keyval == self.__Space

    def is_modifier(self):
        return keysyms.Shift_L <= self.__keyval and self.__keyval <= keysyms.Hyper_R

    def is_shift(self):
        if self.__state & IBus.ModifierType.SHIFT_MASK:
            return True
        if self.__SandS and (self.__modifiers & bits.Space_Bit):
            return True
        if self.__Prefix and (self.__modifiers & (bits.Space_Bit | bits.Prefix_Bit)):
            return True
        return False

    def is_katakana(self):
        if self.__Katakana == keysyms.Shift_R and (self.__modifiers & bits.Dual_ShiftR_Bit):
            return True
        if self.__Katakana == keysyms.Control_R and (self.__modifiers & bits.Dual_ControlR_Bit):
            return True
        if not self.is_modifier() and self.__Katakana == self.__keyval:
            return True
        return False

    def is_henkan(self):
        if self.__Muhenkan == keysyms.VoidSymbol:
            return self.__keyval == self.__Henkan and not self.is_shift()
        return self.__keyval == self.__Henkan

    def is_muhenkan(self):
        if self.__Muhenkan == keysyms.VoidSymbol:
            return self.__keyval == self.__Henkan and self.is_shift()
        return self.__keyval == self.__Muhenkan

    def is_shrink(self):
        print("is_shrink", self.__keyval == keysyms.Right, self.is_shift())
        return self.__keyval == keysyms.Right and self.is_shift()

    def process_key_event(self, keyval, keycode, state):
        # Ignore XFree86 anomaly.
        if keyval == keysyms.ISO_Left_Tab:
            keyval = keysyms.Tab
        elif keyval == 0x1008ff81:
            keyval = keysyms.F13
        elif keyval == 0x1008ff45:
            keyval = keysyms.F14

        self.__modifiers &= ~bits.Dual_Bits
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
            elif keyval == keysyms.Alt_R:
                self.__modifiers |= bits.AltR_Bit
                self.__modifiers &= ~bits.Not_Dual_AltR_Bit

            if (self.__modifiers & bits.Space_Bit) and keyval != keysyms.space:
                self.__modifiers |= bits.Not_Dual_Space_Bit
            if (self.__modifiers & bits.ShiftR_Bit) and keyval != keysyms.Shift_R:
                self.__modifiers |= bits.Not_Dual_ShiftR_Bit
            if (self.__modifiers & bits.ControlR_Bit) and keyval != keysyms.Control_R:
                self.__modifiers |= bits.Not_Dual_ControlR_Bit
            if (self.__modifiers & bits.AltR_Bit) and keyval != keysyms.Alt_R:
                self.__modifiers |= bits.Not_Dual_AltR_Bit

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
            elif keyval == keysyms.Alt_R:
                if not (self.__modifiers & bits.Not_Dual_AltR_Bit):
                    self.__modifiers |= bits.Dual_AltR_Bit
                self.__modifiers &= ~bits.AltR_Bit

        if self.__engine.is_enabled():
            if self.__SandS:
                if (self.__modifiers & bits.Space_Bit) and keyval == keysyms.space:
                    return True
            elif self.__Prefix:
                if (self.__modifiers & bits.Space_Bit) and keyval == keysyms.space:
                    return True
                if self.__modifiers & bits.Dual_Space_Bit:
                    self.__modifiers ^= bits.Prefix_Bit
                    return True

        logger.debug("process_key_event(%s, %04x, %04x) %02x" % (IBus.keyval_name(keyval), keycode, state, self.__modifiers))

        # Ignore normal key release events
        if not is_press and not (self.__modifiers & self.__DualBits):
            self.__modifiers &= ~bits.Prefix_Bit
            return False

        if keyval == self.__Kana:
            if self.__engine.set_mode('あ'):
                return True
        elif keyval == self.__Eisuu:
            if self.__engine.set_mode('A'):
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
        processed = self.__engine.handle_key_event(keyval, keycode, state, self.__modifiers)
        if state & IBus.ModifierType.RELEASE_MASK:
            self.__modifiers &= ~bits.Prefix_Bit
        return processed

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
