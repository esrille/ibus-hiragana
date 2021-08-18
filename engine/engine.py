# ibus-hiragana - Hiragana IME for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2017-2021 Esrille Inc.
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
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, IBus

keysyms = IBus

logger = logging.getLogger(__name__)

_ = lambda a: gettext.dgettext(package.get_name(), a)

HIRAGANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゎゐゑ・ーゝゞ"
KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヮヰヱ・ーヽヾ"

TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)

NON_DAKU = 'あいうえおかきくけこさしすせそたちつてとはひふへほやゆよアイウエオカキクケコサシスセソタチツテトハヒフヘホヤユヨぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョゔヴゝヽゞヾ'
DAKU = 'ぁぃぅぇぉがぎぐげござじずぜぞだぢづでどばびぶべぼゃゅょァィゥェォガギグゲゴザジズゼゾダヂヅデドバビブベボャュョあいゔえおかきくけこさしすせそたちつてとはひふへほやゆよアイヴエオカキクケコサシスセソタチツテトハヒフヘホヤユヨうウゞヾゝヽ'

NON_HANDAKU = 'はひふへほハヒフヘホぱぴぷぺぽパピプペポ'
HANDAKU = 'ぱぴぷぺぽパピプペポはひふへほハヒフヘホ'

ZENKAKU = ''.join(chr(i) for i in range(0xff01, 0xff5f)) + '　￥'
HANKAKU = ''.join(chr(i) for i in range(0x21, 0x7f)) + ' ¥'

TO_HANDAKU = str.maketrans(ZENKAKU, HANKAKU)
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


def to_katakana(kana):
    return kana.translate(TO_KATAKANA)


