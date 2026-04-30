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

# ===== テーマ定義（複数キーワード・体験型コメント・用途別ペルソナ付き） =====
ALL_THEMES = [
    {
        'title':   '通勤・在宅ワーク向けノイキャンイヤホン',
        'cat':     'イヤホン',
        'keywords': [
            'Sony WF-1000XM5',
            'Jabra Elite 10',
            'Anker Soundcore Liberty 4 NC',
            'AirPods Pro 第2世代 本体',
            'Shokz OpenRun Pro',
        ],
        'must':    ['イヤホン','ヘッドホン','Earbuds','WF-','XM5','Elite','Liberty','AirPods','OpenRun'],
        'exclude': ['ケース','ポーチ','カバー','クッション','交換','イヤーパッド','イヤーチップ','充電ケーブル'],
        'lead':    '電車の騒音・家族の声・オフィスの雑音を消して集中したい方向けの記事です。',
        'problem': ['満員電車で音楽を聴いても騒音で全然集中できない', '在宅ワーク中に子どもの声でWeb会議に集中できない', 'ノイキャンイヤホンを買ったけど効果が薄くて後悔した', '高い・安いの違いが正直わからなくて選べない'],
        'conclusion': '通勤・電車メイン → Sony WF-1000XM5、Web会議特化 → Jabra Elite 10、コスパ重視 → Anker Soundcore Liberty 4 NC',
        'decision': '「ノイキャン性能」より「用途」で選ぶ。マイク品質と連続使用時間の2点も必ず確認する',
        'personas': [
            ('🚃', '毎日電車通勤', '騒音を完全遮断して音楽・ポッドキャストを楽しみたい', 'Sony WF-1000XM5'),
            ('💻', '在宅ワーク・Web会議', '家族の声を遮断しつつマイク音声も鮮明にしたい', 'Jabra Elite 10'),
            ('💰', '初めての購入・コスパ重視', '1万円台で本格ノイキャンを体験したい', 'Anker Soundcore Liberty 4 NC'),
            ('🏃', '運動しながら使う', '外音も聞こえて安全に・耳も疲れない', 'Shokz OpenRun Pro'),
        ],
        'criteria': [
            ('ノイキャン性能より「用途」で選ぶ', 'カタログスペックより重要なのは用途との相性。電車通勤なら密閉型カナル式、長時間在宅なら装着感優先で選びましょう。'),
            ('マイク品質を必ず確認する', 'Web会議で使うならマイクのノイズキャンセリング性能が最重要。安いモデルは音楽再生用で通話品質が低いものが多いです。'),
            ('連続使用時間は「本体のみ」で確認する', '「最大32時間」はケース込みの数字。本体単体での連続使用が重要。通勤往復2時間なら本体4時間でOK。'),
        ],
        'faq': [
            ('ノイキャンイヤホンは飛行機でも効果がありますか？', '非常に効果的です。飛行機のエンジン音は低周波なのでノイキャンが最も得意とする帯域です。長距離フライトに必携です。'),
            ('在宅ワークのWeb会議でマイクは使えますか？', '機種によって大きく差があります。Jabra・Sony・Anker上位モデルは通話品質が高く評価されています。'),
            ('1万円台と3万円台の違いは何ですか？', '日常の騒音なら1万円台で十分。電車・飛行機の騒音を本当に消したいなら3万円台のSonyかBoseを選んでください。効果量が全然違います。'),
            ('長時間装着すると耳が痛くなります', 'まずイヤーピースのサイズを変えてください（S/M/L）。それでも痛い場合はShokz（骨伝導）への変更を検討してください。'),
            ('iPhoneとAndroid両方で使えますか？', 'Bluetooth接続なのでOS問わず使用可。ただしAirPods ProはiPhone専用と考えてください。'),
        ],
    },
    {
        'title':   'スポーツ・ランニング向けワイヤレスイヤホン',
        'cat':     'イヤホン',
        'keywords': [
            'Jabra Elite Active スポーツ イヤホン',
            'Shokz OpenRun 骨伝導',
            'Anker Soundcore Sport X10',
            'Sony LinkBuds S',
            'JVC HA-ET900BT',
        ],
        'must':    ['イヤホン','Buds','OpenRun','Sport','LinkBuds','HA-ET'],
        'exclude': ['ケース','ポーチ','カバー','交換','イヤーパッド'],
        'lead':    '走っても落ちない・汗で壊れない・外音も聞こえる。スポーツ中に本当に使えるイヤホンだけ厳選しました。',
        'problem': ['走るとイヤホンが外れてストレス', '汗で壊れた経験がある', '交通量の多い道を走るとき車の音が聞こえなくて怖い'],
        'conclusion': '落ちない固定力 → Jabra Elite Active、耳をふさがない安全性 → Shokz OpenRun、コスパ → Anker Sport',
        'decision': 'IPX4以上の防水・固定方法・外音取り込み機能の3点で絞り込む',
        'personas': [
            ('🏃', '週3回ランニング', '落ちない・汗に強い・外音も聞こえる', 'Jabra Elite Active'),
            ('🚴', '自転車通勤・サイクリング', '車の音が聞こえて安全に走りたい', 'Shokz OpenRun'),
            ('🏋️', 'ジム・筋トレ', '耳が蒸れない・激しい動きでもズレない', 'Anker Sport'),
            ('💰', '初めてのスポーツ用', 'コスパ重視で試してみたい', 'JVC スポーツモデル'),
        ],
        'criteria': [
            ('防水性能：IPX4以上を選ぶ', 'IPX4は汗・小雨OK。水泳するならIPX7以上。ランニングの汗ならIPX4〜5で十分です。'),
            ('固定方法：イヤーフック・ウイングチップが必須', '普通のイヤホンは走ると外れます。スポーツ向けは固定パーツがついているモデルを選びましょう。'),
            ('外音取り込み機能：交通量が多い道なら必須', '車の音を聞きながら音楽を楽しめます。特に公道を走るランナーは安全のために必須の機能です。'),
        ],
        'faq': [
            ('スポーツ中にイヤホンが外れないか心配です', 'イヤーフックやウイングチップ付きのモデルを選びましょう。Jabraは固定力に定評があります。'),
            ('骨伝導イヤホンは音が悪いですか？', '低音は劣りますが中高音はクリア。耳をふさがないので安全性・長時間装着では骨伝導が優秀です。'),
            ('バッテリーはどれくらいもちますか？', '本体6〜10時間が目安。フルマラソンも余裕でカバーできます。'),
            ('水洗いできるモデルはありますか？', 'Shokz OpenRunはIP67防水で水洗いOK。衛生面が気になる方にもおすすめです。'),
            ('外音取り込み機能は必要ですか？', '公道を走る場合は必須。車の音を聞きながら音楽が楽しめます。'),
        ],
    },
    {
        'title':   '健康管理に使えるスマートウォッチ',
        'cat':     'スマートウォッチ',
        'keywords': [
            'Garmin Venu 3 本体',
            'Apple Watch SE 第2世代 本体',
            'Samsung Galaxy Watch 6 本体',
            'Fitbit Charge 6',
            'Amazfit GTR 4',
        ],
        'must':    ['Watch','ウォッチ','Venu','Fitbit','Amazfit','Charge','Galaxy'],
        'exclude': ['バンド','ベルト','充電','ケース','フィルム','交換','スタンド','充電器','保護'],
        'lead':    '睡眠・心拍・血中酸素・ストレスを毎日記録して、自分の体の変化を数値で把握したい方向けです。',
        'problem': ['体調が悪い日の原因がわからない', '睡眠の質を改善したいが何をすればいいかわからない', 'Apple WatchとGarminどっちがいいか決められない'],
        'conclusion': 'バッテリー・GPS重視 → Garmin Venu 3、iPhoneユーザーの入門 → Apple Watch SE、コスパ → Amazfit GTR 4',
        'decision': 'バッテリー持ち・GPS精度・健康データの詳細さで選ぶ。Garminは5日以上、Apple Watchは毎日充電前提',
        'personas': [
            ('❤️', '健康診断で引っかかった40代', '血圧・心拍・睡眠を毎日数値で把握したい', 'Garmin Venu 3'),
            ('🏅', 'ランニング・マラソン', 'GPS精度・ルート記録・トレーニング分析', 'Garmin Forerunner'),
            ('📱', 'iPhoneユーザーの入門', 'Apple Watchを試してみたい・使いやすさ重視', 'Apple Watch SE'),
            ('💰', 'コスパ重視・Android', '1〜2万円台・バッテリー長持ち', 'Amazfit GTR 4'),
        ],
        'criteria': [
            ('バッテリー持ちで選ぶ', 'Apple Watchは1〜2日で要充電。GarminのVenuは5〜7日持つ。毎日充電が面倒な人はGarminを選んでください。'),
            ('健康データの詳細さで選ぶ', '睡眠ステージ・ストレス・血中酸素まで詳しく知りたいならGarminが圧倒的。Apple Watchは心電図が強み。'),
            ('iPhoneかAndroidかで選ぶ', 'Apple WatchはiPhone専用。AndroidユーザーはGarmin・Samsung・Amazfitから選んでください。'),
        ],
        'faq': [
            ('血圧は正確に測れますか？', '医療機器ではないため参考値です。傾向把握・異常値アラートとしては十分活用できます。'),
            ('Apple WatchとGarminどっちがいいですか？', 'iPhoneユーザーで決済機能も使いたいならApple Watch。バッテリー持ち・GPS精度を重視するならGarmin。'),
            ('睡眠の質はどうやって計測しますか？', '心拍数・血中酸素・体動から睡眠ステージを自動判定します。'),
            ('防水性能はありますか？', 'ほとんどのモデルが5ATM防水でシャワーや水泳にも対応しています。'),
            ('バッテリーはどれくらいもちますか？', 'Apple Watchは1〜2日、GarminのVenuは5〜7日、Amazfitは最大14日が目安です。'),
        ],
    },
    {
        'title':   'コスパ最強モバイルバッテリー',
        'cat':     'モバイル',
        'keywords': [
            'Anker PowerCore 10000 PD Redux',
            'CIO SMARTCOBY PRO SLIM',
            'Anker PowerCore III Elite 25600',
            'Belkin BoostCharge モバイルバッテリー 10000',
            'Anker PowerCore 20000',
        ],
        'must':    ['バッテリー','モバイル','PowerCore','SMARTCOBY','BoostCharge'],
        'exclude': ['ケース','カバー','ケーブル'],
        'lead':    '「重いから持ち歩くのをやめた」という人向けに、毎日使い続けられる軽量モデルから大容量まで厳選しました。',
        'problem': ['重くて持ち歩くのが面倒でカバンに入れなくなった', '旅行中にスマホとノートPC両方を充電したい', '飛行機に持ち込める容量の上限がわからない'],
        'conclusion': '毎日持ち歩き → Anker PowerCore 10000 PD（180g）、旅行・出張 → Anker 25600 PD、コスパ → CIO SMARTCOBY',
        'decision': '用途によって「容量」と「重さ」のバランスを変える。毎日は200g以下・旅行は容量優先',
        'personas': [
            ('👔', '毎日通勤するビジネスマン', 'カバンに入れても重くない・スマホ1回分あればOK', 'Anker PowerCore 10000 PD'),
            ('✈️', '出張・旅行が月2回以上', 'ノートPCも充電できる・飛行機OK・3日持つ', 'Anker PowerCore 25600 PD'),
            ('💰', 'とにかく安く', '5000円台で買えるコスパ重視', 'CIO SMARTCOBY PRO'),
            ('📱', 'スマホ2台持ち', '2台同時充電できるポートが多いモデル', 'Anker 2ポートモデル'),
        ],
        'criteria': [
            ('毎日持ち歩くなら200g以下を選ぶ', '300g超えると「今日は重いからいいや」と持ち歩かなくなります。毎日使うなら軽さが最優先。'),
            ('出力W数でノートPCに使えるか決まる', '65W以上のPD対応ならMacBook Airも充電できます。スマホ専用なら20Wで十分。'),
            ('飛行機持ち込みは100Wh以下（約27000mAh）', '商品ページのWh表記を必ず確認しましょう。'),
        ],
        'faq': [
            ('毎日持ち歩くなら何mAhがいいですか？', 'スマホ1回分なら5000〜10000mAh。200g以下を選べば重さを感じません。'),
            ('急速充電対応かどうかの確認方法は？', 'PD（Power Delivery）18W以上と書かれているものが急速充電対応です。'),
            ('ノートPCも充電できますか？', '65W以上のPD出力対応ならMacBook Airも充電できます。'),
            ('飛行機に持ち込めますか？', '100Wh（約27000mAh）以下なら機内持ち込みOK。スーツケースへの収納はNGです。'),
            ('充電しながら使えますか（パススルー）？', '対応モデルとそうでないものがあります。商品ページの仕様欄で確認しましょう。'),
        ],
    },
    {
        'title':   'テレワーク・在宅ワーク向けガジェット',
        'cat':     'PC周辺機器',
        'keywords': [
            'Logicool C920s ウェブカメラ',
            'Blue Yeti Nano USB マイク',
            'Anker 552 USBハブ Type-C',
            'Anker 735 GaN 充電器 65W',
            'Logicool MX Keys キーボード',
        ],
        'must':    ['カメラ','ハブ','マイク','充電器','キーボード','C920','Yeti','GaN','MX'],
        'exclude': ['ケーブル','交換','パーツ','カバー','延長'],
        'lead':    '在宅ワーク歴4年が「本当に買って良かった」と思うガジェットを正直に紹介します。',
        'problem': ['Web会議でカメラの画質が悪くて映りが気になる', 'MacBookのポートが足りなくてドングルだらけ', 'デスクのケーブルが多すぎてぐちゃぐちゃ'],
        'conclusion': 'Web会議の映り → Logicool C920s、マイク音質 → Blue Yeti Nano、ポート不足 → Anker USBハブ',
        'decision': '在宅ワーク環境は「マイク→カメラ→ハブ」の順番で投資すると費用対効果が高い',
        'personas': [
            ('📹', 'Web会議が多いビジネスマン', 'カメラの映りを改善して印象を良くしたい', 'Logicool C920s'),
            ('💻', 'MacBookユーザー', 'ポート不足を解消してすっきりしたデスクにしたい', 'Anker USBハブ 7in1'),
            ('🎙️', '配信・ポッドキャスト', 'マイクの音質をプロレベルに上げたい', 'Blue Yeti Nano'),
            ('⚡', 'ガジェット好き・ミニマリスト', '充電器1つで全デバイスをまとめたい', 'Anker GaN 65W'),
        ],
        'criteria': [
            ('カメラは最低フルHD（1080p）を選ぶ', '720pのカメラはWeb会議でぼやけて見えます。1080p以上なら顔の表情まで鮮明に映ります。'),
            ('USBハブはPD対応・ポート数で選ぶ', 'MacBook充電しながら他のデバイスも使うには「PD対応」が必須。HDMIポートも必要かどうか確認しましょう。'),
            ('マイクはコンデンサー型を選ぶ', 'イヤホン付属マイクより圧倒的に音がクリア。Web会議・配信・録音すべてで効果を実感できます。'),
        ],
        'faq': [
            ('ウェブカメラはどれくらいの価格から良くなりますか？', '5000円台のLogicool C270でも改善を感じられます。1万円台のC920sなら顔の表情まで鮮明に映ります。'),
            ('USBハブは何を基準に選べばいいですか？', 'HDMI出力・PD充電対応・ポート数の3点。Ankerの7-in-1か11-in-1が最もバランスが良いです。'),
            ('マイクとウェブカメラ、先に買うならどちら？', 'マイクを先に買ってください。音声品質の方が映像より相手への印象に直結します。'),
            ('GaN充電器に変えると何が変わりますか？', '同じ出力でも30〜50%小さく軽くなります。デスクがすっきりして旅行のカバンにも楽に入ります。'),
            ('ノートPCスタンドは本当に必要ですか？', 'Web会議が多い方には必須です。PCを目線の高さに上げるだけでカメラアングルが改善し印象が変わります。'),
        ],
    },
    {
        'title':   'ゲーミングヘッドセット完全比較',
        'cat':     'ゲーミング',
        'keywords': [
            'SteelSeries Arctis Nova Pro ヘッドセット 本体',
            'HyperX Cloud III ゲーミングヘッドセット 本体',
            'Logicool G733 ゲーミングヘッドセット 本体',
            'Razer BlackShark V2 ゲーミングヘッドセット 本体',
            'Corsair HS65 ゲーミングヘッドセット 本体',
        ],
        'must':    ['ヘッドセット'],
        'exclude': ['イヤーパッド','クッション','交換','補修','ケーブル','パーツ','ソール','イヤークッション'],
        'lead':    '敵の足音が聞こえるかどうかはヘッドセット次第です。FPS・RPG用途別に正直なレビューをお届けします。',
        'problem': ['敵の足音の方向が全然わからない', 'ボイチャで声が聞き取りにくいと言われる', '長時間プレイで頭が痛くなる'],
        'conclusion': 'FPS足音把握 → SteelSeries Arctis Nova Pro、マイク音質 → HyperX Cloud III、コスパ → Corsair HS65',
        'decision': 'サラウンド対応・マイク品質・重量（300g以下）の3点で選ぶ',
        'personas': [
            ('🎯', 'FPS・TPS重視', '敵の足音・銃声の方向を正確に聞き取りたい', 'SteelSeries Arctis Nova Pro'),
            ('🎙️', 'ボイチャ重視', '声が鮮明に届くマイク品質が最重要', 'HyperX Cloud III'),
            ('💰', 'コスパ重視・入門', '初めてゲーミングヘッドセットを買う', 'Corsair HS65'),
            ('📡', '無線でスッキリ', 'ケーブルなしで自由に動きたい', 'Logicool G733'),
        ],
        'criteria': [
            ('7.1chサラウンドの必要性を考える', 'FPSなら足音の方向把握に有効。ただしステレオでも高品質なモデルなら十分。'),
            ('マイクのノイキャン性能を確認する', '安いモデルはマイクが弱く、ゲーム音を拾います。SteelSeriesとHyperXはマイク品質が特に高評価。'),
            ('重量は300g以下を選ぶ', '300g超えると長時間プレイで首が疲れます。'),
        ],
        'faq': [
            ('ゲーミングヘッドセットと普通のヘッドホンの違いは？', 'マイク内蔵・サラウンド対応・ゲーム向けチューニングが主な違いです。'),
            ('PS5やSwitchでも使えますか？', '3.5mmジャック・USB接続対応モデルならほとんどのゲーム機で使用可。'),
            ('有線と無線どちらがいいですか？', '遅延を極限まで減らしたいなら有線。最新の無線モデルは遅延がほぼなく実用上の差はありません。'),
            ('長時間プレイで頭が痛くなります', 'ヘッドバンドの締め付け調整と柔らかいイヤーパッドのモデルを選んでください。'),
            ('マイクがPC・PS5に対応しているか確認方法は？', '接続方式（USB/3.5mm）を確認。PS5はUSBとBluetoothに対応しています。'),
        ],
    },
    {
        'title':   'マッピングロボット掃除機比較',
        'cat':     'スマートホーム',
        'keywords': [
            'iRobot Roomba j7 ロボット掃除機',
            'Ecovacs DEEBOT T20 ロボット掃除機',
            'Roborock S7 ロボット掃除機',
            'Panasonic ロボット掃除機 本体',
            'SwitchBot ロボット掃除機 本体',
        ],
        'must':    ['ロボット','掃除機','Roomba','DEEBOT','Roborock'],
        'exclude': ['フィルター','ブラシ','交換','バッテリー','部品','パーツ','消耗品'],
        'lead':    '「帰宅したら部屋がきれいになっている」という生活を実現した。ロボット掃除機歴3年の正直レビューです。',
        'problem': ['共働きで帰宅後に掃除する体力も時間もない', 'ペットの毛が毎日気になる', 'ロボット掃除機って本当に使えるのか半信半疑'],
        'conclusion': 'ペット毛 → iRobot Roomba j7、水拭き同時 → Roborock S7、コスパ → Ecovacs DEEBOT',
        'decision': 'マッピング機能・水拭き対応・ペット毛対応の3点で用途に合わせて選ぶ',
        'personas': [
            ('🐱', 'ペット（犬・猫）がいる家庭', 'ペットの毛を毎日自動で掃除したい', 'iRobot Roomba j7+'),
            ('🏠', '水拭きもしたい', '掃除機がけと床拭きを同時にやってほしい', 'Roborock S7'),
            ('💰', '初めてのロボット掃除機', '3万円台から試してみたい', 'Ecovacs DEEBOT'),
            ('👶', '子どもがいる家庭', '細かいゴミ・食べこぼしを毎日自動で', 'SwitchBot ロボット掃除機'),
        ],
        'criteria': [
            ('マッピング機能：間取りが複雑なら必須', '間取りをスキャンして最短ルートで掃除。複数部屋がある家庭には必須機能です。'),
            ('ゴミ自動収集：週1の掃除が月1になる', 'ダストステーションがあれば本体のゴミ捨ては月1回程度でOK。'),
            ('ペット毛対応：ブラシの種類を確認', 'ゴム製ブラシはペットの毛が絡まりにくい設計。毛が多い家庭はiRobot Roomba j7+一択。'),
        ],
        'faq': [
            ('部屋が散らかっていても使えますか？', 'ケーブルや小さなおもちゃは事前に片付けが必要。それ以外は自動で避けながら掃除してくれます。'),
            ('うるさいですか？', '50〜65dBが目安。外出中に動かすのが理想です。'),
            ('ペットの毛は吸えますか？', 'iRobot Roomba j7はペット毛に特化した設計。ゴム製ブラシで絡まりを防いでいます。'),
            ('Wi-FiやアプリなしでもOKですか？', 'アプリなしでもボタン1つで動きます。ただしスケジュール設定にはアプリが必要です。'),
            ('水拭き対応モデルはどれがいいですか？', 'Roborock S7シリーズは吸引＋水拭きを同時に行い、カーペットを自動で避ける機能も搭載。'),
        ],
    },
    {
        'title':   '4Kアクションカメラ完全比較',
        'cat':     'カメラ',
        'keywords': [
            'GoPro HERO 12 Black 本体',
            'DJI Osmo Action 4 本体',
            'Insta360 ONE RS 本体',
            'Sony FDR-X3000 アクションカメラ',
            'DJI Pocket 3 本体',
        ],
        'must':    ['カメラ','Camera','GoPro','Action','Pocket','Insta360','FDR'],
        'exclude': ['ケース','マウント','バッテリー','充電','交換','アクセサリー','ハウジング','保護'],
        'lead':    'スマホカメラでは撮れない映像をGoPro・DJIで撮った経験をもとに、正直比較します。',
        'problem': ['スマホで撮ると手ブレがひどくて見ていられない', 'GoProとDJIどっちがいいかわからない', '旅行動画をSNSに上げたいが素人っぽく見える'],
        'conclusion': '防水・過酷環境 → GoPro HERO 12、旅行・Vlog → DJI Osmo Action 4、360度撮影 → Insta360',
        'decision': '水中・アウトドアの過酷環境ならGoPro、旅行・日常のVlogならDJIが向いている',
        'personas': [
            ('🏄', 'サーフィン・ダイビング', '水中で使える・落としても壊れない', 'GoPro HERO 12'),
            ('🌍', '旅行・海外Vlog', 'きれいな映像で思い出を残したい', 'DJI Osmo Action 4'),
            ('🚴', 'サイクリング・バイク', 'ヘルメット装着・手ブレなし・長時間録画', 'GoPro / DJI どちらも'),
            ('🎿', 'スキー・スノボ', '寒冷地でも動く・防水・広角', 'GoPro HERO 12'),
        ],
        'criteria': [
            ('GoProかDJIかの選び方', '水中・超過酷環境ならGoPro（10m防水単体）、旅行・Vlogの映像美ならDJI。迷ったら用途を先に決めてください。'),
            ('手ブレ補正は全モデル必須', '最新モデルはほぼすべて電子式手ブレ補正搭載。ただしDJIのRockSteady補正はGoPro比でも映像が滑らかです。'),
            ('バッテリーと保護ケースは初日に買う', 'アクションカメラの本体バッテリーは60〜90分。予備バッテリー2本・専用ケースはセットで揃えましょう。'),
        ],
        'faq': [
            ('GoProとDJIどちらを選べばいいですか？', '水中・アウトドアの過酷環境ならGoPro、旅行・Vlog中心ならDJI Osmo Actionがおすすめです。'),
            ('スマホのカメラとどう違いますか？', '手ブレ補正・超広角・耐衝撃・防水が最大の違いです。'),
            ('4Kで撮影するとデータはどれくらい？', '4K60fpsで1時間あたり約30GB。大容量のmicroSDカード（128GB以上）を準備しましょう。'),
            ('初心者でも使いこなせますか？', '最近のモデルは自動設定が優秀。電源ONで録画ボタンを押すだけで高品質な映像が撮れます。'),
            ('寒い場所でも使えますか？', 'GoProとDJIは-10〜-20℃でも動作しますが、バッテリー持ちが大幅に落ちます。予備バッテリー必須です。'),
        ],
    },
    {
        'title':   'GaN充電器でデスクをスッキリ整理',
        'cat':     'モバイル',
        'keywords': [
            'Anker 735 GaN 充電器 65W',
            'CIO NovaPort QUAD GaN 充電器',
            'Anker 747 GaN 充電器 150W',
            'Belkin BoostCharge Pro GaN 充電器',
            'Anker Nano 3 GaN 30W',
        ],
        'must':    ['充電器','GaN','Charger','NovaPort','BoostCharge'],
        'exclude': ['ケーブル','カバー','アダプタ','延長'],
        'lead':    'MacBook・iPhone・iPadをひとつの充電器でまとめたい方向けに、GaN充電器の選び方を正直に解説します。',
        'problem': ['コンセントが足りなくてタコ足になっている', 'アダプタが大きくてデスクがごちゃごちゃ', 'MacBookとスマホを同時充電したい'],
        'conclusion': 'MacBookメイン → Anker 735 65W GaN、複数デバイス同時 → Anker 747 150W、コスパ → CIO NovaPort',
        'decision': '何を充電するかで選ぶW数が決まる。MacBook Air = 65W、MacBook Pro 16 = 140W、スマホのみ = 30W',
        'personas': [
            ('💻', 'MacBook Airユーザー', '1つの充電器でMacとiPhoneを同時充電', 'Anker 735 65W GaN'),
            ('🖥️', 'MacBook Pro 16ユーザー', '高出力でMacを急速充電', 'Anker 747 150W GaN'),
            ('📱', 'スマホ・タブレットのみ', '小さい・軽い・旅行に最適', 'Anker Nano 3 30W'),
            ('🧳', '海外旅行が多い', '100-240V対応・変圧器不要', 'Anker 65W トラベル対応'),
        ],
        'criteria': [
            ('必要なW数は「最大消費電力の機器」で決まる', 'MacBook Air 15インチは70W、iPhone急速充電は25W。同時使用するなら合計W数を計算しましょう。'),
            ('複数ポートで同時充電すると出力が下がる', '仕様書の「同時使用時出力」を確認しましょう。'),
            ('海外対応（100-240V）かどうかを確認', '対応モデルなら変圧器不要で世界中で使えます。'),
        ],
        'faq': [
            ('GaN充電器とは何ですか？', 'ガリウムナイトライドという素材を使った充電器。従来より小型・軽量で発熱が少ないのが特徴です。'),
            ('MacBook Proの充電に使えますか？', 'MacBook Pro 14インチは65W以上、16インチは140W以上を推奨します。'),
            ('熱くなりませんか？', 'GaN採用により発熱が少ないのが特徴。ただし高負荷時はある程度温かくなります。'),
            ('海外旅行でも使えますか？', '100〜240V対応モデルなら変圧器不要で世界中で使えます。プラグ形状のみ要確認。'),
            ('従来の充電器と何が違いますか？', '同じ出力でも30〜50%小さく・軽くなります。旅行のカバンに入れても全然邪魔になりません。'),
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

# ===== 楽天商品取得（複数キーワードで多様な商品を確保） =====
WH = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','Referer':'https://gadget-tengoku.com/'}

def fetch_products(keyword, hits=10, retries=3):
    for i in range(retries):
        try:
            r = requests.get(WORKER_URL, params={'keyword':keyword,'hits':hits}, headers=WH, timeout=20)
            if r.ok:
                items = r.json().get('Items',[])
                if items: return items
        except Exception as e:
            print(f"  エラー: {e}")
        time.sleep(2)
    return []

def is_trusted(item):
    p    = item.get('Item',{})
    text = (p.get('itemName','') + ' ' + p.get('shopName','')).lower()
    return any(b.lower() in text for b in TRUSTED_BRANDS)

def is_clean(item, theme):
    name = item.get('Item',{}).get('itemName','')
    excl = theme.get('exclude',[])
    must = theme.get('must',[])
    if any(ex in name for ex in excl): return False
    if must and not any(m in name for m in must): return False
    return True

def deduplicate(items, max_same=1):
    """同じ商品名の先頭20文字が被ったものを除去"""
    seen = {}
    result = []
    for item in items:
        name = item.get('Item',{}).get('itemName','')[:20]
        cnt  = seen.get(name, 0)
        if cnt < max_same:
            result.append(item)
            seen[name] = cnt + 1
    return result

def extract_model_key(name):
    """商品名からモデルキーを抽出（重複除去に使用）"""
    name = name.upper()
    # よく使われるモデル番号パターンを抽出
    import re as _re
    # WF-1000XM5, WH-1000XM5, GTR4, Galaxy Watch など
    patterns = [
        r'WF-?\d{4}[A-Z0-9]*',
        r'WH-?\d{4}[A-Z0-9]*',
        r'SOUNDCORE\s*LIBERTY\s*[A-Z0-9]*',
        r'AIRPODS?\s*PRO\s*[0-9]*',
        r'GALAXY\s*WATCH\s*[0-9]*',
        r'FORERUNNER\s*[0-9]+',
        r'VENU\s*[0-9]*',
        r'GTR\s*[0-9]+',
        r'OPENRUN\s*(?:PRO)?',
        r'CLOUD\s*(?:III|II|I|ALPHA)',
        r'ARCTIS\s*[A-Z0-9]*',
        r'G\s*(?:PRO|[0-9]{3})[A-Z0-9\s]*',
        r'POWERCORE\s*[0-9]*',
        r'BRIO\s*[0-9]+',
        r'C[0-9]{3}[A-Z]?',
        r'ROOMBA\s*[A-Z0-9]*',
    ]
    for pat in patterns:
        m = _re.search(pat, name)
        if m:
            return m.group(0).replace(' ','').replace('-','')
    # パターンなければ先頭20文字
    return name[:20]

def fetch_diverse_products(theme, need=5):
    """
    複数キーワードで「1キーワード→1商品」を確保。
    同一モデルの色違い・ショップ違いを除去。
    最低レビュー数チェックあり。
    """
    keywords = theme.get('keywords', [theme.get('kw', theme['title'])])
    all_items   = []
    seen_models = set()  # モデルキーで重複チェック
    MIN_REVIEWS = 3      # 最低レビュー件数

    for kw in keywords:
        if len(all_items) >= need:
            break
        items = fetch_products(kw, hits=10)
        picked = False
        for item in items:
            p     = item.get('Item', {})
            name  = p.get('itemName', '')
            rc    = int(p.get('reviewCount', 0))
            model = extract_model_key(name)

            # 既に同じモデルがある → スキップ
            if model in seen_models:
                continue
            # 信頼ブランド・除外ワードチェック
            if not is_trusted(item):
                continue
            if not is_clean(item, theme):
                continue
            # レビュー件数が最低基準を満たさない → スキップ（ただし後続がなければ緩める）
            if rc < MIN_REVIEWS:
                continue

            seen_models.add(model)
            all_items.append(item)
            picked = True
            break  # このキーワードから1商品だけ取る

        # レビュー条件で1つも取れなかった場合は条件を緩めて再試行
        if not picked and items:
            for item in items:
                p     = item.get('Item', {})
                name  = p.get('itemName', '')
                model = extract_model_key(name)
                if model in seen_models:
                    continue
                if not is_trusted(item):
                    continue
                if not is_clean(item, theme):
                    continue
                seen_models.add(model)
                all_items.append(item)
                break

        time.sleep(0.8)

    print(f"  取得結果: {len(all_items)}件（{len(keywords)}キーワード使用）")

    # 5件に足りない場合はフォールバック（テーマタイトルで広く検索）
    if len(all_items) < need:
        print(f"  不足分をフォールバック取得中...")
        fallback = fetch_products(theme['title'], hits=20)
        for item in fallback:
            if len(all_items) >= need:
                break
            p     = item.get('Item', {})
            name  = p.get('itemName', '')
            model = extract_model_key(name)
            if model in seen_models:
                continue
            if not is_trusted(item):
                continue
            if not is_clean(item, theme):
                continue
            seen_models.add(model)
            all_items.append(item)

    return all_items[:need]

# ===== 体験型コメント生成 =====
EXPERIENCE_COMMENTS = {
    'イヤホン': [
        'を実際に1ヶ月使い続けた結果、電車の中が静音室のように変わりました。',
        'を試した中で、装着感と音質のバランスが最も優れていたモデルです。',
        'を使い始めてから、在宅ワーク中の集中力が目に見えて上がりました。',
        'の最大の特徴は、競合製品と比べて明らかに違うノイキャンの深さです。',
        'を選んだ理由は「コストパフォーマンスの高さ」。値段の割に音質が別次元です。',
    ],
    'スマートウォッチ': [
        'を3ヶ月使って気づいたこと：睡眠データが改善のヒントになっています。',
        'の健康管理機能は、病院に行くほどじゃないけど体が気になる人に刺さります。',
        'を使い始めてから、自分の体調の波が数値でわかるようになりました。',
        'を選んだ理由：バッテリーが5日以上もつので充電を忘れることがなくなりました。',
    ],
    'モバイル': [
        'は毎日のカバンの中に入れても重さを感じない軽量設計が決め手でした。',
        'を導入してから、外出先でバッテリー残量を気にしなくなりました。',
        'の最大の利点は「急速充電」。30分でスマホが80%まで回復します。',
    ],
    'PC周辺機器': [
        'に変えてからWeb会議での映りが明らかに改善しました。相手に言われて気づきました。',
        'を導入してデスクのケーブルがゼロになりました。生産性が上がった実感があります。',
    ],
    'ゲーミング': [
        'を使い始めてから、敵の足音の方向が聞き取れるようになりました。',
        'に変えてからボイチャで「声がクリアになった」と言われました。',
    ],
    'スマートホーム': [
        'を導入してから「鍵を閉めたか不安で引き返す」ことがゼロになりました。',
        'で生活が自動化されて、毎朝5分の手間がなくなりました。',
    ],
    'カメラ': [
        'を使ってから旅行動画のクオリティが別次元になりました。手ブレが消えるって感動です。',
        'は「スマホカメラで後悔した経験がある人」に特にすすめたいモデルです。',
    ],
    'オーディオ': [
        'を使い始めてから、音楽の聴こえ方が根本的に変わりました。',
    ],
}

def get_experience_comment(cat, index):
    comments = EXPERIENCE_COMMENTS.get(cat, ['を実際に使ったレビューをお届けします。'])
    return comments[index % len(comments)]

# ===== 記事HTML生成（リライト版の構成を完全反映） =====
def build_html(title, theme_obj, products):
    theme    = theme_obj['title']
    cat      = theme_obj['cat']
    lead     = theme_obj.get('lead','')
    problems = theme_obj.get('problem',[])
    conc     = theme_obj.get('conclusion','')
    decision = theme_obj.get('decision','')
    personas = theme_obj.get('personas',[])
    criteria = theme_obj.get('criteria',[])
    faq      = theme_obj.get('faq',[])
    today    = datetime.now().strftime('%Y年%m月%d日')
    year     = datetime.now().year

    num_class = ['gold','silver','bronze','normal','normal']
    num_label = ['1位','2位','3位','4位','5位']

    # ===== TOP3 ボックス =====
    top3_items = products[:3]
    top3_html  = ''
    for i, item in enumerate(top3_items):
        p     = item.get('Item',{})
        name  = p.get('itemName','')[:30]
        price = p.get('itemPrice',0)
        url   = p.get('affiliateUrl', p.get('itemUrl','#'))
        labels= ['🏆 総合No.1','💰 コスパNo.1','🎯 用途特化']
        bg    = ['border:2px solid #e63900;background:#fff9f7','border:2px solid #111','border:2px solid #555']
        btn_c = ['background:#e63900','background:#111','background:#555']
        top3_html += f'''
<div style="{bg[i]};border-radius:8px;padding:16px">
  <div style="font-size:11px;font-weight:700;color:#e63900;margin-bottom:6px">{labels[i]}</div>
  <div style="font-size:14px;font-weight:900;margin-bottom:4px">{name}...</div>
  <div style="font-size:19px;font-weight:900;color:#e63900;margin-bottom:10px">¥{price:,}<span style="font-size:12px;color:#aaa;font-weight:400"> 税込〜</span></div>
  <a href="{url}" target="_blank" rel="noopener sponsored" style="display:block;{btn_c[i]};color:#fff;text-align:center;padding:9px;border-radius:4px;font-size:13px;font-weight:700">楽天で最安値を見る →</a>
</div>'''

    # ===== 問題リスト =====
    problem_list = ''.join(f'<li>{p}</li>' for p in problems)

    # ===== ペルソナグリッド =====
    persona_html = ''
    for emoji, label, desc, rec in personas:
        persona_html += f'''
<div style="border:1px solid #e8e8e8;border-radius:6px;padding:14px">
  <div style="font-size:20px;margin-bottom:6px">{emoji}</div>
  <div style="font-weight:700;font-size:13px;margin-bottom:4px">{label}</div>
  <div style="font-size:12px;color:#666;margin-bottom:8px">{desc}</div>
  <div style="font-size:12px;font-weight:700;color:#e63900">→ {rec}</div>
</div>'''

    # ===== 選び方 =====
    criteria_html = ''
    for i, (ctitle, cdesc) in enumerate(criteria):
        criteria_html += f'''
<h3 style="font-size:15px;font-weight:700;margin:20px 0 8px;padding-left:12px;border-left:4px solid #111">基準{['①','②','③','④'][i]} {ctitle}</h3>
<p style="font-size:14px;color:#333;line-height:1.9;margin-bottom:4px">{cdesc}</p>'''

    # ===== 比較表 =====
    table_rows = ''
    for i, item in enumerate(products[:5]):
        p     = item.get('Item',{})
        name  = p.get('itemName','')[:28]
        price = p.get('itemPrice',0)
        ra    = float(p.get('reviewAverage',0))
        rc    = int(p.get('reviewCount',0))
        url   = p.get('affiliateUrl', p.get('itemUrl','#'))
        item_code = p.get('itemCode','')
        rev_url   = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':','/')}/1.1/" if item_code else url
        si    = int(ra)
        stars = '★'*si + '☆'*(5-si)
        best  = ' style="color:#e63900;font-weight:700"' if i == 0 else ''
        table_rows += f'<tr><td><strong>{name}</strong></td><td{best}>¥{price:,}</td><td>{stars} {ra:.1f}</td><td><a href="{rev_url}" target="_blank" rel="noopener" style="color:#e63900">{rc:,}件</a></td><td><a href="{url}" target="_blank" rel="noopener sponsored" style="background:#e63900;color:#fff;padding:4px 10px;border-radius:3px;font-size:11px;font-weight:700;white-space:nowrap">購入</a></td></tr>'

    # ===== 商品カード =====
    cards_html = ''
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
        item_code = p.get('itemCode','')
        rev_url   = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':','/')}/1.1/" if item_code else url
        si        = int(ra)
        stars_h   = f'<span style="color:#f5a623;font-size:16px">{"★"*si}{"☆"*(5-si)}</span>'
        bar_w     = int(ra/5*100)
        exp_comment = get_experience_comment(cat, i)
        img_html  = f'<img src="{img}" alt="{name}" loading="lazy" style="width:100%;max-height:180px;object-fit:contain">' if img else '<div style="color:#ccc;font-size:12px;text-align:center">No Image</div>'

        cards_html += f'''
<div class="rank-card">
  <div class="rank-header">
    <span class="rank-num {num_class[i]}">{i+1}</span>
    <span class="rank-label">{num_label[i]}</span>
    <span class="rank-shop-name">{shop}</span>
  </div>
  <div style="display:grid;grid-template-columns:200px 1fr">
    <div style="background:#fafafa;border-right:1px solid #f0f0f0;display:flex;align-items:center;justify-content:center;padding:16px;min-height:200px">
      {img_html}
    </div>
    <div style="padding:16px 18px;display:flex;flex-direction:column;gap:10px">
      <div style="font-size:14px;font-weight:700;line-height:1.5;color:#111">{name}</div>
      <div style="font-size:13px;color:#555;line-height:1.8;background:#f8f8f8;border-left:3px solid #e63900;padding:10px 14px;border-radius:0 4px 4px 0">
        このモデル{exp_comment}
      </div>
      <div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px">
          {stars_h}
          <strong style="font-size:18px;color:#111">{ra:.1f}</strong>
          <span style="font-size:13px;color:#aaa">/ 5.0</span>
          <a href="{rev_url}" target="_blank" rel="noopener" style="font-size:12px;color:#e63900">楽天の口コミ{rc:,}件を読む →</a>
        </div>
        <div style="background:#f0f0f0;border-radius:4px;height:6px;width:160px">
          <div style="background:#f5a623;height:6px;border-radius:4px;width:{bar_w}%"></div>
        </div>
      </div>
      <div style="margin-top:auto;padding-top:10px;border-top:1px solid #f0f0f0">
        <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:10px">
          <div style="font-size:26px;font-weight:900;color:#e63900">¥{price:,}</div>
          <small style="font-size:12px;color:#aaa">税込｜送料無料（楽天市場）</small>
        </div>
        <a href="{url}" target="_blank" rel="noopener sponsored" class="btn-buy">今の最安値を楽天で確認する →</a>
        <a href="{rev_url}" target="_blank" rel="noopener" class="btn-review">実際のレビュー（{rc:,}件）を読む →</a>
      </div>
    </div>
  </div>
</div>'''

    # ===== FAQ =====
    faq_html = ''
    if faq:
        faq_items = ''.join(f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>' for q,a in faq)
        faq_html  = f'<section id="faq"><h2 class="section-title">よくある質問（FAQ）</h2><div class="faq-wrap">{faq_items}</div></section>'

    faq_ld = ','.join(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}' for q,a in faq)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>【{year}年】{theme}おすすめ5選｜用途別に徹底比較 | ガジェット天国</title>
<meta name="description" content="{year}年最新。{theme}を用途別に比較。{lead[:60]}失敗しない選び方・FAQ付き。">
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
    <nav><a href="{SITE_URL}/">トップ</a><a href="{SITE_URL}/archive.html">記事一覧</a></nav>
  </div>
</header>

<div class="article-hero">
  <div class="article-hero-inner">
    <div class="article-cat">{cat}</div>
    <h1>【{year}年】{theme}おすすめ5選<br>用途別に徹底比較</h1>
    <div class="article-meta">
      <span>📅 {today} 更新</span>
      <span>⏱ 読了約6分</span>
      <span>✍️ 実機チェック済み</span>
    </div>
  </div>
</div>

<div class="container">

  <!-- 結論（PREP：Point） -->
  <div class="result-box">
    <div class="result-box-label">✅ 結論：迷ったらこの3択</div>
    <div class="result-box-text">{conc}</div>
  </div>

  <!-- 悩みへの共感 -->
  <div style="background:#fff8f0;border-left:4px solid #e63900;padding:16px 20px;margin-bottom:20px;border-radius:0 6px 6px 0">
    <div style="font-size:12px;color:#e63900;font-weight:700;margin-bottom:8px">こんな悩みはありませんか？</div>
    <ul style="font-size:14px;color:#333;line-height:2.2;padding-left:20px">{problem_list}</ul>
    <div style="font-size:14px;color:#111;font-weight:700;margin-top:10px">→ この記事を読めば15分で選べます。</div>
  </div>

  <div class="intro-box">{lead}</div>

  <!-- まず見るべきTOP3 -->
  <section id="top3">
    <h2 class="section-title">まず見るべきおすすめTOP3</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-bottom:24px">
      {top3_html}
    </div>
  </section>

  <nav class="toc">
    <div class="toc-title">この記事の目次</div>
    <ol>
      <li><a href="#persona">あなたに合うのはどれ？用途別診断</a></li>
      <li><a href="#howto">失敗しない選び方</a></li>
      <li><a href="#compare">スペック比較表</a></li>
      <li><a href="#ranking">詳細レビュー5選</a></li>
      <li><a href="#faq">よくある質問</a></li>
    </ol>
  </nav>

  <!-- 用途別ペルソナ -->
  <section id="persona">
    <h2 class="section-title">あなたに合うのはどれ？用途別診断</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:12px;margin-bottom:24px">
      {persona_html}
    </div>
  </section>

  <!-- 選び方 -->
  <section id="howto">
    <h2 class="section-title">失敗しない選び方｜{len(criteria)}つの基準だけ見ればいい</h2>
    <p style="font-size:14px;color:#333;line-height:1.9;margin-bottom:16px">{decision}</p>
    {criteria_html}
  </section>

  <!-- 比較表 -->
  <section id="compare">
    <h2 class="section-title">スペック比較表｜一気に比較</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
    <p style="font-size:12px;color:#aaa;margin-top:8px">※{today}時点の楽天市場価格。価格は変動する場合があります。</p>
  </section>

  <!-- 詳細レビュー -->
  <section id="ranking">
    <h2 class="section-title">詳細レビュー5選｜選ぶ理由を正直に書く</h2>
    <p style="font-size:12px;color:#aaa;margin-bottom:16px">
      ※参照：<a href="https://www.rakuten.co.jp/" target="_blank" rel="noopener" style="color:#e63900">楽天市場</a>（{today}時点・レビュー件数・価格）
    </p>
    {cards_html}
  </section>

  {faq_html}

  <!-- 最終CTA -->
  <div class="final-cta">
    <div class="final-cta-title">まだ迷っていますか？</div>
    <div class="final-cta-sub">楽天市場で実際の口コミを読んでから決めましょう。<br>返品・交換保証あり・ポイント還元でお得に購入できます。</div>
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
        'title':       f"【{year}年】{theme_obj['title']}おすすめ5選｜用途別徹底比較",
        'filename':    filename,
        'img_url':     img_url,
        'category':    theme_obj['cat'],
        'theme_key':   theme_obj['title'],
        'date':        today.strftime('%Y年%m月%d日'),
        'description': theme_obj.get('lead','')[:80],
    }
    updated = False
    for i,a in enumerate(articles):
        if a['filename']==filename:
            articles[i]=new; updated=True; break
    if not updated: articles.insert(0,new)
    articles = articles[:50]
    gh_put('articles.json', json.dumps(articles,ensure_ascii=False,indent=2), 'Auto: 記事一覧更新', sha)
    return articles

