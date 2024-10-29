# The Hiragana IME Dictionary

Hiragana IME includes dictionaries specifically designed for elementary, middle, and high school students, as well as for adults.
As students move up each grade, they learn more kanji characters.
Consequently, the number of kanji words included in the Hiragana IME dictionaries also increases.

Kanji Dictionary | # of kanji to learn | # of words | Note
--|--:|--:|--
1st grade | 80 | 730
2nd grade | 160 | 3,210
3rd grade | 200 | 6,315
4th grade | 202 | 9,555
5th grade | 193 | 12,574
6th grade | 191 | 14,797 | Learn a total of 1,026 kanji in elementary school
7-9 grades | 1,110 | 29,975 | Learn to read approximately 1,110 more kanji
10-12 grades | (ditto) |32,078 | Learn to write approximately 1,110 more kanji
Adults | — | 34,596
Total | 2,136 | 34,596 | Learn 2,136 Jōyō kanji through schooling

(As of October, 2024)

The grade-specific dictionaries are structured according to the table provided by [MEXT](http://www.mext.go.jp/a_menu/shotou/new-cs/1385768.htm).
For personal names and place names, dictionaries for middle school students and above use kanji not listed in the list of Chinese characters in common use, known as the [Jōyō Kanji Table](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/).


**Note**:
With ordinary IMEs, people often use kanji characters not listed in the Jōyō kanji table, such as '￹此方￺こちら￻に' and '￹纏￺まと￻める'.
Using the Hiragana IME helps avoid these kanji characters that are not taught in schools.
When writing for foreigners living in Japan, it's helpful to know that the [JLPT](https://www.jlpt.jp/) N2 certification standard includes approximately 1,000 kanji and 6,000 words.

## Editing Dictionaries {: #personal-dictionary}

Hiragana IME's dictionary files are text files that use the following format:

```
; Lines starting with a semicolon (;) are comments.
; To add a word, write the reading, followed by a space, and then the word
; enclosed by slashes (/).
きれい /綺麗/
; When you prefix the reading with a minus sign (-), you can revoke words
; in the system dictionary.
-きれい /奇麗/
; Words with the same reading can be added together in one line.
かいざん /改竄/改ざん/
; The reading section of a word with okurigana contains only the hiragana
; part to be replaced with kanji and terminated with a horizontal bar (―).
ささや― /囁k/
あお― /碧i/
```

You can add words to your personal dictionary if you can not find them in Hiragana IME dictionaries.
To edit your personal dictionary, click the **Edit** button in the [Dictionary](settings.html#dictionary) tab of the Hiragana IME Setup Window.


## Adding words with okurigana {: #okurigana}

In user dictionaries, the reading section of a word with okurigana contains only the hiragana part to be replaced with kanji and terminated with a horizontal bar (―).
The format of the word section changes based on its grammatical type, as described below.

### For verbs with Godan conjugation:

In the word section, write kanji, okurigana up to (if any) the conjugative suffix, and one of the conjugative suffix symbols: *kgstnbmrw*.

Gyō | Reading Section | Word Section
---|---|---
か (ka) gyō | か― | 書k
が (ga) gyō | およ― | 泳g
さ (sa) gyō | ち― | 散らs
た (ta) gyō | う― | 打t
な (na) gyō | し― | 死n
ば (ba) gyō | あそ― | 遊b
ま (ma) gyō | あか― | 赤らm
ら (ra) gyō | あず― | 預かr
わ (wa) gyō | あ― | 会w

### For verbs with Kami-ichiidan or Shimo-ichidan conjugation:

In the word section, write kanji, the first letter of the okurigana, which is one of the letters in イ (i)-dan or エ (e)-dan, and the conjugative suffix symbol: *1*.

Conjugation Type | Reading Section | Word Section
---|---|---
Kami-ichiidan | お― | 起き1
Shimo-ichidan | み― | 見え1

### For イ (i)-adjectives

In the word section, write the kanji, the okurigana up to (if any) the conjugative suffix, and the conjugative suffix symbol: *i*.

Reading section | Word section
---|---
あか― | 赤i
つめ― | 冷たi

### For ナ (na)-adjectives

In the word section, write kanji and then stem in hiragana.

Reading section | Word section
---|---
あき― | 明らか
しず― | 静か

### The other types of *okurigana*

In the word section, write kanji and okurigana as they are.

Reading section | Word section
---|---
ひと― | 独り
すこ― | 少し


## Command-line dictionary tool {: #tool}

Hiragana IME provides a command-line tool called <code>ibus-hiragana-tool</code> for maintaining dictionaries.
This tool is especially useful for creating large personal dictionary files.

### Synopsis

```
ibus-hiragana-tool [-h] [-o OUTPUT] [--header] [--one] [--version]
[{diff,hyougai,hyougai-yomi,intersect,katakana,lookup,
  mazeyomi,symbol,taigen,union,wago,yougen,yutou,zyuubako} ...]
```

<code>ibus-hiragana-tool</code> takes a single sub-command as its argument.
For example, to merge two dictionary files, use the <code>union</code> command:


```
$ ibus-hiragana-tool union a.dic b.dic -o c.dic
```


In this example, a dictionary file named <code>c.dic</code> is created by merging <code>a.dic</code> and <code>b.dic</code>.
If the output file name is not specified with the <code>-o</code> option, the result will be printed into the standard output.

<code>ibus-hiragana-tool</code> supports the following sub-commands:

<nobr>Sub-command</nobr>| Description
--|--
diff | output words in the first input file that are not in other input files
hyougai | output words that use *hyōgai* kanji in input files
<nobr>hyougai-yomi</nobr> | output words that use *hyōgai-yomi* in input files
intersect | output words that are common to all input files
katakana | output words that are in katakana in input files
<nobr>lookup WORD</nobr> | find WORD in the input files
mazeyomi | output *yutō-yomi* and *jūbako-yomi* words in input files
symbol | output words using symbol characters in input files
taigen | output non-conjugating words with *okurigana* in input files, excluding single-kanji *taigen* listed in *jōyō* kanji table
union | output all words in input files
wago | output native Japanese words in input files
yougen | output conjugating words in input files, excluding single-kanji *yōgen* listed in *jōyō* kanji table
yutou | output *yutō-yomi* words in input files
zyuubako | output *jūbako-yomi* words in input files

And <code>ibus-hiragana-tool</code> support the following command-line options:

Option | Description
--|--
-h, --help | show help options
-o OUTPUT, --output OUTPUT | write output to OUTPUT
--header | output the header of the first input file
--one | list one word per line
--version | print version information
