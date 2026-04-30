#!/usr/bin/env python3
import os, re, requests, base64, json, random, time
from datetime import datetime

WORKER_URL   = 'https://rakuten-proxy.sobamoripaya.workers.dev'
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO  = 'gadget-tengoku/gadget-lab'
SITE_URL     = 'https://gadget-tengoku.com'
SLOT         = os.environ.get('SLOT', 'am')

TWITTER_API_KEY             = os.environ.get('API_KEY', '')
TWITTER_API_SECRET          = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN        = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

TRUSTED_BRANDS = [
    'anker','sony','apple','samsung','garmin','bose','jbl','panasonic','sharp',
    'dyson','philips','lg','dell','logicool','logitech','shokz','jabra',
    'sennheiser','audio-technica','asus','microsoft','google','gopro','dji',
    'canon','nikon','fujifilm','irobot','ecovacs','switchbot','qrio','buffalo',
    'elecom','belkin','cio','mophie','razer','steelseries','hyperx','corsair',
    'beats','soundcore','edifier','jvc','kenwood','pioneer',
    'パナソニック','シャープ','ソニー','アンカー','エレコム','バッファロー',
    'キヤノン','ニコン','富士フイルム','ダイソン','フィリップス','ケンウッド',
]

# CTA パターン（購買意欲を刺激）
CTA_MAIN = [
    '今の最安値を楽天で確認する →',
    '在庫あり・最短翌日届く｜楽天で購入する',
    '楽天の口コミを読んで購入する →',
    '価格・在庫・レビューを楽天で確認する',
    '迷ったらこれ。楽天で詳細を見る →',
]
CTA_SUB = [
    '実際のレビュー（{rc:,}件）を読む →',
    '他の人の口コミも確認する →',
    '詳細スペックを楽天で確認する →',
]

