# Copyright (c) 2019-2022 Esrille Inc.
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

dist_help_DATA = \
	default.css \
	altgr.html \
	index.html \
	install.html \
	key_assign.html \
	layouts.html \
	roomazi.html \
	settings.html \
	usage.html \
	screenshot.webm \
	undo.webm \
	ibus-setup-hiragana_1.png \
	ibus-setup-hiragana_2.png \
	icon.png \
	input-mode.png \
	keyboard-menu.png \
	screenshot.png \
	settings-altgr.png \
	settings-keyboard.png \
	$(NULL)

helpdir = $(pkgdatadir)/help

EXTRA_DIST = \
	Makefile.am \
	template.html \
	md2html.py \
	toc.py \
	altgr.md \
	index.md \
	install.md \
	key_assign.md \
	layouts.md \
	roomazi.md \
	settings.md \
	usage.md \
	$(NULL)

uninstall-hook:
	-rmdir $(helpdir)

if ENABLE_HTML

CLEANFILES = \
	toc.txt \
	altgr.html \
	index.html \
	install.html \
	key_assign.html \
	layouts.html \
	roomazi.html \
	settings.html \
	usage.html \
	$(NULL)

toc.txt : index.md install.md usage.md key_assign.md settings.md layouts.md roomazi.md altgr.md toc.py
	./toc.py $(wordlist 1,8,$^) > $@

index.html: index.md altgr.md install.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

install.html: install.md index.md usage.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

usage.html: usage.md install.md key_assign.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

key_assign.html: key_assign.md usage.md settings.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

settings.html: settings.md key_assign.md layouts.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

layouts.html: layouts.md settings.md roomazi.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

roomazi.html: roomazi.md layouts.md altgr.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

altgr.html: altgr.md roomazi.md index.md template.html toc.txt md2html.py
	./md2html.py $(wordlist 1,4,$^)

endif
