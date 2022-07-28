# ibus-hiragana - Hiragana IME for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2017-2022 Esrille Inc.
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

from dictionary import Dictionary
import event
from event import Event
import package

import gettext
import json
import logging
import os
import queue
import re
import subprocess
import threading
import time

import gi
gi.require_version('IBus', '1.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gio, Gtk, IBus

keysyms = IBus

logger = logging.getLogger(__name__)

_ = lambda a: gettext.dgettext(package.get_name(), a)

HIRAGANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっゎぱぴぷぺぽゎゐゑ・ーゝゞ"
KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッヮパピプペポヮヰヱ・ーヽヾ"

TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)

NON_DAKU = 'あいうえおかきくけこさしすせそたちつてとはひふへほやゆよわアイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨワぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょゎァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョヮゔヴゝヽゞヾ'
DAKU = 'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょゎァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョヮあいゔえおかきくけこさしすせそたちつてとはひふへほやゆよわアイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨワうウゞヾゝヽ'

NON_HANDAKU = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'
HANDAKU = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

OKURIGANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっゎぱぴぷぺぽゎゐゑ゛゜"

ZENKAKU = ''.join(chr(i) for i in range(0xff01, 0xff5f)) + '　〔〕［］￥？'
HANKAKU = ''.join(chr(i) for i in range(0x21, 0x7f)) + ' ❲❳[]¥?'

TO_HANKAKU = str.maketrans(ZENKAKU, HANKAKU)
TO_ZENKAKU = str.maketrans(HANKAKU, ZENKAKU)

RE_SOKUON = re.compile(r'[kstnhmyrwgzdbpfjv]')

NAME_TO_LOGGING_LEVEL = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

INPUT_MODE_NAMES = ('A', 'あ', 'ア', 'Ａ', 'ｱ')

IAA = '\uFFF9'  # IAA (INTERLINEAR ANNOTATION ANCHOR)
IAS = '\uFFFA'  # IAS (INTERLINEAR ANNOTATION SEPARATOR)
IAT = '\uFFFB'  # IAT (INTERLINEAR ANNOTATION TERMINATOR)

CANDIDATE_FOREGROUND_COLOR = 0x000000
CANDIDATE_BACKGROUND_COLOR = 0xd1eaff

# There are several applications that claim to support
# IBus.Capabilite.SURROUNDING_TEXT but actually don't;
# e.g. Google Chrome v93.0.
# Those applications are marked as SURROUNDING_BROKEN.
# 'focus_in', 'focus_out' and 'reset' signals from those
# applications need to be ignored for Kana-Kanji
# conversion in the legacy mode.
SURROUNDING_RESET = 0
SURROUNDING_COMMITTED = 1
SURROUNDING_SUPPORTED = 2
SURROUNDING_NOT_SUPPORTED = -1
SURROUNDING_BROKEN = -2

# Web applications running on web browsers sometimes need a short delay
# between delete_surrounding_text() and commit_text(), between multiple
# forward_key_event(), and before updating the preedit text.
# Gmail running on Firefox 91.0.2 is an example of such an application.
EVENT_DELAY = 0.02


def get_plain_text(text):
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


def to_katakana(kana):
    return kana.translate(TO_KATAKANA)


