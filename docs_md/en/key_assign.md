# Key Bindings

The Hiragana IME uses the following key bindings.

**Note**:

1. When using Kana input, several keys may be used differently. Refer to each specific Kana keyboard layout.
2. Some Japanese keyboards replaces <span class='key'>変換</span> and <span class='key'>無変換</span> keys with <span class='key'>[あ]</span> and <span class='key'>[A]</span> keys respectively. With Hiragana IME, <span class='key'>[あ]</span> and <span class='key'>[A]</span> keys can be used as <span class='key'>変換</span> and <span class='key'>無変換</span> keys.

## Key Bindings for Changing Input Mode {: #input-mode}

<nobr>Japanese Keyboard</nobr> | <nobr>US Keyboard</nobr> | Action
:--|:--|---
<span class='key'>英数</span>,<br><span class='key'>全角/半角</span>| <span class='key'>Caps&nbsp;Lock</span> | Toggle between Alphanumeric mode and Hiragana mode.
<span class='key'>変換</span>,<br><span class='key'>カタカナ</span>| ― | Enter Hiragana mode.
<span class='key'>無変換</span>| ― | Enter Alphanumeric mode.
<nobr><span class='key'>Shift</span>+<span class='key'>カタカナ</span></nobr>| ― | Enter Katakana mode.
<span class='key'>Shift</span>+<span class='key'>無変換</span>| ― | Enter Full-width Alphanumeric mode.
<nobr><span class='key'>Ctrl</span>+<span class='key'>無変換</span></nobr>| ― | Toggle among Hiragana mode, Katakana mode, and Full-width Katakana mode.

## Key bindings in Hiragana Mode {: #input-hiragana-mode}

<nobr>Japanese Keyboard</nobr> | <nobr>US Keyboard</nobr> | Action
:--|:--|---
<span class='key'>変換</span>|<nobr><span class='key'>Space</span></nobr> | Convert the characters before the cursor.
<nobr><span class='key'>Shift</span>+<span class='key'>変換</span></nobr>|<nobr><span class='key'>Shift</span>+<span class='key'>Space</span></nobr> | Convert the characters before the cursor into kanji with *okurigana*.
<span class='key'>Space</span>| <span class='key'>Space</span><br><small>**Prerequisite**: There should be no characters that can be converted to Kanji or Katakana before the cursor.</small> | Insert a full-width space.
<span class='key'>カタカナ</span>,<br>Right <span class='key'>Shift</span>| Right <span class='key'>Shift</span>| Convert characters before the cursor into katakana. Each time you press the key, a hiragana character before the cursor is replaced with the corresponding katakana.<br><small>**Note**: Right <span class='key'>Shift</span> key can be used as a normal shift key by pressing other keys simultaneously.</small>

<br>
In an application that does not support the surrounding text features, the Hiragana IME also uses the following key bindings:

<nobr>Japanese Keyboard</nobr> | <nobr>US Keyboard</nobr> | Action
:--|:--|---
<span class='key'>Enter</span> | <span class='key'>Enter</span> | Enter the current pre-edit text.
<span class='key'>Esc</span> | <span class='key'>Esc</span> | Cancel the current pre-edit text.

## Key Bindings during Conversion {: #input-conversion}

<nobr>Japanese Keyboard</nobr> | <nobr>US Keyboard</nobr> | Action
:--|:--|---
<span class='key'>Tab</span>| <span class='key'>Tab</span>| Move the beginning of the word boundary to the right.
<nobr><span class='key'>Shift</span>+<span class='key'>Tab</span></nobr> | <nobr><span class='key'>Shift</span>+<span class='key'>Tab</span></nobr> | Move the beginning of the word boundary to the left.
<span class='key'>Enter</span> | <span class='key'>Enter</span> | Enter the current candidate.<br><small>**Note**: If you continue entering characters, the current candidate is automatically entered without typing the <span class='key'>Enter</span> key.</small>
<span class='key'>Esc</span> | <span class='key'>Esc</span> | Cancel the current conversion and revert to hiragana.<br><small>**Note**: When entering romaji, the entire pre-edit text is canceled.</small>

The candidate window appears near the cursor when there are two or more candidates. Use the following key bindings for candidate selection:

<nobr>Japanese Keyboard</nobr> | <nobr>US Keyboard</nobr> | Action
:--|:--|---
<span class='key'>↓</span>,<br><span class='key'>変換</span>| <span class='key'>↓</span>,<br><span class='key'>Space</span> | Move the selection down.
<span class='key'>↑</span>,<br><nobr><span class='key'>Shift</span>+<span class='key'>変換</span></nobr> |<span class='key'>↑</span>,<br><nobr><span class='key'>Shift</span>+<span class='key'>Space</span></nobr> | Move the selection up.
<span class='key'>Page Up</span> | <span class='key'>Page Up</span> | Go to the previous page of candidates.
<span class='key'>Page Down</span> | <span class='key'>Page Down</span> | Go to the next page of candidates.
