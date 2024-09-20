# Usage

**Note**: For instructions on switching between Rōmaji input and Kana input, refer to **Settings** - [Keyboard Tab](settings.html#layout).

## Changing Input Modes {: #input-mode}

Hiragana IME has five input modes, as shown in the table below:

Symbol | Input Mode | Description
:---:|---|---
あ | Hiragana Mode | A mode for entering kanji and kana mixed text
A | Alphanumeric Mode | A mode for entering Latin alphabets and numbers
ア | Katakana Mode | A mode for entering katakana
Ａ | Full-width <nobr>Alphanumeric Mode</nobr> | A mode for entering Latin alphabets and numbers using full-width characters
ｱ | Half-width <nobr>Katakana Mode</nobr> | A mode for entering katakana using half-width characters

**Note**: You would switch between Hiragana and Alphanumeric modes frequently; the other input modes are rarely used.

The current input mode is displayed in the right corner of the desktop top bar.
The current input mode is Hiragana if 'あ' is shown and Alphanumeric if 'A' is shown.

![Input modes](../input-modes.gif)

- With Japanese keyboards, you can switch between Hiragana and Alphanumeric modes by pressing <span class='key'>変換</span> and <span class='key'>無変換</span> keys, respectively.
- With US keyboards, you can toggle between Hiragana and Alphanumeric modes by pressing the <span class='key'>Caps Lock</span> key. Hiragana IME is in Hiragana mode when the Caps Lock LED is turned on.

## Inputting Kanji and Katakana Words {: #input-kanji}

To enter a Kanji or Katana word, type the word in Hiragana first, then press the <span class='key'>変換</span> key to convert the word into Kanji or Katakana.
The text cursor should be at the end of the word before you convert it.
For example, to enter the sentence "しろうとむけのワープロの￹登場￺とうじょう￻を￹期待￺きたい￻したいですね。", type as follows in Hiragana mode:

<pre><code>siroutomukenowa-puro<span class='key'>変換</span>notouzyou<span class='key'>変換</span>wokitai<span class='key'>変換</span>sitaidesune.
</code></pre>

Or as follows using Kana input:

<pre><code>しろうとむけのわーぷろ<span class='key'>変換</span>のとうじょう<span class='key'>変換</span>をきたい<span class='key'>変換</span>したいですね。
</code></pre>

<br>**Homonyms**: With Kanji, there are words with the same reading but different meanings, like "￹衛星￺えいせい￻" (satellite) and "￹衛生￺えいせい￻" (hygiene).
These words are called homonyms.
When you encounter homonyms, use the <span class='key'>変換</span> key to select the right word from the candidate list.
You can also use the up and down arrow keys to select the candidate.
Later, the most recently selected word will appear first in the candidate list when you convert the same homonym again.

### Hints

- If you enable the [Use LLM for candidate selection](settings.html#llm) option, Hiragana IME will pre-select the most probable candidate from homonyms using LLM.
- Words not included in the Hiragana IME dictionaries won't appear in the candidate list when you press the <span class='key'>変換</span> key.
You can add new words to your [user dictionary](settings.html#dictionary).

## Entering Words with Okurigana {: #input-okurigana}

To enter a word with okurigana, press the <span class='key'>変換</span> key right after the part written in kanji.
For example, to enter the sentence "￹赤￺あか￻いチューリップの￹花￺はな￻が￹咲￺さ￻きました。", you will type as follows:

<pre><code>aka<span class='key'>変換</span>ityu-rippu<span class='key'>変換</span>nohana<span class='key'>変換</span>gasa<span class='key'>変換</span>kimasita.
</code></pre>

Or like below using Kana input:

<pre><code>あか<span class='key'>変換</span>いちゅーりっぷ<span class='key'>変換</span>のはな<span class='key'>変換</span>がさ<span class='key'>変換</span>きました。
</code></pre>

When there are multiple conversion candidates, select the one that ends with a '―' (horizontal bar).
For example, select the candidate "<span style="background-color:#d1eaff">さ―</span>" to enter "￹咲￺さ￻き".
After using the word with okurigana, it will also move to the top of the candidate list.

When you type the first okurigana for a word, the word appears in kanji.
If you press the <span class='key'>変換</span> key instead of typing okurigana, all candidates will appear.

Here are some examples:

- おく<span class='key'>変換</span>→ <span style="background-color:#d1eaff">おく―</span><span class='key'>Enter</span> → 後，遅，送，贈
- おく<span class='key'>変換</span>→ <span style="background-color:#d1eaff">おく―</span><span class='key'>る</span> → 送る，贈る

As you type okurigana characters, the number of candidates will decrease.
The okurigana ‘遅る’ is not common.
When you enter up to 'おくる', the candidates are narrowed down to '送る' and '贈る'.

## Changing the Length of the Reading {: #input-shrink}

When converting a word into Kanji or Katakana, Hiragana IME collects words with the longest reading.
Therefore, when you enter "わたしの￹生￺い￻きがい￹論￺ろん￻", Hiragana IME will initially select "￹概論￺がいろん￻" instead of "￹論￺ろん￻".

<pre><code>わたしの生きがいろん<span class='key'>変換</span></code></pre>
<pre><code>わたしの生き<span style="background-color:#d1eaff">概論</span></code></pre>

To shorten the reading, press the <span class='key'>Tab</span> key. The reading will be shortened to 'いろん' like below:

<pre><code>わたしの生き<span style="background-color:#d1eaff">概論</span><span class='key'>Tab</span></code></pre>
<pre><code>わたしの生きが<span style="background-color:#d1eaff">異論</span></code></pre>

Press the <span class='key'>Tab</span> key again to shorten the reading further.
The reading will be shortened to 'ろん' as intended, like below:

<pre><code>わたしの生きが<span style="background-color:#d1eaff">異論</span><span class='key'>Tab</span></code></pre>
<pre><code>わたしの生きがい<span style="background-color:#d1eaff">論</span></code></pre>

When you use the same expression next time, "<u>がい</u><span style="background-color:#d1eaff">論</span>" will appear at the beginning of the candidate list, just like homonyms.

<pre><code>わたしの生きがいろん<span class='key'>変換</span></code></pre>
<pre><code>わたしの生き<u>がい</u><span style="background-color:#d1eaff">論</span></code></pre>

<br>**Hint**: If you enable the [Use LLM for candidate selection](settings.html#llm) option,
a candidate with a shorter reading would appear according to the surrounding text.
When you want to enter "わたしの￹生￺い￻きがい￹論￺ろん￻", Hiragana IME will suggest "<u>がい</u><span style="background-color:#d1eaff">論</span>" as a candidate from the beginning, as shown below:

<pre><code>わたしの生きがいろん<span class='key'>変換</span></code></pre>
<pre><code>わたしの生き<u>がい</u><span style="background-color:#d1eaff">論</span></code></pre>

## Converting into Katakana {: #katanaka}

You can input katakana words using the <span class='key'>カタカナ</span> key even if they are not in the dictionary.
For example, follow these steps to convert "しどっち" into "シドッチ":

After pressing the <span class='key'>カタカナ</span> key, "ち" is converted into "チ" and is highlighted with a light blue background.

<pre><code>しどっち<span class='key'>カタカナ</span></code></pre>
<pre><code>しどっ<span style="background-color:#d1eaff">チ</span></code></pre>

By pressing the <span class='key'>カタカナ</span> key four times in total, you can get "シドッチ" in katakana.

<pre><code>しどっ<span style="background-color:#d1eaff">チ</span><span class='key'>カタカナ</span></code></pre>

<pre><code>しど<span style="background-color:#d1eaff">ッチ</span><span class='key'>カタカナ</span></code></pre>

<pre><code>し<span style="background-color:#d1eaff">ドッチ</span><span class='key'>カタカナ</span></code></pre>

<pre><code><span style="background-color:#d1eaff">シドッチ</span></code></pre>

You can add the new katakana word displayed with a light blue background to your input history. To do so, press the <span class='key'>Enter</span> key when the desired word is highlighted.

<pre><code><span style="background-color:#d1eaff">シドッチ</span><span class='key'>Enter</span></code></pre>

The next time you want to input "シドッチ", you can use the <span class='key'>変換</span> key to enter it.

<pre><code>しどっち<span class='key'>変換</span></code></pre>
<pre><code><span style="background-color:#d1eaff">シドッチ<span></code></pre>

<br>**Hint**: You can use the right <span class='key'>Shift</span> key instead of the <span class='key'>カタカナ</span> key.
<br>**Note**: If you want to use a katakana word after clearing your input history, [register](settings.html#dictionary) it into your personal dictionary.

## Find Information about Hiragana IME {: #about}

Select **About Hiragana IME…** from the keyboard menu on the top bar to open the **About** dialog box.

![Keyboard menu](keyboard-menu.png)

In the About dialog box, you see the following information:

- Hiragana IME version
- LLM and CUDA information

![About...](about.png)

You can also check your GPU model if you have enabled the [Use CUDA for LLM calculation](settings.html#option) option in the Settings window.
