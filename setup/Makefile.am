# Copyright (c) 2020 Esrille Inc.
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

setup_hiragana_PYTHON = \
	main.py \
	setup.glade \
	$(NULL)
BUILT_SOURCES = package.py
nodist_setup_hiragana_PYTHON = package.py
setup_hiraganadir = $(pkgdatadir)/setup

libexec_SCRIPTS = ibus-setup-hiragana

desktop_DATA = ibus-setup-hiragana.desktop
desktopdir = $(datadir)/applications

CLEANFILES = \
	ibus-setup-hiragana \
	ibus-setup-hiragana.desktop \
	ibus-setup-hiragana.in \
	package.py \
	package.py.in \
	$(NULL)

EXTRA_DIST = \
	ibus-setup-hiragana.desktop.in \
	ibus-setup-hiragana.in.in \
	package.py.in.in \
	$(NULL)

package.py: package.py.in
	$(AM_V_GEN) \
	( \
		pkgdatadir=${pkgdatadir}; \
		localedir=${localedir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

ibus-setup-hiragana: ibus-setup-hiragana.in
	$(AM_V_GEN) \
	( \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

ibus-setup-hiragana.desktop: ibus-setup-hiragana.desktop.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@
