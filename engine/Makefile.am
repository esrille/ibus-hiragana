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

engine_replace_with_kanji_PYTHON = \
	dictionary.py \
	engine.py \
	main.py \
	roomazi.py \
	$(NULL)
engine_replace_with_kanjidir = $(datadir)/ibus-replace-with-kanji

libexec_SCRIPTS= ibus-engine-replace-with-kanji

bin_SCRIPTS = ibus-engine-replace-with-kanji

component_DATA = replace-with-kanji-python.xml
componentdir = @IBUS_DATADIR@/ibus/component

CLEANFILES = \
	*.pyc \
	$(NULL)

EXTRA_DIST = \
	dictionary.py.in.in \
	ibus-engine-replace-with-kanji.in \
	replace-with-kanji-python.xml.in.in \
	$(NULL)

dictionary.py: dictionary.py.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

replace-with-kanji-python.xml: replace-with-kanji-python.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

test:
	$(ENV) \
		LANG=en_US \
		PYTHONPATH=$(top_srcdir) \
		$(PYTHON) $(srcdir)/main.py

