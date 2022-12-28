# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2020-2022 Esrille Inc.
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

import package

import gi
from gi.repository import Gio
from gi.repository import GLib

GLib.set_prgname('ibus-setup-hiragana')

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
gi.require_version('IBus', '1.0')
from gi.repository import IBus

import gettext
import locale
import os
import sys

_ = lambda a : gettext.dgettext(package.get_name(), a)


class SetupEngineHiragana:
    def __init__(self):
        self._settings = Gio.Settings.new('org.freedesktop.ibus.engine.hiragana')
        self._settings.connect('changed', self.on_value_changed)
        self._builder = Gtk.Builder()
        self._builder.set_translation_domain(package.get_name())
        self._builder.add_from_file(os.path.join(os.path.dirname(__file__), 'setup.glade'))
        self._builder.connect_signals(self)
        self._init_keyboard_layout()
        self._init_dictionary()
        self._init_nn_as_x4063()
        self._set_current_keyboard(self._settings.get_string('layout'))
        self._window = self._builder.get_object('SetupDialog')
        self._window.set_default_icon_name('ibus-setup-hiragana')
        self._window.show()

    def _init_keyboard_layout(self):
        self._keyboard_layouts = self._builder.get_object('KeyboardLayout')
        model = Gtk.ListStore(str, str, int)
        model.append([_('Rōmaji'), 'roomazi', 0])
        model.append([_('Kana (JIS Layout)'), 'jis', 1])
        model.append([_('Kana (New Stickney Layout)'), 'new_stickney', 2])
        self._keyboard_layouts.set_model(model)
        renderer = Gtk.CellRendererText()
        self._keyboard_layouts.pack_start(renderer, True)
        self._keyboard_layouts.add_attribute(renderer, 'text', 0)

    def _set_current_keyboard(self, layout: str):
        # layouts
        if layout.endswith('.json'):
            layout = layout[layout.rfind('/') + 1:len(layout) - 4]
        model = self._keyboard_layouts.get_model()
        for i in model:
            if i[1] == layout:
                self._keyboard_layouts.set_active(i[2])
                break

    def _init_dictionary(self):
        self._kanzi_dictionaries = self._builder.get_object('KanjiDictionary')
        model = Gtk.ListStore(str, str, int)
        model.append([_('1st grade'), 'restrained.1.dic', 0])
        model.append([_('2nd grade'), 'restrained.2.dic', 1])
        model.append([_('3rd grade'), 'restrained.3.dic', 2])
        model.append([_('4th grade'), 'restrained.4.dic', 3])
        model.append([_('5th grade'), 'restrained.5.dic', 4])
        model.append([_('6th grade'), 'restrained.6.dic', 5])
        model.append([_('7-9th grade'), 'restrained.7.dic', 6])
        model.append([_('10th+ grade (Okurigana: general)'), 'restrained.dic', 7])
        model.append([_('10th+ grade (Okurigana: general + permissible)'), 'restrained.9.dic', 8])
        self._kanzi_dictionaries.set_model(model)
        renderer = Gtk.CellRendererText()
        self._kanzi_dictionaries.pack_start(renderer, True)
        self._kanzi_dictionaries.add_attribute(renderer, 'text', 0)
        self._kanzi_dictionaries.set_active(7)
        current = self._settings.get_string('dictionary')
        current = os.path.basename(current)
        for i in model:
            if i[1] == current:
                self._kanzi_dictionaries.set_active(i[2])
                break

        self._user_dictionary = self._builder.get_object('UserDictionary')
        current = self._settings.get_string('user-dictionary')
        self._user_dictionary.set_text(current)
        self._default_user_dictionary = self._settings.get_default_value('user-dictionary').get_string()

        self._reload_dictionaries = self._builder.get_object('ReloadDictionaries')
        self._clear_input_history = self._builder.get_object('ClearInputHistory')

    def _init_nn_as_x4063(self):
        self._nn_as_x4063 = self._builder.get_object('NnAsX4063')
        current = self._settings.get_value('nn-as-jis-x-4063')
        self._nn_as_x4063.set_active(current)

    def run(self):
        Gtk.main()

    def apply(self):
        # layout
        i = self._keyboard_layouts.get_active()
        layout = self._keyboard_layouts.get_model()[i][1]
        self._settings.set_string('layout', layout)

        # altgr
        self._settings.set_string('altgr', 'altgr')

        # nn-as-jis-x-4063
        nn_as_x4063 = self._nn_as_x4063.get_active()
        self._settings.set_boolean('nn-as-jis-x-4063', nn_as_x4063)

        # dictionary
        i = self._kanzi_dictionaries.get_active()
        dictionary = self._kanzi_dictionaries.get_model()[i][1]
        dictionary = os.path.join(package.get_datadir(), dictionary)
        self._settings.set_string('dictionary', dictionary)

        # user-dictionary
        user = self._user_dictionary.get_text().strip()
        if user == self._default_user_dictionary:
            self._settings.reset('user-dictionary')
        else:
            self._settings.set_string('user-dictionary', user)

        if self._clear_input_history.get_active():
            # clear_input_history also reloads dictionaries
            print('clear_input_history', flush=True)
        elif self._reload_dictionaries.get_active():
            print('reload_dictionaries', flush=True)

    def on_value_changed(self, settings, key):
        value = settings.get_value(key)
        if key == 'layout':
            self._set_current_keyboard(value.get_string())
        elif key == 'nn-as-jis-x-4063':
            t = value.get_boolean()
            self._nn_as_x4063.set_active(value.get_boolean())
        elif key == 'dictionary':
            current = value.get_string()
            current = os.path.basename(current)
            model = self._kanzi_dictionaries.get_model()
            for i in model:
                if i[1] == current:
                    self._kanzi_dictionaries.set_active(i[2])
                    break
        elif key == 'user-dictionary':
            current = value.get_string()
            self._user_dictionary.set_text(current)

    #
    # Glade signal handlers. The signal names are declared in Glade
    #
    def on_apply(self, *args):
        self.apply()

    def on_cancel(self, *args):
        self._window.destroy()

    def on_ok(self, *args):
        self.apply()
        self._window.destroy()

    def on_edit(self, *args):
        path = self._user_dictionary.get_text().strip()
        path = os.path.join(package.get_user_datadir(), path)
        with open(path, 'a+') as f:
            pass
        try:
            Gtk.show_uri_on_window(None, 'file://' + path, Gdk.CURRENT_TIME)
        except Exception:
            pass

    def on_destroy(self, *args):
        Gtk.main_quit()


def main():
    setup = SetupEngineHiragana()
    setup.run()


if __name__ == '__main__':
    try:
        locale.bindtextdomain(package.get_name(), package.get_localedir())
    except Exception:
        pass
    gettext.bindtextdomain(package.get_name(), package.get_localedir())
    main()