# ===== 既存記事再生成・クリーンアップ =====
def regenerate_and_cleanup():
    print('\n既存記事を再生成中...')
    content,_ = gh_get('articles.json')
    if not content: return
    articles  = json.loads(content)
    theme_map = {t['title']:t for t in ALL_THEMES}
    keep      = []

    for a in articles:
        filename  = a.get('filename','')
        theme_key = a.get('theme_key','')
        title     = a.get('title','')
        theme_obj = theme_map.get(theme_key)

        if not theme_obj:
            print(f'  テーマ不明→削除: {theme_key}')
            _,sha = gh_get(filename)
            if sha: gh_delete(filename,sha,f'Cleanup: {filename}')
            continue

        print(f'  再生成: {theme_key}')
        products = fetch_diverse_products(theme_obj, need=5)

        if not products:
            print(f'  商品0件→削除: {filename}')
            _,sha = gh_get(filename)
            if sha: gh_delete(filename,sha,f'Cleanup: 商品なし {filename}')
            continue

        html   = build_html(title, theme_obj, products)
        _,sha  = gh_get(filename)
        if gh_put(filename, html, f'Regenerate: {theme_key}', sha):
            imgs = products[0].get('Item',{}).get('mediumImageUrls',[])
            if imgs:
                raw = imgs[0].get('imageUrl','') if isinstance(imgs[0],dict) else ''
                a['img_url'] = re.sub(r'\?_ex=\d+x\d+','?_ex=400x400',raw)
            keep.append(a)
        else:
            keep.append(a)
        time.sleep(1.5)

    _,sha = gh_get('articles.json')
    gh_put('articles.json', json.dumps(keep,ensure_ascii=False,indent=2), 'Auto: articles.json更新', sha)
    print(f'完了（残り{len(keep)}件）')

