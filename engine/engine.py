# ibus-hiragana - Hiragana IME for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
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

import json
import logging
import os
import queue
import subprocess
import threading
import time

import gi
gi.require_version('IBus', '1.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('GnomeDesktop', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GnomeDesktop
from gi.repository import Gtk
from gi.repository import IBus

import llm
import package
from dictionary import Dictionary
from event import Event, KeyboardController
from package import _

LOGGER = logging.getLogger(__name__)

INPUT_MODES = (
    ('InputMode.Alphanumeric', _('Alphanumeric (A)')),
    ('InputMode.Hiragana', _('Hiragana (あ)')),
    ('InputMode.Katakana', _('Katakana (ア)')),
    ('InputMode.WideAlphanumeric', _('Wide Alphanumeric (Ａ)')),
    ('InputMode.HalfWidthKatakana', _('Halfwidth Katakana (ｱ)'))
)

HIRAGANA = ('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
            'ゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっゎぱぴぷぺぽゎゐゑ・ーゝゞ')
KATAKANA = ('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'
            'ヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッヮパピプペポヮヰヱ・ーヽヾ')

TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)

NON_DAKU = ('あいうえおかきくけこさしすせそたちつてとはひふへほやゆよわ'
            'アイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨワ'
            'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょゎ'
            'ァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョヮ'
            'ゔヴゝヽゞヾ。「」、・｡｢｣､･')
DAKU = ('ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょゎ'
        'ァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョヮ'
        'あいゔえおかきくけこさしすせそたちつてとはひふへほやゆよわ'
        'アイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨワ'
        'うウゞヾゝヽ｡｢｣､･。「」、・')

NON_HANDAKU = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'
HANDAKU = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

NON_TINY = 'あいうえおつやゆよわアイウエオツヤユヨワぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ。「」、・｡｢｣､･'
TINY = 'ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮあいうえおつやゆよわアイウエオツヤユヨワ｡｢｣､･。「」、・'

OKURIGANA = ('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
             'ゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっゎぱぴぷぺぽゎゐゑ゛゜')

ZENKAKU = ''.join(chr(i) for i in range(0xff01, 0xff5f)) + '　〔〕［］￥？'
HANKAKU = ''.join(chr(i) for i in range(0x21, 0x7f)) + ' ❲❳[]¥?'

TO_HANKAKU = str.maketrans(ZENKAKU, HANKAKU)
TO_ZENKAKU = str.maketrans(HANKAKU, ZENKAKU)

ZENKAKU_DIGIT = '０１２３４５６７８９'
HANKAKU_DIGIT = '0123456789'
TO_HANKAKU_DIGIT = str.maketrans(ZENKAKU_DIGIT, HANKAKU_DIGIT)

ZENKAKU_DIGIT_EXTRA = '０１２３４５６７８９、。％'
HANKAKU_DIGIT_EXTRA = '0123456789,.%'
TO_HANKAKU_DIGIT_EXTRA = str.maketrans(ZENKAKU_DIGIT_EXTRA, HANKAKU_DIGIT_EXTRA)

FROM_CIRCUMFLEX = str.maketrans('âîûêôÂÎÛÊÔ', 'aiueoAIUEO')
TO_CIRCUMFLEX = str.maketrans('aiueoAIUEO', 'âîûêôÂÎÛÊÔ')

FROM_MACRON = str.maketrans('āīūēōĀĪŪĒŌ', 'aiueoAIUEO')
TO_MACRON = str.maketrans('aiueoAIUEO', 'āīūēōĀĪŪĒŌ')

SOKUON = 'ksthmyrwgzdbpfjv'

NAME_TO_LOGGING_LEVEL = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

INPUT_MODE_NAMES = ('A', 'あ', 'ア', 'Ａ', 'ｱ')
INPUT_MODE_COUNT = len(INPUT_MODE_NAMES)

IAA = '\uFFF9'  # IAA (INTERLINEAR ANNOTATION ANCHOR)
IAS = '\uFFFA'  # IAS (INTERLINEAR ANNOTATION SEPARATOR)
IAT = '\uFFFB'  # IAT (INTERLINEAR ANNOTATION TERMINATOR)

CANDIDATE_FOREGROUND_COLOR = 0x000000
CANDIDATE_BACKGROUND_COLOR = 0xd1eaff
PREFIX_LOCK_COLOR = 0x3399ff

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
            'ワ': 'ﾜ', 'ン': 'ﾝ', '゛': 'ﾞ', '゜': 'ﾟ',
            'ガ': 'ｶﾞ', 'ギ': 'ｷﾞ', 'グ': 'ｸﾞ', 'ゲ': 'ｹﾞ', 'ゴ': 'ｺﾞ',
            'ザ': 'ｻﾞ', 'ジ': 'ｼﾞ', 'ズ': 'ｽﾞ', 'ゼ': 'ｾﾞ', 'ゾ': 'ｿﾞ',
            'ダ': 'ﾀﾞ', 'ヂ': 'ﾁﾞ', 'ヅ': 'ﾂﾞ', 'デ': 'ﾃﾞ', 'ド': 'ﾄﾞ',
            'バ': 'ﾊﾞ', 'ビ': 'ﾋﾞ', 'ブ': 'ﾌﾞ', 'ベ': 'ﾍﾞ', 'ボ': 'ﾎﾞ',
            'パ': 'ﾊﾟ', 'ピ': 'ﾋﾟ', 'プ': 'ﾌﾟ', 'ペ': 'ﾍﾟ', 'ポ': 'ﾎﾟ',
            'ヴ': 'ｳﾞ'
        }.get(c, c)
    return s


def to_hankaku_digit(yomi):
    return yomi.translate(TO_HANKAKU_DIGIT)


