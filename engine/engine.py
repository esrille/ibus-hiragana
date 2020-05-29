# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2017-2020 Esrille Inc.
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

import bits
from dictionary import Dictionary
from event import Event
from i18n import _
import package

import json
import logging
import os
import re
import sys
import time

import gi
gi.require_version('IBus', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, IBus

keysyms = IBus

logger = logging.getLogger(__name__)

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


class EngineReplaceWithKanji(IBus.Engine):
    __gtype_name__ = 'EngineReplaceWithKanji'

    def __init__(self):
        super().__init__()
        self._mode = 'A'    # _mode must be one of _input_mode_names
        self._override = False

        self._layout = dict()
        self._to_kana = self._handle_roomazi_layout

        self._preedit_string = ''
        self._previous_text = ''
        self._ignore_surrounding_text = False

        self._lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self._lookup_table.set_orientation(IBus.Orientation.VERTICAL)

        self._init_props()

        self._config = IBus.Bus().get_config()
        self._config.connect('value-changed', self._config_value_changed_cb)

        self._logging_level = self._load_logging_level(self._config)
        self._dict = self._load_dictionary(self._config)
        self._layout = self._load_layout(self._config)
        self._delay = self._load_delay(self._config)
        self._event = Event(self, self._delay, self._layout)

        self.set_mode(self._load_input_mode(self._config))
        self._set_x4063_mode(self._load_x4063_mode(self._config))

        self._shrunk = ''

        self._committed = ''
        self._acked = True
        self.connect('set-surrounding-text', self.set_surrounding_text_cb)

        self.connect('set-cursor-location', self.set_cursor_location_cb)

    def _init_props(self):
        self._prop_list = IBus.PropList()
        self._input_mode_prop = IBus.Property(
            key='InputMode',
            prop_type=IBus.PropType.NORMAL,
            symbol=IBus.Text.new_from_string(self._mode),
            label=IBus.Text.new_from_string(_("Input mode (%s)") % self._mode),
            icon=None,
            tooltip=None,
            sensitive=False,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self._prop_list.append(self._input_mode_prop)
        self._about_prop = IBus.Property(
            key='About',
            prop_type=IBus.PropType.NORMAL,
            label=IBus.Text.new_from_string(_("About Hiragana IME...")),
            icon=None,
            tooltip=None,
            sensitive=True,
            visible=True,
            state=IBus.PropState.UNCHECKED,
            sub_props=None)
        self._prop_list.append(self._about_prop)

    def _update_input_mode(self):
        self._input_mode_prop.set_symbol(IBus.Text.new_from_string(self._mode))
        self._input_mode_prop.set_label(IBus.Text.new_from_string(_("Input mode (%s)") % self._mode))
        self.update_property(self._input_mode_prop)

    def _load_input_mode(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'mode')
        if var is None or var.get_type_string() != 's' or not var.get_string() in INPUT_MODE_NAMES:
            mode = 'A'
            if var:
                config.unset('engine/replace-with-kanji-python', 'mode')
        else:
            mode = var.get_string()
        logger.info("input mode: %s", mode)
        return mode

    def _load_logging_level(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'logging_level')
        if var is None or var.get_type_string() != 's' or not var.get_string() in NAME_TO_LOGGING_LEVEL:
            level = 'WARNING'
            if var:
                config.unset('engine/replace-with-kanji-python', 'logging_level')
        else:
            level = var.get_string()
        logger.info("logging_level: %s", level)
        logging.getLogger().setLevel(NAME_TO_LOGGING_LEVEL[level])
        return level

    def _load_dictionary(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'dictionary')
        if var is None or var.get_type_string() != 's':
            path = os.path.join(package.get_datadir(), 'restrained.dic')
            if var:
                config.unset('engine/replace-with-kanji-python', 'dictionary')
        else:
            path = var.get_string()
        return Dictionary(path)

    def _load_layout(self, config):
        default_layout = os.path.join(package.get_datadir(), 'layouts')
        default_layout = os.path.join(default_layout, 'roomazi.json')
        var = config.get_value('engine/replace-with-kanji-python', 'layout')
        if var is None:
            path = default_layout
        elif var.get_type_string() != 's':
            config.unset('engine/replace-with-kanji-python', 'layout')
            path = default_layout
        else:
            path = var.get_string()
        logger.info("layout: %s", path)
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
        else:
            self._to_kana = self._handle_roomazi_layout
        return layout

    def _load_delay(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'delay')
        if var is None or var.get_type_string() != 'i':
            delay = 0
            if var:
                config.unset('engine/replace-with-kanji-python', 'delay')
        else:
            delay = var.get_int32()
        logger.info("delay: %d", delay)
        return delay

    def _load_x4063_mode(self, config):
        var = config.get_value('engine/replace-with-kanji-python', 'nn_as_jis_x_4063')
        if var is None or var.get_type_string() != 'b':
            mode = True
            if var:
                config.unset('engine/replace-with-kanji-python', 'nn_as_jis_x_4063')
        else:
            mode = var.get_boolean()
        logger.info("nn_as_jis_x_4063 mode: {}".format(mode))
        return mode

    def _config_value_changed_cb(self, config, section, name, value):
        section = section.replace('_', '-')
        if section != 'engine/replace-with-kanji-python':
            return
        logger.debug("config_value_changed({}, {}, {})".format(section, name, value))
        if name == "logging_level":
            self._logging_level = self._load_logging_level(config)
        elif name == "delay":
            self._reset()
            self._delay = self._load_delay(config)
            self._event = Event(self, self._delay, self._layout)
        elif name == "layout":
            self._reset()
            self._layout = self._load_layout(config)
            self._event = Event(self, self._delay, self._layout)
        elif name == "dictionary":
            self._reset()
            self._dict = self._load_dictionary(config)
        elif name == "mode":
            self.set_mode(self._load_input_mode(self._config))
            self._override = True
        elif name == "nn_as_jis_x_4063":
            self._set_x4063_mode(self._load_x4063_mode(self._config))

    def _handle_kana_layout(self, preedit, keyval, state=0, modifiers=0):
        yomi = ''
        c = self._event.chr().lower()
        if preedit == '\\':
            preedit = ''
            if self._event.is_shift():
                if 'Shift' in self._layout:
                    yomi = self._layout['\\Shift'][c]
                elif modifiers & bits.ShiftL_Bit:
                    yomi = self._layout['\\ShiftL'][c]
                elif modifiers & bits.ShiftR_Bit:
                    yomi = self._layout['\\ShiftR'][c]
            else:
                yomi = self._layout['\\Normal'][c]
        else:
            if self._event.is_shift():
                if 'Shift' in self._layout:
                    yomi = self._layout['Shift'][c]
                elif modifiers & bits.ShiftL_Bit:
                    yomi = self._layout['ShiftL'][c]
                elif modifiers & bits.ShiftR_Bit:
                    yomi = self._layout['ShiftR'][c]
            else:
                yomi = self._layout['Normal'][c]
            if yomi == '\\':
                preedit += yomi
                yomi = ''
        return yomi, preedit

    def _set_x4063_mode(self, on):
        if on:
            self.character_after_n = "aiueo\'wyn"
        else:
            self.character_after_n = "aiueo\'wy"
        logger.debug("set_x4063_mode({})".format(on))

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
            if yomi == '\\':
                preedit = yomi
                yomi = ''
        elif 2 <= len(preedit) and preedit[0] == preedit[1] and RE_SOKUON.search(preedit[1]):
            yomi += 'っ'
            preedit = preedit[1:]
        return yomi, preedit

    def _get_surrounding_text(self):
        if not (self.client_capabilities & IBus.Capabilite.SURROUNDING_TEXT):
            self._ignore_surrounding_text = True
        if self._ignore_surrounding_text or not self._acked:
            logger.debug("surrounding text: [%s]" % (self._previous_text))
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
        logger.debug("surrounding text: '%s', %d, [%s]", text, pos, self._previous_text)
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

    def enable_ime(self):
        if not self.is_enabled():
            self.set_mode('あ')
            return True
        return False

    def disable_ime(self):
        if self.is_enabled():
            self.set_mode('A')
            return True
        return False

    def switch_zenkaku_hankaku(self):
        mode = self.get_mode()
        mode = {
            'A': 'Ａ',
            'Ａ': 'A',
            'ア': 'ｱ',
            'ｱ': 'ア',
            'あ': 'あ'
        }.get(mode, 'A')
        return self.set_mode(mode)

    def switch_katakana(self):
        mode = self.get_mode()
        mode = {
            'A': 'ｱ',
            'Ａ': 'ア',
            'ア': 'あ',
            'ｱ': 'あ',
            'あ': 'ア'
        }.get(mode, 'ア')
        return self.set_mode(mode)

    def get_mode(self):
        return self._mode

    def set_mode(self, mode):
        self._override = False
        if self._mode == mode:
            return False
        logger.debug("set_mode(%s)" % (mode))
        self._preedit_string = ''
        self._commit()
        self._mode = mode
        self._update()
        self._update_input_mode()
        return True

    def _is_roomazi_mode(self):
        return self._to_kana == self._handle_roomazi_layout

    def do_process_key_event(self, keyval, keycode, state):
        return self._event.process_key_event(keyval, keycode, state)

    def handle_key_event(self, keyval, keycode, state, modifiers):
        logger.debug("handle_key_event(%s, %04x, %04x, %04x)" % (IBus.keyval_name(keyval), keycode, state, modifiers))

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
            if keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                return self.do_page_up()
            elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                return self.do_page_down()
            elif keyval == keysyms.Up or self._event.is_muhenkan():
                return self.do_cursor_up()
            elif keyval == keysyms.Down or self._event.is_henkan():
                return self.do_cursor_down()
            elif keyval == keysyms.Escape:
                return self.handle_escape(state)
            elif keyval == keysyms.Return:
                self._commit()
                return True

        if self._preedit_string:
            if keyval == keysyms.Return:
                if self._preedit_string == 'n':
                    self._preedit_string = 'ん'
                self._commit_string(self._preedit_string)
                self._preedit_string = ''
                self._update()
                return True
            if keyval == keysyms.Escape:
                self._preedit_string = ''
                self._update()
                return True

        # Handle Japanese text
        if self._event.is_henkan():
            return self.handle_replace(keyval, state)
        if self._event.is_shrink():
            return self.handle_shrink(keyval, state)
        self._commit()
        yomi = ''
        if self._event.is_katakana():
            if self._event.is_shift():
                self.switch_katakana()
            else:
                self.handle_katakana()
            return True
        if self._event.is_backspace():
            if 1 <= len(self._preedit_string):
                self._preedit_string = self._preedit_string[:-1]
                self._update()
                return True
            elif 0 < len(self._previous_text):
                self._previous_text = self._previous_text[:-1]
            return False
        if self._event.is_ascii():
            if self.get_mode() == 'Ａ':
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
        self._update()
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
                if self._acked:
                    # For furiganapad, yomi has to be committed anyway.
                    # However, 'ん' will be acked by set_cursor_location_cb()
                    # only after the converted text is committed later.
                    # So we pretend that 'ん' is acked here.
                    self._commit_string('ん')
                    self._acked = True
                    self._committed = ''
                else:
                    size = size - 1
            self._preedit_string = ''
            if 1 < len(self._dict.cand()):
                for c in self._dict.cand():
                    self._lookup_table.append_candidate(IBus.Text.new_from_string(c))
        return (cand, size)

    def handle_katakana(self):
        text, pos = self._get_surrounding_text()
        for i in reversed(range(pos)):
            if 0 <= KATAKANA.find(text[i]):
                continue
            found = HIRAGANA.find(text[i])
            if 0 <= found:
                self._delete_surrounding_text(pos - i)
                self._commit_string(KATAKANA[found] + text[i + 1:pos])
            break
        return True

    def handle_replace(self, keyval, state):
        if not self._dict.current():
            text, pos = self._get_surrounding_text()
            (cand, size) = self.lookup_dictionary(text, pos)
            self._shrunk = ''
        else:
            size = len(self._shrunk) + len(self._dict.current())
            if not self._event.is_shift():
                cand = self._dict.next()
            else:
                cand = self._dict.previous()
        if self._dict.current():
            self._update()
            self._delete_surrounding_text(size)
            self._commit_string(self._shrunk + cand)
        return True

    def handle_shrink(self, keyval, state):
        logger.debug("handle_shrink: '%s'", self._dict.current())
        if not self._dict.current():
            return False
        yomi = self._dict.reading()
        if len(yomi) <= 1:
            self.handle_escape(state)
            return True
        current_size = len(self._shrunk) + len(self._dict.current())
        text, pos = self._get_surrounding_text()
        (cand, size) = self.lookup_dictionary(yomi[1:] + text[pos:], len(yomi) - 1)
        kana = yomi
        if 0 < size:
            kana = kana[:-size]
        self._shrunk += kana
        self._delete_surrounding_text(current_size)
        self._commit_string(self._shrunk + cand)
        # Update preedit *after* committing the string to append preedit.
        self._update()
        return True

    def handle_escape(self, state):
        if not self._dict.current():
            return False
        size = len(self._dict.current())
        yomi = self._dict.reading()
        self._delete_surrounding_text(size)
        self._commit_string(yomi)
        self._reset(False)
        self._update()
        return True

    def _commit(self):
        if self._dict.current():
            self._dict.confirm(self._shrunk)
            self._dict.reset()
            self._lookup_table.clear()
            visible = 0 < self._lookup_table.get_number_of_candidates()
            self.update_lookup_table(self._lookup_table, visible)
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
        self._committed = text
        self._acked = False
        self._previous_text += text
        self.commit_text(IBus.Text.new_from_string(text))

    def _reset(self, full=True):
        self._dict.reset()
        self._lookup_table.clear()
        self._update_lookup_table()
        if full:
            self._committed = ''
            self._acked = True
            self._previous_text = ''
            self._preedit_string = ''
            self._ignore_surrounding_text = False

    def _update_candidate(self):
        index = self._lookup_table.get_cursor_pos()
        size = len(self._shrunk) + len(self._dict.current())
        self._dict.set_current(index)
        self._delete_surrounding_text(size)
        self._commit_string(self._shrunk + self._dict.current())

    def do_page_up(self):
        if self._lookup_table.page_up():
            self._update_lookup_table()
            self._update_candidate()
        return True

    def do_page_down(self):
        if self._lookup_table.page_down():
            self._update_lookup_table()
            self._update_candidate()
        return True

    def do_cursor_up(self):
        if self._lookup_table.cursor_up():
            self._update_lookup_table()
            self._update_candidate()
        return True

    def do_cursor_down(self):
        if self._lookup_table.cursor_down():
            self._update_lookup_table()
            self._update_candidate()
        return True

    def _update(self):
        preedit_len = len(self._preedit_string)
        text = IBus.Text.new_from_string(self._preedit_string)
        if 0 < preedit_len:
            attrs = IBus.AttrList()
            attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE, IBus.AttrUnderline.SINGLE, 0, preedit_len))
            text.set_attributes(attrs)
        # Note self.hide_preedit_text() does not seem to work as expected with Kate.
        # cf. "Qt5 IBus input context does not implement hide_preedit_text()",
        #     https://bugreports.qt.io/browse/QTBUG-48412
        self.update_preedit_text(text, preedit_len, 0 < preedit_len)
        self._update_lookup_table()

    def _update_lookup_table(self):
        if self.is_enabled():
            visible = 0 < self._lookup_table.get_number_of_candidates()
            self.update_lookup_table(self._lookup_table, visible)

    def do_focus_in(self):
        logger.info("focus_in")
        self._event.reset()
        self.register_properties(self._prop_list)
        # Request the initial surrounding-text in addition to the "enable" handler.
        self.get_surrounding_text()

    def do_focus_out(self):
        logger.info("focus_out")
        self._reset()
        self._dict.save_orders()

    def do_enable(self):
        logger.info("enable")
        # Request the initial surrounding-text when enabled as documented.
        self.get_surrounding_text()

    def do_disable(self):
        logger.info("disable")
        self._reset()
        self._mode = 'A'
        self._dict.save_orders()

    def do_reset(self):
        logger.info("reset")
        self._reset()
        # Do not switch back to the Alphabet mode here; 'reset' should be
        # called when the text cursor is moved by a mouse click, etc.

    def do_property_activate(self, prop_name, state):
        logger.info("property_activate(%s, %d)" % (prop_name, state))
        if prop_name == "About":
            dialog = Gtk.AboutDialog()
            dialog.set_program_name(_("Hiragana IME"))
            dialog.set_copyright("Copyright 2017-2020 Esrille Inc.")
            dialog.set_authors(["Esrille Inc."])
            dialog.set_documenters(["Esrille Inc."])
            dialog.set_website("file://" + os.path.join(package.get_datadir(), "help/index.html"))
            dialog.set_website_label(_("Introduction to Hiragana IME"))
            dialog.set_logo_icon_name(package.get_name())
            # To close the dialog when "close" is clicked, e.g. on RPi,
            # we connect the "response" signal to about_response_callback
            dialog.connect("response", self.about_response_callback)
            dialog.show()

    def about_response_callback(self, dialog, response):
        dialog.destroy()

    def set_surrounding_text_cb(self, engine, text, cursor_pos, anchor_pos):
        text = self.get_plain_text(text.get_text()[:cursor_pos])
        if self._committed:
            pos = text.rfind(self._committed)
            if 0 <= pos and pos + len(self._committed) == len(text):
                self._acked = True
                self._committed = ''
        logger.debug("set_surrounding_text_cb(%s, %d, %d) => %d" % (text, cursor_pos, anchor_pos, self._acked))

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
        logger.debug("set_cursor_location_cb(%d, %d, %d, %d)" % (x, y, w, h))
        self._update_lookup_table()
