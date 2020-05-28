# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace with Kanji Japanese input method for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
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

import i18n

import os
import logging
import sys
import getopt

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus
from gi.repository import GLib
from gi.repository import GObject

from engine import EngineReplaceWithKanji


class IMApp:
    def __init__(self, exec_by_ibus):
        engine_name = "replace-with-kanji-python" if exec_by_ibus else "replace-with-kanji-python (debug)"
        self.__component = IBus.Component.new(
            "org.freedesktop.IBus.ReplaceWithKanji",
            "Replace With Kanji Input Method",
            "0.8.0",
            "Apache",
            "Esrille Inc. <info@esrille.com>",
            "https://github.com/esrille/ibus-replace-with-kanji",
            "/usr/bin/exec",
            "ibus-replace-with-kanji")
        engine = IBus.EngineDesc.new(
            "replace-with-kanji-python",
            engine_name,
            "Japanese Replace With Kanji",
            "ja",
            "Apache",
            "Esrille Inc. <info@esrille.com>",
            "",
            "us")
        self.__component.add_engine(engine)
        self.__mainloop = GLib.MainLoop()
        self.__bus = IBus.Bus()
        self.__bus.connect("disconnected", self.__bus_disconnected_cb)
        self.__factory = IBus.Factory.new(self.__bus.get_connection())
        self.__factory.add_engine("replace-with-kanji-python", GObject.type_from_name("EngineReplaceWithKanji"))
        if exec_by_ibus:
            self.__bus.request_name("org.freedesktop.IBus.ReplaceWithKanji", 0)
        else:
            self.__bus.register_component(self.__component)
            self.__bus.set_global_engine_async("replace-with-kanji-python", -1, None, None, None)

    def run(self):
        self.__mainloop.run()

    def __bus_disconnected_cb(self, bus):
        self.__mainloop.quit()


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
