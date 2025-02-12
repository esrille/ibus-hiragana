# Settings

## Hiragana IME Setup Window {: #ibus-setup-hiragana}

You can customize Hiragana IME in the **Hiragana IME Setup** window.
To open the **Hiragana IME Setup** window, select **Setup** from the keyboard menu in the desktop top bar.

![Keyboard menu](keyboard-menu.png)

![Hiragana IME Setup Window](ibus-setup-hiragana_1.png)

The **Hiragana IME Setup** window has the following three tabs:

<nobr>Tab</nobr> | Description
---|---
[Keyboard](#layout) | Switch between Kana input and Rōmaji input.
[Dictionary](#dictionary) | Select the kanji dictionary.
[Option](#option) | Choose the optional settings.

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

### Always convert 'nn' to 'ん' {: #nn}

If you want to enter 'ん' by typing <kbd>n</kbd><kbd>n</kbd>, enable **Always convert 'nn' to 'ん'** option.

Option | Input | Output
--|--|--
Enabled | konnnitiha | こんにちは
Disabled | konnitiha | こんにちは

**Note**: This classic Japanese word processor method is incorrect as Rōmaji spelling.
The JIS standard X4063, which defined this method, was deprecated in 2010.

## Dictionary Tab {: #dictionary}

In the **Dictionary** tab, you can set up the dictionaries used for kana-kanji conversion.

![Hiragana IME Setup Window](ibus-setup-hiragana_2.png)

### Kanji Dictionary

Choose your preferred dictionary from the **Kanji Dictionary** drop-down list.
Hiragana IME offers dictionaries for elementary, middle, and high school students, as well as for adults.
Details about the grade-specific dictionaries are described in the [Hiragana IME Dictionary](dictionary.html).


### User Dictionary Name

You can add words to your personal dictionary if you can not find them in Hiragana IME dictionaries.
You may switch among multiple user dictionaries.

Enter the preferred user dictionary file name in the **User Dictionary Name** textbox.
By default, 'my.dic' is used.
Your dictionaries are stored in the directory <code>~/.local/share/ibus-hiragana/</code>.

Click **Edit** to edit your dictionary.
The file format of the Hiragana IME dictionary is described in [Editing Dictionaries](dictionary.html#personal-dictionary).

### Use permissible okurigana

*Okurigana* are hiragana suffixes attached to words written with kanji characters.
Guidelines on using okurigana have been issued as a [public notice](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/okurikana/index.html) through the Prime Minister in Japan.
Children learn these rules at school.

In practice, there are variations in okurigana.
Turn on the **Use permissible okurigana** switch to use permissible okurigana.
Note that this switch is only effective when using the **Kanji Dictionary** for Adults.

**Examples**:

Main rules | Permissible rules
--|--
お<span class='key'>変換</span>とす → 落とす | おと<span class='key'>変換</span>す → 落す
おこな<span class='key'>変換</span>って → 行って | おこ<span class='key'>変換</span>なって → 行なって
とど<span class='key'>変換</span>けで<span class='key'>変換</span> → 届け出 | とどけで<span class='key'>変換</span> → 届出

Understanding the okurigana rules can be quite challenging.
Without furigana, '<ruby>行<rp>(</rp><rt>おこな</rt><rp>)</rp></ruby>って' and '<ruby>行<rp>(</rp><rt>い</rt><rp>)</rp></ruby>って' cannot be distinguished by the main rules alone. On the other hand, people who are knowledgeable about kanji do not struggle with reading  '<ruby>落<rp>(</rp><rt>おと</rt><rp>)</rp></ruby>す'.
The public notice does not mandate using kanji; it simply provides guidelines on how to add or remove okurigana when using kanji. In the Japanese version of this guide, most Japanese words are written only in hiragana.

### Input history

In the conversion candidate window, frequently used words will appear at the top of the list.
To reset all orders to their initial state, click the **Clear…** button.
Then, click **OK** when the following message box appears.

![Hiragana IME Setup Window](ibus-setup-hiragana_4.png)

## Option Tab {: #option}

In the **Option** tab, you can customize the input assistance features.

![「Hiragana IME Setup」Window](ibus-setup-hiragana_3.png)

### Use half-width digits for Arabic numerals {: #half-width-digits}

When enabled, Hiragana IME enters Arabic numerals using half-width letters, even in Hiragana mode.

Setting | Example
--|--
Off | １２、３４５。６７８
On | 12,345.678

### Combine '^' to the previous vowel character in alphanumeric mode {: #combining-circumflex}

Enable this option if you want to write Japanese in Kunrei-shiki Rōmaji.
When you type <span class='key'>^</span> after a vowel character in Alphanumeric mode, it is combined into a single character.

- Example: a<span class='key'>^</span> → â

When you type <span class='key'>^</span> after a vowel character combined with a circumflex, it is separated back into a vowel and '^'.

- Example: â<span class='key'>^</span> → a^

### Combine '~' to the previous vowel character in alphanumeric mode as '¯' {: #combining-macron}

Enable this option if you want to write Japanese in Hepburn romanization.
When you type <span class='key'>~</span> after a vowel character in Alphanumeric mode, it is combined into a single character as '¯'.

- Example: a<span class='key'>~</span> → ā

When you type <span class='key'>~</span> after a vowel character combined with a macron, it is separated back into a vowel and '~'.

- Example: ā<span class='key'>~</span> → a~

### Use LLM for candidate selection {: #llm}

When enabled, Hiragana IME calculates the probabilities of each candidate's occurrence in the surrounding text and pre-selects the most probable candidate in the candidate window.

For example, when converting 'かいとう', the pre-selected candidate changes as below:

- アンケートにかいとう<span class='key'>変換</span> → アンケートに<span style="background-color:#d1eaff">回答</span>
- 問題のかいとう<span class='key'>変換</span> → 問題の<span style="background-color:#d1eaff">解答</span>

### Use CUDA for LLM calculation {: #cuda}

When enabled, Hiragana IME uses CUDA to calculate the probabilities of each candidate's occurrence with LLM.
If your PC has an NVIDIA GPU, you can reduce the time it takes for the candidate to appear after pressing the conversion key.

**Note**: An NVIDIA driver is necessary to use CUDA with your GPU.
Newer Fedora and Ubuntu offer NVIDIA drivers from the official software repositories.
If the driver is successfully installed, you can see your GPU model name in the **[About](usage.html#about)** dialog box.

### Install required packages for using LLM {: #transformers}

By clicking the **Install…** button, you can install the required packages to use LLM for candidate selection.
For more details, please see "[Install additional components for using LLM](install.html#llm)".
