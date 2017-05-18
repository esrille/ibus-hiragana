# Copyright (c) 2017 Esrille Inc.
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

AC_INIT([ibus-replace-with-kanji], [0.2.1], [https://github.com/esrille/ibus-replace-with-kanji/issues])
AM_INIT_AUTOMAKE([foreign])

# Check IBus
#   Note replace-with-kanji-python.xml uses icon_prop_key and
#   ibus 1.5.11 or later is required
PKG_CHECK_MODULES(IBUS, [ibus-1.0 >= 1.5.11])
AC_SUBST(IBUS_DATADIR, $($PKG_CONFIG --variable=datadir ibus-1.0) )

# Check Python
AM_PATH_PYTHON([3.3])

# OUTPUT files
AC_CONFIG_FILES(Makefile
ibus-replace-with-kanji.spec
engine/Makefile
engine/ibus-engine-replace-with-kanji
engine/replace-with-kanji-python.xml.in
icons/Makefile
layouts/Makefile
dic/Makefile
dic_tools/Makefile
)

AC_OUTPUT