def to_hankaku_digit_extra(yomi):
    return yomi.translate(TO_HANKAKU_DIGIT_EXTRA)


def to_zenkaku(asc):
    return asc.translate(TO_ZENKAKU)


def prettify_state(state: int):
    s = ''
    s += 'U' if state & IBus.ModifierType.RELEASE_MASK else 'D'
    s += 'U' if state & IBus.ModifierType.LOCK_MASK else 'L'
    s += 'G' if state & IBus.ModifierType.MOD5_MASK else '_'
    s += 'S' if state & IBus.ModifierType.MOD4_MASK else '_'
    s += 'A' if state & IBus.ModifierType.MOD1_MASK else '_'
    s += 'C' if state & IBus.ModifierType.CONTROL_MASK else '_'
    s += 'S' if state & IBus.ModifierType.SHIFT_MASK else '_'
    return s


# EngineModeless provides an ideal variant of get_surrounding_text().
# It also supports applications that do not support surrounding text API.
# Note IBus.Engine.get_surrounding_text() can be used only once in
# do_process_key_event(). For modeless IMEs, this is too restrictive.
class EngineModeless(IBus.Engine):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._platform_version = 42
        if hasattr(GnomeDesktop, 'get_platform_version'):
            self._platform_version = GnomeDesktop.get_platform_version()

        display = Gdk.Display.get_default()
        self._is_wayland = 'Wayland' in type(display).__name__

        LOGGER.info(f'platform_version: {self._platform_version} / {"Wayland" if self._is_wayland else "X11"}')

        self._surrounding = SURROUNDING_RESET
        self._preedit_text = None
        self._preedit_pos = 0
        self._preedit_pos_orig = 0
        self._preedit_pos_min = 0
        self.roman_text = ''

    def _forward_backspaces(self, size):
        LOGGER.debug(f'_forward_backspaces({size})')
        for i in range(size):
            self.forward_key_event(IBus.BackSpace, 14, 0)
            time.sleep(EVENT_DELAY)
            self.forward_key_event(IBus.BackSpace, 14, IBus.ModifierType.RELEASE_MASK)

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
            LOGGER.debug(f'check_surrounding_support(): "{self._preedit_text}"')
            self._surrounding = SURROUNDING_BROKEN
            # Hide preedit text for a moment so that the current client can
            # process the backspace keys.
            self.update_preedit_text(IBus.Text.new_from_string(''), 0, 0)
            # Note delete_surrounding_text() doesn't work here.
            if self.has_non_empty_preedit():
                self._forward_backspaces(len(self._preedit_text))

    def clear(self):
        self._surrounding = SURROUNDING_RESET
        self._preedit_text = None
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
        LOGGER.debug(f'commit_string("{text}"): "{self._preedit_text}"')
        if not text:
            return text
        if not self.has_preedit():
            self.get_surrounding_string()
        self._preedit_text = self._preedit_text[:self._preedit_pos] + text + self._preedit_text[self._preedit_pos:]
        self._preedit_pos += len(text)
        if self._surrounding == SURROUNDING_RESET:
            self._surrounding = SURROUNDING_COMMITTED
        return text

    def commit_n(self):
        assert self.roman_text == 'n'
        self.clear_roman()
        self.commit_string('ん')
        if not self.should_draw_preedit():
            # For FuriganaPad, 'ん' needs to be committed.
            self.commit_text(IBus.Text.new_from_string('ん'))
            # The following two steps are necessary to support Wayland IM module on GNOME 46.
            # 1) For LibreOffice, IBus preedit text needs to be cleared before
            # the forthcoming delete_surrounding_string().
            text = IBus.Text.new_from_string('')
            self.update_preedit_text(text, 0, False)
            # 2) A delay is necessary to process surrounding text.
            time.sleep(EVENT_DELAY)
        self._preedit_pos_min += 1
        self._preedit_pos_orig += 1

    def delete_surrounding_string(self, size):
        LOGGER.debug(f'delete_surrounding_string({size})')
        assert size <= self._preedit_pos
        self._preedit_text = self._preedit_text[:self._preedit_pos - size] + self._preedit_text[self._preedit_pos:]
        self._preedit_pos -= size
        if self._preedit_pos < self._preedit_pos_min:
            self._preedit_pos_min = self._preedit_pos

    # Note _roman_text is not flushed; use commit_roman() first.
    def flush(self, text='', force=False):
        if text:
            self.commit_string(text)
        if self._surrounding == SURROUNDING_COMMITTED:
            LOGGER.debug(f'flush("{self._preedit_text}"): committed')
            if self.has_non_empty_preedit():
                self.commit_text(IBus.Text.new_from_string(self._preedit_text))
            if not force:
                return self._preedit_text
        elif self.should_draw_preedit():
            LOGGER.debug(f'flush("{self._preedit_text}"): preedit')
            if self._preedit_text:
                self.commit_text(IBus.Text.new_from_string(self._preedit_text))
                self._surrounding = SURROUNDING_RESET
        elif self.has_preedit():
            LOGGER.debug(f'flush("{self._preedit_text}"): '
                         f'{self._preedit_pos_min}:{self._preedit_pos_orig}:{self._preedit_pos}')
            delete_size = self._preedit_pos_orig - self._preedit_pos_min
            if 0 < delete_size:
                LOGGER.debug(f'flush: delete: {delete_size}')
                self.delete_surrounding_text(-delete_size, delete_size)
            if self._preedit_pos_min < self._preedit_pos:
                text = self._preedit_text[self._preedit_pos_min:self._preedit_pos]
                LOGGER.debug(f'flush: insert: "{text}"')
                if 0 < delete_size:
                    time.sleep(EVENT_DELAY)
                self.commit_text(IBus.Text.new_from_string(text))

        text = self._preedit_text
        self._preedit_text = None
        self._preedit_pos = 0
        self._preedit_pos_min = 0
        self._preedit_pos_orig = 0
        return text

    def get_platform_version(self):
        return self._platform_version

    def get_surrounding_string(self):
        if not (self.client_capabilities & IBus.Capabilite.SURROUNDING_TEXT):
            self._surrounding = SURROUNDING_NOT_SUPPORTED

        if self._surrounding != SURROUNDING_SUPPORTED:
            # Call get_surrounding_text() anyway to see if the surrounding
            # text is supported in the current client.
            super().get_surrounding_text()
            if not self.has_preedit():
                self.clear_preedit()
            assert len(self._preedit_text) == self._preedit_pos
            return self._preedit_text, self._preedit_pos

        if self._preedit_text is not None:
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
        LOGGER.debug(f'get_surrounding_string: "{self._preedit_text}", {self._preedit_pos}')
        return self._preedit_text, self._preedit_pos

    def has_preedit(self):
        return self._preedit_text is not None

    def has_non_empty_preedit(self):
        return self.has_preedit() and 0 < len(self._preedit_text)

    def is_wayland(self):
        return self._is_wayland

    def should_draw_preedit(self):
        return self._surrounding in (SURROUNDING_NOT_SUPPORTED, SURROUNDING_BROKEN)

    #
    # virtual methods of IBus.Engine
    #
    def do_enable(self) -> None:
        LOGGER.debug('do_enable()')
        # Request the initial surrounding-text when enabled as documented.
        super().get_surrounding_text()

    def do_focus_in_id(self, object_path: str, client: str) -> None:
        # Request the initial surrounding-text in addition to the "enable" handler.
        if not self.has_preedit():
            self.clear()
        super().get_surrounding_text()

    def do_set_surrounding_text(self, text: IBus.Text, cursor_pos: int, anchor_pos: int) -> None:
        original = text.get_text()
        original_len = len(original)
        LOGGER.debug(f'do_set_surrounding_text("{get_plain_text(original)}", {cursor_pos}, {anchor_pos})'
                     f': {self._surrounding} "{self._preedit_text}"')
        if self._surrounding == SURROUNDING_BROKEN:
            # flush() will reset the self._surrounding value.
            pass
        elif self._surrounding == SURROUNDING_RESET and original_len == 0:
            # We cannot tell yet if the application implements the surrounding text correctly.
            pass
        elif original_len < cursor_pos or original_len < anchor_pos:
            # Some applications, including GNOME 46 mutter, still report
            # cursor_pos and anchor_pos in byte offsets, and are basically
            # broken.
            # See https://gitlab.gnome.org/GNOME/mutter/-/issues/3440
            if self._surrounding == SURROUNDING_SUPPORTED:
                self._surrounding = SURROUNDING_BROKEN
        else:
            self._surrounding = SURROUNDING_SUPPORTED
            self._preedit_text = None
        IBus.Engine.do_set_surrounding_text(self, text, cursor_pos, anchor_pos)


