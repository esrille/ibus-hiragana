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

m4_define([ibus_hiragana_version], [0.15.4~rc1])
AC_INIT([ibus-hiragana], [ibus_hiragana_version], [https://github.com/esrille/ibus-hiragana/issues])
AC_CONFIG_AUX_DIR([.])
AM_INIT_AUTOMAKE([foreign tar-ustar])

AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_REQUIRE_VERSION([0.19.8])
AM_GNU_GETTEXT_VERSION([0.19.8])

# Check IBus
#   Note hiragana.xml uses icon_prop_key and
#   ibus 1.5.11 or later is required
PKG_CHECK_MODULES([IBUS], [ibus-1.0 >= 1.5.11])

# Check Python
AM_PATH_PYTHON([3.8])

# define GETTEXT_* variables
GETTEXT_PACKAGE=AC_PACKAGE_NAME
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED(
  [GETTEXT_PACKAGE], ["$GETTEXT_PACKAGE"],
    [Define to the read-only architecture-independent data directory.]
)

# For GitHub
m4_define(ibus_hiragana_source_version,
  [m4_esyscmd(echo -n ibus_hiragana_version | tr '~' '-')])
SOURCE_VERSION="ibus_hiragana_source_version"
AC_SUBST(SOURCE_VERSION)

# GSettings
# see https://developer.gnome.org/gio/stable/GSettings.html
GLIB_GSETTINGS

AC_ARG_ENABLE([dic],
[  --enable-dic            Enable regeneration of dictionaries],
[case "${enableval}" in
  yes) dic=true ;;
  no)  dic=false ;;
  *) AC_MSG_ERROR([bad value ${enableval} for --enable-dic]) ;;
esac],[dic=false])
AM_CONDITIONAL([ENABLE_DIC], [test x$dic = xtrue])

AC_ARG_ENABLE([html],
[  --enable-html           Enable regeneration of html files from markdown files],
[case "${enableval}" in
  yes) html=true ;;
  no)  html=false ;;
  *) AC_MSG_ERROR([bad value ${enableval} for --enable-html]) ;;
esac],[html=false])
AM_CONDITIONAL([ENABLE_HTML], [test x$html = xtrue])

# OUTPUT files
AC_CONFIG_FILES(
dic/Makefile
docs/Makefile
engine/hiragana.xml.in
engine/ibus-engine-hiragana
engine/Makefile
engine/package.py.in
icons/Makefile
layouts/Makefile
po/Makefile.in
setup/Makefile
setup/package.py.in
setup/ibus-setup-hiragana.in
Makefile
)

AC_OUTPUT
