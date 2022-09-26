# Copyright (c) 2017-2022 Esrille Inc.
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

import codecs
import itertools
import re
import sys

from toolpath import toolpath


re_kana = re.compile(r"[ぁ-ゖか゚き゚く゚け゚こ゚ァ-ヶーカ゚キ゚ク゚ケ゚コ゚セ゚ツ゚ト゚ㇰ-ㇹㇷ゚ㇺ-ㇿヷヸヹヺ]")

re_non_regular_yomi = re.compile(r"[^ぁ-ゖー#]")

re_skk_yomi = re.compile(r"^[ぁ-ゖー#]+[a-z―]?$")

re_alpha = re.compile(r"[a-zA-Z]")

re_onyomi = re.compile(r"[^ぁ-ゖー]")

# 常用漢字、人名漢字、おもなJIS記号にふくまれない字に一致する正規表現
re_hyogai = re.compile(r"[^0-9A-Za-zぁ-ゖか゚き゚く゚け゚こ゚ァ-ヶーカ゚キ゚ク゚ケ゚コ゚セ゚ツ゚ト゚ㇰ-ㇹㇷ゚ㇺ-ㇿヷヸヹヺ亜哀挨愛曖悪握圧扱宛嵐安案暗以衣位囲医依委威為畏胃尉異移萎偉椅彙意違維慰遺緯域育一壱逸茨芋引印因咽姻員院淫陰飲隠韻右宇羽雨唄鬱畝浦運雲永泳英映栄営詠影鋭衛易疫益液駅悦越謁閲円延沿炎怨宴媛援園煙猿遠鉛塩演縁艶汚王凹央応往押旺欧殴桜翁奥横岡屋億憶臆虞乙俺卸音恩温穏下化火加可仮何花佳価果河苛科架夏家荷華菓貨渦過嫁暇禍靴寡歌箇稼課蚊牙瓦我画芽賀雅餓介回灰会快戒改怪拐悔海界皆械絵開階塊楷解潰壊懐諧貝外劾害崖涯街慨蓋該概骸垣柿各角拡革格核殻郭覚較隔閣確獲嚇穫学岳楽額顎掛潟括活喝渇割葛滑褐轄且株釜鎌刈干刊甘汗缶完肝官冠巻看陥乾勘患貫寒喚堪換敢棺款間閑勧寛幹感漢慣管関歓監緩憾還館環簡観韓艦鑑丸含岸岩玩眼頑顔願企伎危机気岐希忌汽奇祈季紀軌既記起飢鬼帰基寄規亀喜幾揮期棋貴棄毀旗器畿輝機騎技宜偽欺義疑儀戯擬犠議菊吉喫詰却客脚逆虐九久及弓丘旧休吸朽臼求究泣急級糾宮救球給嗅窮牛去巨居拒拠挙虚許距魚御漁凶共叫狂京享供協況峡挟狭恐恭胸脅強教郷境橋矯鏡競響驚仰暁業凝曲局極玉巾斤均近金菌勤琴筋僅禁緊錦謹襟吟銀区句苦駆具惧愚空偶遇隅串屈掘窟熊繰君訓勲薫軍郡群兄刑形系径茎係型契計恵啓掲渓経蛍敬景軽傾携継詣慶憬稽憩警鶏芸迎鯨隙劇撃激桁欠穴血決結傑潔月犬件見券肩建研県倹兼剣拳軒健険圏堅検嫌献絹遣権憲賢謙鍵繭顕験懸元幻玄言弦限原現舷減源厳己戸古呼固股虎孤弧故枯個庫湖雇誇鼓錮顧五互午呉後娯悟碁語誤護口工公勾孔功巧広甲交光向后好江考行坑孝抗攻更効幸拘肯侯厚恒洪皇紅荒郊香候校耕航貢降高康控梗黄喉慌港硬絞項溝鉱構綱酵稿興衡鋼講購乞号合拷剛傲豪克告谷刻国黒穀酷獄骨駒込頃今困昆恨根婚混痕紺魂墾懇左佐沙査砂唆差詐鎖座挫才再災妻采砕宰栽彩採済祭斎細菜最裁債催塞歳載際埼在材剤財罪崎作削昨柵索策酢搾錯咲冊札刷刹拶殺察撮擦雑皿三山参桟蚕惨産傘散算酸賛残斬暫士子支止氏仕史司四市矢旨死糸至伺志私使刺始姉枝祉肢姿思指施師恣紙脂視紫詞歯嗣試詩資飼誌雌摯賜諮示字寺次耳自似児事侍治持時滋慈辞磁餌璽鹿式識軸七𠮟失室疾執湿嫉漆質実芝写社車舎者射捨赦斜煮遮謝邪蛇尺借酌釈爵若弱寂手主守朱取狩首殊珠酒腫種趣寿受呪授需儒樹収囚州舟秀周宗拾秋臭修袖終羞習週就衆集愁酬醜蹴襲十汁充住柔重従渋銃獣縦叔祝宿淑粛縮塾熟出述術俊春瞬旬巡盾准殉純循順準潤遵処初所書庶暑署緒諸女如助序叙徐除小升少召匠床抄肖尚招承昇松沼昭宵将消症祥称笑唱商渉章紹訟勝掌晶焼焦硝粧詔証象傷奨照詳彰障憧衝賞償礁鐘上丈冗条状乗城浄剰常情場畳蒸縄壌嬢錠譲醸色拭食植殖飾触嘱織職辱尻心申伸臣芯身辛侵信津神唇娠振浸真針深紳進森診寝慎新審震薪親人刃仁尽迅甚陣尋腎須図水吹垂炊帥粋衰推酔遂睡穂随髄枢崇数据杉裾寸瀬是井世正生成西声制姓征性青斉政星牲省凄逝清盛婿晴勢聖誠精製誓静請整醒税夕斥石赤昔析席脊隻惜戚責跡積績籍切折拙窃接設雪摂節説舌絶千川仙占先宣専泉浅洗染扇栓旋船戦煎羨腺詮践箋銭潜線遷選薦繊鮮全前善然禅漸膳繕狙阻祖租素措粗組疎訴塑遡礎双壮早争走奏相荘草送倉捜挿桑巣掃曹曽爽窓創喪痩葬装僧想層総遭槽踪操燥霜騒藻造像増憎蔵贈臓即束足促則息捉速側測俗族属賊続卒率存村孫尊損遜他多汰打妥唾堕惰駄太対体耐待怠胎退帯泰堆袋逮替貸隊滞態戴大代台第題滝宅択沢卓拓託濯諾濁但達脱奪棚誰丹旦担単炭胆探淡短嘆端綻誕鍛団男段断弾暖談壇地池知値恥致遅痴稚置緻竹畜逐蓄築秩窒茶着嫡中仲虫沖宙忠抽注昼柱衷酎鋳駐著貯丁弔庁兆町長挑帳張彫眺釣頂鳥朝貼超腸跳徴嘲潮澄調聴懲直勅捗沈珍朕陳賃鎮追椎墜通痛塚漬坪爪鶴低呈廷弟定底抵邸亭貞帝訂庭逓停偵堤提程艇締諦泥的笛摘滴適敵溺迭哲鉄徹撤天典店点展添転塡田伝殿電斗吐妬徒途都渡塗賭土奴努度怒刀冬灯当投豆東到逃倒凍唐島桃討透党悼盗陶塔搭棟湯痘登答等筒統稲踏糖頭謄藤闘騰同洞胴動堂童道働銅導瞳峠匿特得督徳篤毒独読栃凸突届屯豚頓貪鈍曇丼那奈内梨謎鍋南軟難二尼弐匂肉虹日入乳尿任妊忍認寧熱年念捻粘燃悩納能脳農濃把波派破覇馬婆罵拝杯背肺俳配排敗廃輩売倍梅培陪媒買賠白伯拍泊迫剝舶博薄麦漠縛爆箱箸畑肌八鉢発髪伐抜罰閥反半氾犯帆汎伴判坂阪板版班畔般販斑飯搬煩頒範繁藩晩番蛮盤比皮妃否批彼披肥非卑飛疲秘被悲扉費碑罷避尾眉美備微鼻膝肘匹必泌筆姫百氷表俵票評漂標苗秒病描猫品浜貧賓頻敏瓶不夫父付布扶府怖阜附訃負赴浮婦符富普腐敷膚賦譜侮武部舞封風伏服副幅復福腹複覆払沸仏物粉紛雰噴墳憤奮分文聞丙平兵併並柄陛閉塀幣弊蔽餅米壁璧癖別蔑片辺返変偏遍編弁便勉歩保哺捕補舗母募墓慕暮簿方包芳邦奉宝抱放法泡胞俸倣峰砲崩訪報蜂豊飽褒縫亡乏忙坊妨忘防房肪某冒剖紡望傍帽棒貿貌暴膨謀頰北木朴牧睦僕墨撲没勃堀本奔翻凡盆麻摩磨魔毎妹枚昧埋幕膜枕又末抹万満慢漫未味魅岬密蜜脈妙民眠矛務無夢霧娘名命明迷冥盟銘鳴滅免面綿麺茂模毛妄盲耗猛網目黙門紋問冶夜野弥厄役約訳薬躍闇由油喩愉諭輸癒唯友有勇幽悠郵湧猶裕遊雄誘憂融優与予余誉預幼用羊妖洋要容庸揚揺葉陽溶腰様瘍踊窯養擁謡曜抑沃浴欲翌翼拉裸羅来雷頼絡落酪辣乱卵覧濫藍欄吏利里理痢裏履璃離陸立律慄略柳流留竜粒隆硫侶旅虜慮了両良料涼猟陵量僚領寮療瞭糧力緑林厘倫輪隣臨瑠涙累塁類令礼冷励戻例鈴零霊隷齢麗暦歴列劣烈裂恋連廉練錬呂炉賂路露老労弄郎朗浪廊楼漏籠六録麓論和話賄脇惑枠湾腕０-９Ａ-Ｚａ-ｚ々〆〇丑丞乃之乎也云亘些亦亥亨亮仔伊伍伽佃佑伶侃侑俄俠俣俐倭俱倦倖偲傭儲允兎兜其冴凌凜凧凪凰凱函劉劫勁勺勿匁匡廿卜卯卿厨厩叉叡叢叶只吾吞吻哉哨啄哩喬喧喰喋嘩嘉嘗噌噂圃圭坐尭坦埴堰堺堵塙壕壬夷奄奎套娃姪姥娩嬉孟宏宋宕宥寅寓寵尖尤屑峨峻崚嵯嵩嶺巌巫已巳巴巷巽帖幌幡庄庇庚庵廟廻弘弛彗彦彪彬徠忽怜恢恰恕悌惟惚悉惇惹惺惣慧憐戊或戟托按挺挽掬捲捷捺捧掠揃摑摺撒撰撞播撫擢孜敦斐斡斧斯於旭昂昊昏昌昴晏晃晒晋晟晦晨智暉暢曙曝曳朋朔杏杖杜李杭杵杷枇柑柴柘柊柏柾柚桧栞桔桂栖桐栗梧梓梢梛梯桶梶椛梁棲椋椀楯楚楕椿楠楓椰楢楊榎樺榊榛槙槍槌樫槻樟樋橘樽橙檎檀櫂櫛櫓欣欽歎此殆毅毘毬汀汝汐汲沌沓沫洸洲洵洛浩浬淵淳渚淀淋渥湘湊湛溢滉溜漱漕漣澪濡瀕灘灸灼烏焰焚煌煤煉熙燕燎燦燭燿爾牒牟牡牽犀狼猪獅玖珂珈珊珀玲琢琉瑛琥琶琵琳瑚瑞瑶瑳瓜瓢甥甫畠畢疋疏皐皓眸瞥矩砦砥砧硯碓碗碩碧磐磯祇祢祐祷禄禎禽禾秦秤稀稔稟稜穣穹穿窄窪窺竣竪竺竿笈笹笙笠筈筑箕箔篇篠簞簾籾粥粟糊紘紗紐絃紬絆絢綺綜綴緋綾綸縞徽繫繡纂纏羚翔翠耀而耶耽聡肇肋肴胤胡脩腔脹膏臥舜舵芥芹芭芙芦苑茄苔苺茅茉茸茜莞荻莫莉菅菫菖萄菩萌萊菱葦葵萱葺萩董葡蓑蒔蒐蒼蒲蒙蓉蓮蔭蔣蔦蓬蔓蕎蕨蕉蕃蕪薙蕾蕗藁薩蘇蘭蝦蝶螺蟬蟹蠟衿袈袴裡裟裳襖訊訣註詢詫誼諏諄諒謂諺讃豹貰賑赳跨蹄蹟輔輯輿轟辰辻迂迄辿迪迦這逞逗逢遥遁遼邑祁郁鄭酉醇醐醍醬釉釘釧銑鋒鋸錘錐錆錫鍬鎧閃閏閤阿陀隈隼雀雁雛雫霞靖鞄鞍鞘鞠鞭頁頌頗顚颯饗馨馴馳駕駿驍魁魯鮎鯉鯛鰯鱒鱗鳩鳶鳳鴨鴻鵜鵬鷗鷲鷺鷹麒麟麿黎黛鼎亞惡爲逸榮衞謁圓緣薗應櫻奧橫溫價禍悔海壞懷樂渴卷陷寬漢氣祈器僞戲虛峽狹響曉勤謹駈勳薰惠揭鷄藝擊縣儉劍險圈檢顯驗嚴廣恆黃國黑穀碎雜祉視兒濕實社者煮壽收臭從澁獸縱祝暑署緖諸敍將祥涉燒奬條狀乘淨剩疊孃讓釀神眞寢愼盡粹醉穗瀨齊靜攝節專戰纖禪祖壯爭莊搜巢曾裝僧層瘦騷增憎藏贈臟卽帶滯瀧單嘆團彈晝鑄著廳徵聽懲鎭轉傳都嶋燈盜稻德突難拜盃賣梅髮拔繁晚卑祕碑賓敏冨侮福拂佛勉步峯墨飜每萬默埜彌藥與搖樣謠來賴覽欄龍虜凉綠淚壘類禮曆歷練鍊郞朗廊錄⓪①-⑳㉑-㉟㊱-㊿ⓐ-ⓩ⓵-⓾⓿❶-❿⓫-⓴㋐-㋾㊀-㊉㊊-㊰ⅰ-ⅻⅠ-Ⅺ、。，．・：；？！゛゜´｀¨＾‾＿ヽヾゝゞ〃仝〆〇ー—‐／＼〜‖｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】＋−±×÷＝≠＜＞≦≧∞∴♂♀°′″℃￥＄￠￡％＃＆＊＠§☆★○●◎◇◆□■△▲▽▼※〒→←↑↓〓＇＂－～〳〴〵〻〼ヿゟ∈∋⊆⊇⊂⊃∪∩⊄⊅⊊⊋∉∅⌅⌆∧∨￢⇒⇔∀∃⊕⊖⊗∥∦｟｠〘〙〖〗∠⊥⌒∂∇≡≒≪≫√∽∝∵∫∬≢≃≅≈≶≷↔Å‰♯♭♪†‡¶♮♫♬♩◯▷▶◁◀↗↘↖↙⇄⇨⇦⇧⇩⤴⤵⦿◉〽﹆﹅◦•∓ℵℏ㏋ℓ℧゠–⧺⧻♤♠♢♦♡♥♧♣☖☗〠☎☀☁☂☃♨▱⋚⋛⅓⅔⅕✓⌘␣⏎─│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂◐◑◒◓€￤©ª«®￣²³·¸¹º»¼½¾⁑⁂㍉㌔㌢㍍㌘㌧㌃㌶㍑㍗㌍㌦㌣㌫㍊㌻㎜㎝㎞㎎㎏㏄㎡Ⅻ㍻〝〟№㏍℡㈱㈲㈹㍾㍽㍼∮∟⊿❖☞]")

