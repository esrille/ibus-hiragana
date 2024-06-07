# Hiragana IME for IBus

## Introduction {: #introduction}

Hiragana IME is a Japanese input method that makes it easier to input plain Japanese sentences.
An input method is a software program to assist users in entering characters into a computer.
With previous Japanese input methods, people often unintentionally wrote sentences with difficult kanji characters.
Many found themselves using kanji they couldn't even read.

In Hiragana IME, characters are entered as Hiragana-only sentences as you type on the keyboard without automatic kanji conversion. You don't need to press the <span class='key'>Enter</span> key to enter Hiragana into the document. If you want to use kanji, you can easily replace Hiragana characters anywhere in the text later with kanji.

<video controls autoplay muted playsinline>
<source src='../screenshot.webm' type='video/webm'>
Screenshot
</video>

Additionally, when using the [FuriganaPad](https://github.com/esrille/furiganapad) with Hiragana IME, you can automatically add Furigana, or readings, to the kanji. Not everyone can easily read kanji due to dyslexia and other reasons, even in Japan. Digital Japanese textbooks now include Furigana for Japanese schoolchildren.
It is crucial to reshape our society so that no one is left behind just because they cannot read kanji.

You can use Hiragana IME on operating systems that support [IBus](https://github.com/ibus/ibus/wiki), such as Fedora and Ubuntu.

## Modeless input methods {: #modeless}

With the traditional Japanese input methods, you had to convert Hiragana into kanji before entering them into a document using the pre-edit mode. You had to learn complicated keyboard operations to process text in the pre-edit mode.

With Hiragana IME, you can enter Hiragana into the document without using the pre-edit mode. If you want to use kanji, you can replace Hiragana characters anywhere in the document with kanji anytime.

In modern operating systems, input methods can inspect text around the cursor in an application, which is called surrounding text.
When an application program properly provides surrounding text information, input methods can replace a portion of the surrounding text with other characters. Modeless input methods, such as Hiragana IME, utilize these new features.

With modeless input methods, you can use the application's "Undo" function to revert kanji characters to Hiragana. The keyboard operations you need to learn have been considerably reduced.

<video controls autoplay muted playsinline>
<source src='../undo.webm' type='video/webm'>
Undo conversion
</video>

In recent years, many applications, including text editors like FuriganaPad and applications such as Firefox and LibreOffice, have been able to use modeless input methods.
However, several essential applications still need to support modeless input methods properly. You can usually input Latin characters without using a dedicated input method. As a result, applications primarily used with Latin characters often do not fully support the surrounding text features. In such applications, Hiragana IME disables modeless input and uses the pre-edit mode to input characters.

<hr>
<br><small>Copyright 2017-2024 Esrille Inc.</small>
