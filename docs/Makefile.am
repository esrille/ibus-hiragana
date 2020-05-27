# Copyright (c) 2019-2020 Esrille Inc.
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

help_DATA = \
	default.css \
	dictionary.html \
	experimental.html \
	index.html \
	install.html \
	key_assign.html \
	layouts.html \
	settings.html \
	template.html \
	usage.html \
	dconf-editor.png \
	icon.png \
	screenshot.png \
	settings-dictionary.png \
	settings-layout.png \
	settings-nn.png \
	$(NULL)

helpdir = $(pkgdatadir)/help

EXTRA_DIST = \
	update \
	Makefile.am \
	md2html.py \
	dictionary.md \
	experimental.md \
	index.md \
	install.md \
	key_assign.md \
	layouts.md \
	settings.md \
	usage.md \
	default.css \
	dictionary.html \
	experimental.html \
	index.html \
	install.html \
	key_assign.html \
	layouts.html \
	settings.html \
	template.html \
	usage.html \
	dconf-editor.png \
	icon.png \
	screenshot.png \
	settings-dictionary.png \
	settings-layout.png \
	settings-nn.png \
	$(NULL)

uninstall-hook:
	-rmdir $(helpdir)
