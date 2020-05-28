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

import i18n
import package

import getopt
import os
import logging
import sys

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus
from gi.repository import GLib
from gi.repository import GObject

from engine import EngineReplaceWithKanji


class IMApp:
    def __init__(self, exec_by_ibus):
        self._mainloop = GLib.MainLoop()
        self._bus = IBus.Bus()
        self._bus.connect("disconnected", self._bus_disconnected_cb)
        self._factory = IBus.Factory(self._bus)
        self._factory.add_engine("replace-with-kanji-python", GObject.type_from_name("EngineReplaceWithKanji"))
        if exec_by_ibus:
            self._bus.request_name("org.freedesktop.IBus.ReplaceWithKanji", 0)
        else:
            self._component = IBus.Component(
                name="org.freedesktop.IBus.ReplaceWithKanji",
                description="Replace With Kanji Input Method",
                version=package.get_version(),
                license="Apache",
                author="Esrille Inc. <info@esrille.com>",
                homepage="https://github.com/esrille/ibus-replace-with-kanji",
                textdomain="ibus-replace-with-kanji")
            engine = IBus.EngineDesc(
                name="replace-with-kanji-python",
                longname="replace-with-kanji-python",
                description="Japanese Replace With Kanji",
                language="ja",
                license="Apache",
                author="Esrille Inc. <info@esrille.com>",
                icon="ibus-replace-with-kanji",
                layout="default")
            self._component.add_engine(engine)
            self._bus.register_component(self._component)
            self._bus.set_global_engine_async("replace-with-kanji-python", -1, None, None, None)

    def run(self):
        self._mainloop.run()

    def _bus_disconnected_cb(self, bus):
        self._mainloop.quit()


def print_help(v=0):
    print("-i, --ibus             executed by IBus.")
    print("-h, --help             show this message.")
    print("-d, --daemonize        daemonize ibus")
    sys.exit(v)


def main():
    os.umask(0o077)

    # Create user specific data directory
    datadir = os.path.expanduser('~/.local/share/ibus-replace-with-kanji')
    os.makedirs(datadir, 0o700, True)
    os.chmod(datadir, 0o700)  # For logfile created by v0.2.0 or earlier

    # Create a debug log file
    logfile = os.path.expanduser('~/.local/share/ibus-replace-with-kanji/ibus-replace-with-kanji.log')
    logging.basicConfig(filename=logfile, filemode='w', level=logging.WARNING)

    # Load the localization file
    i18n.initialize()

    exec_by_ibus = False
    daemonize = False

    shortopt = "ihd"
    longopt = ["ibus", "help", "daemonize"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
    except getopt.GetoptError as err:
        print_help(1)

    for o, a in opts:
        if o in ("-h", "--help"):
            print_help(0)
        elif o in ("-d", "--daemonize"):
            daemonize = True
        elif o in ("-i", "--ibus"):
            exec_by_ibus = True
        else:
            sys.stderr.write("Unknown argument: %s\n" % o)
            print_help(1)

    if daemonize:
        if os.fork():
            sys.exit()

    IMApp(exec_by_ibus).run()


if __name__ == "__main__":
    main()
