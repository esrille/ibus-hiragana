# Copyright (c) 2017-2024 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
import re
import sys

from toolpath import toolpath


def string_range(a, b):
    return ''.join([chr(x) for x in range(ord(a), ord(b) + 1)])


HIRAGANA = string_range('ぁ', 'ゖ') + 'か゚き゚く゚け゚こ゚'
KATAKANA = 'ー' + string_range('ァ', 'ヶ') + 'カ゚キ゚ク゚ケ゚コ゚セ゚ツ゚ト゚' + 'ㇰㇱㇲㇳㇴㇵㇶㇷㇸㇹㇷ゚ㇺㇻㇼㇽㇾㇿヷヸヹヺ'

# おもにJIS X 0208の記号
# '々' はふくめません。
KIGOU = ('　、。，．・：；？！゛゜´｀¨'
         '＾‾＿ヽヾゝゞ〃仝〆〇ー—‐／'
         '＼〜‖｜…‥‘’“”（）〔〕［］'
         '｛｝〈〉《》「」『』【】＋−±×'
         '÷＝≠＜＞≦≧∞∴♂♀°′″℃￥'
         '＄￠￡％＃＆＊＠§☆★○●◎◇'
         '◆□■△▲▽▼※〒→←↑↓〓＇'
         '＂－〜〳〴〵〻〼ヿゟ∈∋⊆⊇⊂⊃'
         '∪∩⊄⊅⊊⊋∉∅⌅⌆∧∨￢⇒⇔∀'
         '∃⊕⊖⊗∥∦｟｠〘〙〖〗∠⊥⌒∂'
         '∇≡≒≪≫√∽∝∵∫∬≢≃≅≈≶'
         '≷↔Å‰♯♭♪†‡¶♮♫♬♩◯'
         '▷▶◁◀↗↘↖↙⇄⇨⇦⇧⇩⤴⤵'
         '０１２３４５６７８９⦿◉〽﹆﹅◦'
         '•ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯ'
         'ＰＱＲＳＴＵＶＷＸＹＺ∓ℵℏ㏋ℓ'
         '℧ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏ'
         'ｐｑｒｓｔｕｖｗｘｙｚ゠–⧺⧻'
         + string_range('Α', 'Ω')
         + '♤♠♢♦♡♥♧♣'
         + string_range('α', 'ω')
         + string_range('⓵', '⓾')
         + '☖☗〠☎☀☁☂☃♨▱'
         + string_range('А', 'Я')
         + '⎾⎿⏀⏁⏂⏃⏄⏅⏆⏇⏈⏉⏊⏋⏌'
         + string_range('а', 'я')
         + '⋚⋛⅓⅔⅕✓⌘␣⏎'
         '─│┌┐┘└├┬┤┴┼━┃┏┓'
         '┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸'
         '╂'
         + string_range('㉑', '㉟')
         + string_range('㊱', '㊿')
         + '◐◑◒◓‼⁇⁈⁉Ǎ'
         'ǎǐḾḿǸǹǑǒǔǖǘǚǜ'
         '€¡¤￤©ª«®￣²³·¸'
         '¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈ'
         'ÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙ'
         'ÚÛÜÝÞßàáâãäåæçèé'
         'êëìíîïðñòóôõöøùú'
         'ûüýþÿĀĪŪĒŌāīūēō'
         'Ą˘ŁĽŚŠŞŤŹŽŻą˛łľ'
         'śˇšşťź˝žżŔĂĹĆČĘĚ'
         'ĎŃŇŐŘŮŰŢŕăĺćčęěď'
         'đńňőřůűţ˙ĈĜĤĴŜŬĉ'
         'ĝĥĵŝŭɱʋɾʃʒɬɮɹʈɖɳ'
         'ɽʂʐɻɭɟɲʝʎɡŋɰʁħʕ'
         'ʔɦʘǂɓɗʄɠƓœŒɨʉɘɵ'
         'əɜɞɐɯʊɤʌɔɑɒʍɥʢʡɕ'
         'ʑɺɧɚæ̀ǽὰάɔ̀ɔ́ʌ̀ʌ́ə̀ə́ɚ̀ɚ́'
         'ὲέ'
         + string_range('❶', '❿')
         + string_range('⓫', '⓴')
         + string_range('ⅰ', 'ⅻ')
         + string_range('ⓐ', 'ⓩ')
         + string_range('㋐', '㋾')
         + '⁑⁂'
         + string_range('①', '⑳')
         + string_range('Ⅰ', 'Ⅺ')
         + '㍉㌔㌢㍍㌘㌧㌃㌶㍑㍗㌍㌦㌣㌫㍊㌻'
         '㎜㎝㎞㎎㎏㏄㎡Ⅻ㍻'
         '〝〟№㏍℡㊤㊥㊦㊧㊨㈱㈲㈹㍾㍽㍼'
         '∮∟⊿❖☞'
         '⓪⓿'
         + string_range('㊀', '㊉')
         + string_range('㊊', '㊰')
         + '㋿')

