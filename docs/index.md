# ひらがなIMEの￹手￺て￻びき

## はじめに {: #introduction}

　「ひらがな￹IME￺アイエムイー￻」は、かながきの￹部分￺ぶぶん￻のおおくなった￹日本語￺にほんご￻を￹入力￺にゅうりょく￻しやすくした￹日本語￺にほんご￻￹Input￺インプット￻ ￹Method￺メソッド￻ ￹Engine￺エンジン￻です。
キーボードでひらがなをうちこむと、そのまま￹本文￺ほんぶん￻に￹挿入￺そうにゅう￻されます。
いちいち<span class='key'>Enter</span>キーをおして、￹入力￺にゅうりょく￻を￹確定￺かくてい￻したりする￹必要￺ひつよう￻はありません。

　これまでのIMEでは、￹入力￺にゅうりょく￻したひらがなは、まず、￹漢字￺かんじ￻のよみとして￹処理￺しょり￻されていました。
「ひらがなIME」ではそのようなことはありません。
￹漢字￺かんじ￻をつかいたいときは、￹本文￺ほんぶん￻￹中￺ちゅう￻のひらがなをあとからいつでも￹漢字￺かんじ￻におきかえることができます。

　「ひらがなIME」は、FedoraやUbuntuなど、[IBus](https://github.com/ibus/ibus/wiki)に￹対応￺たいおう￻したオペレーティング システム（￹OS￺オーエス￻）で￹利用￺りよう￻できます。

<video controls autoplay muted playsinline>
<source src='screenshot.webm' type='video/webm'>
スクリーンショット
</video>

## モードレス￹入力￺にゅうりょく￻￹方式￺ほうしき￻ {: #modeless}

　「ひらがなIME」のような￹入力￺にゅうりょく￻￹方式￺ほうしき￻は「モードレス￹入力￺にゅうりょく￻￹方式￺ほうしき￻」とよばれています。
￹従来￺じゅうらい￻のIMEにあった「よみの￹入力￺にゅうりょく￻モード」をなくしているためです。
　いまのIMEは、アプリケーション ソフトウェアが￹対応￺たいおう￻してれば、カーソルの￹前後￺ぜんご￻のテキスト（「￹周辺￺しゅうへん￻テキスト」といいます）をしらべることができます。
「ひらがなIME」は、それを￹利用￺りよう￻して、モードレス￹入力￺にゅうりょく￻を￹実現￺じつげん￻しています。
さいきんでは、「[ふりがなパッド](https://github.com/esrille/furiganapad)」のようなテキスト エディターだけでなく、FirefoxやLibreOfficeなどでもモードレス￹入力￺にゅうりょく￻をつかえるようになっています。
　モードレス￹入力￺にゅうりょく￻￹方式￺ほうしき￻では、テキスト エディターやワープロの「￹元￺もと￻に￹戻￺もど￻す (Undo)」をつかって、￹変換￺へんかん￻した￹漢字￺かんじ￻をひらがなにもどすこともできます。

<video controls autoplay muted playsinline>
<source src='undo.webm' type='video/webm'>
変換を元に戻す
</video>

　ざんねんながら、モードレス￹入力￺にゅうりょく￻に￹対応￺たいおう￻していないアプリケーション ソフトウェアもあります。
￹英語￺えいご￻であれば、IMEがなくても￹文字￺もじ￻をふつうに￹入力￺にゅうりょく￻できます。
それで、￹英語￺えいご￻でつかわれることがおおいソフトウェアでは、IMEのサポートが￹完全￺かんぜん￻でないことがよくあるのです。
そうしたソフトでは、「ひらがなIME」でも、￹従来￺じゅうらい￻のIMEとおなじように「よみの￹入力￺にゅうりょく￻モード」をつかって￹文字￺もじ￻を￹入力￺にゅうりょく￻します。

<hr>
<br><small>Copyright 2017-2024 Esrille Inc.</small>
