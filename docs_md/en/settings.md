# Settings

## Hiragana IME Setup Window {: #ibus-setup-hiragana}

You can customize the Hiragana IME in the **Hiragana IME Setup** window.
To open the **Hiragana IME Setup** window, select **Setup** from the keyboard menu in the desktop top bar.

![Keyboard menu](keyboard-menu.png)

![Hiragana IME Setup Window](ibus-setup-hiragana_1.png)

The **Hiragana IME Setup** window has the following three tabs:

<nobr>Tab</nobr> | Description
---|---
[Keyboard](#layout) | Switch between Kana input and Rōmaji input.
[Dictionary](#dictionary) | Select the kanji dictionary.
[Option](#option) | Choose the optional settings.

<!--Click **OK** or **Accept** to confirm the settings immediately.-->

## Keyboard Tab {: #layout}

In the **Keyboard** tab, you can select the Japanese input method using the keyboard.

![Hiragana IME Setup Window](ibus-setup-hiragana_1.png)

Choose the Japanese input method you like from the **Input** drop-down list:

Input | Description
---|---
[Rōmaji](roomazi.html#roomazi) | Use Rōmaji.
[Kana (JIS Layout)](layouts.html#jis) | Use the standard JIS Kana layout.
[<nobr>Kana (New Stickney Layout)</nobr>](layouts.html#new_stickney) | Use New Stickney Kana layout.

Rōmaji input and Kana input are commonly used when entering Japanese sentences using the keyboard.
Rōmaji input is taught in the third grade at school.
You can use Kana input even if you are unfamiliar with Rōmaji.
Using Kana input, you can enter Japanese sentences with fewer keystrokes than using Rōmaji input.

### Always convert ‘nn’ to ‘ん’ {: #nn}

If you want to enter ‘ん’ by typing <kbd>n</kbd><kbd>n</kbd>, enable **Always convert ‘nn’ to ‘ん’** option.

Option | Input | Output
--|--|--
Enabled | konnnitiha | こんにちは
Disabled | konnitiha | こんにちは

If you have been using word processors for a long time, you would be familiar with this behavior.
However, this <kbd>n</kbd><kbd>n</kbd> method was deprecated in 2009 at JIS, and currently, no standard validates this convention.
The correct Rōmaji spelling for 'ん' is <kbd>n</kbd>, or <kbd>n</kbd><kbd>'</kbd> if 'n' is followed by one of 'aiueoy'.

**Hint**: You can also enter 'ん' by pressing the <kbd>Enter</kbd> key after 'n'.

## Dictionary Tab {: #dictionary}

Choose the dictionary for kana-kanji conversion from the the **Kanji Dictionary** combo box.
The Hiragana IME offers dictionaries for each school grade level and an edition assembled for grown up.

![Hiragana IME Setup Window](ibus-setup-hiragana_2.png)

The dictionaries for students in 10th grade and above are composed using kanji from the *List of Chinese Characters in Common Use*, known as the *[Jōyō Kanji Table](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/)*, and kanji characters for use in personal names, known as the *[Jinmeiyō Kanji Table](http://www.moj.go.jp/MINJI/minji86.html)*. The grade-specific dictionary is structured according to the table provided by [MEXT](http://www.mext.go.jp/a_menu/shotou/new-cs/1385768.htm).

*Okurigana* are hiragana suffixes attached to words written with kanji characters. Guidelines on using *okurigana* have been issued as a public notice through the Prime Minister in Japan. Children learn these rules at school. In practice, there are variations in okurigana. The Hiragana IME provides two types of dictionaries for convenience.

Dictionary | Description
--|--
Okurigana: strict | Follow the main rules strictly.
Okurigana: permissive | Permit the use of widely used variations.

For example, the ‘10th+ grade (Okurigana: general + permissible)’ dictionary allows conversions like ‘<ruby>落<rp>(</rp><rt>おと</rt><rp>)</rp></ruby>す’.

Main rules | Permissible rules
--|--
お<span class='key'>変換</span>とす → 落とす | おと<span class='key'>変換</span>す → 落す
おこな<span class='key'>変換</span>って → 行って | おこ<span class='key'>変換</span>なって → 行なって

Understanding *okurigana* can be quite challenging.
Without furigana, ‘<ruby>行<rp>(</rp><rt>おこな</rt><rp>)</rp></ruby>って’ and ‘<ruby>行<rp>(</rp><rt>い</rt><rp>)</rp></ruby>って’ cannot be distinguished by the main rule alone. On the other hand, people who are knowledgeable about kanji do not struggle with reading  ‘<ruby>落<rp>(</rp><rt>おと</rt><rp>)</rp></ruby>す.’

The public notice does not mandate using kanji; it simply provides guidelines on how to add okurigana when using kanji. In the Japanese version of this guide, most Japanese words are written only in hiragana.

### User dictionary

You can add words to your personal dictionary if you can not find a word in the default Hiragana IME dictionaries.

You may switch among multiple user dictionaries.
Your dictionaries are stored in the directory ~/.local/share/ibus-hiragana/.
Enter the preferred user dictionary file name in the **User Dictionary Name** textbox.
By default, 'my.dic' is used.

Click **Edit** to edit your dictionary.
The personal dictionary files are text files using the following format.

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

Press the **OK** or **Apply** button to use the edited personal dictionary. You don't have to restart your PC.

### Adding words with okurigana (*for Advanced Users Only*) {: #okurigana}

In user dictionaries, the reading section of a word with okurigana contains only the hiragana part to be replaced with kanji and terminated with a horizontal bar (―).

The format of the word section changes based on its grammatical part of speech and conjugation type, as described below.

#### For verbs with Godan conjugation:

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

#### For verbs with Kami-ichiidan or Shimo-ichidan conjugation:

In the word section, write kanji, the first letter of the okurigana, which is one of the letters in イ (i)-dan or エ (e)-dan, and the conjugative suffix symbol: *1*.

Conjugation Type | Reading Section | Word Section
---|---|---
Kami-ichiidan | お― | 起き1
Shimo-ichidan | み― | 見え1

#### For イ (i)-adjectives

In the ‘word’ section, write the kanji, the okurigana up to (if any) the conjugative suffix, and the conjugative suffix symbol: *i*.

Reading section | Word section
---|---
あか― | 赤i
つめ― | 冷たi

#### For ナ (na)-adjectives

In the word section, write kanji and then stem in hiragana.

Reading section | Word section
---|---
あき― | 明らか
しず― | 静か

#### The other types of *okurigana*

In the word section, write kanji and okurigana as they are.

Reading section | Word section
---|---
ひと― | 独り
すこ― | 少し

### Clearing the input history

During the conversion of homonyms and words with shortened readings, the frequently used ones will appear at the beginning of the candidate list. If you want to reset the orders to the initial state, turn on the **Clear input history** switch and click **Apply**.

## Option Tab {: #option}

You can customize the input assistance feature.

![「Hiragana IME Setup」Window](ibus-setup-hiragana_3.png)

### Use LLM for candidate selection {: #llm}

This feature utilizes so-called *AI*. LLM stands for Large Language Model.
When enabled, the Hiragana IME calculates the probabilities of each candidate's occurrence in its surrounding text and pre-selects the most probable candidate in the candidate window..

For example, when converting ‘のぼる’, the pre-selected candidate changes as below depending on the surrounding text:

- 山に<span style="background-color:#d1eaff">登る</span>
- 日が<span style="background-color:#d1eaff">昇る</span>

**Note**: Since this is merely based on a probability calculation, the desired candidate may not always be chosen. This feature is disabled by default because it requires a relatively large amount of computational power.

### Combine '^' to the previous vowel character in alphanumeric mode {: #combining-circumflex}

Enable this option if you want to write Japanese in Rōmaji.
When you type <span class='key'>^</span> after a vowel character in Alphanumeric mode, it is combined into a single character.

- Example: a<span class='key'>^</span> → â

When you type <span class='key'>^</span> after a vowel character combined with a circumflex, it is separated back into two characters.

- Example: â<span class='key'>^</span> → a^
