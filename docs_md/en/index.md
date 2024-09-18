# Hiragana IME for IBus

## Introduction {: #introduction}

Hiragana IME is a Japanese input method that simplifies inputting plain Japanese sentences.
An input method is a software component that assists users in entering characters into a computer.
With previous Japanese input methods, people often unintentionally wrote sentences including difficult kanji characters.
Many people found themselves using kanji characters that they couldn't even read.

In Hiragana IME, characters are entered as Hiragana-only sentences as you type without automatic kanji conversion.
You don't need to press the <span class='key'>Enter</span> key to enter Hiragana into the document.
If you want to use kanji, you can replace Hiragana anywhere in the text with kanji later.

<video controls autoplay muted playsinline>
<source src='../screenshot.webm' type='video/webm'>
Screenshot
</video>

Additionally, when using the [FuriganaPad](https://github.com/esrille/furiganapad) with Hiragana IME, you can automatically add Furigana, or readings, to the kanji. Not everyone can easily read kanji due to dyslexia and other reasons, even in Japan. Digital Japanese textbooks now include Furigana for Japanese schoolchildren.
It is crucial to reshape our society so that no one is left behind just because they cannot read kanji.

You can use Hiragana IME on operating systems that support [IBus](https://github.com/ibus/ibus/wiki), such as Fedora and Ubuntu.

## Modeless Input Methods {: #modeless}

With the traditional Japanese input methods, you had to convert Hiragana into kanji before entering them into a document using the pre-edit mode.
You had to learn complicated keyboard bindings to process text in the pre-edit mode.
With Hiragana IME, you can enter Hiragana into the document without using the pre-edit mode.

In modern operating systems, input methods can analyze the text surrounding the cursor within an application, known as *surrounding text*.
When an application provides surrounding text information correctly, input methods can replace parts of surrounding text with different characters.
Hiragana IME uses this new feature to convert Hiragana into kanji.

Recent input methods, including Hiragana IME, avoid using the pre-edit mode whenever possible.
These input methods are called modeless input methods. With modeless input methods, you can use the application's "Undo" function to reverse input method operations.
With Hiragana IME, you can revert kanji characters to Hiragana by using the "Undo" function in the application.
The number of keyboard operations you need to learn has been significantly reduced.

<video controls autoplay muted playsinline>
<source src='../undo.webm' type='video/webm'>
Undo conversion
</video>

In recent years, many applications, including Firefox, LibreOffice, and text editors like FuriganaPad, have become compatible with modeless input methods.
However, several essential applications still need to support modeless input methods properly.
You can usually input Latin characters without using a dedicated input method.
As a result, applications primarily used with Latin characters often do not fully support the surrounding text features.
In such applications, Hiragana IME disables modeless input and uses the pre-edit mode to input characters.

## Utilizing a Large Language Model for Kana-Kanji Conversion {: #llm}

Hiragana IME has a feature that assists kana-kanji conversion using a Large Language Model (LLM).
When enabled, Hiragana IME calculates the probabilities of each candidate's occurrence in the surrounding text and pre-selects the most probable candidate in the candidate window.

For example, when converting 'かいとう', the pre-selected candidate changes as below:

- アンケートにかいとう<span class='key'>変換</span> → アンケートに<span style="background-color:#d1eaff">回答</span>
- ￹問題￺もんだい￻のかいとう<span class='key'>変換</span> → ￹問題￺もんだい￻の<span style="background-color:#d1eaff">解答</span>

This feature is also effective when converting words with *okurigana*:

- ￹車￺くるま￻にの<span class='key'>変換</span>っ → ￹車￺くるま￻に<span style="background-color:#d1eaff">乗っ</span>
- ￹新聞￺しんぶん￻にの<span class='key'>変換</span>っ → ￹新聞￺しんぶん￻に<span style="background-color:#d1eaff">載っ</span>

<br>
**Note**: Since pre-selection is solely based on probability calculations, Hiragana IME may not always choose your desired candidate.
This feature is disabled by default because it requires a relatively large amount of computational power.
To enable this feature, you also need to install several packages.
For more details, please see [Install additional components for using LLM](install.html#llm).


<hr>
<br><small>Copyright 2017-2024 Esrille Inc.</small>