ZYOUYOU = ('亜哀挨愛曖悪握圧扱宛嵐安案暗以衣位囲医依委威為畏胃尉異移萎偉椅彙意違維慰遺緯域育'
           '一壱逸茨芋引印因咽姻員院淫陰飲隠韻右宇羽雨唄鬱畝浦運雲永泳英映栄営詠影鋭衛易疫益'
           '液駅悦越謁閲円延沿炎怨宴媛援園煙猿遠鉛塩演縁艶汚王凹央応往押旺欧殴桜翁奥横岡屋億'
           '憶臆虞乙俺卸音恩温穏下化火加可仮何花佳価果河苛科架夏家荷華菓貨渦過嫁暇禍靴寡歌箇'
           '稼課蚊牙瓦我画芽賀雅餓介回灰会快戒改怪拐悔海界皆械絵開階塊楷解潰壊懐諧貝外劾害崖'
           '涯街慨蓋該概骸垣柿各角拡革格核殻郭覚較隔閣確獲嚇穫学岳楽額顎掛潟括活喝渇割葛滑褐'
           '轄且株釜鎌刈干刊甘汗缶完肝官冠巻看陥乾勘患貫寒喚堪換敢棺款間閑勧寛幹感漢慣管関歓'
           '監緩憾還館環簡観韓艦鑑丸含岸岩玩眼頑顔願企伎危机気岐希忌汽奇祈季紀軌既記起飢鬼帰'
           '基寄規亀喜幾揮期棋貴棄毀旗器畿輝機騎技宜偽欺義疑儀戯擬犠議菊吉喫詰却客脚逆虐九久'
           '及弓丘旧休吸朽臼求究泣急級糾宮救球給嗅窮牛去巨居拒拠挙虚許距魚御漁凶共叫狂京享供'
           '協況峡挟狭恐恭胸脅強教郷境橋矯鏡競響驚仰暁業凝曲局極玉巾斤均近金菌勤琴筋僅禁緊錦'
           '謹襟吟銀区句苦駆具惧愚空偶遇隅串屈掘窟熊繰君訓勲薫軍郡群兄刑形系径茎係型契計恵啓'
           '掲渓経蛍敬景軽傾携継詣慶憬稽憩警鶏芸迎鯨隙劇撃激桁欠穴血決結傑潔月犬件見券肩建研'
           '県倹兼剣拳軒健険圏堅検嫌献絹遣権憲賢謙鍵繭顕験懸元幻玄言弦限原現舷減源厳己戸古呼'
           '固股虎孤弧故枯個庫湖雇誇鼓錮顧五互午呉後娯悟碁語誤護口工公勾孔功巧広甲交光向后好'
           '江考行坑孝抗攻更効幸拘肯侯厚恒洪皇紅荒郊香候校耕航貢降高康控梗黄喉慌港硬絞項溝鉱'
           '構綱酵稿興衡鋼講購乞号合拷剛傲豪克告谷刻国黒穀酷獄骨駒込頃今困昆恨根婚混痕紺魂墾'
           '懇左佐沙査砂唆差詐鎖座挫才再災妻采砕宰栽彩採済祭斎細菜最裁債催塞歳載際埼在材剤財'
           '罪崎作削昨柵索策酢搾錯咲冊札刷刹拶殺察撮擦雑皿三山参桟蚕惨産傘散算酸賛残斬暫士子'
           '支止氏仕史司四市矢旨死糸至伺志私使刺始姉枝祉肢姿思指施師恣紙脂視紫詞歯嗣試詩資飼'
           '誌雌摯賜諮示字寺次耳自似児事侍治持時滋慈辞磁餌璽鹿式識軸七𠮟失室疾執湿嫉漆質実芝'
           '写社車舎者射捨赦斜煮遮謝邪蛇尺借酌釈爵若弱寂手主守朱取狩首殊珠酒腫種趣寿受呪授需'
           '儒樹収囚州舟秀周宗拾秋臭修袖終羞習週就衆集愁酬醜蹴襲十汁充住柔重従渋銃獣縦叔祝宿'
           '淑粛縮塾熟出述術俊春瞬旬巡盾准殉純循順準潤遵処初所書庶暑署緒諸女如助序叙徐除小升'
           '少召匠床抄肖尚招承昇松沼昭宵将消症祥称笑唱商渉章紹訟勝掌晶焼焦硝粧詔証象傷奨照詳'
           '彰障憧衝賞償礁鐘上丈冗条状乗城浄剰常情場畳蒸縄壌嬢錠譲醸色拭食植殖飾触嘱織職辱尻'
           '心申伸臣芯身辛侵信津神唇娠振浸真針深紳進森診寝慎新審震薪親人刃仁尽迅甚陣尋腎須図'
           '水吹垂炊帥粋衰推酔遂睡穂随髄枢崇数据杉裾寸瀬是井世正生成西声制姓征性青斉政星牲省'
           '凄逝清盛婿晴勢聖誠精製誓静請整醒税夕斥石赤昔析席脊隻惜戚責跡積績籍切折拙窃接設雪'
           '摂節説舌絶千川仙占先宣専泉浅洗染扇栓旋船戦煎羨腺詮践箋銭潜線遷選薦繊鮮全前善然禅'
           '漸膳繕狙阻祖租素措粗組疎訴塑遡礎双壮早争走奏相荘草送倉捜挿桑巣掃曹曽爽窓創喪痩葬'
           '装僧想層総遭槽踪操燥霜騒藻造像増憎蔵贈臓即束足促則息捉速側測俗族属賊続卒率存村孫'
           '尊損遜他多汰打妥唾堕惰駄太対体耐待怠胎退帯泰堆袋逮替貸隊滞態戴大代台第題滝宅択沢'
           '卓拓託濯諾濁但達脱奪棚誰丹旦担単炭胆探淡短嘆端綻誕鍛団男段断弾暖談壇地池知値恥致'
           '遅痴稚置緻竹畜逐蓄築秩窒茶着嫡中仲虫沖宙忠抽注昼柱衷酎鋳駐著貯丁弔庁兆町長挑帳張'
           '彫眺釣頂鳥朝貼超腸跳徴嘲潮澄調聴懲直勅捗沈珍朕陳賃鎮追椎墜通痛塚漬坪爪鶴低呈廷弟'
           '定底抵邸亭貞帝訂庭逓停偵堤提程艇締諦泥的笛摘滴適敵溺迭哲鉄徹撤天典店点展添転塡田'
           '伝殿電斗吐妬徒途都渡塗賭土奴努度怒刀冬灯当投豆東到逃倒凍唐島桃討透党悼盗陶塔搭棟'
           '湯痘登答等筒統稲踏糖頭謄藤闘騰同洞胴動堂童道働銅導瞳峠匿特得督徳篤毒独読栃凸突届'
           '屯豚頓貪鈍曇丼那奈内梨謎鍋南軟難二尼弐匂肉虹日入乳尿任妊忍認寧熱年念捻粘燃悩納能'
           '脳農濃把波派破覇馬婆罵拝杯背肺俳配排敗廃輩売倍梅培陪媒買賠白伯拍泊迫剝舶博薄麦漠'
           '縛爆箱箸畑肌八鉢発髪伐抜罰閥反半氾犯帆汎伴判坂阪板版班畔般販斑飯搬煩頒範繁藩晩番'
           '蛮盤比皮妃否批彼披肥非卑飛疲秘被悲扉費碑罷避尾眉美備微鼻膝肘匹必泌筆姫百氷表俵票'
           '評漂標苗秒病描猫品浜貧賓頻敏瓶不夫父付布扶府怖阜附訃負赴浮婦符富普腐敷膚賦譜侮武'
           '部舞封風伏服副幅復福腹複覆払沸仏物粉紛雰噴墳憤奮分文聞丙平兵併並柄陛閉塀幣弊蔽餅'
           '米壁璧癖別蔑片辺返変偏遍編弁便勉歩保哺捕補舗母募墓慕暮簿方包芳邦奉宝抱放法泡胞俸'
           '倣峰砲崩訪報蜂豊飽褒縫亡乏忙坊妨忘防房肪某冒剖紡望傍帽棒貿貌暴膨謀頰北木朴牧睦僕'
           '墨撲没勃堀本奔翻凡盆麻摩磨魔毎妹枚昧埋幕膜枕又末抹万満慢漫未味魅岬密蜜脈妙民眠矛'
           '務無夢霧娘名命明迷冥盟銘鳴滅免面綿麺茂模毛妄盲耗猛網目黙門紋問冶夜野弥厄役約訳薬'
           '躍闇由油喩愉諭輸癒唯友有勇幽悠郵湧猶裕遊雄誘憂融優与予余誉預幼用羊妖洋要容庸揚揺'
           '葉陽溶腰様瘍踊窯養擁謡曜抑沃浴欲翌翼拉裸羅来雷頼絡落酪辣乱卵覧濫藍欄吏利里理痢裏'
           '履璃離陸立律慄略柳流留竜粒隆硫侶旅虜慮了両良料涼猟陵量僚領寮療瞭糧力緑林厘倫輪隣'
           '臨瑠涙累塁類令礼冷励戻例鈴零霊隷齢麗暦歴列劣烈裂恋連廉練錬呂炉賂路露老労弄郎朗浪'
           '廊楼漏籠六録麓論和話賄脇惑枠湾腕')
