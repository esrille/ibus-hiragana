# 日本語漢字置換インプット メソッド for IBus

[置換変換](https://github.com/esrille/replace-with-kanji-by-tutcode)をIBusで利用するための日本語インプット メソッドです。いまところFedoraデスクトップで日本語入力環境の実検用につくっているものです。

インプット メソッド エンジンは、プログラミング言語Pythonで実装されています。

## インストール方法

    ./autogen.sh
    make
    sudo make install
    ibus restart

上記の手順ができたら、IBus Preferencesの"Input Method"タブから、

![アイコン](icons/ibus-replace-with-kanji.png) Japanese - ReplaceWithKanji

を選択してください。

## つかいかた

* 同音異義語ウィンドウは置換候補が複数ある場合にだけ表示されます。
* カタカナは、カタカナ入力モードにきりかえて入力します。
* 辞書の学習結果は、ホームディレクトリの.replace-with-kanji.dicのなかに保存されます。

キーの操作は下記のようになっています。

キー | 内容
------------ | -------------
〔Caps Lock〕 | 英数/かなモードのきりかえ
〔スペース〕 | 置換変換開始, 次候補
〔↓〕 | 次候補
〔Shift〕-〔スペース〕, 〔↑〕 | 前候補
〔Shift〕-〔→〕 | よみをみじかくする
〔Enter〕 | 同音異義語の確定(つづきを入力すれば自動で確定します)
〔Esc〕 | 同音異義語の選択をとりけして、ひらがなにする<br>入力途中のローマ字があれば削除する
〔Page Up〕, 〔Page Down〕 | 同音異義語ウィンドウのページのきりかえ
右〔Shift〕の空打ち | カタカナ入力モード(変換操作でひらがなモードにもどります)<br>※ ローマ字入力およびニュー スティックニー配列を使用時。

### キーボード配列の選択

下記のキーボード配列に対応しています。ファイル名に.109がふくまれているものは、JISキーボード用です。

キーボード配列 | 設定ファイル名 | 補足
------------ | ------------- | -------------
99式ローマ字 | roomazi.json<br>roomazi.109.json | デフォルト
JISかな配列 | jis.109.json |
[ニュー スティックニー配列](https://github.com/esrille/new-stickney) | new_stickney.json |
TRONかな配列 | tron.json | エスリルNISSE用。
NICOLA(親指シフト) | nicola.json<br>nicola_f.json | エスリルNISSE用。<br>同時打鍵判定の遅延時間はIBus configのengine/replace-with-kanji-python:delayにmsec単位で指定できます。

いまのところ設定用の専用UIやコマンドはまだ準備していません。設定を変更するときは、IBus configの、

    engine/replace-with-kanji-python:layout

に上記の設定ファイル名をフルパス名で指定してください。例:

    /usr/local/share/ibus-replace-with-kanji/layouts/roomazi.json

IBus configの設定は、dconf Editorを実行して、

    /destop/ibus

から変更できます。変更した設定は自動的に反映されます。

※ エスリルのNISSEをつかわれている場合は、キーボードをpcモードに設定して、~/.Xmodmapを以下のように設定しておくと、FNキーで〔英数〕と〔かな〕のモードきりかえができるようになります。(IMEのon/offにCaps Lock はつかいません。)

    keycode 191 = F13 F13 F13
    keycode 192 = F14 F14 F14

### 制限事項

* 置換変換はIBus.Engineのget_surrounding_text()およびdelete_surrounding_text() APIをつかって実現しています。これらのAPIに未対応あるいは完全には対応できていないアプリケーションでは、直前に入力した文字列にたいしてのみ置換変換をすることができます(カーソルを移動してあとから置換変換することはできなくなります)。
* 候補ウィンドウから同音異義語を選択するときに、数字キーには対応していません(対応未定)。
* 辞書(restrained.dic)はUTF-8でエンコードされている必要があります(EUC-JPではありません)。
* 設定のカスタマイズ用のUIやコマンドはまだ用意していません。
* バイナリ配付用のリポジトリはまだ用意していません(未定)。

## 参考

* [『日本語と事務革命』— 梅棹式表記法のための日本語入力システムをかんがえる](http://shiki.esrille.com/2017/04/blog-post.html)
* [梅棹式表記法のための日本語入力システムをかんがえる(その2)](http://shiki.esrille.com/2017/04/2.html)
