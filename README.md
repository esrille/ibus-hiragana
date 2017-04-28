# 漢字置換変換インプット メソッド for IBus

漢字[置換変換](https://github.com/esrille/replace-with-kanji-by-tutcode)をIBusで利用するための日本語インプット メソッドです。いまところFedoraデスクトップで日本語入力環境の実検用につくっているものです。

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

* ローマ字は99式をつかって入力できます(基本部分は訓令式とおなじです)。
* 同音異義語ウィンドウは置換候補が複数ある場合にだけ表示されます。
* カタカナを入力するときは、IMEをオンにした状態でCAPSキーをロックします。

キーの操作は下記のようになっています。

キー | 内容
------------ | -------------
変換 | IME オン
無変換 | IME オフ
<スペース> | 置換変換開始, 次候補
→ | 次候補
<シフト>-<スペース>, ← | 前候補
<シフト>-→ | よみをみじかくする
<エンター> | 同音異義語の確定(つづきを入力すれば自動で確定します)
↑, ↓ | 同音異義語ウィンドウのページのきりかえ

※ エスリルのNISSEをつかわれている場合は、xmodmapで以下のような感じに設定しておくと、TRONかな配列などでも置換変換を使用できます。

    keycode 130 = Henkan
    keycode 131 = Muhenkan
    keycode 191 = Henkan
    keycode 192 = Muhenkan

### 制限事項

* 置換変換はIBus.Engineのget_surrounding_text()およびdelete_surrounding_text() APIをつかって実現しています。これらのAPIに未対応のアプリでは利用できません。
* 辞書の学習結果は、いまのところファイルにかきもどしていません(対応予定)。
* 候補ウィンドウから同音異義語を選択するときに、数字キーには対応していません(対応未定)。
* 辞書(restrained.dic)はUTF-8でエンコードされている必要があります(EUC-JPではありません)。
* [ニュー スティックニー配列](https://github.com/esrille/new-stickney)用の設定は準備中です。
* 設定のカスタマイズ用のUIは用意していません。
* バイナリ配付用のリポジトリはまだ用意していません(未定)。

## 参考

* [『日本語と事務革命』— 梅棹式表記法のための日本語入力システムをかんがえる](http://shiki.esrille.com/2017/04/blog-post.html)
* [梅棹式表記法のための日本語入力システムをかんがえる(その2)](http://shiki.esrille.com/2017/04/2.html)
