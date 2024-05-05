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

import gi
gi.require_version('IBus', '1.0')
from gi.repository import IBus

LOGGER = logging.getLogger(__name__)

MODIFIERS = (IBus.Shift_L, IBus.Shift_R, IBus.Control_L, IBus.Control_R, IBus.Alt_L, IBus.Alt_R)

SHIFT_L_BIT = 0x01
SHIFT_R_BIT = 0x02
CONTROL_L_BIT = 0x04
CONTROL_R_BIT = 0x08
ALT_L_BIT = 0x10
ALT_R_BIT = 0x20
SPACE_BIT = 0x40
PREFIX_BIT = 0x80
SHIFT_BITS = SHIFT_L_BIT | SHIFT_R_BIT
CONTROL_BITS = CONTROL_L_BIT | CONTROL_R_BIT
MODIFIER_BITS = SHIFT_BITS | CONTROL_L_BIT | CONTROL_R_BIT | ALT_L_BIT | ALT_R_BIT | SPACE_BIT

DUAL_SHIFT_L_BIT = SHIFT_L_BIT << 8
DUAL_SHIFT_R_BIT = SHIFT_R_BIT << 8
DUAL_CONTROL_R_BIT = CONTROL_R_BIT << 8
DUAL_ALT_R_BIT = ALT_R_BIT << 8
DUAL_SPACE_BIT = SPACE_BIT << 8
DUAL_BITS = DUAL_SPACE_BIT | DUAL_SHIFT_L_BIT | DUAL_SHIFT_R_BIT | DUAL_CONTROL_R_BIT | DUAL_ALT_R_BIT

NOT_DUAL_SHIFT_L_BIT = SHIFT_L_BIT << 16
NOT_DUAL_SHIFT_R_BIT = SHIFT_R_BIT << 16
NOT_DUAL_CONTROL_R_BIT = CONTROL_R_BIT << 16
NOT_DUAL_ALT_R_BIT = ALT_R_BIT << 16
NOT_DUAL_SPACE_BIT = SPACE_BIT << 16


class Event:

    def __init__(self, controller: 'KeyboardController', keyval, keycode, state, modifiers):
        self._controller = controller
        self.keyval = keyval
        self.keycode = keycode
        self.state = state
        self.modifiers = modifiers

    def has_altgr(self) -> bool:
        return bool(self.modifiers & ALT_R_BIT)

    def is_release(self) -> bool:
        return bool(self.state & IBus.ModifierType.RELEASE_MASK)

    def is_press(self) -> bool:
        return not self.is_release()

    def is_key(self, keyval) -> bool:
        if keyval == IBus.VoidSymbol:
            return False
        if not self.is_modifier() and keyval == self.keyval:
            return True
        if keyval == IBus.Shift_L and (self.modifiers & DUAL_SHIFT_L_BIT):
            return True
        if keyval == IBus.Shift_R and (self.modifiers & DUAL_SHIFT_R_BIT):
            return True
        if keyval == IBus.Control_R and (self.modifiers & DUAL_CONTROL_R_BIT):
            return True
        if keyval == IBus.Alt_R and (self.modifiers & DUAL_ALT_R_BIT):
            return True
        return False

    def is_space(self) -> bool:
        if self.is_key(self._controller._Space):
            return True
        if self.keyval == IBus.space:
            return not (self._controller._Prefix and self.is_release())
        return False

    def is_backspace(self) -> bool:
        return self.keyval == IBus.BackSpace

    def is_ascii(self) -> bool:
        # IBus.yen is treated as '¥' for Japanese 109 keyboard.
        return (IBus.exclam <= self.keyval <= IBus.asciitilde
                or self.keyval == IBus.yen
                or self.keyval == IBus.periodcentered
                or self.is_space())

    def is_modifier(self) -> bool:
        return bool(self.keyval in MODIFIERS)

    def is_prefix(self) -> bool:
        return (self._controller._Prefix
                and self.keyval == IBus.space
                and (self.modifiers & PREFIX_BIT)
                and self.is_release())

    def is_prefixed(self) -> bool:
        return self._controller._Prefix and (self.modifiers & PREFIX_BIT)

    def is_control(self) -> bool:
        mask = CONTROL_BITS
        if self.keyval == IBus.Control_R and (self.modifiers & DUAL_CONTROL_R_BIT):
            mask &= ~CONTROL_R_BIT
        return bool(self.modifiers & mask)

    def is_shift(self) -> bool:
        mask = SHIFT_BITS
        if self._controller._SandS and (self.modifiers & SPACE_BIT):
            return True
        if self._controller._Prefix and (self.modifiers & (SPACE_BIT | PREFIX_BIT)):
            return True
        if self.keyval == IBus.Shift_R and (self.modifiers & DUAL_SHIFT_R_BIT):
            mask &= ~SHIFT_R_BIT
        if self.keyval == IBus.Shift_L and (self.modifiers & DUAL_SHIFT_L_BIT):
            mask &= ~SHIFT_L_BIT
        return bool(self.modifiers & mask)

    def is_katakana(self) -> bool:
        return self.is_key(self._controller._Kana) or self.is_key(IBus.Hiragana_Katakana)

    def is_henkan(self) -> bool:
        if self.is_key(self._controller._Henkan) or self.is_key(IBus.Henkan) or self.is_key(IBus.Hangul):
            return not (self.is_control() or self.is_shift())
        return False

    def is_muhenkan(self) -> bool:
        if self.is_key(self._controller._Muhenkan):
            return True
        if self.is_key(self._controller._Henkan) or self.is_key(IBus.Henkan) or self.is_key(IBus.Hangul):
            return self.is_shift() and not self.is_control()
        return False

    def is_dual_role(self) -> bool:
        return bool(self.modifiers & DUAL_BITS)

    def get_string(self) -> str:
        return self._controller.get_string(self)