# おもなJIS記号に一致する正規表現
re_kigou = re.compile(r"[Α-Ωα-ως⓪①-⑳㉑-㉟㊱-㊿ⓐ-ⓩ⓵-⓾⓿❶-❿⓫-⓴㋐-㋾㊀-㊉㊊-㊰ⅰ-ⅻⅠ-Ⅺ、。，．・：；？！゛゜´｀¨＾‾＿ヽヾゝゞ〃仝〆〇ー—‐／＼〜‖｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】＋−±×÷＝≠＜＞≦≧∞∴♂♀°′″℃￥＄￠￡％＃＆＊＠§☆★○●◎◇◆□■△▲▽▼※〒→←↑↓〓＇＂－～〳〴〵〻〼ヿゟ∈∋⊆⊇⊂⊃∪∩⊄⊅⊊⊋∉∅⌅⌆∧∨￢⇒⇔∀∃⊕⊖⊗∥∦｟｠〘〙〖〗∠⊥⌒∂∇≡≒≪≫√∽∝∵∫∬≢≃≅≈≶≷↔Å‰♯♭♪†‡¶♮♫♬♩◯▷▶◁◀↗↘↖↙⇄⇨⇦⇧⇩⤴⤵⦿◉〽﹆﹅◦•∓ℵℏ㏋ℓ℧゠–⧺⧻♤♠♢♦♡♥♧♣☖☗〠☎☀☁☂☃♨▱⋚⋛⅓⅔⅕✓⌘␣⏎─│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂◐◑◒◓€￤©ªV«®￣²³·¸¹º»¼½¾⁑⁂㍉㌔㌢㍍㌘㌧㌃㌶㍑㍗㌍㌦㌣㌫㍊㌻㎜㎝㎞㎎㎏㏄㎡Ⅻ㍻〝〟№㏍℡㈱㈲㈹㍾㍽㍼∮∟⊿❖☞]")