assert len(ZYOUYOU) == 2136

ZINMEI = ('丑丞乃之乎也云亘些亦亥亨亮仔伊伍伽佃佑伶侃侑俄俠俣俐倭俱倦倖偲傭儲允兎兜其冴凌凜凧凪凰凱函劉劫勁勺勿'
          '匁匡廿卜卯卿厨厩叉叡叢叶只吾吞吻哉哨啄哩喬喧喰喋嘩嘉嘗噌噂圃圭坐尭坦埴堰堺堵塙壕壬夷奄奎套娃姪姥娩嬉'
          '孟宏宋宕宥寅寓寵尖尤屑峨峻崚嵯嵩嶺巌巫已巳巴巷巽帖幌幡庄庇庚庵廟廻弘弛彗彦彪彬徠忽怜恢恰恕悌惟惚悉惇'
          '惹惺惣慧憐戊或戟托按挺挽掬捲捷捺捧掠揃摑摺撒撰撞播撫擢孜敦斐斡斧斯於旭昂昊昏昌昴晏晃晒晋晟晦晨智暉暢'
          '曙曝曳朋朔杏杖杜李杭杵杷枇柑柴柘柊柏柾柚桧栞桔桂栖桐栗梧梓梢梛梯桶梶椛梁棲椋椀楯楚楕椿楠楓椰楢楊榎樺'
          '榊榛槙槍槌樫槻樟樋橘樽橙檎檀櫂櫛櫓欣欽歎此殆毅毘毬汀汝汐汲沌沓沫洸洲洵洛浩浬淵淳渚淀淋渥渾湘湊湛溢滉'
          '溜漱漕漣澪濡瀕灘灸灼烏焰焚煌煤煉熙燕燎燦燭燿爾牒牟牡牽犀狼猪獅玖珂珈珊珀玲琢琉瑛琥琶琵琳瑚瑞瑶瑳瓜瓢'
          '甥甫畠畢疋疏皐皓眸瞥矩砦砥砧硯碓碗碩碧磐磯祇祢祐祷禄禎禽禾秦秤稀稔稟稜穣穹穿窄窪窺竣竪竺竿笈笹笙笠筈'
          '筑箕箔篇篠簞簾籾粥粟糊紘紗紐絃紬絆絢綺綜綴緋綾綸縞徽繫繡纂纏羚翔翠耀而耶耽聡肇肋肴胤胡脩腔脹膏臥舜舵'
          '芥芹芭芙芦苑茄苔苺茅茉茸茜莞荻莫莉菅菫菖萄菩萌萊菱葦葵萱葺萩董葡蓑蒔蒐蒼蒲蒙蓉蓮蔭蔣蔦蓬蔓蕎蕨蕉蕃蕪'
          '薙蕾蕗藁薩蘇蘭蝦蝶螺蟬蟹蠟衿袈袴裡裟裳襖訊訣註詢詫誼諏諄諒謂諺讃豹貰賑赳跨蹄蹟輔輯輿轟辰辻迂迄辿迪迦'
          '這逞逗逢遥遁遼邑祁郁鄭酉醇醐醍醬釉釘釧銑鋒鋸錘錐錆錫鍬鎧閃閏閤阿陀隈隼雀雁雛雫霞靖鞄鞍鞘鞠鞭頁頌頗顚'
          '颯饗馨馴馳駕駿驍魁魯鮎鯉鯛鰯鱒鱗鳩鳶鳳鴨鴻鵜鵬鷗鷲鷺鷹麒麟麿黎黛鼎'
          '亙凛堯巖晄檜槇渚猪琢禰祐禱祿禎穰萠遙'
          '亞惡爲逸榮衞謁圓緣薗應櫻奧橫溫價禍悔海壞懷樂渴卷陷寬漢氣祈器僞戲虛峽狹響曉勤謹駈勳薰惠揭鷄藝擊縣儉劍'
          '險圈檢顯驗嚴廣恆黃國黑穀碎雜祉視兒濕實社者煮壽收臭從澁獸縱祝暑署緖諸敍將祥涉燒奬條狀乘淨剩疊孃讓釀神'
          '眞寢愼盡粹醉穗瀨齊靜攝節專戰纖禪祖壯爭莊搜巢曾裝僧層瘦騷增憎藏贈臟卽帶滯瀧單嘆團彈晝鑄著廳徵聽懲鎭轉'
          '傳都嶋燈盜稻德突難拜盃賣梅髮拔繁晚卑祕碑賓敏冨侮福拂佛勉步峯墨飜每萬默埜彌藥與搖樣謠來賴覽欄龍虜凉綠'
          '淚壘類禮曆歷練鍊郞朗廊錄')
