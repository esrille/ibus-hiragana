# ひらがなIME for IBus

　「ひらがな￹IME￺アイエムイー￻」は、かながきする￹部分￺ぶぶん￻のおおくなった￹日本語￺にほんご￻を￹入力￺にゅうりょく￻しやすくした￹日本語￺にほんご￻インプット メソッドです。Fedora、Ubuntu、Raspberry Pi OSなど、[IBus](https://github.com/ibus/ibus/wiki)に￹対応￺たいおう￻したオペレーティング システム（OS）で￹利用￺りよう￻できます。

　これまでの￹日本語￺にほんご￻IMEとちがって、「ひらがなIME」には「よみの￹入力￺にゅうりょく￻モード」がありません。ひらがなを￹入力￺にゅうりょく￻するのに、いちいち〔Enter〕キーや〔￹無変換￺むへんかん￻〕キーをおす￹必要￺ひつよう￻はありません。そのかわりに、￹文中￺ぶんちゅう￻のひらがなの￹部分￺ぶぶん￻を、いつでも￹漢字￺かんじ￻におきかえることができます。

![スクリーンショット](docs/screenshot.png)

　また、「[ふりがなパッド](https://github.com/esrille/furiganapad)」といっしょにつかうと、￹総￺そう￻ふりがなをうった￹文章￺ぶんしょう￻をかんたんにかくことができます。

## インストール￹方法￺ほうほう￻

　つかっているOSが、Fedora, Ubuntu, Raspberry Pi OSのどれかであれば、インストール￹用￺よう￻のソフトウェア パッケージを「[Releases](https://github.com/esrille/ibus-hiragana/releases)」ページからダウンロードできます。

　インストールができたら、

- 「￹設定￺せってい￻」の「￹地域￺ちいき￻と￹言語￺げんご￻」タブの「￹入力￺にゅうりょく￻ソース」、もしくは、
- 「IBusの￹設定￺せってい￻(IBus Preferences)」の「￹入力￺にゅうりょく￻メソッド(Input Method)」タブで、

![アイコン](icons/ibus-hiragana.png) ￹日本語￺にほんご￻(Japanese) - Hiragana IME

を￹追加￺ついか￻してください。

　IMEのきりかえは、トップバー（システムトレイ）の「en」や「あ」といった￹表示￺ひょうじ￻がされているアイコンをクリックしておこないます。

※ 「ひらがなIME」をじぶんでビルドしてインストールしたいときは、つぎの￹手順￺てじゅん￻でインストールできます。
```
git clone https://github.com/esrille/ibus-hiragana.git
./autogen.sh
make
sudo make install
```

## ￹資料￺しりょう￻

　くわしい、つかいかたについては、「ひらがなIME」の￹手￺て￻びきをみてください。

- [ひらがなIMEの￹手￺て￻びき](https://esrille.github.io/ibus-hiragana/)
- [ひらがなIMEの￹開発￺かいはつ￻について](https://github.com/esrille/ibus-hiragana/blob/master/CONTRIBUTING.md)
