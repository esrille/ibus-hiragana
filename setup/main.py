# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2020-2024 Esrille Inc.
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

import argparse
import gettext
import locale
import logging
import os
import sys

import gi
gi.require_version('GLib', '2.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import GLib
# set_prgname before importing other modules to show the name in warning messages
GLib.set_prgname('ibus-setup-hiragana')
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import Vte

import package
from package import _

MODEL_NAME = 'cl-tohoku/bert-base-japanese-v3'
USER_DICTIONARY_COMMENT = _("""; Hiragana IME User Dictionary
;
; Lines starting with a semicolon (;) are comments.
; To add a word, write the reading, followed by a space, and then the word
; enclosed by slashes (/):
;
;   Example) きれい /綺麗/
;
; For more details, see the 'Settings' - ‘Dictionary Tab’ in the Help.
;

""")


# Note Python caches the module in the directory when the program starts
def check_requirements() -> bool:
    try:
        from transformers import AutoModelForMaskedLM, AutoTokenizer
    except ImportError as e:
        logging.debug(f'{e}')
        return False
    try:
        AutoModelForMaskedLM.from_pretrained(MODEL_NAME, local_files_only=True)
        AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
    except OSError:
        return False
    return True


class InstallDialog:
    def __init__(self, builder):
        self._pid = -1

        self._builder = builder
        self._dialog = self._builder.get_object('InstallDialog')
        self._dialog.set_default_icon_name('ibus-setup-hiragana')
        self._dialog.set_modal(True)
        self._dialog.connect('key-press-event', self.on_key_press)

        log = builder.get_object('Log')
        self._terminal = Vte.Terminal()
        self._terminal.set_hexpand(True)
        self._terminal.set_vexpand(True)
        self._terminal.connect('child-exited', self.on_child_exited)
        log.add(self._terminal)

    def destroy(self):
        self._dialog.destroy()

    def hide(self):
        self._dialog.hide()

    def is_visible(self):
        self._dialog.is_visible()

    def show(self):
        self._dialog.show_all()

    def complete(self):
        button = self._builder.get_object('InstallButton')
        button.set_use_underline(True)
        button.set_label(_('Close'))

    def is_completed(self) -> bool:
        button = self._builder.get_object('InstallButton')
        return button.get_label() == _('Close')

    def spawn(self, commands):
        self._terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            commands,
            [],
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            -1,
            None,
            self.spawn_callback,
            None
        )

    def set_label(self, commands):
        label = self._builder.get_object('Command')
        label.set_text('$ ' + ' '.join(commands))

    def spawn_callback(self, terminal, pid, error, user_data):
        self._pid = pid

    def on_child_exited(self, terminal, status):
        self.complete()

    def is_child_alive(self):
        return self._pid != -1 and not self.is_completed()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            # Do not close the dialog box
            return True
        return False