re_zinmei = re.compile(r"[丑丞乃之乎也云亘些亦亥亨亮仔伊伍伽佃佑伶侃侑俄俠俣俐倭俱倦倖偲傭儲允兎兜其冴凌凜凧凪凰凱函劉劫勁勺勿匁匡廿卜卯卿厨厩叉叡叢叶只吾吞吻哉哨啄哩喬喧喰喋嘩嘉嘗噌噂圃圭坐尭坦埴堰堺堵塙壕壬夷奄奎套娃姪姥娩嬉孟宏宋宕宥寅寓寵尖尤屑峨峻崚嵯嵩嶺巌巫已巳巴巷巽帖幌幡庄庇庚庵廟廻弘弛彗彦彪彬徠忽怜恢恰恕悌惟惚悉惇惹惺惣慧憐戊或戟托按挺挽掬捲捷捺捧掠揃摑摺撒撰撞播撫擢孜敦斐斡斧斯於旭昂昊昏昌昴晏晃晒晋晟晦晨智暉暢曙曝曳朋朔杏杖杜李杭杵杷枇柑柴柘柊柏柾柚桧栞桔桂栖桐栗梧梓梢梛梯桶梶椛梁棲椋椀楯楚楕椿楠楓椰楢楊榎樺榊榛槙槍槌樫槻樟樋橘樽橙檎檀櫂櫛櫓欣欽歎此殆毅毘毬汀汝汐汲沌沓沫洸洲洵洛浩浬淵淳渚淀淋渥湘湊湛溢滉溜漱漕漣澪濡瀕灘灸灼烏焰焚煌煤煉熙燕燎燦燭燿爾牒牟牡牽犀狼猪獅玖珂珈珊珀玲琢琉瑛琥琶琵琳瑚瑞瑶瑳瓜瓢甥甫畠畢疋疏皐皓眸瞥矩砦砥砧硯碓碗碩碧磐磯祇祢祐祷禄禎禽禾秦秤稀稔稟稜穣穹穿窄窪窺竣竪竺竿笈笹笙笠筈筑箕箔篇篠簞簾籾粥粟糊紘紗紐絃紬絆絢綺綜綴緋綾綸縞徽繫繡纂纏羚翔翠耀而耶耽聡肇肋肴胤胡脩腔脹膏臥舜舵芥芹芭芙芦苑茄苔苺茅茉茸茜莞荻莫莉菅菫菖萄菩萌萊菱葦葵萱葺萩董葡蓑蒔蒐蒼蒲蒙蓉蓮蔭蔣蔦蓬蔓蕎蕨蕉蕃蕪薙蕾蕗藁薩蘇蘭蝦蝶螺蟬蟹蠟衿袈袴裡裟裳襖訊訣註詢詫誼諏諄諒謂諺讃豹貰賑赳跨蹄蹟輔輯輿轟辰辻迂迄辿迪迦這逞逗逢遥遁遼邑祁郁鄭酉醇醐醍醬釉釘釧銑鋒鋸錘錐錆錫鍬鎧閃閏閤阿陀隈隼雀雁雛雫霞靖鞄鞍鞘鞠鞭頁頌頗顚颯饗馨馴馳駕駿驍魁魯鮎鯉鯛鰯鱒鱗鳩鳶鳳鴨鴻鵜鵬鷗鷲鷺鷹麒麟麿黎黛鼎亞惡爲逸榮衞謁圓緣薗應櫻奧橫溫價禍悔海壞懷樂渴卷陷寬漢氣祈器僞戲虛峽狹響曉勤謹駈勳薰惠揭鷄藝擊縣儉劍險圈檢顯驗嚴廣恆黃國黑穀碎雜祉視兒濕實社者煮壽收臭從澁獸縱祝暑署緖諸敍將祥涉燒奬條狀乘淨剩疊孃讓釀神眞寢愼盡粹醉穗瀨齊靜攝節專戰纖禪祖壯爭莊搜巢曾裝僧層瘦騷增憎藏贈臟卽帶滯瀧單嘆團彈晝鑄著廳徵聽懲鎭轉傳都嶋燈盜稻德突難拜盃賣梅髮拔繁晚卑祕碑賓敏冨侮福拂佛勉步峯墨飜每萬默埜彌藥與搖樣謠來賴覽欄龍虜凉綠淚壘類禮曆歷練鍊郞朗廊錄]")

