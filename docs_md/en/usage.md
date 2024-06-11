# Usage

**Note**: For instructions on switching between Romaji input and Kana input, refer to **Settings** - [Keyboard Tab](settings.html#layout).

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

![Input modes](../input-modes.gif)

- With Japanese keyboards, you can switch between Hiragana and Alphanumeric modes by pressing <span class='key'>変換</span> and <span class='key'>無変換</span> keys, respectively.
- With English keyboards, you can toggle between Hiragana and Alphanumeric modes by pressing the <span class='key'>Caps Lock</span> key. Hiragana IME is in Hiragana mode when the Caps Lock LED is turned on.

## Inputting Kanji and Katakana Words {: #input-kanji}

To enter a Kanji or Katana word, type the word in Hiragana first, then press the <span class='key'>変換</span> key to convert the word into Kanji or Katakana.
The text cursor should be at the end of the word before you convert it.
For example, to enter the sentence "しろうとむけのワープロの登場を期待したいですね。", type as follows in Hiragana mode:

<pre><code>siroutomukenowa-puro<span class='key'>変換</span>notouzyou<span class='key'>変換</span>wokitai<span class='key'>変換</span>sitaidesune.
</code></pre>

Or as follows using Kana input:

<pre><code>しろうとむけのわーぷろ<span class='key'>変換</span>のとうじょう<span class='key'>変換</span>をきたい<span class='key'>変換</span>したいですね。
</code></pre>

<br>**Homonyms**: With Kanji, there are words with the same reading but different meanings, like "衛星" (satellite) and "衛生" (hygiene). These words are called homonyms. When you encounter homonyms, use the <span class='key'>変換</span> key to select the right word from the candidate list. You can also use the up and down arrow keys to select the candidate.

Later, when you convert the same homonym again, the last selected word will appear first in the candidate list. Less frequently used homonyms will move towards the end of the list.
So you won't have to keep selecting between homonyms over time.

## Entering Words with Okurigana {: #input-okurigana}

To enter a word with okurigana, press the <span class='key'>変換</span> key right after the part written in kanji. For example, to enter the sentence "赤いチューリップの花が咲きました。", you will type as follows:

<pre><code>aka<span class='key'>変換</span>ityu-rippu<span class='key'>変換</span>nohana<span class='key'>変換</span>gasa<span class='key'>変換</span>kimasita.
</code></pre>

Or like below using Kana input:

<pre><code>あか<span class='key'>変換</span>いちゅーりっぷ<span class='key'>変換</span>のはな<span class='key'>変換</span>がさ<span class='key'>変換</span>きました。
</code></pre>

When you type the first okurigana for a word, the word appears in kanji.
If you press the <span class='key'>変換</span> key instead of typing okurigana, all candidates will appear.

Here are some examples:

- おく<span class='key'>変換</span>→ <span style="background-color:#d1eaff">おく―</span><span class='key'>Enter</span> → 後，遅，送，贈
- おく<span class='key'>変換</span>→ <span style="background-color:#d1eaff">おく―</span><span class='key'>る</span> → 送る，贈る

As you type okurigana, the candidate list becomes shorter.

When there are multiple conversion candidates, select the one that ends with a '―' (horizontal bar). For example, when you want to convert "咲き", select the candidate "<span style="background-color:#d1eaff">さ―</span>".
Initially, the conversion candidate ending with a '―' may be at the bottom of the list. However, after using the word, it will move to the top of the list. In this way, you can save the keystrokes.

## Changing the Length of the Reading {: #input-shrink}

When you want to enter "生きがい論", you will type as below:

<pre><code>生きがいろん<span class='key'>変換</span></code></pre>

When converting a word into Kanji or Katakana, Hiragana IME selects words with the longest reading. Therefore, Hiragana IME initially selects "概論" (がいろん) instead of "論" (ろん). The screen will be changed like below:

<pre><code>生き<span style="background-color:#d1eaff">概論</span></code></pre>

Press the <span class='key'>Tab</span> key to shorten the reading. The reading will be shortened to 'いろん', and the screen will change to:

<pre><code>生きが<span style="background-color:#d1eaff">異論</span></code></pre>

Press the <span class='key'>Tab</span> key to shorten the reading again to 'ろん'. The screen will change to '生きがい論' as intended, like below:

<pre><code>生きがい<span style="background-color:#d1eaff">論</span></code></pre>

When using a shortened word next time, it will appear at the beginning of the candidate list, just like homonyms do.