assert len(ZINMEI) == 863

CONJUGATION = '1iIkKgsStnbmrwW235'

RE_KANA = re.compile('[' + HIRAGANA + KATAKANA + ']')
RE_HIRAGANA = re.compile('[' + HIRAGANA + ']')
RE_HIRAGANA_AND_CONJUGATION = re.compile('[' + HIRAGANA + CONJUGATION + ']')
RE_SKK_YOMI = re.compile(r'^[ぁ-ゖー#]+[a-z―]?$')
RE_ALPHA = re.compile(r'[a-zA-Z]')
RE_ONYOMI = re.compile(r'[^ぁ-ゖー]')
RE_KIGOU = re.compile('[' + KIGOU + ']')
RE_OKURI = re.compile('[' + HIRAGANA + ']+$')
RE_PREFIX = re.compile('^[' + HIRAGANA + ']+')
RE_KATAKANA = re.compile('^[' + KATAKANA + ']+')

# 常用漢字、人名漢字、記号にふくまれない字に一致する正規表現
RE_HYOUGAI = re.compile('[^' + '#0-9A-Za-z' + HIRAGANA + KATAKANA + ZYOUYOU + '々' + KIGOU + ZINMEI + ']')

TO_HIRAGANA = str.maketrans(string_range('ァ', 'ヶ') + 'カ゚キ゚ク゚ケ゚コ゚', string_range('ぁ', 'ゖ') + 'か゚き゚く゚け゚こ゚')

