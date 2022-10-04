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

from engine import EngineHiragana
import package

import getopt
import gettext
import os
import locale
import logging
import sys
import gi
gi.require_version('IBus', '1.0')
from gi.repository import GLib, GObject, IBus


logger = logging.getLogger(__name__)


class IMApp:
    def __init__(self, exec_by_ibus):
        self._mainloop = GLib.MainLoop()
        self._bus = IBus.Bus()
        self._bus.connect("disconnected", self._bus_disconnected_cb)
        self._factory = IBus.Factory(self._bus)
        self._factory.add_engine("hiragana", GObject.type_from_name("EngineHiragana"))
        if exec_by_ibus:
            self._bus.request_name("org.freedesktop.IBus.Hiragana", 0)
        else:
            self._component = IBus.Component(
                name="org.freedesktop.IBus.Hiragana",
                description="Hiragana IME",
                version=package.get_version(),
                license="Apache",
                author="Esrille Inc. <info@esrille.com>",
                homepage="https://github.com/esrille/" + package.get_name(),
                textdomain=package.get_name())
            engine = IBus.EngineDesc(
                name="hiragana",
                longname="Hiragana IME",
                description="Hiragana IME",
                language="ja",
                license="Apache",
                author="Esrille Inc. <info@esrille.com>",
                icon=package.get_name(),
                layout="default")
            self._component.add_engine(engine)
            self._bus.register_component(self._component)
            self._bus.set_global_engine_async("hiragana", -1, None, None, None)

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
    user_datadir = package.get_user_datadir()
    os.makedirs(user_datadir, 0o700, True)
    os.chmod(user_datadir, 0o700)   # For logfile created by v0.2.0 or earlier

    if __debug__:
        logging.basicConfig(level=logging.DEBUG)
    else:
        # Create a debug log file
        logfile = os.path.join(user_datadir, package.get_name() + '.log')
        logging.basicConfig(filename=logfile, filemode='w', level=logging.WARNING)

    exec_by_ibus = False
    daemonize = False

    shortopt = "ihd"
    longopt = ["ibus", "help", "daemonize"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
    except getopt.GetoptError:
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
    try:
        locale.bindtextdomain(package.get_name(), package.get_localedir())
    except:
        logger.exception('crashed')
    gettext.bindtextdomain(package.get_name(), package.get_localedir())
    try:
        main()
    except:
        logger.exception('main crashed')
