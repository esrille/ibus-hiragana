# インストール￹方法￺ほうほう￻

　つかっているOSが、Fedora, Ubuntu, Raspbianのどれかであれば、インストール￹用￺よう￻のソフトウェア パッケージを「[Releases](https://github.com/esrille/ibus-hiragana/releases)」ページからダウンロードできます。

　インストールができたら、「IBusの￹設定￺せってい￻(IBus Preferences)」の「￹入力￺にゅうりょく￻メソッド(Input Method)」タブで、
<br><br>
![アイコン](icon.png) ￹日本語￺にほんご￻(Japanese) - Hiragana
<br><br>
を￹選択￺せんたく￻してください。

<br>※ GNOMEのばあいは、「￹設定￺せってい￻」―「￹地域￺ちいき￻と￹言語￺げんご￻」―「￹入力￺にゅうりょく￻ソース」の「￹日本語￺にほんご￻」のなかから￹選択￺せんたく￻してください。

## じぶんでビルドする￹方法￺ほうほう￻

　「ひらがなIME」をじぶんでビルドしてインストールしたいときは、つぎの￹手順￺てじゅん￻でインストールできます。

```
git clone https://github.com/esrille/ibus-hiragana.git
./autogen.sh
make
sudo make install
```
