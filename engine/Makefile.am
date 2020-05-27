# Copyright (c) 2017-2020 Esrille Inc.
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

engine_replace_with_kanji_PYTHON = \
	bits.py \
	dictionary.py \
	engine.py \
	event.py \
	i18n.py \
	main.py \
	roomazi.py \
	$(NULL)

engine_replace_with_kanjidir = $(datadir)/ibus-replace-with-kanji

libexec_SCRIPTS= ibus-engine-replace-with-kanji

component_DATA = replace-with-kanji-python.xml
componentdir = @IBUS_DATADIR@/ibus/component

gsettings_SCHEMAS = org.freedesktop.ibus.engine.replace-with-kanji-python.gschema.xml

@GSETTINGS_RULES@

CLEANFILES = \
	ibus-engine-replace-with-kanji \
	org.freedesktop.ibus.engine.replace-with-kanji-python.gschema.xml \
	replace-with-kanji-python.xml \
	$(NULL)

EXTRA_DIST = \
	ibus-engine-replace-with-kanji.in \
	replace-with-kanji-python.xml.in.in \
	org.freedesktop.ibus.engine.replace-with-kanji-python.gschema.xml.in \
	$(NULL)

replace-with-kanji-python.xml: replace-with-kanji-python.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

org.freedesktop.ibus.engine.replace-with-kanji-python.gschema.xml: org.freedesktop.ibus.engine.replace-with-kanji-python.gschema.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@