ALL_THEMES = [
    {
        'kw':'Sony WF-1000XM5 ワイヤレスイヤホン ノイキャン',
        'title':'通勤・在宅ワーク向けノイキャンイヤホン',
        'cat':'イヤホン',
        'must':['イヤホン','ヘッドホン'],
        'exclude':['ケース','ポーチ','カバー','クッション','交換','イヤーパッド','イヤーチップ'],
        'lead':'電車の騒音・家族の声・オフィスの雑音を消して、音楽もWeb会議も快適にしたい方向けの記事です。',
        'persona':'毎日満員電車で通勤する30代ビジネスマン。周囲の騒音でリモート会議の声が聞き取れない',
        'pain':'「電車でイヤホンをしていても騒音が気になる」「在宅で家族の声が会議中に入る」',
        'decision':'ノイキャン性能・装着感・マイク品質の3点で選ぶと失敗しません',
        'faq':[
            ('ノイキャンイヤホンは飛行機でも効果がありますか？','はい、飛行機のエンジン音は低周波なのでノイキャンが特に効果的です。長距離フライトに必携です。'),
            ('長時間（8時間以上）つけていても耳が痛くなりませんか？','イヤーピースのサイズが合っていれば4〜6時間は問題なし。それ以上はカナル型より開放型の検討も。'),
            ('Web会議のマイク品質はどうですか？','上位モデルはビームフォーミングマイクを採用し、周囲のノイズを拾いにくい設計です。'),
            ('iPhoneとAndroid両方で使えますか？','Bluetooth接続なのでOS問わず使用可。ただし専用アプリの機能はiOSの方が充実しているケースも。'),
            ('洗えますか？汗や雨に強いですか？','IPX4以上のモデルは小雨・汗程度なら問題なし。水没はNGなのでジムのシャワーには注意。'),
        ],
    },
    {
        'kw':'Jabra Elite ワイヤレスイヤホン スポーツ 防水',
        'title':'ランニング・スポーツ向けワイヤレスイヤホン',
        'cat':'イヤホン',
        'must':['イヤホン'],
        'exclude':['ケース','ポーチ','カバー','交換'],
        'lead':'走っても落ちない・汗で壊れない・外音も聞こえる。スポーツ中に本当に使えるイヤホンを探している方向けです。',
        'persona':'週3回ランニングする健康意識の高い30代。運動中にイヤホンが外れて困っている',
        'pain':'「走るとイヤホンがずれる」「汗で壊れた経験がある」「車の音が聞こえなくて怖い」',
        'decision':'防水（IPX5以上）・固定方法（イヤーフック）・外音取り込みの3点で絞り込む',
        'faq':[
            ('スポーツ中にイヤホンが外れないか心配です','イヤーフックやウイングチップ付きのモデルを選びましょう。Jabraは固定力に定評があります。'),
            ('防水はどれくらい必要ですか？','ランニングの汗・小雨ならIPX4〜5で十分。水泳するならIPX7以上が必要です。'),
            ('外音取り込み機能は必要ですか？','交通量の多い道を走るなら必須です。車の音を聞きながら音楽を楽しめて安全です。'),
            ('骨伝導イヤホンとどちらが向いていますか？','音質重視ならインイヤー、安全性・長時間装着ならShokzなどの骨伝導を検討してください。'),
            ('バッテリーはどれくらいもちますか？','スポーツ向けは本体6〜8時間が目安。フルマラソンも余裕でカバーできます。'),
        ],
    },
    {
        'kw':'Anker Soundcore Liberty ワイヤレスイヤホン コスパ',
        'title':'1万円以下で買えるコスパ最強ワイヤレスイヤホン',
        'cat':'イヤホン',
        'must':['イヤホン'],
        'exclude':['ケース','ポーチ','カバー','交換'],
        'lead':'「AirPodsは高すぎる。でも安すぎると音質が心配」という方向けに、1万円以下で本当に使えるモデルだけ厳選しました。',
        'persona':'予算1万円以内でAirPodsの代わりを探している20代・大学生',
        'pain':'「3万円はさすがに高い」「でも安物買いの銭失いはしたくない」',
        'decision':'Anker・Soundcoreなど信頼ブランドの1万円以下モデルに絞れば失敗しない',
        'faq':[
            ('1万円以下でも音質は大丈夫ですか？','AnkerやEarFunなど信頼ブランドなら十分満足できる音質。ハイレゾ対応モデルも増えています。'),
            ('AirPodsと何が違いますか？','音質は同等以上のモデルも存在。Androidユーザーならむしろコスパ系の方が機能が豊富なことも。'),
            ('1万円以下でもノイキャンはついていますか？','AnkerのSoundcoreシリーズなら搭載モデルあり。高額機より効果は劣りますが十分実用的です。'),
            ('保証は何年ですか？','Ankerは18ヶ月保証。国内正規品を購入すれば安心して使えます。'),
            ('充電ケースの充電方法は何ですか？','多くのモデルはUSB-C対応。ワイヤレス充電対応モデルもあります。'),
        ],
    },
    {
        'kw':'Shokz OpenRun 骨伝導イヤホン',
        'title':'耳をふさがない骨伝導イヤホン完全ガイド',
        'cat':'イヤホン',
        'must':['骨伝導','Shokz'],
        'exclude':['ケース','カバー','交換'],
        'lead':'耳の穴をふさがずに音楽が聴ける骨伝導イヤホン。自転車・ランニング・長時間装着に最適な理由を解説します。',
        'persona':'自転車通勤者・長距離ランナー。耳をふさいで事故に遭いそうで怖い',
        'pain':'「普通のイヤホンは危ない」「長時間つけると耳が痛い」「メガネと干渉する」',
        'decision':'Shokz一択。あとはOpenRunかOpenRun Proかを予算で決めるだけ',
        'faq':[
            ('普通のイヤホンより音が悪いですか？','低音域は劣りますが中高音はクリア。通話品質は特に優秀で、テレワークでも重宝します。'),
            ('メガネをしていても使えますか？','Shokzはメガネとの干渉が少ない設計。ただし初めて使う際は装着感を確認しましょう。'),
            ('防水性能はどれくらいですか？','OpenRunはIP67防水。雨天・汗・水洗いもOKです。'),
            ('テレワークのWeb会議でも使えますか？','マイク内蔵でノイズキャンセリングも優秀。会議用としての評価が非常に高いです。'),
            ('耳の穴をふさがないと音楽が漏れませんか？','静かな場所では多少聞こえます。電車の中などでの使用は音量に注意が必要です。'),
        ],
    },
    {
        'kw':'Sony WH-1000XM5 ノイキャン ヘッドホン 本体',
        'title':'在宅ワーク・テレワークで使えるノイキャンヘッドホン',
        'cat':'オーディオ',
        'must':['ヘッドホン'],
        'exclude':['イヤーパッド','クッション','ケーブル','交換','補修','イヤーカップ'],
        'lead':'家族の声・生活音をシャットアウトして、Web会議と作業に集中したい在宅ワーカー向けの記事です。',
        'persona':'週4日在宅勤務のエンジニア。子どもの声でWeb会議に集中できない',
        'pain':'「家で仕事に集中できない」「Web会議中に家族の声が入る」「長時間つけると疲れる」',
        'decision':'ノイキャン性能・マイク品質・長時間装着の快適さで選ぶ',
        'faq':[
            ('長時間（8時間以上）つけていても疲れませんか？','重量と側圧が重要。250g以下・柔らかいイヤーパッドのモデルなら長時間OK。'),
            ('Web会議のマイク品質はどうですか？','ビームフォーミングマイク搭載モデルは周囲のノイズを拾いにくく好評です。'),
            ('有線と無線どちらがいいですか？','在宅メインなら有線でも不便なし。外出も考えるなら無線モデルを選びましょう。'),
            ('眼鏡をしていても快適に使えますか？','側圧の強さとイヤーカップの形状が重要。試着できる機会があれば必ず確認を。'),
            ('音楽を聴かないときはノイキャンだけ使えますか？','はい、対応モデルはNCだけをONにして外部音を遮断できます。'),
        ],
    },
    {
        'kw':'Garmin Venu スマートウォッチ 健康管理',
        'title':'毎日の健康データを記録できるスマートウォッチ',
        'cat':'スマートウォッチ',
        'must':['スマートウォッチ','ウォッチ'],
        'exclude':['バンド','ベルト','充電','ケース','フィルム','交換','スタンド'],
        'lead':'睡眠・心拍・血中酸素・ストレスを毎日記録して、自分の体の変化を可視化したい方向けです。',
        'persona':'健康診断で引っかかった40代。病院に行くほどじゃないが体の状態を把握したい',
        'pain':'「体調が悪い日の原因がわからない」「睡眠の質を改善したい」「運動量が足りているか不安」',
        'decision':'バッテリー持ち・GPS精度・健康データの詳細さで選ぶ。Garminが圧倒的に優秀',
        'faq':[
            ('血圧は正確に測れますか？','医療機器ではないため参考値。ただし傾向把握・異常値アラートとして十分活用できます。'),
            ('睡眠の質はどうやって計測しますか？','心拍・血中酸素・体動から睡眠ステージ（深い/浅い/REM）を自動判定します。'),
            ('Apple Watchと何が違いますか？','Garminはバッテリー持ち5日以上・GPS精度・健康データの詳細さが強み。Apple WatchはiPhone連携と決済機能が強み。'),
            ('防水性能はありますか？','5ATM防水で水泳にも対応。毎日シャワーを浴びながら装着してOKです。'),
            ('バッテリーはどれくらいもちますか？','通常使用で5〜7日。GPS使用時は約20時間が目安です。'),
        ],
    },
    {
        'kw':'Apple Watch SE Series9 本体',
        'title':'初めてのApple Watch選び方｜SEとSeries 9どっちを買うべきか',
        'cat':'スマートウォッチ',
        'must':['Apple Watch'],
        'exclude':['バンド','ベルト','充電','ケース','フィルム','カバー','交換'],
        'lead':'「Apple WatchのSE・Series 9・Ultraの違いがわからない」という初めて買う方向けに、ズバリどれを選ぶべきかを解説します。',
        'persona':'iPhone歴5年・初めてスマートウォッチを買う30代。何を選べばいいかわからない',
        'pain':'「SEとSeries 9の違いがわからない」「Ultraは高すぎる」「失敗したくない」',
        'decision':'初めてならSE一択。Series 9は心電図・血中酸素が必要な方だけ選べばOK',
        'faq':[
            ('SEとSeries 9どちらを選べばいいですか？','初めてならSEで十分。約2万円の差額を払う価値があるのは心電図・血中酸素計機能が必要な方だけです。'),
            ('Androidでも使えますか？','Apple WatchはiPhone専用です。Androidユーザーはガーミンやサムスンが選択肢になります。'),
            ('バッテリーはどれくらいもちますか？','通常使用で約18時間。毎日充電するスタイルが前提の設計です。'),
            ('防水性能はありますか？','水深50m防水（WR50M）。水泳やシャワーも問題なし。'),
            ('社外バンドは使えますか？','はい、多数の社外品があり安価に楽しめます。公式バンドより格安で豊富なデザインが選べます。'),
        ],
    },
    {
        'kw':'Anker PowerCore モバイルバッテリー 軽量 薄型',
        'title':'毎日のカバンに入れたい軽量モバイルバッテリー',
        'cat':'モバイル',
        'must':['バッテリー','モバイル'],
        'exclude':['ケース','カバー'],
        'lead':'「重いから持ち歩くのをやめた」という経験がある方向けに、毎日使い続けられる軽量モデルだけを厳選しました。',
        'persona':'毎日通勤するビジネスパーソン。スマホが夕方に切れそうで不安だが重いのは嫌',
        'pain':'「重いバッテリーは結局カバンに入れなくなる」「薄くて軽くて容量もある商品がわからない」',
        'decision':'200g以下・10000mAh・USB-C対応の3条件を満たせばOK',
        'faq':[
            ('毎日持ち歩くなら何mAhが適切ですか？','スマホ1回分なら5000〜10000mAh。200g以下を選べば重さを感じません。'),
            ('急速充電対応かどうかの確認方法は？','PD（Power Delivery）18W以上と書かれているものが急速充電対応です。'),
            ('飛行機に持ち込めますか？','100Wh（約27000mAh）以下なら機内持ち込みOK。スーツケースへの収納はNGです。'),
            ('充電しながら使えますか（パススルー充電）？','対応モデルとそうでないものがあります。商品ページの仕様欄で確認しましょう。'),
            ('複数のデバイスを同時充電できますか？','ポート数を確認。USB-C×2のモデルならスマホとイヤホンを同時充電できます。'),
        ],
    },
    {
        'kw':'Anker PowerCore 20000 モバイルバッテリー 大容量',
        'title':'旅行・出張で絶対に電池切れにならないモバイルバッテリー',
        'cat':'モバイル',
        'must':['バッテリー','モバイル'],
        'exclude':['ケース','カバー'],
        'lead':'「3泊4日の旅行でスマホとノートPCを充電し続けたい」という方向けに、大容量モデルを厳選しました。',
        'persona':'月2〜3回出張がある営業マン。ホテルのコンセントを探し回るのに疲れた',
        'pain':'「出張先で充電切れ」「ノートPCも充電できるバッテリーが見つからない」',
        'decision':'65W以上のPD対応・20000mAh以上を選べばノートPCも含め全デバイスをカバーできる',
        'faq':[
            ('ノートPCも充電できますか？','65W以上のPD出力対応ならMacBook Airの充電も可能。100Wあれば14インチProもOK。'),
            ('スマホを何回充電できますか？','20000mAhならiPhone換算で約5回。変換効率を考えると実際は4回程度です。'),
            ('満充電にどれくらいかかりますか？','入力もPD対応なら約4時間。非対応だと8〜10時間かかる場合があります。'),
            ('重さはどれくらいですか？','20000mAhクラスは350〜450gが一般的。出張用と割り切れば許容範囲です。'),
            ('飛行機に持ち込めますか？','100Wh以下なら機内持ち込みOK。多くの20000mAhモデルは96〜99Wh設計です。'),
        ],
    },
    {
        'kw':'Anker GaN充電器 65W コンパクト 本体',
        'title':'GaN充電器に変えたらデスクがスッキリした話',
        'cat':'モバイル',
        'must':['充電器','GaN'],
        'exclude':['ケーブル','カバー'],
        'lead':'MacBook・iPhone・iPad・Androidをひとつの充電器でまとめたい方向けに、GaN充電器の選び方を解説します。',
        'persona':'Mac・iPhone・iPadを使うクリエイター。デスクの充電器だらけを解消したい',
        'pain':'「コンセントが足りない」「アダプタが大きすぎてタコ足になっている」',
        'decision':'ポート数・最大出力（W数）・サイズの3点で選ぶ。Ankerが最もバランスが良い',
        'faq':[
            ('GaN充電器とは何ですか？','ガリウムナイトライドという素材を使った充電器。従来より小型・軽量で発熱が少ないのが特徴です。'),
            ('MacBook Proの充電に使えますか？','MacBook Pro 14インチは65W以上、16インチは140W以上を推奨します。'),
            ('複数ポートで同時充電すると出力は下がりますか？','下がります。重要なデバイスを1ポートで充電するか、出力分配の仕様を事前に確認しましょう。'),
            ('海外旅行でも使えますか？','100〜240V対応モデルなら変圧器不要で世界中で使えます。プラグ形状のみ要確認。'),
            ('従来の充電器と何が違うのですか？','同じ出力でも30〜50%小さく・軽くなります。旅行のカバンに入れても負担になりません。'),
        ],
    },
    {
        'kw':'Logicool G PRO ゲーミングマウス 本体',
        'title':'エイムが上がるゲーミングマウスの選び方【FPS向け】',
        'cat':'ゲーミング',
        'must':['マウス'],
        'exclude':['パッド','グリップ','交換','ソール','マウスソール'],
        'lead':'「マウスを変えたらエイムが改善した」は本当です。選ぶべき軽量マウスの条件を解説します。',
        'persona':'FPSゲームで上位ランクを目指す大学生。エイムの安定性を上げたい',
        'pain':'「重いマウスで長時間プレイすると腕が疲れる」「クリック感が悪い」',
        'decision':'60g以下・高精度センサー・持ち方に合った形状の3点で選ぶ',
        'faq':[
            ('軽量マウスは何グラム以下がいいですか？','60g以下が軽量の基準。プロゲーマーの多くは55〜70gを使っています。'),
            ('有線と無線どちらがいいですか？','遅延を極限まで減らしたいなら有線。最新の無線も遅延はほぼなく実用上の差はありません。'),
            ('DPIはいくつに設定すればいいですか？','FPSは400〜1600DPIが一般的。ゲームと画面サイズに合わせて調整しましょう。'),
            ('グリップスタイルで選び方は変わりますか？','かぶせ持ちは大型・重め、つかみ・つまみ持ちは小型・軽量が向いています。'),
            ('マウスパッドは必要ですか？','ゲーミングマウスパッドと組み合わせることでセンサーの性能を最大限発揮できます。'),
        ],
    },
    {
        'kw':'SteelSeries Arctis HyperX Cloud ゲーミングヘッドセット 本体',
        'title':'敵の足音が聞こえるゲーミングヘッドセットの選び方',
        'cat':'ゲーミング',
        'must':['ヘッドセット'],
        'exclude':['イヤーパッド','クッション','交換','補修','ケーブル','パーツ','ソール'],
        'lead':'FPSで敵の位置を音で把握できるかどうかは、ヘッドセット次第です。選び方の基準を解説します。',
        'persona':'FPS・RPGを本格的に楽しみたいゲーマー。敵の足音の方向を正確に聞き取りたい',
        'pain':'「敵の足音が聞こえない」「ボイチャの声が聞き取りにくい」「長時間プレイで頭が痛い」',
        'decision':'サラウンド対応・マイク品質・重量（300g以下）の3点で選ぶ',
        'faq':[
            ('ゲーミングヘッドセットと普通のヘッドホンの違いは？','マイク内蔵・サラウンド対応・ゲーム向けチューニングが違い。ゲームと通話を1台でこなせます。'),
            ('7.1chサラウンドは本当に効果がありますか？','FPSでは足音の方向把握に有効。ただしステレオでも高品質なモデルなら十分です。'),
            ('PS5やSwitchでも使えますか？','3.5mmジャック・USB接続対応モデルならほとんどのゲーム機で使用可。'),
            ('マイクの品質が悪くてボイチャで怒られます','ノイズキャンセリングマイク搭載モデルを選びましょう。SteelSeries Arctisは特に評判が良いです。'),
            ('長時間プレイで頭が痛くなります','側圧の強さとクッションの柔らかさが重要。購入前に300g以下かどうか確認しましょう。'),
        ],
    },
    {
        'kw':'iRobot Roomba ロボット掃除機 本体',
        'title':'ロボット掃除機で毎日の掃除から解放される方法',
        'cat':'スマートホーム',
        'must':['ロボット','掃除機'],
        'exclude':['フィルター','ブラシ','交換','バッテリー','部品','パーツ'],
        'lead':'「帰宅したら部屋がきれいになっている」という生活は、ロボット掃除機1台で実現できます。',
        'persona':'共働き夫婦。帰宅後に掃除する体力も時間もない。猫を飼っている',
        'pain':'「毎日掃除機をかけたいけど無理」「ペットの毛が気になる」「ロボット掃除機って本当に使えるの？」',
        'decision':'マッピング機能・吸引力・ペット対応の3点で選ぶ。iRobotが実績ナンバーワン',
        'faq':[
            ('部屋が多少散らかっていても使えますか？','ケーブルや小さなおもちゃは片付けが必要。それ以外は自動で避けながら掃除してくれます。'),
            ('段差は乗り越えられますか？','多くのモデルは2cm程度の段差をクリア。厚めのラグには乗り越えられない場合もあります。'),
            ('うるさいですか？在宅中も使えますか？','50〜65dBが目安。外出時に動かすのがベストですが、最新モデルは静音性が上がっています。'),
            ('ペットの毛は吸えますか？','iRobotのj7+などはペット毛に特化した設計。ゴム製ブラシで絡まりを防いでいます。'),
            ('Wi-Fi・スマホアプリは必須ですか？','スケジュール設定・清掃マップ確認にアプリは便利。なくても使えますが効果が半減します。'),
        ],
    },
    {
        'kw':'SwitchBot スマートロック 後付け 本体',
        'title':'賃貸でもできるスマートロック導入ガイド',
        'cat':'スマートホーム',
        'must':['スマートロック','ロック','SwitchBot'],
        'exclude':['交換','部品','キー','スペア'],
        'lead':'「鍵を閉めたか不安で引き返したことがある」という方向けに、工事不要で取り付けられるスマートロックを解説します。',
        'persona':'賃貸一人暮らしで鍵の閉め忘れが不安な20〜30代',
        'pain':'「外出後に鍵閉めたか不安で戻る」「荷物の多い帰宅時に鍵を出すのが面倒」',
        'decision':'SwitchBot Lock一択。賃貸でも工事不要・既存の鍵をそのまま使える',
        'faq':[
            ('賃貸に取り付けても問題ありませんか？','両面テープで取り付けるため原状回復が可能。退去時に取り外しできます。'),
            ('既存の鍵はそのまま使えますか？','はい、既存の鍵の上に取り付ける後付けタイプです。鍵自体は交換しません。'),
            ('バッテリーが切れたらどうなりますか？','切れると操作できなくなります。低残量アラートで事前に通知が来ます。'),
            ('Wi-Fiがなくても使えますか？','Bluetooth接続ならWi-Fiなしでもスマホから操作可。外出先からの遠隔操作はハブが必要。'),
            ('取り付けに工事は必要ですか？','SwitchBotは工具不要で10分以内に設置可能。ただし一部のシリンダー形状には非対応の場合も。'),
        ],
    },
    {
        'kw':'GoPro HERO アクションカメラ 本体',
        'title':'旅行・アウトドアの映像を劇的に変えるアクションカメラ',
        'cat':'カメラ',
        'must':['カメラ','GoPro'],
        'exclude':['ケース','マウント','バッテリー','充電','交換','アクセサリ'],
        'lead':'スマホカメラでは撮れない手ブレなし・防水・超広角の映像。アクションカメラが必要な理由と選び方を解説します。',
        'persona':'旅行・登山・サーフィンが好きな30代。ダイナミックな映像をSNSに投稿したい',
        'pain':'「スマホで撮ると手ブレがひどい」「水中で撮りたい」「GoProとDJIどっちがいいかわからない」',
        'decision':'GoProかDJIの2択。水中・過酷環境はGoPro、旅行・日常動画はDJIが向いている',
        'faq':[
            ('GoProとDJIどちらを選べばいいですか？','水中・アウトドアの過酷な環境ならGoPro、旅行・Vlog中心ならDJI Osmo Actionが優秀です。'),
            ('防水はどれくらいですか？','GoPro HERO12は単体で10m防水。それ以上の深さは専用ハウジングが必要です。'),
            ('スマホで撮った映像と何が違いますか？','手ブレ補正・超広角・耐衝撃・防水が最大の違い。動きのある場面での安定性が圧倒的です。'),
            ('4K撮影するとデータ容量はどれくらいですか？','4K60fpsで1時間あたり約30GB。大容量のmicroSDカードを事前に準備しましょう。'),
            ('初心者でも使いこなせますか？','最近のモデルは自動設定が優秀。電源ONで撮影ボタンを押すだけで高品質な映像が撮れます。'),
        ],
    },
]