def to_hirakana(s):
    katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヴ"
    hirakana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゔ"
    t = ''
    for c in s:
        i = katakana.find(c)
        if i == -1:
            t += c
        else:
            t += hirakana[i]
    return t

def to_seion(s):
    dakuon = "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉゃゅょっゔ"
    seion  = "かきくけこさしすせそたちつてとはひふへほはひふへほあいうえおやゆよつう"
    t = ''
    for c in s:
        i = dakuon.find(c)
        if i == -1:
            t += c
        else:
            t += seion[i]
    return t

def output(dict):
    for yomi, kanji in sorted(dict.items()):
        print(yomi, ' /', '/'.join(kanji), '/', sep='')

# 常用漢字表から辞書をつくります。
def zyouyou(grade = 10):
    dict = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as zyouyou:
        for row in zyouyou:
            row = row.strip(" \n").split(",")
            kanji = row[0]
            row.remove(kanji)
            for yomi in row[:]:
                g = int(yomi[-1])
                if grade < g:
                    continue
                g = yomi[-2:]
                k = kanji
                yomi = yomi[:-2]
                yomi = yomi.strip("（）")
                yomi = to_hirakana(yomi)
                pos = yomi.find('―')
                if 0 <= pos:
                    k += yomi[pos + 1:]
                    yomi = yomi[:pos + 1]
                k += g
                if not yomi in dict:
                    dict[yomi] = list()
                    dict[yomi].append(k)
                elif not k in dict[yomi]:
                    dict[yomi].append(k)
    for yomi, kanji in dict.items():
        l = list()
        for i in range(1, 10):
            for k in kanji:
                if int(k[-1]) == i:
                    if not k[:-2] in l:
                        l.append(k[:-2])
        dict[yomi] = l
    return dict

