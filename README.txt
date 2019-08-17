# ひらがなIME for IBus

　「ひらがなIME」は、かながきする￹部分￺ぶぶん￻のおおくなった￹日本語￺にほんご￻を￹入力￺にゅうりょく￻しやすくした￹日本語￺にほんご￻インプット メソッドです。Fedora、Ubuntu、Raspberry Pi￹用￺よう￻のRaspbianなど、[IBus](https://github.com/ibus/ibus/wiki)に￹対応￺たいおう￻したオペレーティング システム（OS）で￹利用￺りよう￻できます。

　これまでの￹日本語￺にほんご￻IMEとちがって、「ひらがなIME」には「よみの￹入力￺にゅうりょく￻モード」がありません。ひらがなを￹入力￺にゅうりょく￻するのに、いちいち〔￹確定￺かくてい￻〕キーや〔￹無変換￺むへんかん￻〕キーなどをおす￹必要￺ひつよう￻はありません。￹文中￺ぶんちゅう￻のひらがなの￹部分￺ぶぶん￻は、あとから、いつでも￹漢字￺かんじ￻におきかえることができます。

![スクリーンショット](screenshot.png)

　「[ふりがなパッド](https://github.com/esrille/furiganapad)」といっしょにつかうと、￹総￺そう￻ふりがなをうった￹文章￺ぶんしょう￻をかんたんにかくことができます。

## インストール￹方法￺ほうほう￻

　つかっているOSが、Fedora, Ubuntu, Raspbianのどれかであれば、インストール￹用￺よう￻のソフトウェア パッケージを「[Releases](https://github.com/esrille/ibus-replace-with-kanji/releases)」ページからダウンロードできます。

　インストールができたら、「IBusの￹設定￺せってい￻(IBus Preferences)」の「￹入力￺にゅうりょく￻メソッド(Input Method)」タブで、

![アイコン](icons/ibus-replace-with-kanji.png) ￹日本語￺にほんご￻(Japanese) - ReplaceWithKanji

を￹選択￺せんたく￻してください。

※ 「ひらがなIME」をじぶんでビルドしてインストールしたいときは、つぎの￹手順￺てじゅん￻でインストールできます。
```
$ ./autogen.sh
$ make
$ sudo make install
$ ibus restart
```

## ￹資料￺しりょう￻

　くわしい、つかいかたについては、「ひらがなIME」の￹手￺て￻びきをみてください。

- [ひらがなIMEの￹手￺て￻びき](https://esrille.github.io/ibus-replace-with-kanji/)
- [ひらがなIMEの￹開発￺かいはつ￻について](https://github.com/esrille/ibus-replace-with-kanji/blob/master/CONTRIBUTING.md)