# ===== GitHub API =====
def gh_get(path):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
    h   = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    r   = requests.get(url, headers=h)
    if r.ok:
        d = r.json()
        return base64.b64decode(d['content']).decode('utf-8'), d['sha']
    return None, None

def gh_put(path, content, msg, sha=None):
    url  = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
    h    = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    data = {'message': msg, 'content': base64.b64encode(content.encode()).decode()}
    if sha: data['sha'] = sha
    r  = requests.put(url, headers=h, json=data)
    ok = r.status_code in [200, 201]
    print(f"  {'✅' if ok else '❌'} {path}")
    return ok

def gh_delete(path, sha, msg):
    url  = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
    h    = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    data = {'message': msg, 'sha': sha}
    r    = requests.delete(url, headers=h, json=data)
    ok   = r.status_code in [200, 204]
    print(f"  {'🗑️' if ok else '❌削除失敗'} {path}")
    return ok

# ===== 楽天商品取得 =====
WH = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','Referer':'https://gadget-tengoku.com/'}

def fetch_products(keyword, hits=20, retries=3):
    for i in range(retries):
        try:
            r = requests.get(WORKER_URL, params={'keyword':keyword,'hits':hits}, headers=WH, timeout=20)
            if r.ok:
                items = r.json().get('Items',[])
                if items: return items
        except Exception as e:
            print(f"  Workerエラー: {e}")
        time.sleep(2)
    return []

