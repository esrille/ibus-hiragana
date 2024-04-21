# Copyright (c) 2017-2024 Esrille Inc.
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

engine_hiragana_PYTHON = \
	dictionary.py \
	engine.py \
	event.py \
	main.py \
	$(NULL)
BUILT_SOURCES = package.py
nodist_engine_hiragana_PYTHON = package.py
engine_hiraganadir = $(pkgdatadir)/engine

libexec_SCRIPTS= ibus-engine-hiragana

component_DATA = hiragana.xml
componentdir = $(datadir)/ibus/component

gsettings_SCHEMAS = org.freedesktop.ibus.engine.hiragana.gschema.xml

@GSETTINGS_RULES@

CLEANFILES = \
	ibus-engine-hiragana \
	org.freedesktop.ibus.engine.hiragana.gschema.xml \
	package.py \
	hiragana.xml \
	$(NULL)

EXTRA_DIST = \
	ibus-engine-hiragana.in \
	org.freedesktop.ibus.engine.hiragana.gschema.xml.in \
	package.py.in.in \
	hiragana.xml.in.in \
	$(NULL)

package.py: package.py.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		localedir=${localedir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

hiragana.xml: hiragana.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

org.freedesktop.ibus.engine.hiragana.gschema.xml: org.freedesktop.ibus.engine.hiragana.gschema.xml.in
	$(AM_V_GEN) \
	( \
		pkgdatadir=${pkgdatadir}; \
		PACKAGE=${PACKAGE}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

uninstall-hook:
	-rmdir $(engine_hiraganadir)/__pycache__
	-rmdir $(engine_hiraganadir)