# 常用漢字表から漢字の学習年度辞書をつくります。
def zyouyou_grades():
    grades = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as zyouyou:
        for row in zyouyou:
            grade = 10
            row = row.strip(' \n').split(',')
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
    try:
        file = codecs.open(path, "r", encoding)
    except:
        pass
    else:
        for row in file:
            row = row.strip(" \n")
            if not row or row[0] == ';':
                continue
            row = row.split(" ", 1)
            yomi = row[0]
            if not re_skk_yomi.match(yomi):
                continue
            if re_alpha.match(yomi[-1]):
                # SKK辞書のおくりありのよみ
                yomi = yomi[:-1] + '―'
            kanji = row[1].strip(" \n/").split("/")
            s = list()
            for i in kanji:
                pos = i.find(';')
                if 0 == pos:
                    continue
                if 0 < pos:
                    i = i[:pos]
                if not i in s:
                    s.append(i)
            if s:
                if not yomi in dict:
                    dict[yomi] = s
                else:
                    dict[yomi].extend([x for x in s if x not in dict[yomi]])
        file.close()
    return dict

def _get_grade(cand, grades):
    grade = 1
    for i in cand:
        g = grades.get(i, grade)
        if grade < g:
            grade = g
    return grade

# 付表をよみこみます。
def load_huhyou(path, grade = 10):
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
                s = list()
                for i in cand:
                    if _get_grade(i, grades) <= grade:
                        s.append(i)
            if s:
                if not yomi in dict:
                    dict[yomi] = s
                else:
                    dict[yomi].extend([x for x in s if x not in dict[yomi]])
    return dict

