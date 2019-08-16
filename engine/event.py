# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
#
# Copyright (c) 2017-2019 Esrille Inc.
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

        self.MODIFIERS = (keysyms.Shift_L, keysyms.Shift_R, keysyms.Control_L, keysyms.Control_R, keysyms.Alt_L, keysyms.Alt_R)

        # Set to the default values
        self.__OnOffByCaps = True               # or False
        self.__SandS = False                    # True if SandS is used
        self.__Henkan = keysyms.space           # or keysyms.Henkan
        self.__Muhenkan = keysyms.VoidSymbol    # or keysyms.Muhenkan
        self.__Eisuu = keysyms.VoidSymbol       # or keysyms.Eisu_toggle
        self.__Kana = keysyms.Control_R         # or keysyms.Hiragana_Katakana, keysyms.Control_R
        self.__Space = keysyms.Shift_R          # Extra space key in Kana mode
        self.__Prefix = False                   # True if Shift is to be prefixed
        self.__DualBits = bits.Dual_ShiftL_Bit

        if "Keyboard" in layout:
            keyboard = layout["Keyboard"]
            if keyboard == "109":
                self.__Henkan = keysyms.VoidSymbol
                self.__Muhenkan = keysyms.VoidSymbol
                self.__Kana = keysyms.Hiragana_Katakana
                self.__Eisuu = keysyms.Eisu_toggle
                self.__Space = keysyms.VoidSymbol

        if "OnOffByCaps" in layout:
            self.__OnOffByCaps = layout["OnOffByCaps"]

        if "SandS" in layout:
            self.__SandS = layout["SandS"]
            if self.__SandS:
                self.__DualBits |= bits.Dual_Space_Bit
        elif "Prefix" in layout:
            self.__Prefix = layout["Prefix"]
            if self.__Prefix:
                self.__DualBits |= bits.Dual_Space_Bit

        if "Space" in layout:
            self.__Space = IBus.keyval_from_name(layout["Space"])
        if "Henkan" in layout:
            self.__Henkan = IBus.keyval_from_name(layout["Henkan"])
        if "Muhenkan" in layout:
            self.__Muhenkan = IBus.keyval_from_name(layout["Muhenkan"])

        # Check dual role modifiers
        for k in (self.__Henkan, self.__Muhenkan, self.__Kana, self.__Space):
            if k in self.MODIFIERS:
                self.__DualBits |= bits.Dual_ShiftL_Bit << self.MODIFIERS.index(k)

        # Current event
        self.__keyval = keysyms.VoidSymbol
        self.__keycode = 0
        self.reset()

    def reset(self):
        self.__state = 0
        self.__modifiers = 0                 # See bits.py

    def is_key(self, keyval):
        if keyval == keysyms.VoidSymbol:
            return False
        if not self.is_modifier() and keyval == self.__keyval:
            return True
        if keyval == keysyms.Shift_L and (self.__modifiers & bits.Dual_ShiftL_Bit):
            return True
        if keyval == keysyms.Shift_R and (self.__modifiers & bits.Dual_ShiftR_Bit):
            return True
        if keyval == keysyms.Control_R and (self.__modifiers & bits.Dual_ControlR_Bit):
            return True
        if keyval == keysyms.Alt_R and (self.__modifiers & bits.Dual_AltR_Bit):
            return True
        return False

    def is_space(self):
        if self.is_key(self.__Space):
            return True
        return self.__keyval == keysyms.space

    def is_backspace(self):
        return self.__keyval == keysyms.BackSpace

    def is_ascii(self):
        # keysyms.yen is treated as '¥' for Japanese 109 keyboard.
        return keysyms.exclam <= self.__keyval and self.__keyval <= keysyms.asciitilde or self.__keyval == keysyms.yen or self.__keyval == keysyms.space

    def is_modifier(self):
        return self.__keyval in self.MODIFIERS

    def is_shift(self):
        mask = bits.ShiftL_Bit | bits.ShiftR_Bit
        if self.__SandS and (self.__modifiers & bits.Space_Bit):
            return True
        if self.__Prefix and (self.__modifiers & (bits.Space_Bit | bits.Prefix_Bit)):
            return True
        if self.__keyval == keysyms.Shift_R and (self.__modifiers & bits.Dual_ShiftR_Bit):
            mask &= ~bits.ShiftR_Bit
        if self.__keyval == keysyms.Shift_L and (self.__modifiers & bits.Dual_ShiftL_Bit):
            mask &= ~bits.ShiftL_Bit
        if self.__modifiers & mask:
            return True
        return False

    def is_katakana(self):
        return self.is_key(self.__Kana)

    def is_henkan(self):
        if self.is_key(self.__Henkan) or self.is_key(keysyms.Henkan):
            return not self.is_shift()
        return False

    def is_muhenkan(self):
        if self.is_key(self.__Henkan) or self.is_key(keysyms.Henkan):
            return self.is_shift()
        return self.is_key(self.__Muhenkan) or self.is_key(keysyms.Muhenkan)

    def is_shrink(self):
        return self.__keyval == keysyms.Tab

    def is_suffix(self):
        return self.__modifiers & bits.Dual_ShiftL_Bit

    def process_key_event(self, keyval, keycode, state):
        logger.debug("process_key_event(%s, %04x, %04x) %02x" % (IBus.keyval_name(keyval), keycode, state, self.__modifiers))

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
                self.__modifiers &= ~bits.Not_Dual_ShiftL_Bit
            elif keyval == keysyms.Shift_R:
                self.__modifiers |= bits.ShiftR_Bit
                self.__modifiers &= ~bits.Not_Dual_ShiftR_Bit
            elif keyval == keysyms.Control_L:
                self.__modifiers |= bits.ControlL_Bit
            elif keyval == keysyms.Control_R:
                self.__modifiers |= bits.ControlR_Bit
                self.__modifiers &= ~bits.Not_Dual_ControlR_Bit
            elif keyval == keysyms.Alt_R:
                self.__modifiers |= bits.AltR_Bit
                self.__modifiers &= ~bits.Not_Dual_AltR_Bit

            if (self.__modifiers & bits.Space_Bit) and keyval != keysyms.space:
                self.__modifiers |= bits.Not_Dual_Space_Bit
            if (self.__modifiers & bits.ShiftL_Bit) and keyval != keysyms.Shift_L:
                self.__modifiers |= bits.Not_Dual_ShiftL_Bit
            if (self.__modifiers & bits.ShiftR_Bit) and keyval != keysyms.Shift_R:
                self.__modifiers |= bits.Not_Dual_ShiftR_Bit
            if (self.__modifiers & bits.ControlR_Bit) and keyval != keysyms.Control_R:
                self.__modifiers |= bits.Not_Dual_ControlR_Bit
            if (self.__modifiers & bits.AltR_Bit) and keyval != keysyms.Alt_R:
                self.__modifiers |= bits.Not_Dual_AltR_Bit

            # Check CAPS LOCK for IME on/off
            if self.__OnOffByCaps:
                if keyval == keysyms.Caps_Lock:
                    # Note CAPS LOCK LED is turned off after the key release event.
                    if state & IBus.ModifierType.LOCK_MASK:
                        self.__engine.disable_ime()
                    else:
                        self.__engine.enable_ime()
                    return True
                elif not self.__engine.is_overridden():
                    if state & IBus.ModifierType.LOCK_MASK:
                        self.__engine.enable_ime()
                    else:
                        self.__engine.disable_ime()
            elif keyval == self.__Eisuu:
                if self.__engine.is_enabled():
                    self.__engine.disable_ime()
                else:
                    self.__engine.enable_ime()
                return True

        else:
            if keyval == keysyms.space:
                if not (self.__modifiers & bits.Not_Dual_Space_Bit):
                    self.__modifiers |= bits.Dual_Space_Bit
                self.__modifiers &= ~bits.Space_Bit
            elif keyval == keysyms.Shift_L:
                if not (self.__modifiers & bits.Not_Dual_ShiftL_Bit):
                    self.__modifiers |= bits.Dual_ShiftL_Bit
                self.__modifiers &= ~bits.ShiftL_Bit
            elif keyval == keysyms.Shift_R:
                if not (self.__modifiers & bits.Not_Dual_ShiftR_Bit):
                    self.__modifiers |= bits.Dual_ShiftR_Bit
                self.__modifiers &= ~bits.ShiftR_Bit
            elif keyval == keysyms.Control_L:
                self.__modifiers &= ~bits.ControlL_Bit
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

        # Ignore normal key release events
        if not is_press and not (self.__modifiers & self.__DualBits):
            self.__modifiers &= ~bits.Prefix_Bit
            return False

        if self.__engine.is_enabled():
            if 0 < self.__delay:
                GLib.timeout_add(self.__delay, self.handle_key_event_timeout, keyval, keycode, state)
                return True
            return self.handle_key_event(keyval, keycode, state)

        if not is_press:
            return False
        if state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK):
            return False
        self.update_key_event(keyval, keycode, state)
        c = self.chr()
        if c:
            # Commit a remapped character
            self.__engine.commit_text(IBus.Text.new_from_string(c))
            return True
        return False

    def handle_key_event_timeout(self, keyval, keycode, state):
        if not self.handle_key_event(keyval, keycode, state):
            self.__engine.forward_key_event(keyval, keycode, state)
        # Stop timer by returning False
        return False

    def update_key_event(self, keyval, keycode, state):
        if keyval == keysyms.backslash and keycode == 0x7c:
            # Treat Yen key separately for Japanese 109 keyboard.
            keyval = keysyms.yen
        elif self.is_suffix():
            keyval = keysyms.hyphen
        self.__keyval = keyval
        self.__keycode = keycode
        self.__state = state
        if self.is_space():
            self.__keyval = keysyms.space
        return self.__keyval

    def handle_key_event(self, keyval, keycode, state):
        keyval = self.update_key_event(keyval, keycode, state)
        processed = self.__engine.handle_key_event(keyval, keycode, state, self.__modifiers)
        if state & IBus.ModifierType.RELEASE_MASK:
            self.__modifiers &= ~bits.Prefix_Bit
        return processed

    def chr(self):
        c = ''
        if self.is_ascii():
            if self.__keyval == keysyms.yen:
                c = '¥'
            elif self.__keyval == keysyms.asciitilde and self.__keycode == 0x0b:
                c = '_'
            else:
                c = chr(self.__keyval)
        return c
