# インストール￹方法￺ほうほう￻

　つかっているOSが、Fedora, Ubuntu, Raspbianのどれかであれば、インストール￹用￺よう￻のソフトウェア パッケージを「[Releases](https://github.com/esrille/ibus-replace-with-kanji/releases)」ページからダウンロードできます。

　インストールができたら、「IBusの￹設定￺せってい￻(IBus Preferences)」の「￹入力￺にゅうりょく￻メソッド(Input Method)」タブで、
<br><br>
![アイコン](icon.png) ￹日本語￺にほんご￻(Japanese) - ReplaceWithKanji
<br><br>
を￹選択￺せんたく￻してください。

<br>※ Ubuntuのばあいは、「￹設定￺せってい￻」―「￹地域￺ちいき￻と￹言語￺げんご￻」―「￹入力￺にゅうりょく￻ソース」の「￹日本語￺にほんご￻」のなかから￹選択￺せんたく￻してください。

## じぶんでビルドする￹方法￺ほうほう￻

　「ひらがなIME」をじぶんでビルドしてインストールしたいときは、つぎの￹手順￺てじゅん￻でインストールできます。

```
$ ./autogen.sh
$ make
$ sudo make install
$ ibus restart
```

## 「ひらがなIME」のプログラム

　「ひらがなIME」のプログラムは、すべて￹Python￺バイソン￻でかいてあります。プログラムの￹行数￺ぎょうすう￻は、￹約￺やく￻1,500￹行￺ぎょう￻(v0.6.0)です。
「ひらがなIME」の￹開発￺かいはつ￻は[GitHub](https://github.com/esrille/ibus-replace-with-kanji)￹上￺じょう￻ですすめています。