DAKUON = 'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉゃゅょっゔ'
SEION = 'かきくけこさしすせそたちつてとはひふへほはひふへほあいうえおやゆよつう'
TO_SEION = str.maketrans(DAKUON, SEION)


def to_hiragana(s):
    return s.translate(TO_HIRAGANA)


def to_seion(s):
    return s.translate(TO_SEION)


def output(dict, file=sys.stdout, single=False):
    for yomi, words in sorted(dict.items()):
        if not single:
            print(f'{yomi} /{"/".join(words)}/', file=file)
        else:
            for word in words:
                print(f'{yomi} /{word}/', file=file)


def add_word(dict, yomi, word):
    if yomi not in dict:
        dict[yomi] = [word]
    elif word not in dict[yomi]:
        dict[yomi].append(word)


def lookup(dict, word):
    d = {}
    for yomi, words in dict.items():
        if word in words:
            add_word(d, yomi, word)
    return d


# 常用漢字表から辞書をつくります。
def zyouyou(grade=10, exclude_special=False):
    dict = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as f:
        for row in f:
            row = row.strip().split(',')
            kanji = row[0]
            for yomi in row[1:]:
                g = int(yomi[-1])
                if grade < g:
                    continue
                g = yomi[-2:]
                k = kanji
                yomi = yomi[:-2]
                if yomi[0] == '（' and exclude_special:
                    continue
                yomi = yomi.strip('（）')
                yomi = to_hiragana(yomi)
                pos = yomi.find('―')
                if 0 <= pos:
                    k += yomi[pos + 1:]
                    yomi = yomi[:pos + 1]
                k += g
                if yomi not in dict:
                    dict[yomi] = []
                    dict[yomi].append(k)
                elif k not in dict[yomi]:
                    dict[yomi].append(k)
    for yomi, kanji in dict.items():
        cand = []
        for i in range(1, 10):
            for k in kanji:
                if int(k[-1]) == i:
                    if not k[:-2] in cand:
                        cand.append(k[:-2])
        dict[yomi] = cand
    return dict