class EngineHiragana(EngineModeless):
    __gtype_name__ = 'EngineHiragana'

    def __init__(self, bus: IBus.Bus, object_path: str):
        props = {
            'connection': bus.get_connection(),
            'object_path': object_path
        }
        if hasattr(IBus.Engine.props, 'active_surrounding_text'):
            props['active_surrounding_text'] = True
        if hasattr(IBus.Engine.props, 'has_focus_id'):
            props['has_focus_id'] = True
        super().__init__(**props)

        self._mode = 'A'  # _mode must be one of _input_mode_names
        self._override = False
        self._caps_lock_state = None
        self._to_kana = self._handle_default_layout
        self._to_tiny = None
        self._shrunk = []
        self._completed = ''
        self._lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self._lookup_table.set_orientation(IBus.Orientation.VERTICAL)
        self._selected = False  # True if a candidate is selected by the user

        self._init_props()

        self._settings = Gio.Settings.new('org.freedesktop.ibus.engine.hiragana')
        self._settings_handler = 0

        # Note Gdk.Keymap does *not* work as expected in Wayland.
        self._keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
        self._keymap_handler = 0

        self._logging_level = self._load_logging_level()

        self._dict = self._load_dictionary()
        self._controller = KeyboardController(self._load_layout())

        self.set_mode(self._load_input_mode())
        self._set_x4063_mode(self._load_x4063_mode())
        self._set_combining_circumflex(self._load_combining_circumflex())
        self._set_combining_macron(self._load_combining_macron())

        self._use_half_width_digits = self._load_use_half_width_digits()

        self._use_llm = self._load_use_llm()
        self._assisted = 0
        self._ignored = {}

        self._about_dialog = None
        self._setup_proc = None
        self._q = queue.Queue()

        self._focus_id = ''

    def __del__(self):
        LOGGER.debug('EngineHiragana.__del__')
        self._disconnect_handlers()

    def _disconnect_handlers(self):
        if 0 < self._settings_handler:
            self._settings.disconnect(self._settings_handler)
            self._settings_handler = 0
        if 0 < self._keymap_handler:
            self._keymap.disconnect(self._keymap_handler)
            self._keymap_handler = 0

    def _assist(self, text, pos):
        if not self._use_llm:
            return 0
        cand = self._dict.cand()
        if len(cand) <= 1:
            return 0

        yomi = self._dict.reading()

        LOGGER.debug(f'_assist("{text}", {pos}): {yomi}')

        prefix = get_plain_text(text[:pos - len(yomi)])
        if prefix == '':
            return 0

        yougen, yougen_shrunk, yougen_yomi = self._dict.lookup_yougen()
        LOGGER.debug(f'_assist: {yougen}, {yougen_shrunk}, {yougen_yomi}')

        self._assisted = llm.pick(prefix, cand, yougen, yougen_shrunk, yougen_yomi)
        LOGGER.debug(f'_assist: "{cand[self._assisted]}"/"{yomi}" ({self._assisted})')
        yomi, assisted = self._dict.get_stem(self._assisted)
        if assisted in self._ignored.get(yomi, set()):
            LOGGER.debug(f'_assist: ignore "{cand[self._assisted]}", use "{cand[0]}"')
            return 0
        return self._assisted

    def _confirm_candidate(self):
        current = self._dict.current()
        if current:
            if not self._dict.is_pseudo_candidate():
                yomi, assisted = self._dict.get_stem(self._assisted)
                LOGGER.debug(f'_confirm_candidate: current: "{current}", assisted: {yomi} /{assisted}/')
                no = self._dict.confirm(''.join(self._shrunk))
                if no == self._assisted:
                    LOGGER.debug(f'_confirm_candidate: restore {yomi} /{assisted}/')
                    if yomi in self._ignored:
                        self._ignored[yomi].discard(assisted)
                elif self._assisted < len(self._dict.cand()):
                    LOGGER.debug(f'_confirm_candidate: ignore {yomi} /{assisted}/')
                    if yomi in self._ignored:
                        self._ignored[yomi].add(assisted)
                    else:
                        self._ignored[yomi] = {assisted}
            self._dict.reset()
            self._lookup_table.clear()
        return current

    def _handle_default_layout(self, preedit, c, e: Event):
        return c, ''

    def _handle_kana_layout(self, preedit, c, e: Event):
        kana = self._controller.kana(e)
        yomi = kana if kana else c
        return yomi, preedit

    def _handle_roomazi_layout(self, preedit, c, e: Event):
        yomi = ''
        post = ''
        c = c.lower()
        if c in 'âîûêôÂÎÛÊÔ':
            c = c.translate(FROM_CIRCUMFLEX)
            post = 'ー'
        elif c in 'āīūēōĀĪŪĒŌ':
            c = c.translate(FROM_MACRON)
            post = 'ー'
        if preedit == 'n' and self.character_after_n.find(c) < 0:
            yomi = 'ん'
            preedit = preedit[1:]
        preedit += c
        kana = self._controller.transliterate_back(preedit)
        if kana:
            yomi += kana + post
            if yomi == 'ー':
                text, pos = self.get_surrounding_string()
                if pos <= 0 or text[pos - 1] not in (HIRAGANA + KATAKANA):
                    yomi = '－'
            preedit = ''
        elif 2 <= len(preedit) and preedit[0] == preedit[1] and preedit[1] in SOKUON:
            yomi += 'っ'
            preedit = preedit[1:]
        elif preedit == c and c not in 'abcdefghijklmnopqrstuvwxyz':
            yomi += c
            preedit = ''
        return yomi, preedit

    def _init_input_mode_props(self):
        props = IBus.PropList()
        for key, label in INPUT_MODES:
            prop = IBus.Property(key=key, prop_type=IBus.PropType.RADIO, label=IBus.Text.new_from_string(label))
            props.append(prop)
        return props

    def _init_props(self):
        self._prop_list = IBus.PropList()
        self._input_mode_prop = IBus.Property(
            key='InputMode',
            prop_type=IBus.PropType.MENU,
            symbol=IBus.Text.new_from_string(self._mode),
            label=IBus.Text.new_from_string(_('Input mode (%s)') % self._mode))
        self._input_mode_prop.set_sub_props(self._init_input_mode_props())
        self._prop_list.append(self._input_mode_prop)
        prop = IBus.Property(key='Setup', label=IBus.Text.new_from_string(_('Setup')))
        self._prop_list.append(prop)
        prop = IBus.Property(key='Help', label=IBus.Text.new_from_string(_('Help')))
        self._prop_list.append(prop)
        prop = IBus.Property(key='About', label=IBus.Text.new_from_string(_('About Hiragana IME...')))
        self._prop_list.append(prop)

    def _is_tiny(self, c):
        return c == self._to_tiny

    def _load_combining_circumflex(self) -> bool:
        mode = self._settings.get_boolean('combining-circumflex')
        LOGGER.debug(f'combining-circumflex: {mode}')
        return mode

    def _load_combining_macron(self) -> bool:
        mode = self._settings.get_boolean('combining-macron')
        LOGGER.debug(f'combining-macron: {mode}')
        return mode

    def _load_dictionary(self, clear_history=False):
        permissible = self._settings.get_boolean('permissible')
        system = self._settings.get_string('dictionary')
        slash = system.rfind('/')
        if 0 <= slash:
            # for v0.15.0 or earlier
            system = system[slash + 1:]
            if system == 'restrained.dic':
                system = 'restrained.8.dic'
        user = self._settings.get_string('user-dictionary')
        dict = Dictionary(system, user, clear_history, permissible)
        dict.use_romazi(self._to_kana != self._handle_kana_layout)
        return dict

    def _load_input_mode(self):
        mode = self._settings.get_string('mode')
        if mode not in INPUT_MODE_NAMES:
            mode = 'A'
            self._settings.reset('mode')
        LOGGER.debug(f'input mode: {mode}')
        return mode

    def _load_json(self, pathname):
        LOGGER.debug(f'_load_json("{pathname}")')
        layout = {}
        try:
            with open(pathname) as f:
                layout = json.load(f)
        except OSError:
            LOGGER.exception(f'could not load "{pathname}"')
        return layout

    def _load_layout(self):
        input_sources = Gio.Settings.new('org.gnome.desktop.input-sources')
        mru_sources = input_sources.get_value('mru-sources')
        xkb_layout = 'us'
        for i in range(mru_sources.n_children()):
            v = mru_sources.get_child_value(i)
            assert v.n_children() == 2
            source_type = v.get_child_value(0).get_string()
            source_name = v.get_child_value(1).get_string()
            if source_type == 'xkb':
                xkb_layout = source_name
                break
        LOGGER.info(f'xkb layout: {xkb_layout}')
        if xkb_layout in ('us', 'jp'):
            default_layout = os.path.join(package.get_datadir(), 'layouts', 'roomazi.' + xkb_layout + '.json')
        else:
            default_layout = os.path.join(package.get_datadir(), 'layouts', 'roomazi.' + 'us' + '.json')
        path = package.load_from_data_dirs(
            os.path.join('layouts', self._settings.get_string('layout') + '.' + xkb_layout + '.json'))
        LOGGER.info(f'keyboard layout: "{path}"')
        layout = self._load_json(path)
        if not layout:
            layout = self._load_json(default_layout)
        path = package.load_from_data_dirs(
            os.path.join('layouts', self._settings.get_string('altgr') + '.' + xkb_layout + '.json'))
        altgr = self._load_json(path)
        if altgr:
            layout.update(altgr)
        if layout.get('Type') == 'Kana':
            self._to_kana = self._handle_kana_layout
            self._dict.use_romazi(False)
        elif 'Roomazi' in layout:
            self._to_kana = self._handle_roomazi_layout
            self._dict.use_romazi(True)
        else:
            self._to_kana = self._handle_default_layout
            self._dict.use_romazi(True)
        self._to_tiny = layout.get('Tiny')
        return layout

    def _load_logging_level(self):
        level = self._settings.get_string('logging-level')
        if level not in NAME_TO_LOGGING_LEVEL:
            level = 'WARNING'
            self._settings.reset('logging-level')
        LOGGER.info(f'logging-level: {level}')
        logging.getLogger().setLevel(NAME_TO_LOGGING_LEVEL[level])
        return level

    def _load_x4063_mode(self):
        mode = self._settings.get_boolean('nn-as-jis-x-4063')
        LOGGER.info(f'nn-as-jis-x-4063: {mode}')
        return mode

    def _load_use_half_width_digits(self):
        enabled = self._settings.get_boolean('use-half-width-digits')
        LOGGER.info(f'use-half-width-digits: {enabled}')
        return enabled

    def _load_use_llm(self):
        enabled = self._settings.get_boolean('use-llm')
        LOGGER.info(f'use-llm: {enabled}')
        llm.load(enabled)
        return enabled

    def _lookup_dictionary(self, text, pos, anchor=0):
        self._lookup_table.clear()
        cand = self._dict.lookup(text, pos, anchor)
        size = len(self._dict.reading())
        self._selected = False
        self._assisted = 0
        # Note if the current conversion is complete, it is automatically confirmed.
        # No LLM assistance is necessary in this case.
        if 0 < size and 1 < len(self._dict.cand()) and not self._dict.is_complete():
            for i, c in enumerate(self._dict.cand()):
                self._lookup_table.append_candidate(IBus.Text.new_from_string(c))
                self._lookup_table.set_label(i, IBus.Text.new_from_string(' '))
            cursor_pos = self._assist(text, pos)
            if 0 < cursor_pos:
                self._lookup_table.set_cursor_pos(cursor_pos)
                self._update_candidate()
        return cand, size

    def _process_dakuten(self, c):
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
        elif self._is_tiny(self.roman_text):
            found = NON_TINY.find(text[pos - 1])
            if 0 <= found:
                self.roman_text = ''
                self.delete_surrounding_string(1)
                c = TINY[found]
        return c

    def _process_escape(self):
        assert self._dict.current()
        self.clear_roman()
        yomi = self._dict.reading()
        self._reset(False)
        yomi = yomi.replace('―', '')
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
        LOGGER.debug(f'_process_okurigana: "{text[:pos_yougen]}:{text[pos_yougen:pos]}", "{self.roman_text}"')
        if text[-1] != '―':
            cand, size = self._lookup_dictionary(text, pos, pos_yougen)
        if not self._dict.current():
            cand = text[pos_yougen:pos]
            size = len(cand)
            self._dict.create_pseudo_candidate(cand)
        assert self._dict.current()
        self.delete_surrounding_string(size)
        return True

    def _process_replace(self, e: Event) -> bool:
        LOGGER.debug(f'_process_replace(): _completed="{self._completed}"')
        if self._dict.current():
            return True
        # Check 'n'
        if self.roman_text == 'n':
            committed_n = True
            self.commit_n()
        else:
            committed_n = False
        text, pos = self.get_surrounding_string()
        # Check Return for yôgen conversion
        if e.is_henkan() or e.is_key(IBus.Return):
            cand, size = self._lookup_dictionary(text, pos)
        elif 1 <= pos:
            assert e.is_muhenkan()
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
            if self._completed:
                # 直前の変換のおくりがなの部分をスキップするようする。
                plain = get_plain_text(text[:pos])
                completed_pos = plain.rfind(self._completed)
                if 0 <= completed_pos:
                    max_size = len(plain) - completed_pos - len(self._completed)
                    while max_size < size:
                        self._process_shrink()
                        current = self._dict.current()
                        if cand == current:
                            break
                        LOGGER.debug(f'auto shrink: from "{cand}" to "{current}"')
                        cand = current
                        size = len(self._dict.reading())
        elif not committed_n:
            # Commit a white space
            self.commit_string(' ' if e.is_muhenkan() or self.get_mode() == 'ｱ' else '　')
        return True

    def _process_shrink(self):
        LOGGER.debug(f'_process_shrink: "{self._dict.current()}"')
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

    def _process_surrounding_text(self, e: Event) -> bool:
        if self._dict.current():
            if e.keyval == IBus.Tab:
                if not e.is_shift():
                    return self._process_shrink()
                else:
                    return self._process_expand()
            if e.keyval == IBus.Escape:
                self._process_escape()
                return True
            if e.keyval == IBus.Return:
                if self._dict.is_pseudo_candidate():
                    self._process_escape()
                    return True
                current = self._confirm_candidate()
                self.commit_string(current)
                if current[-1] == '―':
                    return self._process_replace(e)
                else:
                    if not self.commit_roman():
                        self._set_completed(current)
                    self.flush()
                    return True

        if e.keyval == IBus.Return and self.commit_roman():
            return True
        if e.keyval == IBus.Escape and self.clear_roman():
            return True

        if (self.get_mode() == 'あ'
                and (e.is_henkan() or e.is_muhenkan())
                and not e.has_altgr()):
            return self._process_replace(e)

        text, pos = self.get_surrounding_string()
        pos_yougen = -1
        to_revert = False
        current = self._dict.current()
        if current:
            # Commit the current candidate
            yomi = self._dict.reading()
            self._confirm_candidate()
            self.commit_string(current)
            LOGGER.debug(f'current: "{current}", yomi: "{yomi}", roman: "{self.roman_text}"')
            if current[-1] == '―':
                pos_yougen = pos
            elif current[-1] in OKURIGANA or yomi[-1] == '―' or self.roman_text:
                if not self._selected:
                    pos_yougen = pos
                    to_revert = True
                    current = yomi
                else:
                    self._set_completed(current)
                    if self.should_draw_preedit():
                        self.flush()
            elif self.should_draw_preedit():
                self.flush()

        if e.is_katakana():
            self._process_katakana()
            return True
        if e.is_backspace():
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
        c = e.get_string()
        if e.has_altgr():
            if not c:
                self.clear_roman()
                return True
            if c not in 'âîûêôÂÎÛÊÔ':
                yomi = c
        if c:
            if yomi:
                pass
            elif self.get_mode() == 'A':
                text, pos = self.get_surrounding_string()
                if self.combining_circumflex and 0 < pos and c == '^':
                    if text[pos - 1] in 'aiueoAIUEO':
                        yomi = text[pos - 1].translate(TO_CIRCUMFLEX)
                        self.delete_surrounding_string(1)
                    elif text[pos - 1] in 'âîûêôÂÎÛÊÔ':
                        yomi = text[pos - 1].translate(FROM_CIRCUMFLEX) + c
                        self.delete_surrounding_string(1)
                    else:
                        return False
                elif self.combining_macron and 0 < pos and c == '~':
                    if text[pos - 1] in 'aiueoAIUEO':
                        yomi = text[pos - 1].translate(TO_MACRON)
                        self.delete_surrounding_string(1)
                    elif text[pos - 1] in 'āīūēōĀĪŪĒŌ':
                        yomi = text[pos - 1].translate(FROM_MACRON) + c
                        self.delete_surrounding_string(1)
                    else:
                        return False
                else:
                    if chr(e.keyval) == c:
                        return False
                    yomi = c
            elif self.get_mode() == 'Ａ':
                yomi = to_zenkaku(c)
            else:
                yomi, self.roman_text = self._to_kana(self.roman_text, c, e)
                if yomi:
                    if self.get_mode() == 'ア':
                        yomi = to_katakana(yomi)
                    elif self.get_mode() == 'ｱ':
                        yomi = to_hankaku(to_katakana(yomi))
                    if self._use_half_width_digits:
                        text, pos = self.get_surrounding_string()
                        if 0 < pos and text[pos - 1] in HANKAKU_DIGIT:
                            yomi = to_hankaku_digit_extra(yomi)
                        else:
                            yomi = to_hankaku_digit(yomi)

        elif e.is_prefix():
            pass
        elif self.has_non_empty_preedit() and self.should_draw_preedit():
            if e.keyval == IBus.Escape:
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
                if current[-1] in HIRAGANA:
                    self._set_completed(current[:-1])
        return True

    def _reset(self, full=True):
        self._dict.reset()
        self._lookup_table.clear()
        self._update_lookup_table()
        self._completed = ''
        if full:
            self.clear()
        self._update_preedit()
        assert not self._dict.current()
        self._setup_sync()

    def _set_combining_circumflex(self, mode):
        self.combining_circumflex = mode
        LOGGER.debug(f'_set_combining_circumflex({mode})')

    def _set_combining_macron(self, mode):
        self.combining_macron = mode
        LOGGER.debug(f'_set_combining_macron({mode})')

    def _set_completed(self, cand):
        LOGGER.debug(f'_set_completed("{cand}")')
        if cand[-1] in HIRAGANA:
            self._completed = cand
        else:
            self._completed = ''

    def _set_x4063_mode(self, on):
        if on:
            self.character_after_n = "aiueo'wyn"
        else:
            self.character_after_n = "aiueo'wy"
        LOGGER.debug(f'_set_x4063_mode({on})')

    def _update_candidate(self):
        index = self._lookup_table.get_cursor_pos()
        self._dict.set_current(index)
        self._update_preedit()

    def _update_input_mode(self):
        self._input_mode_prop.set_symbol(IBus.Text.new_from_string(self._mode))
        self._input_mode_prop.set_label(IBus.Text.new_from_string(_('Input mode (%s)') % self._mode))
        self.update_property(self._input_mode_prop)

    def _update_input_mode_list(self):
        key = {
            'A': 'InputMode.Alphanumeric',
            'あ': 'InputMode.Hiragana',
            'ア': 'InputMode.Katakana',
            'Ａ': 'InputMode.WideAlphanumeric',
            'ｱ': 'InputMode.HalfWidthKatakana'
        }.get(self._mode, 'InputMode.Alphanumeric')
        prop_list = self._input_mode_prop.get_sub_props()
        for i in range(INPUT_MODE_COUNT):
            prop = prop_list.get(i)
            if prop.get_key() == key:
                prop.set_state(IBus.PropState.CHECKED)
            else:
                prop.set_state(IBus.PropState.UNCHECKED)
            self.update_property(prop)

    def _update_lookup_table(self):
        if self.is_enabled():
            visible = 0 < self._lookup_table.get_number_of_candidates()
            self.update_lookup_table(self._lookup_table, visible)

    def _update_preedit(self, locked=''):
        cand = self._dict.current()
        if self.has_non_empty_preedit() and self.should_draw_preedit():
            preedit_text = self._preedit_text
        else:
            preedit_text = ''
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
            attrs.append(IBus.Attribute.new(IBus.AttrType.FOREGROUND, PREFIX_LOCK_COLOR, pos, pos + locked_len))
            pos += preedit_len
        if attrs:
            text.set_attributes(attrs)

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
                self._setup_proc.stdin.write('present\n')
                self._setup_proc.stdin.flush()
                return
            self._setup_proc = None
        try:
            filename = os.path.join(package.get_libexecdir(), 'ibus-setup-hiragana')
            self._setup_proc = subprocess.Popen([filename], text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            t = threading.Thread(target=self._setup_readline, args=(self._setup_proc,), daemon=True)
            t.start()
        except (OSError, ValueError):
            LOGGER.exception('_setup_start')

    def _setup_sync(self):
        last = ''
        while True:
            try:
                line = self._q.get_nowait()
                if line == last:
                    continue
                last = line
                LOGGER.info(f'_setup_sync: {line}')
                if line == 'reload_dictionaries':
                    self._dict = self._load_dictionary()
                elif line == 'clear_input_history':
                    self._dict = self._load_dictionary(clear_history=True)
                    self._ignored = {}
            except queue.Empty:
                break

    #
    # callback methods
    #
    def _about_response_cb(self, dialog, response):
        dialog.destroy()
        self._about_dialog = None

    def _config_value_changed_cb(self, settings, key):
        LOGGER.debug(f'config_value_changed("{key}")')
        if key == 'logging-level':
            self._logging_level = self._load_logging_level()
        elif key == 'layout' or key == 'altgr':
            self._reset()
            self._controller = KeyboardController(self._load_layout())
        elif key in ('dictionary', 'user-dictionary', 'permissible'):
            self._reset()
            self._dict = self._load_dictionary()
        elif key == 'mode':
            mode = self._load_input_mode()
            if mode != self.get_mode():
                self.set_mode(mode, True)
        elif key == 'nn-as-jis-x-4063':
            self._set_x4063_mode(self._load_x4063_mode())
        elif key == 'combining-circumflex':
            self._set_combining_circumflex(self._load_combining_circumflex())
        elif key == 'combining-macron':
            self._set_combining_macron(self._load_combining_macron())
        elif key == 'use-half-width-digits':
            self._use_half_width_digits = self._load_use_half_width_digits()
        elif key == 'use-llm':
            self._use_llm = self._load_use_llm()

    def _keymap_state_changed_cb(self, keymap):
        if self._controller.is_onoff_by_caps():
            lock = keymap.get_caps_lock_state()
            if self._caps_lock_state != lock:
                LOGGER.debug(f'_keymap_state_changed_cb: {keymap.get_caps_lock_state()}')
                self._caps_lock_state = lock
                if lock:
                    self.enable_ime()
                else:
                    self.disable_ime()
        return True

    #
    # public methods
    #
    def disable_ime(self, override=False):
        LOGGER.debug(f'disable_ime({override})')
        if self.is_enabled():
            self.set_mode('A', override)
            return True
        return False

    def enable_ime(self, override=False):
        LOGGER.debug(f'enable_ime({override})')
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

    def process_key_event(self, e: Event) -> bool:
        if e.is_dual_role():
            pass
        elif e.is_modifier():
            # Ignore modifier keys
            return False
        elif e.state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK):
            self.clear_roman()
            self.flush(self._confirm_candidate())
            self._update_preedit()
            return False

        # Handle candidate window
        if 0 < self._lookup_table.get_number_of_candidates():
            if e.keyval in (IBus.Page_Up, IBus.KP_Page_Up):
                return self.do_page_up()
            elif e.keyval in (IBus.Page_Down, IBus.KP_Page_Down):
                return self.do_page_down()
            elif e.keyval == IBus.Up or e.is_muhenkan():
                return self.do_cursor_up()
            elif e.keyval == IBus.Down or e.is_henkan():
                return self.do_cursor_down()

        if e.is_backspace():
            if e.is_prefixed():
                # Clear the indication of the prefixed lock.
                self._update_preedit()
                return True
            if self.roman_text:
                self.backspace()
                self._update_preedit()
                return True

        # Cache the current surrounding text into the EngineModless's local buffer.
        self.get_surrounding_string()
        # Edit the local surrounding text buffer as we need.
        result = self._process_surrounding_text(e)
        # Flush the local surrounding text buffer into the IBus client.
        if self.get_mode() != 'あ':
            self.flush(force=True)
        elif self._surrounding in (SURROUNDING_COMMITTED, SURROUNDING_SUPPORTED):
            self.flush()

        # Lastly, update the preedit text. To support LibreOffice, the
        # surrounding text needs to be updated before updating the preedit text.
        if e.is_prefix():
            self._update_preedit('＿' if e.is_prefixed() else '')
        else:
            self._update_preedit()
        return result

    def set_mode(self, mode, override=False, update_list=True) -> None:
        LOGGER.debug(f'set_mode({mode}, {override}, {update_list}): {self._mode}')
        self._override = override
        if self._mode != mode:
            self.clear_roman()
            self.flush(self._confirm_candidate())
            self._update_preedit()
            self._mode = mode
            self._update_lookup_table()
            self._update_input_mode()
            self._settings.set_string('mode', mode)
            if update_list:
                self._update_input_mode_list()

    #
    # virtual methods of IBus.Engine
    #
    def do_candidate_clicked(self, index: int, button: int, state: int) -> None:
        LOGGER.debug(f'do_candidate_clicked({index}, {button}, {state})')
        if button != 1 or not self._dict.current():
            return
        cursor_pos = self._lookup_table.get_cursor_pos()
        page_size = self._lookup_table.get_page_size()
        base = cursor_pos - (cursor_pos % page_size)
        if page_size <= index:
            cursor_pos = index
        else:
            cursor_pos = base + index
        self._lookup_table.set_cursor_pos(cursor_pos)
        self._dict.set_current(cursor_pos)

        current = self._confirm_candidate()
        self.commit_string(current)
        if current[-1] == '―':
            self._process_replace(self._controller.create_event(IBus.VoidSymbol, 0, 0, 0))
            if self._surrounding in (SURROUNDING_COMMITTED, SURROUNDING_SUPPORTED):
                self.flush()
        else:
            if not self.commit_roman():
                self._set_completed(current)
            self.flush()
        self._update_preedit()

    def do_cursor_down(self) -> bool:
        self._selected = True
        if self._lookup_table.cursor_down():
            self._update_candidate()
        return True

    def do_cursor_up(self) -> bool:
        self._selected = True
        if self._lookup_table.cursor_up():
            self._update_candidate()
        return True

    def do_disable(self) -> None:
        LOGGER.debug('do_disable()')
        self._reset()
        self._mode = 'A'
        self._dict.save_orders()
        self._disconnect_handlers()

    def do_enable(self) -> None:
        super().do_enable()
        self._caps_lock_state = None
        self._keymap_state_changed_cb(self._keymap)
        self._keymap_handler = self._keymap.connect('state-changed', self._keymap_state_changed_cb)
        self._settings_handler = self._settings.connect('changed', self._config_value_changed_cb)

    def do_focus_in(self) -> None:
        self.do_focus_in_id('', '')

    def do_focus_in_id(self, object_path: str, client: str) -> None:
        LOGGER.debug(f'do_focus_in_id("{object_path}", "{client}"): {self._surrounding}')
        if client == 'fake':
            return
        if self._focus_id != object_path:
            if self._surrounding == SURROUNDING_BROKEN:
                self._reset()
                self._dict.save_orders()
        self._focus_id = object_path
        self._controller.reset()
        self.register_properties(self._prop_list)
        self._update_preedit()
        super().do_focus_in_id(object_path, client)

    def do_focus_out(self) -> None:
        self.do_focus_out_id('')

    def do_focus_out_id(self, object_path: str):
        LOGGER.debug(f'do_focus_out_id("{object_path}"): {self._surrounding}')
        if self._surrounding != SURROUNDING_BROKEN:
            self._reset()
            self._dict.save_orders()

    def do_page_down(self) -> bool:
        self._selected = True
        if self._lookup_table.page_down():
            self._update_candidate()
        return True

    def do_page_up(self) -> bool:
        self._selected = True
        if self._lookup_table.page_up():
            self._update_candidate()
        return True

    # Note IBus.ModifierType.LOCK_MASK bit is always off with the text boxes
    # inside GNOME Shell on X11. This issue is fixed with Wayland.
    def do_process_key_event(self, keyval: int, keycode: int, state: int) -> bool:
        LOGGER.debug(f'do_process_key_event({keyval:#04x}({IBus.keyval_name(keyval)}), '
                     f'{keycode}, {state:#010x}({prettify_state(state)}))')
        if keyval == IBus.Super_L or (state & IBus.ModifierType.MOD4_MASK):
            return False
        if not (state & IBus.ModifierType.RELEASE_MASK):
            self.check_surrounding_support()
        return self._controller.process_key_event(self, keyval, keycode, state)

    def do_property_activate(self, prop_name: str, state: int) -> None:
        LOGGER.debug(f'property_activate({prop_name}, {state})')
        if prop_name == 'Setup':
            self._setup_start()
        elif prop_name == 'Help':
            lang = _('en')
            if lang == 'ja':
                lang = ''
            url = 'file://' + os.path.join(package.get_datadir(), 'docs', lang, 'index.html')
            LOGGER.debug(f'{url}')
            # Use yelp to open local HTML help files.
            subprocess.Popen(['yelp', url])
        elif prop_name == 'About':
            if self._about_dialog:
                self._about_dialog.present()
                return
            dialog = Gtk.AboutDialog()
            dialog.set_program_name(_('Hiragana IME'))
            dialog.set_copyright('Copyright 2017-2024 Esrille Inc.')
            dialog.set_authors(['Esrille Inc.'])
            dialog.set_documenters(['Esrille Inc.'])
            dialog.set_website('https://www.esrille.com/')
            dialog.set_website_label('Esrille Inc.')
            dialog.set_logo_icon_name(package.get_name())
            dialog.set_default_icon_name(package.get_name())
            dialog.set_version(package.get_version())
            # To close the dialog when "close" is clicked on Raspberry Pi OS,
            # we connect the "response" signal to _about_response_cb
            dialog.connect('response', self._about_response_cb)
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
                self.set_mode(mode, override=True, update_list=False)

    def do_reset(self) -> None:
        LOGGER.debug(f'reset: {self._surrounding}')
        if self._surrounding != SURROUNDING_BROKEN:
            self._reset()
        else:
            self._update_preedit()

    def do_set_cursor_location(self, x: int, y: int, w: int, h: int) -> None:
        # On Raspbian, at least till Buster, the candidate window does not
        # always follow the cursor position. The following code is not
        # necessary on Ubuntu 18.04 or Fedora 30.
        LOGGER.debug(f'do_set_cursor_location({x}, {y}, {w}, {h})')
        self._update_lookup_table()
        EngineModeless.do_set_cursor_location(self, x, y, w, h)