def to_hankaku(kana):
    str = ''
    for c in kana:
        c = c.translate(TO_HANDAKU)
        str += {
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
    return str


def to_zenkaku(asc):
    return asc.translate(TO_ZENKAKU)


class EngineHiragana(IBus.Engine):
    __gtype_name__ = 'EngineHiragana'

    def __init__(self):
        super().__init__()
        self._mode = 'A'  # _mode must be one of _input_mode_names
        self._override = False

        self._layout = dict()
        self._to_kana = self._handle_default_layout

        self._preedit_string = ''
        self._previous_text = ''
        self._ignore_surrounding_text = False

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

        self._shrunk = []

        self._acked = False
        self.connect('set-surrounding-text', self.set_surrounding_text_cb)
        self.connect('set-cursor-location', self.set_cursor_location_cb)

        self._about_dialog = None
        self._setup_proc = None
        self._q = queue.Queue()

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

    def _update_input_mode(self):
        self._input_mode_prop.set_symbol(IBus.Text.new_from_string(self._mode))
        self._input_mode_prop.set_label(IBus.Text.new_from_string(_("Input mode (%s)") % self._mode))
        self.update_property(self._input_mode_prop)

    def _load_input_mode(self, settings):
        mode = settings.get_string('mode')
        if mode not in INPUT_MODE_NAMES:
            mode = 'A'
            settings.reset('mode')
        logger.info(f'input mode: {mode}')
        return mode

    def _load_logging_level(self, settings):
        level = settings.get_string('logging-level')
        if not level in NAME_TO_LOGGING_LEVEL:
            level = 'WARNING'
            settings.reset('logging-level')
        logger.info(f'logging_level: {level}')
        logging.getLogger().setLevel(NAME_TO_LOGGING_LEVEL[level])
        return level

    def _load_dictionary(self, settings, clear_history=False):
        path = settings.get_string('dictionary')
        user = settings.get_string('user-dictionary')
        return Dictionary(path, user, clear_history)

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
        elif 'Roomazi' in layout:
            self._to_kana = self._handle_roomazi_layout
        else:
            self._to_kana = self._handle_default_layout
        return layout

    def _load_delay(self, settings):
        delay = settings.get_int('delay')
        logger.info(f'delay: {delay}')
        return delay

    def _load_x4063_mode(self, settings):
        mode = settings.get_boolean('nn-as-jis-x-4063')
        logger.info(f'nn_as_jis_x_4063 mode: {mode}')
        return mode

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

    def _handle_default_layout(self, preedit, keyval, state=0, modifiers=0):
        return self._event.chr(), ''

    def _handle_kana_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        c = self._event.chr().lower()
        if c == '_' and self._event._keycode == 0x59:
            c = '¦'
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

    def _set_x4063_mode(self, on):
        if on:
            self.character_after_n = "aiueo'wyn"
        else:
            self.character_after_n = "aiueo'wy"
        logger.debug(f'set_x4063_mode({on})')

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

    def _get_surrounding_text(self):
        if not (self.client_capabilities & IBus.Capabilite.SURROUNDING_TEXT):
            self._ignore_surrounding_text = True
        if self._ignore_surrounding_text or not self._acked:
            logger.debug(f'surrounding text: "{self._previous_text}"')
            return self._previous_text, len(self._previous_text)

        tuple = self.get_surrounding_text()
        text = tuple[0].get_text()
        pos = tuple[1]

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

        # Qt seems to insert self._preedit_string to the text, while GTK doesn't.
        # We mimic GTK's behavior here.
        preedit_len = len(self._preedit_string)
        if 0 < preedit_len and preedit_len <= pos and text[pos - preedit_len:pos] == self._preedit_string:
            text = text[:-preedit_len]
            pos -= preedit_len
        logger.debug(f'surrounding text: "{text}", {pos}, "{self._previous_text}"')
        return text, pos

    def _delete_surrounding_text(self, size):
        self._previous_text = self._previous_text[:-size]
        if not self._ignore_surrounding_text and self._acked:
            self.delete_surrounding_text(-size, size)
        else:
            # Note a short delay after each BackSpace is necessary for the target application to catch up.
            for i in range(size):
                self.forward_key_event(IBus.BackSpace, 14, 0)
                time.sleep(0.02)
            self.forward_key_event(IBus.BackSpace, 14, IBus.ModifierType.RELEASE_MASK)

    def is_overridden(self):
        return self._override

    def is_enabled(self):
        return self.get_mode() != 'A'

    def enable_ime(self, override=False):
        if not self.is_enabled():
            self.set_mode('あ', override)
            return True
        return False

    def disable_ime(self, override=False):
        if self.is_enabled():
            self.set_mode('A', override)
            return True
        return False

    def get_mode(self):
        return self._mode

    def set_mode(self, mode, override=False):
        self._override = override
        if self._mode == mode:
            return False
        logger.debug(f'set_mode({mode})')
        self._preedit_string = ''
        self._commit()
        self._mode = mode
        self._update_roomazi_preedit()
        self._update_lookup_table()
        self._update_input_mode()
        return True

    def _is_roomazi_mode(self):
        return self._to_kana == self._handle_roomazi_layout

    def do_process_key_event(self, keyval, keycode, state):
        return self._event.process_key_event(keyval, keycode, state)

    def handle_alt_graph(self, keyval, keycode, state, modifiers):
        logger.debug(f'handle_alt_graph("{self._event.chr()}")')
        c = self._event.chr().lower()
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

    def handle_key_event(self, keyval, keycode, state, modifiers):
        logger.debug(f'handle_key_event("{IBus.keyval_name(keyval)}", {keyval:#04x}, {keycode:#04x}, {state:#010x}, {modifiers:#07x})')

        if self._event.is_dual_role():
            pass
        elif self._event.is_modifier():
            # Ignore modifier keys
            return False
        elif state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK):
            self._commit()
            return False

        # Handle Candidate window
        if 0 < self._lookup_table.get_number_of_candidates():
            if keyval in (keysyms.Page_Up, keysyms.KP_Page_Up):
                return self.do_page_up()
            elif keyval in (keysyms.Page_Down, keysyms.KP_Page_Down):
                return self.do_page_down()
            elif keyval == keysyms.Up or self._event.is_muhenkan():
                return self.do_cursor_up()
            elif keyval == keysyms.Down or self._event.is_henkan():
                return self.do_cursor_down()

        if self._preedit_string:
            if keyval == keysyms.Return:
                if self._preedit_string == 'n':
                    self._preedit_string = 'ん'
                self._commit_string(self._preedit_string)
                self._preedit_string = ''
                self._update_roomazi_preedit()
                return True
            if keyval == keysyms.Escape:
                self._preedit_string = ''
                self._update_roomazi_preedit()
                return True

        if self._dict.current():
            if keyval == keysyms.Tab:
                if not self._event.is_shift():
                    return self.handle_shrink()
                else:
                    return self.handle_expand()
            if keyval == keysyms.Escape:
                return self.handle_escape()
            if keyval == keysyms.Return:
                self._commit()
                return True

        # Handle Japanese text
        if self._event.is_henkan() and not(modifiers & event.ALT_R_BIT):
            return self.handle_replace(keyval, state)
        self._commit()
        yomi = ''
        if self._event.is_katakana():
            self.handle_katakana()
            return True
        if self._event.is_backspace():
            if 1 <= len(self._preedit_string):
                self._preedit_string = self._preedit_string[:-1]
                self._update_roomazi_preedit()
                return True
            elif 0 < len(self._previous_text):
                self._previous_text = self._previous_text[:-1]
            return False
        if self._event.is_ascii():
            if modifiers & event.ALT_R_BIT:
                yomi = self.handle_alt_graph(keyval, keycode, state, modifiers)
                if yomi:
                    self._preedit_string = ''
            elif self.get_mode() == 'Ａ':
                yomi = to_zenkaku(self._event.chr())
            else:
                yomi, self._preedit_string = self._to_kana(self._preedit_string, keyval, state, modifiers)
        elif keyval == keysyms.hyphen:
            yomi = '―'
        else:
            self._previous_text = ''
            return False
        if yomi:
            if self.get_mode() == 'ア':
                yomi = to_katakana(yomi)
            elif self.get_mode() == 'ｱ':
                yomi = to_hankaku(to_katakana(yomi))
            self._commit_string(yomi)
        self._update_roomazi_preedit()
        return True

    def lookup_dictionary(self, yomi, pos):
        if self._preedit_string == 'n':
            yomi = yomi[:pos] + 'ん'
            pos += 1
        self._lookup_table.clear()
        cand = self._dict.lookup(yomi, pos)
        size = len(self._dict.reading())
        if 0 < size:
            if self._preedit_string == 'n':
                # For FuriganaPad, yomi has to be committed anyway.
                self._commit_string('ん')
            self._preedit_string = ''
            if 1 < len(self._dict.cand()):
                for c in self._dict.cand():
                    self._lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_katakana(self):
        text, pos = self._get_surrounding_text()
        if self._preedit_string == 'n':
            self._preedit_string = ''
            text = text[:pos] + 'ん'
            pos += 1
            self._commit_string('ん')
        for i in reversed(range(pos)):
            if 0 <= KATAKANA.find(text[i]):
                continue
            found = HIRAGANA.find(text[i])
            if 0 <= found:
                self._update_roomazi_preedit()
                self._delete_surrounding_text(pos - i)
                self._commit_string(KATAKANA[found] + text[i + 1:pos])
            break
        return True

    def handle_replace(self, keyval, state):
        if not self._dict.current():
            text, pos = self._get_surrounding_text()
            (cand, size) = self.lookup_dictionary(text, pos)
            if self._dict.current():
                self._shrunk = []
                self._update_roomazi_preedit()
                self._delete_surrounding_text(size)
                self._update_candidate_preedit(cand)
        else:
            if not self._event.is_shift():
                cand = self._dict.next()
            else:
                cand = self._dict.previous()
            self._update_candidate_preedit(cand)
        return True

    def handle_expand(self):
        assert self._dict.current()
        if not self._shrunk:
            return True
        kana = self._shrunk[-1]
        yomi = self._dict.reading()
        text, pos = self._get_surrounding_text()
        (cand, size) = self.lookup_dictionary(kana + yomi + text[pos:], len(kana + yomi))
        assert 0 < size
        self._delete_surrounding_text(len(kana))
        self._shrunk.pop(-1)
        self._update_candidate_preedit(cand)
        return True

    def handle_shrink(self):
        logger.debug(f'handle_shrink: "{self._dict.current()}"')
        assert self._dict.current()
        yomi = self._dict.reading()
        if len(yomi) <= 1 or yomi[1] == '―':
            return True
        text, pos = self._get_surrounding_text()
        (cand, size) = self.lookup_dictionary(yomi[1:] + text[pos:], len(yomi) - 1)
        kana = yomi
        if 0 < size:
            kana = kana[:-size]
            self._shrunk.append(kana)
            self._commit_string(kana)
        else:
            (cand, size) = self.lookup_dictionary(yomi + text[pos:], len(yomi))
        self._update_candidate_preedit(cand)
        return True

    def handle_escape(self):
        assert self._dict.current()
        yomi = self._dict.reading()
        self._reset(False)
        self._commit_string(yomi)
        return True

    def _commit(self):
        current = self._dict.current()
        if current:
            self._dict.confirm(''.join(self._shrunk))
            self._dict.reset()
            self._lookup_table.clear()
            self._update_candidate_preedit('')
            self._commit_string(current)
            self._previous_text = ''

    def _commit_string(self, text):
        if text == '゛':
            prev, pos = self._get_surrounding_text()
            if 0 < pos:
                found = NON_DAKU.find(prev[pos - 1])
                if 0 <= found:
                    self._delete_surrounding_text(1)
                    text = DAKU[found]
        elif text == '゜':
            prev, pos = self._get_surrounding_text()
            if 0 < pos:
                found = NON_HANDAKU.find(prev[pos - 1])
                if 0 <= found:
                    self._delete_surrounding_text(1)
                    text = HANDAKU[found]
        self._previous_text += text
        self.commit_text(IBus.Text.new_from_string(text))

    def _reset(self, full=True):
        self._dict.reset()
        self._lookup_table.clear()
        self._update_lookup_table()
        if full:
            self._acked = False
            self._previous_text = ''
            self._preedit_string = ''
            self._ignore_surrounding_text = False
        self._update_roomazi_preedit()

        assert not self._dict.current()
        self._handle_setup_proc()

    def _update_candidate(self):
        index = self._lookup_table.get_cursor_pos()
        self._dict.set_current(index)
        self._update_candidate_preedit(self._dict.current())

    def do_page_up(self):
        if self._lookup_table.page_up():
            self._update_candidate()
        return True

    def do_page_down(self):
        if self._lookup_table.page_down():
            self._update_candidate()
        return True

    def do_cursor_up(self):
        if self._lookup_table.cursor_up():
            self._update_candidate()
        return True

    def do_cursor_down(self):
        if self._lookup_table.cursor_down():
            self._update_candidate()
        return True

    def _update_roomazi_preedit(self):
        text = IBus.Text.new_from_string(self._preedit_string)
        preedit_len = len(self._preedit_string)
        if 0 < preedit_len:
            attrs = IBus.AttrList()
            attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE, IBus.AttrUnderline.SINGLE, 0, preedit_len))
            text.set_attributes(attrs)
        # Note self.hide_preedit_text() does not seem to work as expected with Kate.
        # cf. "Qt5 IBus input context does not implement hide_preedit_text()",
        #     https://bugreports.qt.io/browse/QTBUG-48412
        self.update_preedit_text(text, preedit_len, 0 < preedit_len)

    def _update_candidate_preedit(self, cand):
        assert len(self._preedit_string) == 0
        text = IBus.Text.new_from_string(cand)
        cand_len = len(cand)
        if 0 < cand_len:
            attrs = IBus.AttrList()
            attrs.append(IBus.Attribute.new(IBus.AttrType.FOREGROUND, CANDIDATE_FOREGROUND_COLOR, 0, cand_len))
            attrs.append(IBus.Attribute.new(IBus.AttrType.BACKGROUND, CANDIDATE_BACKGROUND_COLOR, 0, cand_len))
            text.set_attributes(attrs)
        # Note self.hide_preedit_text() does not seem to work as expected with Kate.
        # cf. "Qt5 IBus input context does not implement hide_preedit_text()",
        #     https://bugreports.qt.io/browse/QTBUG-48412
        self.update_preedit_text(text, cand_len, 0 < cand_len)
        self._update_lookup_table()

    def _update_lookup_table(self):
        if self.is_enabled():
            visible = 0 < self._lookup_table.get_number_of_candidates()
            self.update_lookup_table(self._lookup_table, visible)

    def is_lookup_table_visible(self):
        return 0 < self._lookup_table.get_number_of_candidates()

    def do_focus_in(self):
        logger.info('focus_in')
        self._event.reset()
        self.register_properties(self._prop_list)
        # Request the initial surrounding-text in addition to the "enable" handler.
        self.get_surrounding_text()

    def do_focus_out(self):
        logger.info('focus_out')
        self._reset()
        self._dict.save_orders()

    def do_enable(self):
        logger.info('enable')
        # Request the initial surrounding-text when enabled as documented.
        self.get_surrounding_text()

    def do_disable(self):
        logger.info('disable')
        self._reset()
        self._mode = 'A'
        self._dict.save_orders()

    def do_reset(self):
        logger.info('reset')
        self._reset()
        # Do not switch back to the Alphabet mode here; 'reset' should be
        # called when the text cursor is moved by a mouse click, etc.

    def _readline(self, process: subprocess.Popen):
        for line in iter(process.stdout.readline, ''):
            self._q.put(line.strip())
            if process.poll() is not None:
                return

    def _start_setup(self):
        if self._setup_proc:
            if self._setup_proc.poll() is None:
                return
            self._setup_proc = None
        try:
            filename = os.path.join(package.get_libexecdir(), 'ibus-setup-hiragana')
            self._setup_proc = subprocess.Popen([filename], text=True, stdout=subprocess.PIPE)
            t = threading.Thread(target=self._readline, args=(self._setup_proc,), daemon=True)
            t.start()
        except OSError as e:
            logger.error(e)
        except ValueError as e:
            logger.error(e)

    def _handle_setup_proc(self):
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

    def do_property_activate(self, prop_name, state):
        logger.info(f'property_activate({prop_name}, {state})')
        if prop_name == 'Setup':
            self._start_setup()
        elif prop_name == 'About':
            if self._about_dialog:
                self._about_dialog.present()
                return
            dialog = Gtk.AboutDialog()
            dialog.set_program_name(_("Hiragana IME"))
            dialog.set_copyright("Copyright 2017-2021 Esrille Inc.")
            dialog.set_authors(["Esrille Inc."])
            dialog.set_documenters(["Esrille Inc."])
            dialog.set_website("file://" + os.path.join(package.get_datadir(), "help/index.html"))
            dialog.set_website_label(_("Introduction to Hiragana IME"))
            dialog.set_logo_icon_name(package.get_name())
            dialog.set_default_icon_name(package.get_name())
            dialog.set_version(package.get_version())
            # To close the dialog when "close" is clicked, e.g. on RPi,
            # we connect the "response" signal to about_response_callback
            dialog.connect("response", self.about_response_callback)
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

    def about_response_callback(self, dialog, response):
        dialog.destroy()
        self._about_dialog = None

    def set_surrounding_text_cb(self, engine, text, cursor_pos, anchor_pos):
        self._acked = True
        text = self.get_plain_text(text.get_text())
        logger.debug(f'set_surrounding_text_cb("{text}", {cursor_pos}, {anchor_pos})')

    def get_plain_text(self, text):
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

    def set_cursor_location_cb(self, engine, x, y, w, h):
        # On Raspbian, at least till Buster, the candidate window does not
        # always follow the cursor position. The following code is not
        # necessary on Ubuntu 18.04 or Fedora 30.
        logger.debug(f'set_cursor_location_cb({x}, {y}, {w}, {h})')
        self._update_lookup_table()