# 常用漢字表から漢字の学習年度辞書をつくります。
def zyouyou_grades():
    grades = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as f:
        for row in f:
            grade = 10
            row = row.strip().split(',')
            kanji = row[0]
            for yomi in row[1:]:
                g = int(yomi[-1])
                if g < grade:
                    grade = g
            grades[kanji] = grade
    return grades


def _get_encoding(path):
    if 0 <= path.find('SKK-JISYO'):     # SKKの辞書
        return 'euc_jp'
    if 0 <= path.find('mazegaki.dic'):  # tc2の辞書
        return 'euc_jp'
    return 'utf-8'


# SKK辞書をよみこみます。用言は、よみの末尾に'―'をつけた形に変換します。
# ※ annotationはとりのぞきます。
def load(path):
    encoding = _get_encoding(path)
    dict = {}
    with open(path, encoding=encoding) as f:
        for row in f:
            row = row.strip()
            if not row or row[0] == ';':
                continue
            row = row.split(maxsplit=2)
            yomi = row[0]
            if not RE_SKK_YOMI.match(yomi):
                continue
            skk_code = ''
            if RE_ALPHA.match(yomi[-1]):
                # SKK辞書のおくりありのよみ
                skk_code = yomi[-1]
                yomi = yomi[:-1]
            words = row[1].strip(' \n/').split('/')
            for word in words:
                pos = word.find(';')
                if 0 == pos:
                    continue
                if 0 < pos:
                    word = word[:pos]
                if word == '':
                    continue
                yy = yomi
                m = RE_OKURI.search(word)
                if m:
                    okuri = m.group()
                    if yomi.endswith(okuri):
                        yy = yy[:-(len(okuri))] + '―'
                word += skk_code
                if skk_code and yomi[-1] != '―':
                    yy += '―'
                add_word(dict, yy, word)
    return dict


def _get_grade(cand, grades):
    grade = 1
    for i in cand:
        g = grades.get(i, grade)
        if grade < g:
            grade = g
    return grade


# 付表をよみこみます。
def load_huhyou(path, grade=10):
    grades = zyouyou_grades()
    dict = {}
    with open(path, 'r') as file:
        for row in file:
            row = row.strip(' \n')
            if not row or row[0] == ';':
                continue
            row = row.split(':', 1)
            level = int(row[0])
            if level == 4 and grade < 9:
                continue
            if level == 3 and grade < 8:
                continue
            elif level == 2 and grade < 7:
                continue
            row = row[1].split(' ', 1)
            yomi = row[0]
            cand = row[1].strip(' \n/').split('/')
            if 1 < level:
                s = cand
            else:
                s = []
                for i in cand:
                    if _get_grade(i, grades) <= grade:
                        s.append(i)
            if s:
                if yomi not in dict:
                    dict[yomi] = s
                else:
                    dict[yomi].extend([x for x in s if x not in dict[yomi]])
    return dict


# SKK辞書のヘッダー部分を出力します。
def copy_header(path):
    encoding = _get_encoding(path)
    with open(path, encoding=encoding) as f:
        for row in f:
            if not row or row[0] != ';':
                break
            row = row.strip(' \n')
            if row == ';; okuri-ari entries.':
                break
            if 'euc-jp' in row:
                continue
            print(row)


# 2つの辞書の共通部分をとりだした辞書をかえします。
def intersection(a, b):
    d = {}
    for yomi in set(a) & set(b):
        assert yomi in a and yomi in b
        words = [x for x in a[yomi] if x in b[yomi]]
        if words:
            d[yomi] = words
    return d


# 2つの辞書の和集合をとりだした辞書をかえします。
def union(a, b):
    d = {}
    for yomi in set(a) | set(b):
        if yomi not in a:
            d[yomi] = b[yomi][:]
        elif yomi not in b:
            d[yomi] = a[yomi][:]
        else:
            d[yomi] = a[yomi] + [x for x in b[yomi] if x not in a[yomi]]
    return d