class SetupEngineHiragana:

    def __init__(self, loaded: bool):
        self._loaded = loaded

        self._settings = Gio.Settings.new('org.freedesktop.ibus.engine.hiragana')
        self._settings.connect('changed', self.on_value_changed)
        self._builder = Gtk.Builder()
        self._builder.set_translation_domain(package.get_name())
        self._builder.add_from_file(os.path.join(os.path.dirname(__file__), 'setup.glade'))
        self._builder.connect_signals(self)
        self._init_keyboard_layout()
        self._init_dictionary()
        self._init_nn_as_x4063()
        self._init_combining_circumflex()
        self._init_combining_macron()
        self._init_permissible()
        self._init_use_half_width_digits()
        self._init_use_cuda()
        self._init_use_llm()
        self._set_current_keyboard(self._settings.get_string('layout'))

        postinst = os.path.join(package.get_prefix(), 'libexec', 'ibus-postinst-hiragana')
        self._install_dialog = InstallDialog(self._builder)
        self._install_dialog.set_label([postinst])
        self._install_dialog.hide()

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
            layout = layout[layout.rfind('/') + 1:len(layout) - 5]
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
        model.append([_('10-12th grade'), 'restrained.8.dic', 7])
        model.append([_('Adults'), 'restrained.9.dic', 8])
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

    def _init_nn_as_x4063(self):
        self._nn_as_x4063 = self._builder.get_object('NnAsX4063')
        current = self._settings.get_value('nn-as-jis-x-4063')
        self._nn_as_x4063.set_active(current)

    def _init_combining_circumflex(self):
        self._combining_circumflex = self._builder.get_object('CombiningCircumflex')
        current = self._settings.get_value('combining-circumflex')
        self._combining_circumflex.set_active(current)

    def _init_combining_macron(self):
        self._combining_macron = self._builder.get_object('CombiningMacron')
        current = self._settings.get_value('combining-macron')
        self._combining_macron.set_active(current)

    def _init_permissible(self):
        self._permissible = self._builder.get_object('UsePermissible')
        current = self._settings.get_value('permissible')
        self._permissible.set_active(current)

    def _init_use_half_width_digits(self):
        self._use_half_width_digits = self._builder.get_object('UseHalfWidthDigits')
        current = self._settings.get_value('use-half-width-digits')
        self._use_half_width_digits.set_active(current)

    def _init_use_llm(self):
        self._use_llm = self._builder.get_object('UseLLM')
        current = self._settings.get_value('use-llm')
        self._use_llm.set_active(current)

    def _init_use_cuda(self):
        self._use_cuda = self._builder.get_object('UseCUDA')
        current = self._settings.get_value('use-cuda')
        self._use_cuda.set_active(current)

    def _on_stdin_input(self, source, condition):
        line = source.readline().strip()
        if line == 'present':
            self._window.present()
        return True

    def run(self):
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self._on_stdin_input)
        Gtk.main()

    def _has_llm(self) -> bool:
        return self._loaded or self._install_dialog.is_completed() or check_requirements()

    def apply(self) -> bool:
        # layout
        i = self._keyboard_layouts.get_active()
        layout = self._keyboard_layouts.get_model()[i][1]
        self._settings.set_string('layout', layout)

        # altgr
        self._settings.set_string('altgr', 'altgr')

        # nn-as-jis-x-4063
        nn_as_x4063 = self._nn_as_x4063.get_active()
        self._settings.set_boolean('nn-as-jis-x-4063', nn_as_x4063)

        # combining-circumflex
        combining_circumflex = self._combining_circumflex.get_active()
        self._settings.set_boolean('combining-circumflex', combining_circumflex)

        # combining-macron
        combining_macron = self._combining_macron.get_active()
        self._settings.set_boolean('combining-macron', combining_macron)

        # dictionary
        i = self._kanzi_dictionaries.get_active()
        dictionary = self._kanzi_dictionaries.get_model()[i][1]
        self._settings.set_string('dictionary', dictionary)

        # user-dictionary
        user = self._user_dictionary.get_text().strip()
        if user == self._default_user_dictionary:
            self._settings.reset('user-dictionary')
        else:
            self._settings.set_string('user-dictionary', user)

        # permissible
        permissible = self._permissible.get_active()
        self._settings.set_boolean('permissible', permissible)

        # use-half-width-digits
        use_half_width_digits = self._use_half_width_digits.get_active()
        self._settings.set_boolean('use-half-width-digits', use_half_width_digits)

        # use-cuda
        use_cuda = self._use_cuda.get_active()
        self._settings.set_boolean('use-cuda', use_cuda)

        # use-llm
        use_llm = self._use_llm.get_active()
        if use_llm and not self._has_llm():
            if not self._install_dialog.is_visible():
                self._install_dialog.show()
            return False
        self._settings.set_boolean('use-llm', use_llm)

        print('reload_dictionaries', flush=True)

        return True

    def on_value_changed(self, settings, key):
        value = settings.get_value(key)
        if key == 'layout':
            self._set_current_keyboard(value.get_string())
        elif key == 'nn-as-jis-x-4063':
            self._nn_as_x4063.set_active(value.get_boolean())
        elif key == 'combining-circumflex':
            self._combining_circumflex.set_active(value.get_boolean())
        elif key == 'combining-macron':
            self._combining_macron.set_active(value.get_boolean())
        elif key == 'dictionary':
            current = value.get_string()
            current = os.path.basename(current)
            model = self._kanzi_dictionaries.get_model()
            for i in model:
                if i[1] == current:
                    self._kanzi_dictionaries.set_active(i[2])
                    break
        elif key == 'permissible':
            self._permissible.set_active(value.get_boolean())
        elif key == 'user-dictionary':
            current = value.get_string()
            self._user_dictionary.set_text(current)
        elif key == 'use-half-width-digits':
            self._use_half_width_digits.set_active(value.get_boolean())
        elif key == 'use-cuda':
            self._use_cuda.set_active(value.get_boolean())
        elif key == 'use-llm':
            self._use_llm.set_active(value.get_boolean())

    #
    # Glade signal handlers. The signal names are declared in Glade
    #
    def on_apply(self, *args):
        self.apply()

    def on_cancel(self, *args):
        self._window.destroy()

    def on_ok(self, *args):
        if self.apply():
            self._window.destroy()

    def on_edit(self, *args):
        path = self._user_dictionary.get_text().strip()
        path = os.path.join(package.get_user_datadir(), path)
        logging.info(f'on_edit: {path}')
        try:
            if os.path.abspath(path) != path:
                raise PermissionError(_('Invalid characters in User Dictionary Name'))
            if not os.path.isfile(path):
                with open(path, 'w') as file:
                    file.write(USER_DICTIONARY_COMMENT)
            else:
                with open(path, 'a+'):
                    pass
            Gtk.show_uri_on_window(None, 'file://' + path, Gdk.CURRENT_TIME)
        except (OSError, GLib.Error) as e:
            logging.exception(f'Could not open "{path}"')
            dialog = Gtk.MessageDialog(
                transient_for=self._window,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_('Could not open file'),
            )
            dialog.format_secondary_text(_('Error opening file "{path}": {message}').format(path=path, message=str(e)))
            dialog.run()
            dialog.destroy()

    def on_destroy(self, *args):
        Gtk.main_quit()

    def on_install_llm(self, *args):
        if not self._install_dialog.is_visible():
            self._install_dialog.show()

    def on_install(self, *args):
        if self._install_dialog.is_completed():
            self._install_dialog.hide()
        elif not self._install_dialog.is_child_alive():
            postinst = os.path.join(package.get_prefix(), 'libexec', 'ibus-postinst-hiragana')
            self._install_dialog.spawn([postinst])

    def on_cancel_install(self, *args):
        if not self._install_dialog.is_child_alive():
            self._install_dialog.hide()

    def on_clear_history(self, *args):
        dialog = Gtk.MessageDialog(
            transient_for=self._window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=_('Clear input history'),
        )
        dialog.format_secondary_text(_('Do you want to clear your input history?'))
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            print('clear_input_history', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loaded', action='store_true')
    args = parser.parse_args()
    setup = SetupEngineHiragana(args.loaded)
    setup.run()


if __name__ == '__main__':
    locale.bindtextdomain(package.get_name(), package.get_localedir())
    gettext.bindtextdomain(package.get_name(), package.get_localedir())
    if __debug__:
        logging.basicConfig(level=logging.DEBUG)
    main()
