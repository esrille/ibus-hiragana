# -*- coding: utf-8 -*-
#
# ibus-replace-with-kanji - Replace With Kanji input method for IBus
#
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

# ローマ字かな変換表(Default)
layout = {
    "Roomazi": {
        '!'  :'！', '"'  :'・', '#'  :'＃', '$'  :'＄', '%'  :'％',
        '&'  :'＆', '\'' :'　', '('  :'（', ')'  :'）', '*'  :'＊',
        '+'  :'＋', ','  :'、', '-'  :'ー', '.'  :'。', '/'  :'・',
        '1'  :'１', '2'  :'２', '3'  :'３', '4'  :'４', '5'  :'５',
        '6'  :'６', '7'  :'７', '8'  :'８', '9'  :'９', '0'  :'０',
        ':'  :'：', ';'  :'；', '<'  :'＜', '='  :'＝', '>'  :'＞',
        '?'  :'？', '@'  :'＠', '['  :'「', ']' :'」',
        '^'  :'＾', '_'  :'＿', '`'  :'…', '{'  :'『', '|'  :'｜',
        '}'  :'』', '~'  :'〜',

        'a'  :'あ', 'i'  :'い', 'u'  :'う', 'e'  :'え', 'o'  :'お',
        'xa' :'ぁ', 'xi' :'ぃ', 'xu' :'ぅ', 'xe' :'ぇ', 'xo' :'ぉ',
        'vu' :'ゔ',
        'ka' :'か', 'ki' :'き', 'ku' :'く', 'ke' :'け', 'ko' :'こ',
        'sa' :'さ', 'si' :'し', 'su' :'す', 'se' :'せ', 'so' :'そ',
        'ta' :'た', 'ti' :'ち', 'tu' :'つ', 'te' :'て', 'to' :'と',
        'xtu':'っ',
        'na' :'な', 'ni' :'に', 'nu' :'ぬ', 'ne' :'ね', 'no' :'の',
        'ha' :'は', 'hi' :'ひ', 'hu' :'ふ', 'he' :'へ', 'ho' :'ほ',
        'ma' :'ま', 'mi' :'み', 'mu' :'む', 'me' :'め', 'mo' :'も',
        'ya' :'や', 'yu' :'ゆ', 'yo' :'よ',
        'xya':'ゃ', 'xyu':'ゅ', 'xyo':'ょ',
        'ra' :'ら', 'ri' :'り', 'ru' :'る', 're' :'れ', 'ro' :'ろ',
        'wa' :'わ', 'wo' :'を', 'nn' :'ん', 'n\'':'ん',
        'ga' :'が', 'gi' :'ぎ', 'gu' :'ぐ', 'ge' :'げ', 'go' :'ご',
        'za' :'ざ', 'zi' :'じ', 'zu' :'ず', 'ze' :'ぜ', 'zo' :'ぞ',
        'da' :'だ', 'di' :'ぢ', 'du' :'づ', 'de' :'で', 'do' :'ど',
        'ba' :'ば', 'bi' :'び', 'bu' :'ぶ', 'be' :'べ', 'bo' :'ぼ',
        'pa' :'ぱ', 'pi' :'ぴ', 'pu' :'ぷ', 'pe' :'ぺ', 'po' :'ぽ',
        'kya':'きゃ', 'kyu':'きゅ', 'kyo':'きょ',
        'sya':'しゃ', 'syu':'しゅ', 'syo':'しょ',
        'tya':'ちゃ', 'tyu':'ちゅ', 'tyo':'ちょ',
        'nya':'にゃ', 'nyu':'にゅ', 'nyo':'にょ',
        'hya':'ひゃ', 'hyu':'ひゅ', 'hyo':'ひょ',
        'mya':'みゃ', 'myu':'みゅ', 'myo':'みょ',
        'rya':'りゃ', 'ryu':'りゅ', 'ryo':'りょ',
        'gya':'ぎゃ', 'gyu':'ぎゅ', 'gyo':'ぎょ',
        'zya':'じゃ', 'zyu':'じゅ', 'zyo':'じょ',
        'bya':'びゃ', 'byu':'びゅ', 'byo':'びょ',
        'pya':'ぴゃ', 'pyu':'ぴゅ', 'pyo':'ぴょ',

        # ワープロ式
        'xka':'ヵ', 'xke':'ヶ',
        'xwa':'ゎ', 'wyi':'ゐ', 'wye':'ゑ',

        # 99式
        'yi':'いぃ', 'ye':'いぇ',
        'kyi':'きぃ', 'kye':'きぇ',
        'syi':'しぃ', 'sye':'しぇ',
        'tyi':'ちぃ', 'tye':'ちぇ',
        'nyi':'にぃ', 'nye':'にぇ',
        'hyi':'ひぃ', 'hye':'ひぇ',
        'myi':'みぃ', 'mye':'みぇ',
        'ryi':'りぃ', 'rye':'りぇ',
        'gyi':'ぎぃ', 'gye':'ぎぇ',
        'zyi':'じぃ', 'zye':'じぇ',
        'byi':'びぃ', 'bye':'びぇ',
        'pyi':'ぴぃ', 'pye':'ぴぇ',
        'wi':'うぃ', 'we':'うぇ',
        'kwa':'くぁ', 'kwi':'くぃ', 'kwu':'くぅ', 'kwe':'くぇ', 'kwo':'くぉ',
        'swa':'すぁ', 'swi':'すぃ', 'swu':'すぅ', 'swe':'すぇ', 'swo':'すぉ',
        'nwa':'ぬぁ', 'nwi':'ぬぃ', 'nwu':'ぬぅ', 'nwe':'ぬぇ', 'nwo':'ぬぉ',
        'mwa':'むぁ', 'mwi':'むぃ', 'mwu':'むぅ', 'mwe':'むぇ', 'mwo':'むぉ',
        'rwa':'るぁ', 'rwi':'るぃ', 'rwu':'るぅ', 'rwe':'るぇ', 'rwo':'るぉ',
        'gwa':'ぐぁ', 'gwi':'ぐぃ', 'gwu':'ぐぅ', 'gwe':'ぐぇ', 'gwo':'ぐぉ',
        'bwa':'ぶぁ', 'bwi':'ぶぃ', 'bwu':'ぶぅ', 'bwe':'ぶぇ', 'bwo':'ぶぉ',
        'pwa':'ぷぁ', 'pwi':'ぷぃ', 'pwu':'ぷぅ', 'pwe':'ぷぇ', 'pwo':'ぷぉ',
        'tsa':'つぁ', 'tsi':'つぃ', 'tsu':'つぅ', 'tse':'つぇ', 'tso':'つぉ',
        'zwa':'づぁ', 'zwi':'づぃ', 'zwu':'づぅ', 'zwe':'づぇ', 'zwo':'づぉ',
        'twa':'とぁ', 'twi':'とぃ', 'twu':'とぅ', 'twe':'とぇ', 'two':'とぉ',
        'dwa':'どぁ', 'dwi':'どぃ', 'dwu':'どぅ', 'dwe':'どぇ', 'dwo':'どぉ',
        'fa':'ふぁ', 'fi':'ふぃ', 'fu':'ふぅ', 'fe':'ふぇ', 'fo':'ふぉ',
        'hwa':'ほぁ', 'hwi':'ほぃ', 'hwu':'ほぅ', 'hwe':'ほぇ', 'hwo':'ほぉ',
        'va':'ゔぁ', 'vi':'ゔぃ', 'vu':'ゔ', 've':'ゔぇ', 'vo':'ゔぉ',
        'tja':'てゃ', 'tji':'てぃ', 'tju':'てゅ', 'tje':'てぇ', 'tjo':'てょ',
        'dja':'でゃ', 'dji':'でぃ', 'dju':'でゅ', 'dje':'でぇ', 'djo':'でょ',
        'fya':'ふゃ', 'fyu':'ふゅ', 'fyo':'ふょ',
        'vya':'ゔゃ', 'vyu':'ゔゅ', 'vyo':'ゔょ',
        'dya':'ぢゃ', 'dyi':'ぢぃ', 'dyu':'ぢゅ',
        'dye':'ぢぇ', 'dyo':'ぢょ',

        # ヘボン式
        'sha':'しゃ', 'shi':'し', 'shu':'しゅ', 'she':'しぇ', 'sho':'しょ',
        'cha':'ちゃ', 'chi':'ち', 'chu':'ちゅ', 'che':'ちぇ', 'cho':'ちょ',
        'ja':'じゃ', 'ji':'じ', 'ju':'じゅ', 'je':'じぇ', 'jo':'じょ',

        # 1音の動詞
        '\\i':'射', '\\xi':'生',
        '\\u':'売', '\\e':'得',
        '\\o':'負', '\\xo':'織',
        '\\ka':'買', '\\ga':'飼', '\\xka':'欠',
        '\\ki':'切', '\\gi':'着',
        '\\ta':'裁',
        '\\to':'解', '\\do':'説',
        '\\ni':'似', '\\xni':'煮',
        '\\\\':'￥',

        # Mozc互換
        'z ': '　',
        'z.': '…',
        'z/': '・',
        'z[': '『',
        'z]': '』'
    }
}