# 2つの辞書の差集合をとりだした辞書をかえします。
def difference(a, b):
    d = {}
    for yomi in a:
        if yomi in b:
            words = [x for x in a[yomi] if x not in b[yomi]]
            if words:
                d[yomi] = words
        else:
            d[yomi] = a[yomi][:]
    return d


# 2つの辞書のよみの共通部分をとりだした辞書をかえします。
def intersection_yomi(a, b):
    d = {}
    for yomi in set(a) & set(b):
        assert yomi in a and yomi in b
        d[yomi] = a[yomi] + [x for x in b[yomi] if x not in a[yomi]]
    return d


# 記号をつかっている語をとりだします。
def kigou(dict):
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if word not in s and RE_KIGOU.search(word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# 表外漢字をつかっている熟語をとりだします。
def hyougai(dict):
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if word not in s and RE_HYOUGAI.search(word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# おくりがなをふくんだ活用しない語をとりだします。
def okuri(dict):
    d = {}
    for yomi, words in dict.items():
        s = []
        if yomi[-1] == '―':
            for word in words:
                if word[-1] not in CONJUGATION:
                    s.append(word)
        else:
            for word in words:
                if RE_HIRAGANA.search(word):
                    s.append(word)
        if s:
            d[yomi] = s
    return d


# 最後におくりがなのある語をとりだします。
def okuri_end(dict):
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if RE_HIRAGANA.search(word[-1]):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# 活用する語をとりだします
def yougen(dict):
    d = {}
    for yomi, words in dict.items():
        if yomi[-1] == '―':
            s = []
            for word in words:
                if word[-1] in CONJUGATION:
                    s.append(word)
            if s:
                d[yomi] = s
    return d


# 用言と体言をまとめた辞書をつくります。
def mix_yougen(dict):
    d = dict.copy()
    for yomi, words in dict.items():
        if yomi[-1] != '―':
            continue
        yomi = yomi[:-1]
        if yomi not in d:
            s = []
            for word in words:
                s.append(word + '―')
            d[yomi] = s
            continue
        for word in words:
            if word not in d[yomi]:
                d[yomi].append(word + '―')
    return d


def _is_hyounai_yomi(zyouyou, yomi, word):
    # ― と # をとりのぞく。
    yomi = yomi.replace('―', '')
    yomi = yomi.replace('#', '')
    word = word.replace('#', '')

    m = RE_PREFIX.search(word)
    if m and yomi.startswith(m.group()):
        word = word[m.end():]
        yomi = yomi[m.end():]
    if not yomi or not word:
        return True

    m = RE_OKURI.search(word)
    if m:
        okuri = m.group()
        word = word[:m.start()]
        if yomi.endswith(okuri):
            yomi = yomi[:-(len(okuri))]
        if not word:
            return True

    if len(word) == 1:
        if word not in zyouyou:
            return False
        for i in zyouyou[word]:
            if to_seion(yomi) == to_seion(i):
                return True
        return False
    c = word[0]
    if c not in zyouyou:
        return False
    s = zyouyou[c]
    b = c
    for c in word[1:]:
        if c == '々':
            if b == c:
                # e.g. 個人々々
                return False
            t = set(itertools.product(s, zyouyou[b]))
        elif RE_KANA.match(c):
            t = set(itertools.product(s, set(c)))
        elif c not in zyouyou:
            return False
        else:
            t = set(itertools.product(s, zyouyou[c]))
        s = set()
        for y in t:
            s.add(to_seion(''.join(y)))
            if 2 <= len(y[0]):
                # 促音化の許容
                if (0 <= 'きくキク'.find(y[0][-1]) and 0 <= 'かきくけこカキクケコ'.find(y[1][0])
                    or 0 <= 'ちつチツ'.find(y[0][-1])
                        and 0 <= 'かきくけこカキクケコさしすせそサシスセソたちつてとタチツテトはひふへほハヒフヘホ'.find(y[1][0])):
                    s.add(to_seion(y[0][0:-1] + 'つ' + y[1]))
        b = c
    return to_seion(yomi) in s


# 表外のよみかたをつかっている熟語をとりだします。
def hyougai_yomi(dict, grade=10):
    zyouyou = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as f:
        for row in f:
            row = row.strip().split(',')
            kanji = row[0]
            s = set()
            for yomi in row[1:]:
                g = int(yomi[-1])
                if grade < g:
                    continue
                yomi = yomi[:-2]
                yomi = yomi.strip('（）')
                pos = yomi.find('―')
                if 0 <= pos:
                    yomi = yomi[:pos]
                if not yomi:
                    continue
                s.add(to_hiragana(yomi))
            if s:
                zyouyou[kanji] = s
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if not _is_hyounai_yomi(zyouyou, yomi, to_hiragana(word)):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# 常用漢字表から音よみと訓よみをわけてとりだします。
def load_onkun(grade=10, okuri=True, drop=False):
    kunyomi = {}
    onyomi = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as f:
        for row in f:
            row = row.strip().split(',')
            kanji = row[0]
            on = set()
            kun = set()
            for yomi in row[1:]:
                g = int(yomi[-1])
                if grade < g:
                    continue
                yomi = yomi[:-2]
                yomi = yomi.strip('（）')
                pos = yomi.find('―')
                if 0 <= pos:
                    if okuri:
                        yomi = yomi[:pos]
                    else:
                        continue
                if yomi:
                    if RE_ONYOMI.search(yomi):
                        on.add(to_hiragana(yomi))
                    else:
                        kun.add(yomi)

            if drop:
                intersection = kun & on
                kun -= intersection
                on -= intersection

            if kun:
                kunyomi[kanji] = kun
            if on:
                onyomi[kanji] = on
    return onyomi, kunyomi


# 和語の熟語をとりだします。
def wago(dict, grade=10, okuri=True):
    onyomi, kunyomi = load_onkun(grade, okuri)
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if _is_hyounai_yomi(kunyomi, yomi, word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


def _is_maze_yomi(first: dict, second: dict, yomi, word):
    # ― と # をとりのぞく。
    yomi = yomi.replace('―', '')
    yomi = yomi.replace('#', '')
    word = word.replace('#', '')

    m = RE_OKURI.search(word)
    if m:
        okuri = m.group()
        word = word[:m.start()]
        if yomi.endswith(okuri):
            yomi = yomi[:-(len(okuri))]

    if len(word) != 2:
        return False

    c = word[0]
    if c not in first:
        return False
    s = first[c]

    c = word[1]
    if c == '々':
        return False
    if c not in second:
        return False
    t = set(itertools.product(s, second[c]))
    s = set()
    for y in t:
        s.add(to_seion(''.join(y)))
        if 2 <= len(y[0]):
            # 促音化の許容
            if (0 <= 'きくキク'.find(y[0][-1]) and 0 <= 'かきくけこカキクケコ'.find(y[1][0])
                or 0 <= 'ちつチツ'.find(y[0][-1])
                    and 0 <= 'かきくけこカキクケコさしすせそサシスセソたちつてとタチツテトはひふへほハヒフヘホ'.find(y[1][0])):
                s.add(to_seion(y[0][0:-1] + 'つ' + y[1]))

    return to_seion(yomi) in s


# 重箱よみの語をとりだします。
def zyuubako(dict, grade=10, okuri=True):
    onyomi, kunyomi = load_onkun(grade, okuri, drop=True)
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if _is_maze_yomi(onyomi, kunyomi, yomi, word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# 湯桶よみの語をとりだします。
def yutou(dict, grade=10, okuri=True):
    onyomi, kunyomi = load_onkun(grade, okuri, drop=True)
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if _is_maze_yomi(kunyomi, onyomi, yomi, word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# 重箱よみと湯桶よみの語をとりだします。
def mazeyomi(dict, grade=10, okuri=True):
    onyomi, kunyomi = load_onkun(grade, okuri, drop=True)
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if _is_maze_yomi(kunyomi, onyomi, yomi, word) or _is_maze_yomi(onyomi, kunyomi, yomi, word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# カタカナの語をとりだします。
def katakana(dict):
    d = {}
    for yomi, words in dict.items():
        s = []
        for word in words:
            if RE_KATAKANA.match(word):
                s.append(word)
        if s:
            d[yomi] = s
    return d


# 許容されているおくりがなをとりだします。
def permissible():
    dict = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as file:
        for row in file:
            row = row.strip().split(',')
            kanji = row[0]
            for yomi in row[1:]:
                if int(yomi[-1]) < 9:
                    continue
                yomi = yomi[:-2]
                yomi = yomi.strip('（）')
                yomi = to_hiragana(yomi)
                pos = yomi.find('―')
                if pos < 0:
                    continue
                assert 1 < pos
                word = kanji + yomi[pos + 1:]
                yomi = yomi[:pos + 1]
                add_word(dict, yomi, word)
    return dict