def filter_items(items, theme):
    must=theme.get('must',[]); excl=theme.get('exclude',[])
    result=[]
    for item in items:
        p=item.get('Item',{}); name=p.get('itemName',''); shop=p.get('shopName','')
        if any(ex in name for ex in excl): continue
        if must and not any(m in name for m in must): continue
        if not any(b.lower() in (name+' '+shop).lower() for b in TRUSTED_BRANDS): continue
        result.append(item)
    return result

def fetch_trusted(theme, need=5):
    items=fetch_products(theme['kw'],hits=30)
    filtered=filter_items(items,theme)
    print(f"  '{theme['kw'][:35]}' → 全{len(items)}件 / フィルタ後{len(filtered)}件")
    if len(filtered)>=3: return filtered[:need]
    soft=[i for i in items if not any(ex in i.get('Item',{}).get('itemName','') for ex in theme.get('exclude',[]))]
    return soft[:need] if soft else items[:need]

# ===== 記事HTML生成（CV最大化版） =====
def build_html(title, theme_obj, products):
    theme   = theme_obj['title']
    persona = theme_obj.get('persona','')
    pain    = theme_obj.get('pain','')
    lead    = theme_obj.get('lead','')
    decision= theme_obj.get('decision','')
    faq     = theme_obj.get('faq',[])
    today   = datetime.now().strftime('%Y年%m月%d日')
    year    = datetime.now().year
    num_class=['gold','silver','bronze','normal','normal']
    cta_main = random.choice(CTA_MAIN)

    cards=''; rows=''
    for i, item in enumerate(products[:5]):
        p         = item.get('Item',{})
        name      = p.get('itemName','')[:60]
        price     = p.get('itemPrice',0)
        shop      = p.get('shopName','')[:18]
        ra        = float(p.get('reviewAverage',0))
        rc        = int(p.get('reviewCount',0))
        url       = p.get('affiliateUrl', p.get('itemUrl','#'))
        imgs      = p.get('mediumImageUrls',[])
        img       = ''
        if imgs:
            raw = imgs[0].get('imageUrl','') if isinstance(imgs[0],dict) else ''
            img = re.sub(r'\?_ex=\d+x\d+','?_ex=400x400',raw)
        item_code  = p.get('itemCode','')
        review_url = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':','/')}/1.1/" if item_code else url
        si         = int(ra)
        stars_html = f'<span class="stars">{"★"*si}{"☆"*(5-si)}</span>'
        bar_w      = int(ra/5*100)
        img_html   = f'<img src="{img}" alt="{name}" loading="lazy">' if img else '<div style="color:#ccc;font-size:12px;text-align:center">No Image</div>'
        cta_sub    = f'実際のレビュー（{rc:,}件）を読む →'

        cards += f'''
<div class="rank-card">
  <div class="rank-header">
    <span class="rank-num {num_class[i]}">{i+1}</span>
    <span class="rank-label">{i+1}位</span>
    <span class="rank-shop-name">{shop}</span>
  </div>
  <div class="rank-layout">
    <div class="rank-img-col">{img_html}</div>
    <div class="rank-info-col">
      <div class="rank-name">{name}</div>
      <div class="review-block">
        <div class="review-stars-row">
          {stars_html}
          <span class="review-score">{ra:.1f}</span>
          <span class="review-max">/ 5.0</span>
          <a href="{review_url}" target="_blank" rel="noopener" class="review-link">口コミ{rc:,}件を見る →</a>
        </div>
        <div class="review-bar-wrap"><div class="review-bar" style="width:{bar_w}%"></div></div>
      </div>
      <div class="price-area">
        <div class="price-row">
          <div class="price">¥{price:,}</div>
          <small class="price-note">税込｜送料無料（楽天市場）</small>
        </div>
        <a href="{url}" class="btn-buy" target="_blank" rel="noopener sponsored">{cta_main}</a>
        <a href="{review_url}" class="btn-review" target="_blank" rel="noopener">{cta_sub}</a>
      </div>
    </div>
  </div>
</div>'''

        rows += f'<tr><td><span class="rank-no">{i+1}</span>{name[:28]}</td><td class="best">¥{price:,}</td><td>{"★"*si}{"☆"*(5-si)} {ra:.1f}</td><td><a href="{review_url}" target="_blank" rel="noopener" style="color:#e63900">{rc:,}件</a></td><td><a href="{url}" target="_blank" rel="noopener sponsored" class="btn-buy" style="font-size:11px;padding:6px 10px;display:inline-block">購入</a></td></tr>'

    # FAQ HTML
    faq_html=''
    if faq:
        faq_items=''.join(f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>' for q,a in faq)
        faq_html=f'<section id="faq"><h2 class="section-title">よくある質問（FAQ）</h2><div class="faq-wrap">{faq_items}</div></section>'

    # JSON-LD FAQ
    faq_ld=','.join(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}' for q,a in faq)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新。{theme}の選び方・おすすめランキングTOP5。{pain}を解決します。楽天市場の実売データ・口コミ参照。">
<link rel="canonical" href="{SITE_URL}/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
</script>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="{SITE_URL}/" class="logo">Gadget<span>天国</span></a>
    <nav>
      <a href="{SITE_URL}/">トップ</a>
      <a href="{SITE_URL}/archive.html">記事一覧</a>
    </nav>
  </div>
</header>

<div class="article-hero">
  <div class="article-hero-inner">
    <div class="article-cat">{theme}</div>
    <h1>{title}</h1>
    <div class="article-meta">
      <span>📅 {today} 更新</span>
      <span>📊 楽天市場 実売データ参照</span>
      <span>⏱ 読了4分</span>
    </div>
  </div>
</div>

<div class="container">

  <!-- 結論先出し（PREP：Point） -->
  <div class="result-box">
    <div class="result-box-label">✅ この記事の結論</div>
    <div class="result-box-text">
      <strong>{theme}</strong>で迷っているなら<strong>1位のモデルを選べば間違いありません。</strong>
      {decision}
    </div>
  </div>

  <!-- ペルソナ・悩み（共感獲得） -->
  <div class="persona-box">
    <div class="persona-label">こんな方におすすめ</div>
    <div class="persona-text">{persona}</div>
    <div class="pain-text">💬 よくある悩み：{pain}</div>
  </div>

  <div class="intro-box">{lead}</div>

  <nav class="toc">
    <div class="toc-title">この記事の目次</div>
    <ol>
      <li><a href="#ranking">おすすめランキングTOP5</a></li>
      <li><a href="#compare">スペック比較表</a></li>
      <li><a href="#guide">失敗しない選び方</a></li>
      <li><a href="#faq">よくある質問</a></li>
    </ol>
  </nav>

  <section id="ranking">
    <h2 class="section-title">おすすめランキングTOP5</h2>
    <p style="font-size:12px;color:#aaa;margin-bottom:16px">
      ※参照：<a href="https://www.rakuten.co.jp/" target="_blank" rel="noopener" style="color:#e63900">楽天市場</a>のレビュー件数・評価点（{today}時点）。価格は変動する場合があります。
    </p>
    {cards}
  </section>

  <section id="compare">
    <h2 class="section-title">スペック比較表</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </section>

  <section id="guide">
    <h2 class="section-title">失敗しない選び方のポイント</h2>
    <div class="guide-grid">
      <div class="guide-item"><div class="guide-item-title">① 予算を先に決める</div><div class="guide-item-desc">価格帯によって候補が変わります。1万・3万・5万円の区切りを意識して絞り込みましょう。</div></div>
      <div class="guide-item"><div class="guide-item-title">② レビュー件数を確認</div><div class="guide-item-desc">1,000件以上なら実績十分。件数が多いほど「外れ」が少なく安心して選べます。</div></div>
      <div class="guide-item"><div class="guide-item-title">③ 用途を具体的にイメージ</div><div class="guide-item-desc">「どこで・何のために使うか」を明確にしてから選ぶと後悔しません。</div></div>
      <div class="guide-item"><div class="guide-item-title">④ 国内正規品を選ぶ</div><div class="guide-item-desc">楽天市場の公式ストアやメーカー直営店なら保証・サポートが充実しています。</div></div>
    </div>
  </section>

  {faq_html}

  <!-- 最終CTA（背中を押す） -->
  <div class="final-cta">
    <div class="final-cta-title">まだ迷っていますか？</div>
    <div class="final-cta-sub">楽天市場で実際の口コミを読んでから決めましょう。返品・交換保証があるので安心です。</div>
    <a href="https://search.rakuten.co.jp/search/mall/{requests.utils.quote(theme)}/" target="_blank" rel="noopener" class="final-cta-btn">
      楽天で「{theme}」を今すぐ検索する →
    </a>
  </div>

</div>

<footer>
  <div class="footer-inner">
    <div class="footer-logo">Gadget<span>天国</span></div>
    <div class="footer-links">
      <a href="{SITE_URL}/">トップ</a>
      <a href="{SITE_URL}/archive.html">記事一覧</a>
      <a href="{SITE_URL}/privacy.html">プライバシーポリシー</a>
    </div>
  </div>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。掲載価格は{today}時点の楽天市場価格です。</p>
  <p style="text-align:center;margin-top:12px;font-size:11px;color:#444">© {year} ガジェット天国</p>
</footer>
</body>
</html>'''

# ===== articles.json 更新 =====
def update_articles_json(theme_obj, filename, img_url, today):
    content, sha = gh_get('articles.json')
    articles     = json.loads(content) if content else []
    year         = datetime.now().year
    new = {
        'title':       f"【{year}年最新】{theme_obj['title']} おすすめランキングTOP5",
        'filename':    filename,
        'img_url':     img_url,
        'category':    theme_obj['cat'],
        'theme_key':   theme_obj['title'],
        'date':        today.strftime('%Y年%m月%d日'),
        'description': theme_obj.get('lead','')[:80],
    }
    updated=False
    for i,a in enumerate(articles):
        if a['filename']==filename:
            articles[i]=new; updated=True; break
    if not updated: articles.insert(0,new)
    articles=articles[:50]
    gh_put('articles.json',json.dumps(articles,ensure_ascii=False,indent=2),'Auto: 記事一覧更新',sha)
    return articles

# ===== 既存記事再生成・クリーンアップ =====
def regenerate_and_cleanup():
    print('\n既存記事を再生成中...')
    content,_=gh_get('articles.json')
    if not content: return
    articles=json.loads(content)
    theme_map={t['title']:t for t in ALL_THEMES}
    keep=[]
    for a in articles:
        filename=a.get('filename',''); theme_key=a.get('theme_key',''); title=a.get('title','')
        theme_obj=theme_map.get(theme_key)
        if not theme_obj:
            print(f'  テーマ不明→削除: {theme_key}')
            _,sha=gh_get(filename)
            if sha: gh_delete(filename,sha,f'Cleanup: {filename}')
            continue
        print(f'  再生成: {theme_key}')
        products=fetch_trusted(theme_obj,need=5)
        if not products:
            print(f'  商品0件→削除: {filename}')
            _,sha=gh_get(filename)
            if sha: gh_delete(filename,sha,f'Cleanup: 商品なし {filename}')
            continue
        html=build_html(title,theme_obj,products)
        _,sha=gh_get(filename)
        if gh_put(filename,html,f'Regenerate: {theme_key}',sha):
            imgs=products[0].get('Item',{}).get('mediumImageUrls',[])
            if imgs:
                raw=imgs[0].get('imageUrl','') if isinstance(imgs[0],dict) else ''
                a['img_url']=re.sub(r'\?_ex=\d+x\d+','?_ex=400x400',raw)
            keep.append(a)
        else: keep.append(a)
        time.sleep(1.5)
    _,sha=gh_get('articles.json')
    gh_put('articles.json',json.dumps(keep,ensure_ascii=False,indent=2),'Auto: articles.json更新',sha)
    print(f'完了（残り{len(keep)}件）')

# ===== アーカイブ =====
def build_archive(articles):
    arts=[a for a in articles if a.get('img_url','').strip()]
    cards=''.join(f'''
<a href="{a["filename"]}" style="display:block;border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;text-decoration:none;color:#111;transition:box-shadow .2s" onmouseover="this.style.boxShadow='0 4px 16px rgba(0,0,0,.08)'" onmouseout="this.style.boxShadow=''">
  <img src="{a["img_url"]}" alt="{a["title"]}" style="width:100%;height:150px;object-fit:contain;padding:10px;background:#fafafa">
  <div style="padding:12px;border-top:1px solid #f0f0f0">
    <div style="font-size:11px;color:#e63900;font-weight:700;margin-bottom:4px">{a.get("category","")}</div>
    <div style="font-size:13px;font-weight:700;line-height:1.45;margin-bottom:5px">{a["title"]}</div>
    <div style="font-size:11px;color:#bbb">{a["date"]}</div>
  </div>
</a>''' for a in arts)
    return f'''<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>記事一覧 | ガジェット天国</title>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
</head><body>
<header><div class="header-inner">
  <a href="{SITE_URL}/" class="logo">Gadget<span>天国</span></a>
  <nav><a href="{SITE_URL}/">トップ</a></nav>
</div></header>
<div style="border-bottom:2px solid #111;padding:24px 20px">
  <div style="max-width:1000px;margin:0 auto">
    <h1 style="font-size:22px;font-weight:900">記事一覧</h1>
    <p style="font-size:13px;color:#aaa;margin-top:5px">全{len(arts)}記事 | 毎日更新</p>
  </div>
</div>
<div style="max-width:1000px;margin:0 auto;padding:24px 20px 56px">
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px">{cards}</div>
</div>
<footer><div class="footer-inner">
  <div class="footer-logo">Gadget<span>天国</span></div>
  <div class="footer-links"><a href="{SITE_URL}/">トップ</a><a href="{SITE_URL}/privacy.html">プライバシーポリシー</a></div>
</div>
<p class="footer-note">© {datetime.now().year} ガジェット天国</p>
</footer></body></html>'''

# ===== サイトマップ =====
def build_sitemap(extra):
    today=datetime.now().strftime('%Y-%m-%d')
    bases=['','earphone.html','smartwatch.html','battery.html','archive.html','privacy.html']
    urls=[f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod><priority>{"1.0" if u=="" else "0.8"}</priority></url>' for u in bases]
    for f in extra: urls.append(f'  <url><loc>{SITE_URL}/{f}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+'\n'.join(urls)+'\n</urlset>'

# ===== Twitter =====
def post_twitter(title, url, theme_obj):
    if not all([TWITTER_API_KEY,TWITTER_API_SECRET,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET]):
        print('⚠ Twitter Secrets未設定'); return
    try:
        import tweepy
        auth=tweepy.OAuth1UserHandler(TWITTER_API_KEY,TWITTER_API_SECRET,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
        pain=theme_obj.get('pain','')
        text=f"新着記事📱\n{title}\n\n{pain}\n→解決策はこちら✅\n\nFAQ・比較表つきで選び方もわかる！\n\n{url}\n\n#{theme_obj['cat']} #ガジェット #楽天"
        tweepy.API(auth).update_status(text[:280])
        print('✅ Twitter投稿成功')
    except Exception as e:
        print(f'❌ Twitter失敗: {e}')

# ===== テーマ選択 =====
def select_theme():
    content,_=gh_get('articles.json')
    used=set()
    if content:
        try: used={a.get('theme_key','') for a in json.loads(content)[:40]}
        except: pass
    available=[t for t in ALL_THEMES if t['title'] not in used] or ALL_THEMES
    am=['イヤホン','オーディオ','スマートウォッチ']
    pm=['ゲーミング','PC周辺機器','スマートホーム','カメラ','モバイル','生活家電']
    pool=[t for t in available if t['cat'] in (am if SLOT=='am' else pm)] or available
    return random.choice(pool)

# ===== メイン =====
def main():
    today=datetime.now()
    print(f"=== {today.strftime('%Y年%m月%d日')} [{SLOT.upper()}] ===")
    theme=select_theme()
    print(f"テーマ: {theme['title']}")
    products=fetch_trusted(theme,need=5)
    if not products:
        print('❌ 商品取得失敗'); return
    title=f"【{today.year}年最新】{theme['title']} おすすめランキングTOP5"
    html=build_html(title,theme,products)
    date_str=today.strftime('%Y%m%d')
    safe=re.sub(r'[^\w]','-',theme['title'])[:25]
    filename=f"article-{safe}-{SLOT}-{date_str}.html"
    _,sha=gh_get(filename)
    gh_put(filename,html,f"Auto: {theme['title']}",sha)
    img_url=''
    if products:
        imgs=products[0].get('Item',{}).get('mediumImageUrls',[])
        if imgs:
            raw=imgs[0].get('imageUrl','') if isinstance(imgs[0],dict) else ''
            img_url=re.sub(r'\?_ex=\d+x\d+','?_ex=400x400',raw)
    update_articles_json(theme,filename,img_url,today)
    regenerate_and_cleanup()
    content,_=gh_get('articles.json')
    if content:
        _,sha=gh_get('archive.html')
        gh_put('archive.html',build_archive(json.loads(content)),'Auto: アーカイブ更新',sha)
    _,sha=gh_get('sitemap.xml')
    gh_put('sitemap.xml',build_sitemap([filename]),'Auto: サイトマップ',sha)
    post_twitter(title,f"{SITE_URL}/{filename}",theme)
    print(f"\n=== 完了: {SITE_URL}/{filename} ===")

if __name__ == '__main__':
    main()
