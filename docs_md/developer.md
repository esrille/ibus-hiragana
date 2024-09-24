# ￹開発￺かいはつ￻￹者￺しゃ￻むけの￹情報￺じょうほう￻

## ソースからビルドしてインストールする

　「ひらがなIME」をソースからビルドしてインストールするには、つぎのようにします。

```
git clone https://github.com/esrille/ibus-hiragana.git
cd ibus-hiragana
meson setup --prefix /usr _build [-Denable-dic=true] [-Denable-html=true]
ninja -C _build
ninja -C _build install
```

- -Denable-dic=trueを￹指定￺してい￻すると、￹漢字￺かんじ￻￹辞書￺じしょ￻とカタカナ￹辞書￺じしょ￻をビルドすることができます。
- -Denable-html=trueを￹指定￺してい￻すると、マークダウン ファイルからヘルプ￹用￺よう￻のhtmlファイルをビルドすることができます。

　ビルドするときに￹必要￺ひつよう￻なパッケージについては、debian/controlのBuild-Depends、あるいは、ibus-hiragana.specのBuildRequiresを￹参考￺さんこう￻にしてください。
　Fedoraであれば、つぎのコマンドでビルドに￹必要￺ひつよう￻なパッケージをインストールできます。

```
sudo yum-builddep ibus-hiragana.spec
```

　Ubuntuであれば、つぎのコマンドでビルドに￹必要￺ひつよう￻なパッケージをインストールできます。
```
sudo apt build-dep .
```

## テストのしかた {: #tests}

　「ひらがなIME」は、Pythonのvenvのなかで￹実行￺じっこう￻されています。
テストもvenvのなかで￹実行￺じっこう￻します。
テストによっては、あらかじめ￹大規模￺だいきぼ￻￹言語￺げんご￻モデル￹用￺よう￻のパッケージも[インストール](install.html#llm)しておく￹必要￺ひつよう￻があります。

```
source ~/.local/share/ibus-hiragana/venv/bin/activate
meson test -C _build --verbose
```

## アンインストールのしかた {: #uninstall}

　ソースからインストールした「ひらがなIME」をアンインストールするには、つぎのようにします。

```
sudo ninja -C _build uninstall
```
　ninjaのuninstallコマンドは、ディレクトリ <code>/usr/share/ibus-hiragana</code> までは￹削除￺さくじょ￻しません。
このディレクトリが￹不要￺ふよう￻なときは、つぎのようにして￹削除￺さくじょ￻します。
```
sudo rm -rf /usr/share/ibus-hiragana
```


