# ひらがなIME for IBus

　「ひらがなIME」は、かながきする<ruby>部分<rp>(</rp><rt>ぶぶん</rt><rp>)</rp></ruby>のおおくなった<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>を<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>しやすくした<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>インプット メソッドです。Fedora、Ubuntu、Raspberry Pi<ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby>のRaspbianなど、[IBus](https://github.com/ibus/ibus/wiki)に<ruby>対応<rp>(</rp><rt>たいおう</rt><rp>)</rp></ruby>したオペレーティング システム（OS）で<ruby>利用<rp>(</rp><rt>りよう</rt><rp>)</rp></ruby>できます。

　これまでの<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>IMEとちがって、「ひらがなIME」には「よみの<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>モード」がありません。ひらがなを<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>するのに、いちいち〔<ruby>確定<rp>(</rp><rt>かくてい</rt><rp>)</rp></ruby>〕キーや〔<ruby>無変換<rp>(</rp><rt>むへんかん</rt><rp>)</rp></ruby>〕キーなどをおす<ruby>必要<rp>(</rp><rt>ひつよう</rt><rp>)</rp></ruby>はありません。<ruby>文中<rp>(</rp><rt>ぶんちゅう</rt><rp>)</rp></ruby>のひらがなの<ruby>部分<rp>(</rp><rt>ぶぶん</rt><rp>)</rp></ruby>は、あとから、いつでも<ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>におきかえることができます。

![スクリーンショット](docs/screenshot.png)

　「[ふりがなパッド](https://github.com/esrille/furiganapad)」といっしょにつかうと、<ruby>総<rp>(</rp><rt>そう</rt><rp>)</rp></ruby>ふりがなをうった<ruby>文章<rp>(</rp><rt>ぶんしょう</rt><rp>)</rp></ruby>をかんたんにかくことができます。

## インストール<ruby>方法<rp>(</rp><rt>ほうほう</rt><rp>)</rp></ruby>

　つかっているOSが、Fedora, Ubuntu, Raspbianのどれかであれば、インストール<ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby>のソフトウェア パッケージを「[Releases](https://github.com/esrille/ibus-replace-with-kanji/releases)」ページからダウンロードできます。

　インストールができたら、「IBusの<ruby>設定<rp>(</rp><rt>せってい</rt><rp>)</rp></ruby>(IBus Preferences)」の「<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>メソッド(Input Method)」タブで、

![アイコン](icons/ibus-replace-with-kanji.png) <ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>(Japanese) - ReplaceWithKanji

を<ruby>選択<rp>(</rp><rt>せんたく</rt><rp>)</rp></ruby>してください。

※ 「ひらがなIME」をじぶんでビルドしてインストールしたいときは、つぎの<ruby>手順<rp>(</rp><rt>てじゅん</rt><rp>)</rp></ruby>でインストールできます。
```
$ ./autogen.sh
$ make
$ sudo make install
$ ibus restart
```

## <ruby>資料<rp>(</rp><rt>しりょう</rt><rp>)</rp></ruby>

　くわしい、つかいかたについては、「ひらがなIME」の<ruby>手<rp>(</rp><rt>て</rt><rp>)</rp></ruby>びきをみてください。

- [ひらがなIMEの<ruby>手<rp>(</rp><rt>て</rt><rp>)</rp></ruby>びき](https://esrille.github.io/ibus-replace-with-kanji/)
- [ひらがなIMEの<ruby>開発<rp>(</rp><rt>かいはつ</rt><rp>)</rp></ruby>について](https://github.com/esrille/ibus-replace-with-kanji/blob/master/CONTRIBUTING.md)
