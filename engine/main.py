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

import getopt
import gettext
import locale
import logging
import os
import signal
import sys

import gi
gi.require_version('GLib', '2.0')
gi.require_version('IBus', '1.0')
from gi.repository import GLib
from gi.repository import IBus

import package
from factory import EngineFactory

FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
DICT_NAMES = ('restrained.1.dic',
              'restrained.2.dic',
              'restrained.3.dic',
              'restrained.4.dic',
              'restrained.5.dic',
              'restrained.6.dic',
              'restrained.7.dic',
              'restrained.8.dic',
              'restrained.9.dic')

LOGGER = logging.getLogger(__name__)


class IMApp:

    def __init__(self, exec_by_ibus):
        self._mainloop = GLib.MainLoop()
        self._bus = IBus.Bus()
        self._bus.connect('disconnected', self._bus_disconnected_cb)
        self._factory = self._factory = EngineFactory(self._bus)
        if exec_by_ibus:
            self._bus.request_name('org.freedesktop.IBus.Hiragana', 0)
        else:
            self._component = IBus.Component(
                name='org.freedesktop.IBus.Hiragana',
                description='Hiragana IME',
                version=package.get_version(),
                license='Apache',
                author='Esrille Inc. <info@esrille.com>',
                homepage='https://github.com/esrille/' + package.get_name(),
                textdomain=package.get_name())
            engine = IBus.EngineDesc(
                name='hiragana',
                longname='Hiragana IME',
                description='Hiragana IME',
                language='ja',
                license='Apache',
                author='Esrille Inc. <info@esrille.com>',
                icon=package.get_name(),
                layout='default')
            self._component.add_engine(engine)
            self._bus.register_component(self._component)
            self._bus.set_global_engine_async('hiragana', -1, None, None, None)

    def run(self):
        self._mainloop.run()

    def quit(self):
        LOGGER.debug('quit()')
        self._bus_disconnected_cb()

    def _bus_disconnected_cb(self, bus=None):
        self._mainloop.quit()


def print_help(v=0):
    print('-i, --ibus             executed by IBus.')
    print('-h, --help             show this message.')
    print('-d, --daemonize        daemonize ibus')
    sys.exit(v)


def initialize():
    user_datadir = package.get_user_datadir()
    user_dic_datadir = os.path.join(user_datadir, 'dic')

    try:
        os.umask(0o077)

        # Create user specific data directory
        os.makedirs(user_datadir, 0o700, True)

        # For v0.2.0 or earlier
        os.chmod(user_datadir, 0o700)

        if not os.path.isdir(user_dic_datadir):
            # Create user specific dictionary directory
            if os.path.exists(user_dic_datadir):
                bak = user_dic_datadir + '~'
                if os.path.exists(bak):
                    os.remove(bak)
                os.rename(user_dic_datadir, bak)
            os.makedirs(user_dic_datadir, 0o700, True)

            # For v0.15.0 or earlier, 'restrained.8.dic' does not exist.
            old = os.path.join(user_datadir, 'restrained.dic')
            new = os.path.join(user_datadir, 'restrained.8.dic')
            if os.path.exists(old) and not os.path.exists(new):
                os.rename(old, new)

            # For v0.15.3 or earlier, move orders files
            # from ~/.local/share/ibus-hiragana/
            # to ~/.local/share/ibus-hiragana/dic.
            for name in DICT_NAMES:
                old = os.path.join(user_datadir, name)
                new = os.path.join(user_dic_datadir, name)
                if os.path.exists(old):
                    os.rename(old, new)

    except OSError:
        LOGGER.exception('initialize')


def cleanup(app: IMApp):
    app.quit()


def main():
    initialize()

    if __debug__:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        # Create a debug log file
        logfile = os.path.join(package.get_user_datadir(), package.get_name() + '.log')
        logging.basicConfig(filename=logfile,
                            filemode='w',
                            level=logging.WARNING,
                            format=FORMAT)

    exec_by_ibus = False
    daemonize = False

    shortopt = 'ihd'
    longopt = ['ibus', 'help', 'daemonize']

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
    except getopt.GetoptError:
        print_help(1)

    for o, a in opts:
        if o in ('-h', '--help'):
            print_help(0)
        elif o in ('-d', '--daemonize'):
            daemonize = True
        elif o in ('-i', '--ibus'):
            exec_by_ibus = True

    if daemonize:
        if os.fork():
            sys.exit()

    IBus.init()
    app = IMApp(exec_by_ibus)
    signal.signal(signal.SIGTERM, lambda signum, frame: cleanup(app))
    signal.signal(signal.SIGINT, lambda signum, frame: cleanup(app))
    app.run()


# Catch exceptions from GLib.MainLoop
def handle_exception(exception_type, value, traceback):
    LOGGER.error('crashed:', exc_info=(exception_type, value, traceback))


if __name__ == '__main__':
    sys.excepthook = handle_exception
    locale.bindtextdomain(package.get_name(), package.get_localedir())
    gettext.bindtextdomain(package.get_name(), package.get_localedir())
    main()
