# Copyright (c) 2017 Esrille Inc.
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
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

# if not 1, append datestamp to the version number.
m4_define([package_name], [ibus-replace-with-kanji])
m4_define([ibus_released], [0])
m4_define([ibus_major_version], [1])
m4_define([ibus_minor_version], [2])
m4_define([ibus_micro_version], [99])
m4_define(ibus_maybe_datestamp,
    m4_esyscmd([if test x]ibus_released[ != x1; then date +.%Y%m%d | tr -d '\n\r'; fi]))

m4_define([ibus_version],
    ibus_major_version.ibus_minor_version.ibus_micro_version[]ibus_maybe_datestamp)

AC_INIT([package_name], [ibus_version], [https://github.com/esrille/ibus-replace-with-kanji], [package_name])
AM_INIT_AUTOMAKE([1.10])

AC_CONFIG_MACRO_DIR([m4])
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])

# define PACKAGE_VERSION_* variables
AS_VERSION
AS_NANO
AM_SANITY_CHECK
AM_MAINTAINER_MODE

# check ibus
PKG_CHECK_MODULES(IBUS, [
    ibus-1.0 >= 1.3.0
])

AC_SUBST(IBUS_DATADIR, $($PKG_CONFIG --variable=datadir ibus-1.0) )

#check python
AM_PATH_PYTHON([3.0])

# OUTPUT files
AC_CONFIG_FILES(Makefile
engine/Makefile
engine/ibus-engine-replace-with-kanji
engine/replace-with-kanji-python.xml.in
engine/dictionary.py.in
icons/Makefile
m4/Makefile
dic/Makefile
)

AC_OUTPUT