class KeyboardController:

    def __init__(self, layout):
        self._layout = layout
        self._modifiers = 0

        # Set to the default values
        self._OnOffByCaps = True            # or False
        self._SandS = False                 # True if SandS is used
        self._Henkan = IBus.VoidSymbol      # or IBus.Henkan, IBus.space
        self._Muhenkan = IBus.VoidSymbol    # or IBus.Muhenkan
        self._Eisuu = IBus.VoidSymbol       # or IBus.Eisu_toggle
        self._Kana = IBus.VoidSymbol        # or IBus.Hiragana_Katakana, IBus.Control_R
        self._Space = IBus.VoidSymbol       # Extra space key
        self._Prefix = False                # True if Shift is to be prefixed
        self._HasYen = False
        self._DualBits = 0

        if layout.get('Keyboard') == '109':
            self._Kana = IBus.Hiragana_Katakana
            self._Eisuu = IBus.Eisu_toggle

        self._OnOffByCaps = layout.get('OnOffByCaps', self._OnOffByCaps)
        self._HasYen = layout.get('HasYen', self._HasYen)

        self._SandS = layout.get('SandS', False)
        if self._SandS:
            self._DualBits |= DUAL_SPACE_BIT
        else:
            self._Prefix = layout.get('Prefix', False)
            if self._Prefix:
                self._DualBits |= DUAL_SPACE_BIT

        if 'Space' in layout:
            self._Space = IBus.keyval_from_name(layout['Space'])
        if 'Henkan' in layout:
            self._Henkan = IBus.keyval_from_name(layout['Henkan'])
        if 'Muhenkan' in layout:
            self._Muhenkan = IBus.keyval_from_name(layout['Muhenkan'])
        if 'Katakana' in layout:
            self._Kana = IBus.keyval_from_name(layout['Katakana'])

        # Check dual role modifiers
        self._capture_alt_r = False
        for k in (self._Henkan, self._Muhenkan, self._Kana, self._Space):
            if k in MODIFIERS:
                self._DualBits |= DUAL_SHIFT_L_BIT << MODIFIERS.index(k)
            if k == IBus.Alt_R:
                self._capture_alt_r = True

    def reset(self):
        self._modifiers = 0

    def process_key_event(self, engine: IBus.Engine, keyval, keycode, state) -> bool:
        LOGGER.info(f'process_event: {self._modifiers:#07x}')

        # Ignore XFree86 anomaly
        if keyval == IBus.ISO_Left_Tab:
            keyval = IBus.Tab
        elif keyval == IBus.Meta_L:
            # [Shift]-[Alt_L]
            keyval = IBus.Alt_L
        elif keyval in (IBus.Meta_R, IBus.ISO_Level3_Shift):
            # [Shift]-[Alt_R] or [AltGr]
            keyval = IBus.Alt_R

        self._modifiers &= ~DUAL_BITS
        is_press = not (state & IBus.ModifierType.RELEASE_MASK)
        if is_press:
            # Test state first to support On-Screen Keyboard since it may
            # not generate key events for shift keys.
            if state & IBus.ModifierType.SHIFT_MASK:
                self._modifiers |= SHIFT_L_BIT
            elif self._modifiers & SHIFT_L_BIT:
                self._modifiers &= ~SHIFT_L_BIT

            if keyval == IBus.space:
                if self._modifiers & (MODIFIER_BITS & ~SPACE_BIT):
                    self._modifiers |= NOT_DUAL_SPACE_BIT
                else:
                    self._modifiers &= ~NOT_DUAL_SPACE_BIT
                self._modifiers |= SPACE_BIT
            elif keyval == IBus.Shift_L:
                if self._modifiers & MODIFIER_BITS:
                    self._modifiers |= NOT_DUAL_SHIFT_L_BIT
                else:
                    self._modifiers &= ~NOT_DUAL_SHIFT_L_BIT
                self._modifiers |= SHIFT_L_BIT
            elif keyval == IBus.Shift_R:
                if self._modifiers & MODIFIER_BITS:
                    self._modifiers |= NOT_DUAL_SHIFT_R_BIT
                else:
                    self._modifiers &= ~NOT_DUAL_SHIFT_R_BIT
                self._modifiers |= SHIFT_R_BIT
            elif keyval == IBus.Control_L:
                self._modifiers |= CONTROL_L_BIT
            elif keyval == IBus.Control_R:
                if self._modifiers & MODIFIER_BITS:
                    self._modifiers |= NOT_DUAL_CONTROL_R_BIT
                else:
                    self._modifiers &= ~NOT_DUAL_CONTROL_R_BIT
                self._modifiers |= CONTROL_R_BIT
            elif keyval == IBus.Alt_R:
                if self._modifiers & MODIFIER_BITS:
                    self._modifiers |= NOT_DUAL_ALT_R_BIT
                else:
                    self._modifiers &= ~NOT_DUAL_ALT_R_BIT
                self._modifiers |= ALT_R_BIT

            if (self._modifiers & SPACE_BIT) and keyval != IBus.space:
                self._modifiers |= NOT_DUAL_SPACE_BIT
            if (self._modifiers & SHIFT_L_BIT) and keyval != IBus.Shift_L:
                self._modifiers |= NOT_DUAL_SHIFT_L_BIT
            if (self._modifiers & SHIFT_R_BIT) and keyval != IBus.Shift_R:
                self._modifiers |= NOT_DUAL_SHIFT_R_BIT
            if (self._modifiers & CONTROL_R_BIT) and keyval != IBus.Control_R:
                self._modifiers |= NOT_DUAL_CONTROL_R_BIT
            if (self._modifiers & ALT_R_BIT) and keyval != IBus.Alt_R:
                self._modifiers |= NOT_DUAL_ALT_R_BIT

            # Check CAPS LOCK for IME on/off
            if self._OnOffByCaps:
                if keyval == IBus.Caps_Lock:
                    # Note CAPS LOCK LED is turned off after the key release event.
                    if state & IBus.ModifierType.LOCK_MASK:
                        engine.disable_ime()
                    else:
                        engine.enable_ime()
                    return False
                elif not engine.is_overridden() and engine.is_wayland():
                    # Do not run the following block on X11 due to the reason
                    # commented in EngineHiragana.do_process_key_event.
                    if state & IBus.ModifierType.LOCK_MASK:
                        engine.enable_ime()
                    else:
                        engine.disable_ime()

            if keyval in (IBus.Muhenkan, IBus.Hangul_Hanja):
                # [無変換], [A]
                if self._modifiers & SHIFT_BITS:
                    mode = 'Ａ'
                elif self._modifiers & (CONTROL_L_BIT | CONTROL_R_BIT):
                    mode = {
                        'ア': 'ｱ',
                        'ｱ': 'あ',
                        'あ': 'ア'
                    }.get(engine.get_mode(), 'あ')
                else:
                    mode = 'A'
                if engine.set_mode(mode, True):
                    return True
            elif keyval in (IBus.Henkan, IBus.Hangul, IBus.Hiragana_Katakana):
                # [変換], [あ], [ひらがな]
                if not engine.is_lookup_table_visible():
                    mode = 'あ'
                    if keyval == IBus.Hiragana_Katakana and (self._modifiers & SHIFT_BITS):
                        mode = 'ア'
                    if engine.set_mode(mode, True):
                        return True
            elif keyval in (self._Eisuu, IBus.Zenkaku_Hankaku):
                # [英数], [全角/半角]
                mode = 'A' if engine.get_mode() != 'A' else 'あ'
                engine.set_mode(mode, True)
                return True

        else:

            if keyval == IBus.space:
                if not (self._modifiers & NOT_DUAL_SPACE_BIT):
                    self._modifiers |= DUAL_SPACE_BIT
                self._modifiers &= ~SPACE_BIT
            elif keyval == IBus.Shift_L:
                if not (self._modifiers & NOT_DUAL_SHIFT_L_BIT):
                    self._modifiers |= DUAL_SHIFT_L_BIT
                self._modifiers &= ~SHIFT_L_BIT
            elif keyval == IBus.Shift_R:
                if not (self._modifiers & NOT_DUAL_SHIFT_R_BIT):
                    self._modifiers |= DUAL_SHIFT_R_BIT
                self._modifiers &= ~SHIFT_R_BIT
            elif keyval == IBus.Control_L:
                self._modifiers &= ~CONTROL_L_BIT
            elif keyval == IBus.Control_R:
                if not (self._modifiers & NOT_DUAL_CONTROL_R_BIT):
                    self._modifiers |= DUAL_CONTROL_R_BIT
                self._modifiers &= ~CONTROL_R_BIT
            elif keyval == IBus.Alt_R:
                if not (self._modifiers & NOT_DUAL_ALT_R_BIT):
                    self._modifiers |= DUAL_ALT_R_BIT
                self._modifiers &= ~ALT_R_BIT

        if engine.get_mode() in ('あ', 'ア', 'ｱ'):
            if keyval == IBus.space:
                if self._SandS and is_press:
                    return True
                elif self._Prefix:
                    if is_press:
                        if not (self._modifiers & (NOT_DUAL_SPACE_BIT | PREFIX_BIT)):
                            return True
                    else:
                        if self._modifiers & DUAL_SPACE_BIT:
                            self._modifiers ^= PREFIX_BIT
                        else:
                            return True

        # Ignore normal key release events
        if not is_press and not (self._modifiers & self._DualBits):
            self._modifiers &= ~PREFIX_BIT
            return False

        # Treat Yen key separately for Japanese 109 keyboard.
        if keyval == IBus.backslash and keycode == 0x7c:
            keyval = IBus.yen

        # Call back the engine with an event
        event = self.create_event(keyval, keycode, state)
        processed = engine.process_key_event(event)

        if keyval == IBus.Alt_R and self._capture_alt_r:
            return True
        if event.is_dual_role():
            # Modifiers have to be further processed.
            return False
        return processed

    def is_onoff_by_caps(self):
        LOGGER.info(f'is_onoff_by_caps: {self._OnOffByCaps}')
        return self._OnOffByCaps

    def create_event(self, keyval, keycode, state) -> Event:
        return Event(self, keyval, keycode, state, self._modifiers)

    def get_string(self, e: Event) -> str:
        c = ''
        if e.has_altgr() and 'AltGr' in self._layout:
            if e.keycode < len(self._layout['AltGr']):
                a = self._layout['AltGr'][e.keycode]
                c = a[3] if e.is_shift() else a[2]
        elif e.is_ascii():
            keyval = IBus.space if e.is_space() else e.keyval
            if keyval == IBus.yen:
                c = '¥'
            elif keyval == IBus.asciitilde and e.keycode == 0x0b:
                c = '_'
            else:
                c = chr(keyval)
        return c

    def kana(self, e: Event) -> str:
        c = ''
        if 'Key' in self._layout and e.keycode < len(self._layout['Key']):
            a = self._layout['Key'][e.keycode]
            c = a[3] if e.is_shift() else a[2]
            LOGGER.debug(f'kana: {c}')
        return c

    def transliterate_back(self, roman: str) -> str:
        if roman in self._layout['Roomazi']:
            return self._layout['Roomazi'][roman]
        return ''
