# Copyright (c) 2019-2021 Esrille Inc.
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
	experimental.html \
	index.html \
	install.html \
	key_assign.html \
	layouts.html \
	settings.html \
	template.html \
	usage.html \
	icon.png \
	screenshot.png \
	ibus-setup-hiragana_1.png \
	ibus-setup-hiragana_2.png \
	$(NULL)

helpdir = $(pkgdatadir)/help

EXTRA_DIST = \
	update \
	Makefile.am \
	md2html.py \
	experimental.md \
	index.md \
	install.md \
	key_assign.md \
	layouts.md \
	settings.md \
	usage.md \
	$(NULL)

uninstall-hook:
	-rmdir $(helpdir)