# SKK辞書のヘッダー部分を出力します。
def copy_header(path):
    encoding = _get_encoding(path)
    try:
        file = codecs.open(path, "r", encoding)
    except:
        pass
    else:
        for row in file:
            if not row or row[0] != ';':
                break
            row = row.strip(" \n")
            if row == ';; okuri-ari entries.':
                break
            print(row)
        file.close()

# 2つの辞書の共通部分をとりだした辞書をかえします。
def intersection(a, b):
    dict = {}
    keys = set(a.keys()).intersection(set(b.keys()))
    for yomi in keys:
        if not yomi in a or not yomi in b:
            continue
        kanji = [x for x in a[yomi] if x in b[yomi]]
        if not kanji:
            continue
        dict[yomi] = kanji
    return dict

# 2つの辞書の和集合をとりだした辞書をかえします。
def union(a, b):
    c = a.copy()
    for yomi, kanji in b.items():
        if not yomi in c:
            c[yomi] = kanji
        else:
            c[yomi].extend([x for x in kanji if x not in c[yomi]])
    return c

# 2つの辞書の差集合をとりだした辞書をかえします。
def difference(a, b):
    c = a.copy()
    for yomi, kanji in b.items():
        if yomi in c:
            c[yomi] = [x for x in c[yomi] if x not in kanji]
            if not c[yomi]:
                del c[yomi]
    return c