def to_hankaku(kana):
    s = ''
    for c in kana:
        c = c.translate(TO_HANKAKU)
        s += {
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
    return s


def to_zenkaku(asc):
    return asc.translate(TO_ZENKAKU)


# EngineModeless provides an ideal variant of get_surrounding_text().
# It also supports applications that do not support surrounding text API.
# Note IBus.Engine.get_surrounding_text() can be used only once in
# do_process_key_event(). For modeless IMEs, this is too restrictive.
class EngineModeless(IBus.Engine):
    def __init__(self):
        super().__init__()
        self._surrounding = SURROUNDING_RESET
        self._preedit_text = ''
        self._preedit_pos = 0
        self._preedit_pos_orig = 0
        self._preedit_pos_min = 0
        self.roman_text = ''
        self.connect('set-surrounding-text', self._set_surrounding_text_cb)

    def _forward_backspaces(self, size):
        logger.debug(f'_forward_backspaces({size})')
        for i in range(size):
            self.forward_key_event(IBus.BackSpace, 14, 0)
            time.sleep(EVENT_DELAY)
            self.forward_key_event(IBus.BackSpace, 14, IBus.ModifierType.RELEASE_MASK)

    def _set_surrounding_text_cb(self, engine, text, cursor_pos, anchor_pos):
        self._surrounding = SURROUNDING_SUPPORTED
        self._preedit_text = ''
        text = get_plain_text(text.get_text())
        logger.debug(f'_set_surrounding_text_cb("{text}", {cursor_pos}, {anchor_pos})')

    def backspace(self):
        if self.roman_text:
            self.roman_text = self.roman_text[:-1]
            return True
        if self.should_draw_preedit() and 0 < self._preedit_pos:
            self._preedit_text = self._preedit_text[:self._preedit_pos - 1] + self._preedit_text[self._preedit_pos:]
            self._preedit_pos -= 1
            return True
        return False

    def check_surrounding_support(self):
        if self._surrounding == SURROUNDING_COMMITTED:
            logger.debug(f'check_surrounding_support(): "{self._preedit_text}"')
            self._surrounding = SURROUNDING_BROKEN
            # Hide preedit text for a moment so that the current client can
            # process the backspace keys.
            self.update_preedit_text(IBus.Text.new_from_string(''), 0, 0)
            # Note delete_surrounding_text() doesn't work here.
            self._forward_backspaces(len(self._preedit_text))

    def clear(self):
        self._surrounding = SURROUNDING_RESET
        self._preedit_text = ''
        self._preedit_pos = 0
        self.roman_text = ''

    def clear_preedit(self):
        text = self._preedit_text
        self._preedit_text = ''
        self._preedit_pos = 0
        return text

    def clear_roman(self):
        text = self.roman_text
        self.roman_text = ''
        return text

    def commit_roman(self):
        text = self.roman_text
        if text:
            if text == 'n':
                text = 'ん'
            self.commit_string(text)
            self.roman_text = ''
        return text

    def commit_string(self, text):
        if not text:
            return text
        logger.debug(f'commit_string("{text}"): "{self._preedit_text}"')
        self._preedit_text = self._preedit_text[:self._preedit_pos] + text + self._preedit_text[self._preedit_pos:]
        self._preedit_pos += len(text)
        if self._surrounding == SURROUNDING_RESET:
            self._surrounding = SURROUNDING_COMMITTED
        return text

    def delete_surrounding_string(self, size):
        logger.debug(f'delete_surrounding_string({size})')
        assert size <= self._preedit_pos
        self._preedit_text = self._preedit_text[:self._preedit_pos - size] + self._preedit_text[self._preedit_pos:]
        self._preedit_pos -= size
        if self._preedit_pos < self._preedit_pos_min:
            self._preedit_pos_min = self._preedit_pos

    # Note _roman_text is not flushed; use commit_roman() first.
    def flush(self, text=''):
        if text:
            self.commit_string(text)

        if self._surrounding == SURROUNDING_COMMITTED:
            logger.debug(f'flush("{self._preedit_text}"): committed')
            if self._preedit_text:
                self.commit_text(IBus.Text.new_from_string(self._preedit_text))
            return self._preedit_text
        elif self.should_draw_preedit():
            logger.debug(f'flush("{self._preedit_text}"): preedit')
            if self._preedit_text:
                self.commit_text(IBus.Text.new_from_string(self._preedit_text))
        else:
            logger.debug(f'flush("{self._preedit_text}"): {self._preedit_pos_min}:{self._preedit_pos_orig}:{self._preedit_pos}')
            delete_size = self._preedit_pos_orig - self._preedit_pos_min
            if 0 < delete_size:
                delete_size = self._preedit_pos_orig - self._preedit_pos_min
                logger.debug(f'flush: delete: {delete_size}')
                self.delete_surrounding_text(-delete_size, delete_size)
            if self._preedit_pos_min < self._preedit_pos:
                size = self._preedit_pos - self._preedit_pos_min
                logger.debug(f'flush: insert: "{self._preedit_text[self._preedit_pos - size:self._preedit_pos]}"')
                if 0 < delete_size:
                    time.sleep(EVENT_DELAY)
                self.commit_text(IBus.Text.new_from_string(self._preedit_text[self._preedit_pos - size:self._preedit_pos]))

        text = self._preedit_text
        self._preedit_text = ''
        self._preedit_pos = 0
        self._preedit_pos_min = 0
        self._preedit_pos_orig = 0
        return text

    def get_surrounding_string(self):
        if not (self.client_capabilities & IBus.Capabilite.SURROUNDING_TEXT):
            self._surrounding = SURROUNDING_NOT_SUPPORTED
        if self._surrounding != SURROUNDING_SUPPORTED:
            # Call get_surrounding_text() anyway to see if the surrounding
            # text is supported in the current client.
            super().get_surrounding_text()
            logger.debug(f'surrounding text: "{self._preedit_text}"')
            assert len(self._preedit_text) == self._preedit_pos
            return self._preedit_text, self._preedit_pos

        if self._preedit_text:
            return self._preedit_text, self._preedit_pos

        # Cache the current surrounding text in _preedit_text and _preedit_pos
        surrounding_text = super().get_surrounding_text()
        text: str = surrounding_text[0].get_text()
        pos = surrounding_text[1]

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

        # Several applications insert the preedit text to the surrounding text.
        # GTK IBus generally expects that preedit texts are not included in the surrounding text.
        # We mimic GTK IBus's behavior here.
        roman_len = len(self.roman_text)
        if 0 < roman_len and text[:pos].endswith(self.roman_text):
            text = text[:-roman_len] + text[pos:]
            pos -= roman_len

        self._preedit_text = text
        self._preedit_pos = pos
        self._preedit_pos_min = pos
        self._preedit_pos_orig = pos
        logger.debug(f'surrounding text: "{self._preedit_text}", {self._preedit_pos}')
        return self._preedit_text, self._preedit_pos

    def has_preedit(self):
        return self._preedit_text

    def should_draw_preedit(self):
        return self._surrounding in (SURROUNDING_NOT_SUPPORTED, SURROUNDING_BROKEN)

    #
    # virtual methods of IBus.Engine
    #
    def do_enable(self):
        logger.info('enable')
        # Request the initial surrounding-text when enabled as documented.
        super().get_surrounding_text()

    def do_focus_in(self):
        # Request the initial surrounding-text in addition to the "enable" handler.
        if not self._preedit_text:
            self._surrounding = SURROUNDING_RESET
        super().get_surrounding_text()


class EngineHiragana(EngineModeless):
    __gtype_name__ = 'EngineHiragana'

    def __init__(self):
        super().__init__()
        self._mode = 'A'  # _mode must be one of _input_mode_names
        self._override = False
        self._layout = dict()
        self._to_kana = self._handle_default_layout
        self._shrunk = []
        self._lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self._lookup_table.set_orientation(IBus.Orientation.VERTICAL)

        self._init_props()

        self._settings = Gio.Settings.new('org.freedesktop.ibus.engine.hiragana')
        self._settings.connect('changed', self._config_value_changed_cb)

        self._logging_level = self._load_logging_level(self._settings)
        self._dict = self._load_dictionary(self._settings)
        self._layout = self._load_layout(self._settings)
        self._delay = self._load_delay(self._settings)
        self._event = Event(self, self._delay, self._layout)

        self.set_mode(self._load_input_mode(self._settings))
        self._set_x4063_mode(self._load_x4063_mode(self._settings))

        self._keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
        self._keymap.connect('state-changed', self._keymap_state_changed_cb)

        self.connect('set-cursor-location', self._set_cursor_location_cb)

        self._about_dialog = None
        self._setup_proc = None
        self._q = queue.Queue()

    def _confirm_candidate(self):
        current = self._dict.current()
        if current:
            self._dict.confirm(''.join(self._shrunk))
            self._dict.reset()
            self._lookup_table.clear()
        return current

    def _handle_default_layout(self, preedit, keyval, state=0, modifiers=0):
        return self._event.chr(), ''

    def _handle_kana_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        c = self._event.chr().lower()
        if self._event.is_shift():
            if 'Shift' in self._layout:
                yomi = self._layout['Shift'].get(c, '')
            elif modifiers & event.SHIFT_L_BIT:
                yomi = self._layout['ShiftL'].get(c, '')
            elif modifiers & event.SHIFT_R_BIT:
                yomi = self._layout['ShiftR'].get(c, '')
        else:
            yomi = self._layout['Normal'].get(c, '')
        return yomi, preedit

    def _handle_roomazi_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        c = self._event.chr().lower()
        if preedit == 'n' and self.character_after_n.find(c) < 0:
            yomi = 'ん'
            preedit = preedit[1:]
        preedit += c
        if preedit in self._layout['Roomazi']:
            yomi += self._layout['Roomazi'][preedit]
            preedit = ''
        elif 2 <= len(preedit) and preedit[0] == preedit[1] and RE_SOKUON.search(preedit[1]):
            yomi += 'っ'
            preedit = preedit[1:]
        return yomi, preedit

    def _init_input_mode_props(self):
        props = IBus.PropList()
        props.append(IBus.Property(key='InputMode.Alphanumeric',
                                   prop_type=IBus.PropType.RADIO,
                                   label=IBus.Text.new_from_string(_("Alphanumeric (A)")),
                                   icon=None,
                                   tooltip=None,
                                   sensitive=True,
                                   visible=True,
                                   state=IBus.PropState.CHECKED,
                                   sub_props=None))
        props.append(IBus.Property(key='InputMode.Hiragana',
                                   prop_type=IBus.PropType.RADIO,
                                   label=IBus.Text.new_from_string(_("Hiragana (あ)")),
                                   icon=None,
                                   tooltip=None,
                                   sensitive=True,
                                   visible=True,
                                   state=IBus.PropState.UNCHECKED,
                                   sub_props=None))
        props.append(IBus.Property(key='InputMode.Katakana',
                                   prop_type=IBus.PropType.RADIO,
                                   label=IBus.Text.new_from_string(_("Katakana (ア)")),
                                   icon=None,
                                   tooltip=None,
                                   sensitive=True,
                                   visible=True,
                                   state=IBus.PropState.UNCHECKED,
                                   sub_props=None))
        props.append(IBus.Property(key='InputMode.WideAlphanumeric',
                                   prop_type=IBus.PropType.RADIO,
                                   label=IBus.Text.new_from_string(_("Wide Alphanumeric (Ａ)")),
                                   icon=None,
                                   tooltip=None,
                                   sensitive=True,
                                   visible=True,
                                   state=IBus.PropState.UNCHECKED,
                                   sub_props=None))
        props.append(IBus.Property(key='InputMode.HalfWidthKatakana',
                                   prop_type=IBus.PropType.RADIO,
                                   label=IBus.Text.new_from_string(_("Halfwidth Katakana (ｱ)")),
                                   icon=None,
                                   tooltip=None,
                                   sensitive=True,
                                   visible=True,
                                   state=IBus.PropState.UNCHECKED,
                                   sub_props=None))
        return props

    def _init_props(self):
        self._prop_list = IBus.PropList()
        self._input_mode_prop = IBus.Property(
            key='InputMode',
            prop_type=IBus.PropType.MENU,
            symbol=IBus.Text.new_from_string(self._mode),
            label=IBus.Text.new_from_string(_("Input mode (%s)") % self._mode),
            icon=None,
            tooltip=None,
            sensitive=True,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self._input_mode_prop.set_sub_props(self._init_input_mode_props())
        self._prop_list.append(self._input_mode_prop)
        prop = IBus.Property(
            key='Setup',
            prop_type=IBus.PropType.NORMAL,
            label=IBus.Text.new_from_string(_("Setup")),
            icon=None,
            tooltip=None,
            sensitive=True,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self._prop_list.append(prop)
        prop = IBus.Property(
            key='Help',
            prop_type=IBus.PropType.NORMAL,
            label=IBus.Text.new_from_string(_("Help")),
            icon=None,
            tooltip=None,
            sensitive=True,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self._prop_list.append(prop)
        prop = IBus.Property(
            key='About',
            prop_type=IBus.PropType.NORMAL,
            label=IBus.Text.new_from_string(_("About Hiragana IME...")),
            icon=None,
            tooltip=None,
            sensitive=True,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self._prop_list.append(prop)

    def _load_delay(self, settings):
        delay = settings.get_int('delay')
        logger.info(f'delay: {delay}')
        return delay

    def _load_dictionary(self, settings, clear_history=False):
        path = settings.get_string('dictionary')
        user = settings.get_string('user-dictionary')
        return Dictionary(path, user, clear_history)

    def _load_input_mode(self, settings):
        mode = settings.get_string('mode')
        if mode not in INPUT_MODE_NAMES:
            mode = 'A'
            settings.reset('mode')
        logger.info(f'input mode: {mode}')
        return mode

    def _load_layout(self, settings):
        default_layout = os.path.join(package.get_datadir(), 'layouts')
        default_layout = os.path.join(default_layout, 'roomazi.json')
        path = settings.get_string('layout')
        logger.info(f'layout: {path}')
        layout = dict()
        try:
            with open(path) as f:
                layout = json.load(f)
        except Exception as error:
            logger.error(error)
        if not layout:
            try:
                with open(default_layout) as f:
                    layout = json.load(f)
            except Exception as error:
                logger.error(error)
        if layout.get('Type') == 'Kana':
            self._to_kana = self._handle_kana_layout
            self._dict.use_romazi(False)
        elif 'Roomazi' in layout:
            self._to_kana = self._handle_roomazi_layout
            self._dict.use_romazi(True)
        else:
            self._to_kana = self._handle_default_layout
            self._dict.use_romazi(True)
        return layout

    def _load_logging_level(self, settings):
        level = settings.get_string('logging-level')
        if level not in NAME_TO_LOGGING_LEVEL:
            level = 'WARNING'
            settings.reset('logging-level')
        logger.info(f'logging_level: {level}')
        logging.getLogger().setLevel(NAME_TO_LOGGING_LEVEL[level])
        return level

    def _load_x4063_mode(self, settings):
        mode = settings.get_boolean('nn-as-jis-x-4063')
        logger.info(f'nn_as_jis_x_4063 mode: {mode}')
        return mode

    def _lookup_dictionary(self, yomi, pos, process_n=True):
        if process_n and self.roman_text == 'n':
            yomi = yomi[:pos] + 'ん'
            pos += 1
        self._lookup_table.clear()
        cand = self._dict.lookup(yomi, pos)
        size = len(self._dict.reading())
        if 0 < size:
            if process_n and self.roman_text == 'n':
                # For FuriganaPad, yomi has to be committed anyway.
                self.clear_roman()
                self.commit_string('ん')
            if 1 < len(self._dict.cand()):
                for c in self._dict.cand():
                    self._lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return cand, size

    def _process_dakuten(self, c):
        if c not in '゛゜':
            return c
        text, pos = self.get_surrounding_string()
        if pos <= 0:
            return c
        if c == '゛':
            found = NON_DAKU.find(text[pos - 1])
            if 0 <= found:
                self.delete_surrounding_string(1)
                c = DAKU[found]
        elif c == '゜':
            found = NON_HANDAKU.find(text[pos - 1])
            if 0 <= found:
                self.delete_surrounding_string(1)
                c = HANDAKU[found]
        return c

    def _process_escape(self):
        self.clear_roman()
        assert self._dict.current()
        yomi = self._dict.reading()
        self._reset(False)
        self.commit_string(yomi)

    def _process_expand(self):
        assert self._dict.current()
        if not self._shrunk:
            return True
        kana = self._shrunk[-1]
        yomi = self._dict.reading()
        text, pos = self.get_surrounding_string()
        (cand, size) = self._lookup_dictionary(kana + yomi + text[pos:], len(kana + yomi))
        assert 0 < size
        self.delete_surrounding_string(len(kana))
        self._shrunk.pop(-1)
        return True

    def _process_katakana(self):
        text, pos = self.get_surrounding_string()
        if self.roman_text == 'n':
            self.clear_roman()
            text = text[:pos] + 'ん'
            pos += 1
            self.commit_string('ん')
        for i in reversed(range(pos)):
            if 0 <= KATAKANA.find(text[i]):
                continue
            found = HIRAGANA.find(text[i])
            if 0 <= found:
                self.delete_surrounding_string(pos - i)
                self.commit_string(KATAKANA[found] + text[i + 1:pos])
            break
        return True

    def _process_okurigana(self, pos_yougen):
        text, pos = self.get_surrounding_string()
        assert pos_yougen < pos
        text = text[pos_yougen:pos]
        pos = len(text)
        logger.debug(f"_process_okurigana: '{text}', '{self.roman_text}'")
        cand, size = self._lookup_dictionary(text, pos, False)
        if not self._dict.current():
            self._dict.create_pseudo_candidate(text)
            cand = text
            size = len(text)
        if self._dict.current():
            self._shrunk = []
            self.delete_surrounding_string(size)
        return True

    def _process_replace(self):
        if self._dict.current():
            return True
        text, pos = self.get_surrounding_string()
        # Check Return for yôgen conversion
        if self._event.is_henkan() or self._event.is_key(keysyms.Return):
            cand, size = self._lookup_dictionary(text, pos)
        elif 1 <= pos:
            assert self._event.is_muhenkan()
            suffix = text[:pos].rfind('―')
            if 0 < suffix:
                cand, size = self._lookup_dictionary(text, pos)
            else:
                self.commit_string('―')
                text, pos = self.get_surrounding_string()
                cand, size = self._lookup_dictionary(text, pos)
                if not cand:
                    self.delete_surrounding_string(1)
        if self._dict.current():
            self._shrunk = []
            self.delete_surrounding_string(size)
        return True

    def _process_shrink(self):
        logger.debug(f'_process_shrink: "{self._dict.current()}"')
        assert self._dict.current()
        yomi = self._dict.reading()
        if len(yomi) <= 1 or yomi[1] == '―':
            return True
        text, pos = self.get_surrounding_string()
        (cand, size) = self._lookup_dictionary(yomi[1:] + text[pos:], len(yomi) - 1)
        if 0 < size:
            kana = yomi[:-size]
            self._shrunk.append(kana)
            self.commit_string(kana)
        else:
            (cand, size) = self._lookup_dictionary(yomi + text[pos:], len(yomi))
        return True

    def _process_surrounding_text(self, keyval, keycode, state, modifiers):
        if self._dict.current():
            if keyval == keysyms.Tab:
                if not self._event.is_shift():
                    return self._process_shrink()
                else:
                    return self._process_expand()
            if keyval == keysyms.Escape:
                self._process_escape()
                return True
            if keyval == keysyms.Return:
                current = self._confirm_candidate()
                self.commit_string(current)
                if current[-1] == '―':
                    return self._process_replace()
                else:
                    self.commit_roman()
                    self.flush()
                    return True

        if keyval == keysyms.Return and self.commit_roman():
            return True
        if keyval == keysyms.Escape and self.clear_roman():
            return True

        if (self._event.is_henkan() or self._event.is_muhenkan()) and not(modifiers & event.ALT_R_BIT):
            return self._process_replace()

        text, pos = self.get_surrounding_string()
        pos_yougen = -1
        to_revert = False
        current = self._dict.current()
        if current:
            # Commit the current candidate
            yomi = self._dict.reading()
            self._confirm_candidate()
            self.commit_string(current)
            logger.debug(f"_process_text: '{text}', current: '{current}', yomi: '{yomi}'")
            if current[-1] == '―':
                pos_yougen = pos
            elif self._dict.not_selected() and (current[-1] in OKURIGANA or yomi[-1] == '―' or self.roman_text):
                pos_yougen = pos
                to_revert = True
                current = yomi
            elif self.should_draw_preedit():
                self.flush()

        if self._event.is_katakana():
            self._process_katakana()
            return True
        if self._event.is_backspace():
            if to_revert:
                if self.roman_text:
                    self.roman_text = self.roman_text[:-1]
                else:
                    current = current[:-1]
                text, pos = self.get_surrounding_string()
                self.delete_surrounding_string(pos - pos_yougen)
                self.commit_string(current)
                return self._process_okurigana(pos_yougen)
            if self.backspace():
                return True
            return False

        yomi = ''
        if self._event.is_ascii():
            if modifiers & event.ALT_R_BIT:
                yomi = self.process_alt_graph(keyval, keycode, state, modifiers)
                if yomi:
                    if self.get_mode() != 'ｱ':
                        yomi = to_zenkaku(yomi)
                    self.clear_roman()
            elif self.get_mode() == 'Ａ':
                yomi = to_zenkaku(self._event.chr())
            else:
                yomi, self.roman_text = self._to_kana(self.roman_text, keyval, state, modifiers)
                if yomi:
                    if self.get_mode() == 'ア':
                        yomi = to_katakana(yomi)
                    elif self.get_mode() == 'ｱ':
                        yomi = to_hankaku(to_katakana(yomi))
        elif keyval == keysyms.hyphen:
            yomi = '―'
        elif self._event.is_prefix():
            pass
        elif self.has_preedit() and self.should_draw_preedit():
            if keyval == keysyms.Escape:
                self.clear_preedit()
            else:
                self.clear_roman()
                self.flush()
            return True
        else:
            # Let the IBus client process the key
            self.clear_roman()
            return False

        if to_revert and (not yomi or yomi[-1] in OKURIGANA or self.roman_text):
            text, pos = self.get_surrounding_string()
            self.delete_surrounding_string(pos - pos_yougen)
            self.commit_string(current)
        yomi = self._process_dakuten(yomi)
        self.commit_string(yomi)
        if 0 <= pos_yougen and (not yomi or yomi[-1] in OKURIGANA or self.roman_text):
            self._process_okurigana(pos_yougen)
            current = self._dict.current()
            if current and self._dict.is_complete():
                self._confirm_candidate()
                self.commit_string(current)
        return True

    def _reset(self, full=True):
        self._dict.reset()
        self._lookup_table.clear()
        self._update_lookup_table()
        if full:
            self.clear()
        self._update_preedit()
        assert not self._dict.current()
        self._setup_sync()

    def _set_x4063_mode(self, on):
        if on:
            self.character_after_n = "aiueo'wyn"
        else:
            self.character_after_n = "aiueo'wy"
        logger.debug(f'set_x4063_mode({on})')

    def _update_candidate(self):
        index = self._lookup_table.get_cursor_pos()
        self._dict.set_current(index)
        self._update_preedit()

    def _update_input_mode(self):
        self._input_mode_prop.set_symbol(IBus.Text.new_from_string(self._mode))
        self._input_mode_prop.set_label(IBus.Text.new_from_string(_("Input mode (%s)") % self._mode))
        self.update_property(self._input_mode_prop)

    def _update_lookup_table(self):
        if self.is_enabled():
            visible = 0 < self._lookup_table.get_number_of_candidates()
            self.update_lookup_table(self._lookup_table, visible)

    def _update_preedit(self, locked=''):
        cand = self._dict.current()
        preedit_text = self._preedit_text if self.should_draw_preedit() else ''
        text = IBus.Text.new_from_string(preedit_text + cand + self.roman_text + locked)
        preedit_len = len(preedit_text)
        cand_len = len(cand)
        roman_len = len(self.roman_text)
        locked_len = len(locked)
        text_len = preedit_len + cand_len + roman_len + locked_len
        attrs = IBus.AttrList() if 0 < text_len else None
        pos = 0
        if 0 < preedit_len:
            attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE, IBus.AttrUnderline.SINGLE, pos, pos + preedit_len))
            pos += preedit_len
        if 0 < cand_len:
            attrs.append(IBus.Attribute.new(IBus.AttrType.FOREGROUND, CANDIDATE_FOREGROUND_COLOR, pos, pos + cand_len))
            attrs.append(IBus.Attribute.new(IBus.AttrType.BACKGROUND, CANDIDATE_BACKGROUND_COLOR, pos, pos + cand_len))
            pos += cand_len
        if 0 < roman_len:
            attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE, IBus.AttrUnderline.SINGLE, pos, pos + roman_len))
            pos += preedit_len
        if 0 < locked_len:
            attrs.append(IBus.Attribute.new(IBus.AttrType.FOREGROUND, CANDIDATE_FOREGROUND_COLOR, pos, pos + locked_len))
            attrs.append(IBus.Attribute.new(IBus.AttrType.BACKGROUND, CANDIDATE_BACKGROUND_COLOR, pos, pos + locked_len))
            pos += preedit_len
        if attrs:
            text.set_attributes(attrs)

        # A delay is necessary for textareas of Firefox 102.0.1.
        if text:
            time.sleep(EVENT_DELAY)

        # Note self.hide_preedit_text() does not seem to work as expected with Kate.
        # cf. "Qt5 IBus input context does not implement hide_preedit_text()",
        #     https://bugreports.qt.io/browse/QTBUG-48412
        self.update_preedit_text(text, text_len, 0 < text_len)
        self._update_lookup_table()

    #
    # setup process methods
    #
    def _setup_readline(self, process: subprocess.Popen):
        for line in iter(process.stdout.readline, ''):
            self._q.put(line.strip())
            if process.poll() is not None:
                return

    def _setup_start(self):
        if self._setup_proc:
            if self._setup_proc.poll() is None:
                return
            self._setup_proc = None
        try:
            filename = os.path.join(package.get_libexecdir(), 'ibus-setup-hiragana')
            self._setup_proc = subprocess.Popen([filename], text=True, stdout=subprocess.PIPE)
            t = threading.Thread(target=self._setup_readline, args=(self._setup_proc,), daemon=True)
            t.start()
        except OSError as e:
            logger.error(e)
        except ValueError as e:
            logger.error(e)

    def _setup_sync(self):
        last = ''
        while True:
            try:
                line = self._q.get_nowait()
                if line == last:
                    continue
                last = line
                logger.info(line)
                if line == 'reload_dictionaries':
                    self._dict = self._load_dictionary(self._settings)
                elif line == 'clear_input_history':
                    self._dict = self._load_dictionary(self._settings, clear_history=True)
            except queue.Empty:
                break

    #
    # callback methods
    #
    def _about_response_cb(self, dialog, response):
        dialog.destroy()
        self._about_dialog = None

    def _config_value_changed_cb(self, settings, key):
        logger.debug(f'config_value_changed("{key}")')
        if key == 'logging-level':
            self._logging_level = self._load_logging_level(settings)
        elif key == 'delay':
            self._reset()
            self._delay = self._load_delay(settings)
            self._event = Event(self, self._delay, self._layout)
        elif key == 'layout':
            self._reset()
            self._layout = self._load_layout(settings)
            self._event = Event(self, self._delay, self._layout)
        elif key == 'dictionary' or key == 'user-dictionary':
            self._reset()
            self._dict = self._load_dictionary(settings)
        elif key == 'mode':
            self.set_mode(self._load_input_mode(settings), True)
        elif key == 'nn-as-jis-x-4063':
            self._set_x4063_mode(self._load_x4063_mode(settings))

    def _keymap_state_changed_cb(self, keymap):
        if self._event.is_onoff_by_caps():
            logger.debug(f'caps lock: {keymap.get_caps_lock_state()}')
            if keymap.get_caps_lock_state():
                self.enable_ime()
            else:
                self.disable_ime()
        return True

    def _set_cursor_location_cb(self, engine, x, y, w, h):
        # On Raspbian, at least till Buster, the candidate window does not
        # always follow the cursor position. The following code is not
        # necessary on Ubuntu 18.04 or Fedora 30.
        logger.debug(f'_set_cursor_location_cb({x}, {y}, {w}, {h})')
        self._update_lookup_table()

    #
    # public methods
    #
    def disable_ime(self, override=False):
        if self.is_enabled():
            self.set_mode('A', override)
            return True
        return False

    def enable_ime(self, override=False):
        if not self.is_enabled():
            self.set_mode('あ', override)
            return True
        return False

    def get_mode(self):
        return self._mode

    def is_enabled(self):
        return self.get_mode() != 'A'

    def is_lookup_table_visible(self):
        return 0 < self._lookup_table.get_number_of_candidates()

    def is_overridden(self):
        return self._override

    def process_alt_graph(self, keyval, keycode, state, modifiers):
        logger.debug(f'process_alt_graph("{self._event.chr()}")')
        c = self._event.chr().lower()
        if c == '_' and self._event._keycode == 0x0b:
            c = '0'
        if not c:
            return c
        if not self._event.is_shift():
            return self._layout['\\Normal'].get(c, '')
        if '\\Shift' in self._layout:
            return self._layout['\\Shift'].get(c, '')
        if modifiers & event.SHIFT_L_BIT:
            return self._layout['\\ShiftL'].get(c, '')
        if modifiers & event.SHIFT_R_BIT:
            return self._layout['\\ShiftR'].get(c, '')

    def process_key_event(self, keyval, keycode, state, modifiers):
        logger.debug(f'process_key_event("{IBus.keyval_name(keyval)}", {keyval:#04x}, {keycode:#04x}, {state:#010x}, {modifiers:#07x})')

        if self._event.is_dual_role():
            pass
        elif self._event.is_modifier():
            # Ignore modifier keys
            return False
        elif state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK):
            self.clear_roman()
            self.flush(self._confirm_candidate())
            self._update_preedit()
            return False

        self.check_surrounding_support()

        # Handle candidate window
        if 0 < self._lookup_table.get_number_of_candidates():
            if keyval in (keysyms.Page_Up, keysyms.KP_Page_Up):
                return self.do_page_up()
            elif keyval in (keysyms.Page_Down, keysyms.KP_Page_Down):
                return self.do_page_down()
            elif keyval == keysyms.Up or self._event.is_muhenkan():
                return self.do_cursor_up()
            elif keyval == keysyms.Down or self._event.is_henkan():
                return self.do_cursor_down()

        # Cache the current surrounding text into the EngineModless's local buffer.
        self.get_surrounding_string()
        # Edit the local surrounding text buffer as we need.
        result = self._process_surrounding_text(keyval, keycode, state, modifiers)
        # Flush the local surrounding text buffer into the IBus client.
        if self._surrounding in (SURROUNDING_COMMITTED, SURROUNDING_SUPPORTED):
            self.flush()

        # Lastly, update the preedit text. To support LibreOffice, the
        # surrounding text needs to be updated before updating the preedit text.
        if self._event.is_prefix():
            self._update_preedit('＿' if self._event.is_prefixed() else '')
        else:
            self._update_preedit()
        return result

    def set_mode(self, mode, override=False):
        self._override = override
        if self._mode == mode:
            return False
        logger.debug(f'set_mode({mode})')
        self.clear_roman()
        self.flush(self._confirm_candidate())
        self._update_preedit()
        self._mode = mode
        self._update_lookup_table()
        self._update_input_mode()
        return True

    #
    # virtual methods of IBus.Engine
    #
    def do_cursor_down(self):
        if self._lookup_table.cursor_down():
            self._update_candidate()
        return True

    def do_cursor_up(self):
        if self._lookup_table.cursor_up():
            self._update_candidate()
        return True

    def do_disable(self):
        logger.info('disable')
        self._reset()
        self._mode = 'A'
        self._dict.save_orders()

    def do_focus_in(self):
        logger.info(f'focus_in: {self._surrounding}')
        self._event.reset()
        self.register_properties(self._prop_list)
        self._update_preedit()
        super().do_focus_in()

    def do_focus_out(self):
        logger.info(f'focus_out: {self._surrounding}')
        if self._surrounding != SURROUNDING_BROKEN:
            self._reset()
            self._dict.save_orders()

    def do_page_down(self):
        if self._lookup_table.page_down():
            self._update_candidate()
        return True

    def do_page_up(self):
        if self._lookup_table.page_up():
            self._update_candidate()
        return True

    def do_process_key_event(self, keyval, keycode, state):
        return self._event.process_key_event(keyval, keycode, state)

    def do_property_activate(self, prop_name, state):
        logger.info(f'property_activate({prop_name}, {state})')
        if prop_name == 'Setup':
            self._setup_start()
        elif prop_name == 'Help':
            url = 'file://' + os.path.join(package.get_datadir(), 'help/index.html')
            # Use yelp to open local HTML help files.
            subprocess.Popen(['yelp', url])
        elif prop_name == 'About':
            if self._about_dialog:
                self._about_dialog.present()
                return
            dialog = Gtk.AboutDialog()
            dialog.set_program_name(_("Hiragana IME"))
            dialog.set_copyright("Copyright 2017-2022 Esrille Inc.")
            dialog.set_authors(["Esrille Inc."])
            dialog.set_documenters(["Esrille Inc."])
            dialog.set_website("https://www.esrille.com/")
            dialog.set_website_label("Esrille Inc.")
            dialog.set_logo_icon_name(package.get_name())
            dialog.set_default_icon_name(package.get_name())
            dialog.set_version(package.get_version())
            # To close the dialog when "close" is clicked on Raspberry Pi OS,
            # we connect the "response" signal to _about_response_cb
            dialog.connect("response", self._about_response_cb)
            self._about_dialog = dialog
            dialog.show()
        elif prop_name.startswith('InputMode.'):
            if state == IBus.PropState.CHECKED:
                mode = {
                    'InputMode.Alphanumeric': 'A',
                    'InputMode.Hiragana': 'あ',
                    'InputMode.Katakana': 'ア',
                    'InputMode.WideAlphanumeric': 'Ａ',
                    'InputMode.HalfWidthKatakana': 'ｱ',
                }.get(prop_name, 'A')
                self.set_mode(mode, True)

    def do_reset(self):
        logger.info(f'reset: {self._surrounding}')
        if self._surrounding != SURROUNDING_BROKEN:
            self._reset()
        else:
            self._update_preedit()