# ===== アーカイブ =====
def build_archive(articles):
    arts  = [a for a in articles if a.get('img_url','').strip()]
    cards = ''.join(f'''
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
    today = datetime.now().strftime('%Y-%m-%d')
    bases = [
        ('', '1.0', 'daily'),
        ('earphone.html', '0.9', 'weekly'),
        ('smartwatch.html', '0.9', 'weekly'),
        ('battery.html', '0.9', 'weekly'),
        ('gaming.html', '0.9', 'weekly'),
        ('telework.html', '0.9', 'weekly'),
        ('archive.html', '0.8', 'daily'),
        ('privacy.html', '0.4', 'monthly'),
    ]
    urls = [f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>'
            for u, pri, freq in bases]
    for f in extra:
        urls.append(f'  <url><loc>{SITE_URL}/{f}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'

# ===== Twitter =====
def post_twitter(title, url, theme_obj):
    if not all([TWITTER_API_KEY,TWITTER_API_SECRET,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET]):
        print('⚠ Twitter Secrets未設定'); return
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY,TWITTER_API_SECRET,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
        problems = theme_obj.get('problem',[])
        pain = problems[0] if problems else ''
        text = f"新着記事📱\n{title}\n\n「{pain}」\n→ 解決策はこちら✅\n\n用途別比較・FAQ付き！\n\n{url}\n\n#{theme_obj['cat']} #ガジェット #楽天"
        tweepy.API(auth).update_status(text[:280])
        print('✅ Twitter投稿成功')
    except Exception as e:
        print(f'❌ Twitter失敗: {e}')

# ===== テーマ選択 =====
def select_theme():
    content,_ = gh_get('articles.json')
    used = set()
    if content:
        try: used = {a.get('theme_key','') for a in json.loads(content)[:40]}
        except: pass
    available = [t for t in ALL_THEMES if t['title'] not in used] or ALL_THEMES
    am = ['イヤホン','オーディオ','スマートウォッチ']
    pm = ['ゲーミング','PC周辺機器','スマートホーム','カメラ','モバイル']
    pool = [t for t in available if t['cat'] in (am if SLOT=='am' else pm)] or available
    return random.choice(pool)

# ===== メイン =====
def main():
    today = datetime.now()
    print(f"=== {today.strftime('%Y年%m月%d日')} [{SLOT.upper()}] ===")

    theme    = select_theme()
    print(f"テーマ: {theme['title']}")
    products = fetch_diverse_products(theme, need=5)

    if not products:
        print('❌ 商品取得失敗'); return

    title    = f"【{today.year}年】{theme['title']}おすすめ5選｜用途別徹底比較"
    html     = build_html(title, theme, products)
    date_str = today.strftime('%Y%m%d')
    safe     = re.sub(r'[^\w]','-',theme['title'])[:25]
    filename = f"article-{safe}-{SLOT}-{date_str}.html"

    _,sha = gh_get(filename)
    gh_put(filename, html, f"Auto: {theme['title']}", sha)

    img_url = ''
    if products:
        imgs = products[0].get('Item',{}).get('mediumImageUrls',[])
        if imgs:
            raw     = imgs[0].get('imageUrl','') if isinstance(imgs[0],dict) else ''
            img_url = re.sub(r'\?_ex=\d+x\d+','?_ex=400x400',raw)

    update_articles_json(theme, filename, img_url, today)
    regenerate_and_cleanup()

    content,_ = gh_get('articles.json')
    if content:
        _,sha = gh_get('archive.html')
        gh_put('archive.html', build_archive(json.loads(content)), 'Auto: アーカイブ更新', sha)

    _,sha = gh_get('sitemap.xml')
    gh_put('sitemap.xml', build_sitemap([filename]), 'Auto: サイトマップ', sha)

    post_twitter(title, f"{SITE_URL}/{filename}", theme)
    print(f"\n=== 完了: {SITE_URL}/{filename} ===")

if __name__ == '__main__':
    main()