# 2つの辞書のよみの共通部分をとりだした辞書をかえします。
def intersection_yomi(a, b):
    dict = {}
    keys = set(a.keys()).intersection(set(b.keys()))
    for yomi in keys:
        if yomi in a and yomi in b:
            kanji = a[yomi]
            kanji.extend([x for x in b[yomi] if x not in kanji])
        elif yomi in a:
            kanji = a[yomi]
        else:
            kanji = b[yomi]
        dict[yomi] = kanji
    return dict

# 記号をつかっている語をとりだします。
def kigou(dict):
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if i not in s and re_kigou.search(i):
                s.append(i)
        if s:
            d[yomi] = s
    return d

# 表外漢字をつかっている熟語をとりだします。
def hyougai(dict):
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if i not in s and re_hyogai.search(i):
                s.append(i)
        if s:
            d[yomi] = s
    return d

# 人名漢字をつかっている熟語をとりだします。
def zinmei(dict):
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if i not in s and re_zinmei.search(i):
                s.append(i)
        if s:
            d[yomi] = s
    return d

# おくりがなのある語をとりだします。
def okuri(dict):
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if i not in s and re_kana.search(i):
                s.append(i)
        if s:
            d[yomi] = s
    return d

# 最後におくりがなのある語をとりだします。
def okuri_end(dict):
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if re_kana.search(i[-1]):
                s.append(i)
        if s:
            d[yomi] = s
    return d

