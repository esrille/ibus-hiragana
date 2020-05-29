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

AC_INIT([ibus-hiragana], [0.8.0], [https://github.com/esrille/ibus-hiragana/issues])
AM_INIT_AUTOMAKE([foreign tar-ustar])

# Check IBus
#   Note hiragana.xml uses icon_prop_key and
#   ibus 1.5.11 or later is required
PKG_CHECK_MODULES(IBUS, [ibus-1.0 >= 1.5.11])
AC_SUBST(IBUS_DATADIR, $($PKG_CONFIG --variable=datadir ibus-1.0) )

# Check Python
AM_PATH_PYTHON([3.3])

# GSettings
# see https://developer.gnome.org/gio/stable/GSettings.html
GLIB_GSETTINGS

# OUTPUT files
AC_CONFIG_FILES(Makefile
ibus-hiragana.spec
engine/Makefile
engine/ibus-engine-hiragana
engine/package.py.in
engine/hiragana.xml.in
icons/Makefile
layouts/Makefile
locale/Makefile
dic/Makefile
dic_tools/Makefile
docs/Makefile
)

AC_OUTPUT
