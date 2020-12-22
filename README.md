# ひらがなIME for IBus

　「ひらがな<ruby>IME<rp>(</rp><rt>アイエムイー</rt><rp>)</rp></ruby>」は、かながきする<ruby>部分<rp>(</rp><rt>ぶぶん</rt><rp>)</rp></ruby>のおおくなった<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>を<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>しやすくした<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>インプット メソッドです。Fedora、Ubuntu、Raspberry Pi OSなど、[IBus](https://github.com/ibus/ibus/wiki)に<ruby>対応<rp>(</rp><rt>たいおう</rt><rp>)</rp></ruby>したオペレーティング システム（OS）で<ruby>利用<rp>(</rp><rt>りよう</rt><rp>)</rp></ruby>できます。

　これまでの<ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>IMEとちがって、「ひらがなIME」には「よみの<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>モード」がありません。ひらがなを<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>するのに、いちいち〔Enter〕キーや〔<ruby>無変換<rp>(</rp><rt>むへんかん</rt><rp>)</rp></ruby>〕キーをおす<ruby>必要<rp>(</rp><rt>ひつよう</rt><rp>)</rp></ruby>はありません。そのかわりに、<ruby>文中<rp>(</rp><rt>ぶんちゅう</rt><rp>)</rp></ruby>のひらがなの<ruby>部分<rp>(</rp><rt>ぶぶん</rt><rp>)</rp></ruby>を、いつでも<ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>におきかえることができます。

![スクリーンショット](docs/screenshot.png)

　また、「[ふりがなパッド](https://github.com/esrille/furiganapad)」といっしょにつかうと、<ruby>総<rp>(</rp><rt>そう</rt><rp>)</rp></ruby>ふりがなをうった<ruby>文章<rp>(</rp><rt>ぶんしょう</rt><rp>)</rp></ruby>をかんたんにかくことができます。

## インストール<ruby>方法<rp>(</rp><rt>ほうほう</rt><rp>)</rp></ruby>

　つかっているOSが、Fedora, Ubuntu, Raspberry Pi OSのどれかであれば、インストール<ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby>のソフトウェア パッケージを「[Releases](https://github.com/esrille/ibus-hiragana/releases)」ページからダウンロードできます。

　インストールができたら、

- 「<ruby>設定<rp>(</rp><rt>せってい</rt><rp>)</rp></ruby>」の「<ruby>地域<rp>(</rp><rt>ちいき</rt><rp>)</rp></ruby>と<ruby>言語<rp>(</rp><rt>げんご</rt><rp>)</rp></ruby>」タブの「<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>ソース」、もしくは、
- 「IBusの<ruby>設定<rp>(</rp><rt>せってい</rt><rp>)</rp></ruby>(IBus Preferences)」の「<ruby>入力<rp>(</rp><rt>にゅうりょく</rt><rp>)</rp></ruby>メソッド(Input Method)」タブで、

![アイコン](icons/ibus-hiragana.png) <ruby>日本語<rp>(</rp><rt>にほんご</rt><rp>)</rp></ruby>(Japanese) - Hiragana IME

を<ruby>追加<rp>(</rp><rt>ついか</rt><rp>)</rp></ruby>してください。

　IMEのきりかえは、トップバー（システムトレイ）の「en」や「あ」といった<ruby>表示<rp>(</rp><rt>ひょうじ</rt><rp>)</rp></ruby>がされているアイコンをクリックしておこないます。

※ 「ひらがなIME」をじぶんでビルドしてインストールしたいときは、つぎの<ruby>手順<rp>(</rp><rt>てじゅん</rt><rp>)</rp></ruby>でインストールできます。
```
git clone https://github.com/esrille/ibus-hiragana.git
./autogen.sh
make
sudo make install
```

## <ruby>資料<rp>(</rp><rt>しりょう</rt><rp>)</rp></ruby>

　くわしい、つかいかたについては、「ひらがなIME」の<ruby>手<rp>(</rp><rt>て</rt><rp>)</rp></ruby>びきをみてください。

- [ひらがなIMEの<ruby>手<rp>(</rp><rt>て</rt><rp>)</rp></ruby>びき](https://esrille.github.io/ibus-hiragana/)
- [ひらがなIMEの<ruby>開発<rp>(</rp><rt>かいはつ</rt><rp>)</rp></ruby>について](https://github.com/esrille/ibus-hiragana/blob/master/CONTRIBUTING.md)
