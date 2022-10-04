# Copyright (c) 2017-2022 Esrille Inc.
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

TOOLS_DIR = ../dic_tools

dic_DATA = \
	restrained.dic \
	restrained.1.dic \
	restrained.2.dic \
	restrained.3.dic \
	restrained.4.dic \
	restrained.5.dic \
	restrained.6.dic \
	restrained.7.dic \
	restrained.9.dic \
	katakana.dic \
	$(NULL)

dicdir = $(pkgdatadir)

EXTRA_DIST = $(dic_DATA) COPYING

if ENABLE_DIC

CLEANFILES = $(dic_DATA)

katakana.dic : $(TOOLS_DIR)/third_party/edrdg/edict2
	$(TOOLS_DIR)/katakana.py $< > $@

restrained.1.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 1 > $@

restrained.2.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 2 > $@

restrained.3.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 3 > $@

restrained.4.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 4 > $@

restrained.5.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 5 > $@

restrained.6.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 6 > $@

restrained.7.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 7 > $@

restrained.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 8 > $@

restrained.9.dic : $(TOOLS_DIR)/third_party/skk/SKK-JISYO.ML
	$(TOOLS_DIR)/restrain.py $< 9 > $@

endif