# 用言をリストアップします。
def yougen(dict):
    d = {}
    for yomi, kanji in dict.items():
        if yomi[-1] == '―':
            d[yomi] = kanji
    return d

# 用言と体言をまとめた辞書をつくります。
def mix_yougen(dict):
    d = dict.copy()
    for yomi, kanji in dict.items():
        if yomi[-1] != '―':
            continue
        yomi = yomi[:-1]
        if not yomi in d:
            s = list()
            for i in kanji:
                s.append(i + '―')
            d[yomi] = s
            continue
        for i in kanji:
            if not i in d[yomi]:
                d[yomi].append(i + '―')
    return d

def _is_hyounai_yomi(zyouyou, yomi, kanji):
    # ― と # をとりのぞく。
    yomi = yomi.replace('―', '')
    yomi = yomi.replace('#', '')
    kanji = kanji.replace('#', '')
    if len(kanji) == 1:
        if not kanji in zyouyou:
            return False
        return yomi in zyouyou[kanji]
    c = kanji[0]
    if not c in zyouyou:
        return False
    s = zyouyou[c]
    b = c
    for c in kanji[1:]:
        if c == '々':
            if b == c:
                # e.g. 個人々々
                return False
            t = set(itertools.product(s, zyouyou[b]))
        elif re_kana.match(c):
            t = set(itertools.product(s, set(c)))
        elif not c in zyouyou:
            return False
        else:
            t = set(itertools.product(s, zyouyou[c]))
        s = set()
        for y in t:
            s.add(to_seion(''.join(y)))
            if 2 <= len(y[0]):
                # 促音化の許容
                if 0 <= "きくキク".find(y[0][-1]) and 0 <= "かきくけこカキクケコ".find(y[1][0]) or 0 <= "ちつチツ".find(y[0][-1]) and 0 <= "かきくけこカキクケコさしすせそサシスセソたちつてとタチツテトはひふへほハヒフヘホ".find(y[1][0]):
                    s.add(to_seion(y[0][0:-1] + "つ" + y[1]))
        b = c
    return to_seion(yomi) in s

# 表外のよみかたをつかっている熟語をとりだします。
def hyougai_yomi(dict, grade = 10):
    zyouyou = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as file:
        for row in file:
            row = row.strip(" \n").split(",")
            kanji = row[0]
            row.remove(kanji)
            s = set()
            for yomi in row[:]:
                g = int(yomi[-1])
                if grade < g:
                    continue
                yomi = yomi[:-2]
                yomi = yomi.strip("（）")
                pos = yomi.find('―')
                if 0 <= pos:
                    yomi = yomi[:pos]
                if not yomi:
                    continue
                s.add(to_hirakana(yomi))
            if s:
                zyouyou[kanji] = s
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if not _is_hyounai_yomi(zyouyou, yomi, i):
                s.append(i)
        if s:
            d[yomi] = s
    return d

# 和語の熟語をとりだします。
def wago(dict, grade = 10):
    zyouyou = {}
    with open(toolpath('zyouyou-kanji.csv'), 'r') as file:
        for row in file:
            row = row.strip(" \n").split(",")
            kanji = row[0]
            row.remove(kanji)
            s = set()
            for yomi in row[:]:
                g = int(yomi[-1])
                if grade < g:
                    continue
                yomi = yomi[:-2]
                yomi = yomi.strip("（）")
                pos = yomi.find('―')
                if 0 <= pos:
                    yomi = yomi[:pos]
                if not yomi:
                    continue
                if re_onyomi.search(yomi):
                    continue
                s.add(yomi)
            if s:
                zyouyou[kanji] = s
    d = {}
    for yomi, kanji in dict.items():
        s = list()
        for i in kanji:
            if _is_hyounai_yomi(zyouyou, yomi, i):
                s.append(i)
        if s:
            d[yomi] = s
    return d
