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
    # ===== イヤホン系 (8テーマ) =====
    {
        'title': '通勤・在宅ワーク向けノイキャンイヤホン',
        'cat': 'イヤホン',
        'kw_short': 'ノイキャンイヤホン 通勤',
        'keywords': ['Sony WF-1000XM5', 'Jabra Elite 10', 'Anker Soundcore Liberty 4 NC', 'AirPods Pro 第2世代 本体', 'Shokz OpenRun Pro'],
        'must': ['イヤホン','ヘッドホン','Earbuds','WF-','Elite','Liberty','AirPods','OpenRun'],
        'exclude': ['ケース','ポーチ','カバー','クッション','交換','イヤーパッド','イヤーチップ','充電ケーブル'],
        'lead': '電車の騒音・家族の声・オフィスの雑音を消して集中したい方向けの記事です。',
        'problem': ['満員電車で音楽を聴いても騒音で集中できない', '在宅ワーク中に子どもの声でWeb会議に集中できない', 'ノイキャンイヤホンを買ったが効果が薄くて後悔した', '1万円台と3万円台の違いが正直わからない'],
        'conclusion': '通勤・電車メイン → Sony WF-1000XM5｜Web会議特化 → Jabra Elite 10｜コスパ重視 → Anker Soundcore Liberty 4 NC',
        'decision': '「ノイキャン性能」より「用途」で選ぶ。マイク品質と連続使用時間も必ず確認する',
        'personas': [('🚃','毎日電車通勤','騒音を完全遮断して音楽・ポッドキャストを楽しみたい','Sony WF-1000XM5'),('💻','在宅ワーク・Web会議','家族の声を遮断しマイク音声も鮮明にしたい','Jabra Elite 10'),('💰','初めての購入・コスパ重視','1万円台で本格ノイキャンを体験したい','Anker Soundcore Liberty 4 NC'),('🏃','運動しながら使う','外音も聞こえて安全に・耳も疲れない','Shokz OpenRun Pro')],
        'criteria': [('ノイキャン性能より「用途」で選ぶ','電車通勤なら密閉型カナル式、長時間在宅なら装着感優先で選びましょう。'),('マイク品質を必ず確認する','Web会議で使うならマイクのNC性能が最重要。安いモデルは通話品質が低いものが多い。'),('連続使用時間は「本体のみ」で確認する','「最大32時間」はケース込み。本体単体での時間が重要。通勤往復2時間なら本体4時間でOK。')],
        'faq': [('ノイキャンイヤホンは飛行機でも効果がありますか？','非常に効果的です。飛行機のエンジン音は低周波でノイキャンが最も得意とする帯域です。'),('在宅ワークのWeb会議でマイクは使えますか？','機種によって大きく差があります。Jabra・Sony・Anker上位モデルは通話品質が高い評価です。'),('1万円台と3万円台の違いは何ですか？','日常の騒音なら1万円台で十分。電車・飛行機の騒音を本当に消したいなら3万円台を選んでください。'),('長時間装着すると耳が痛くなります','まずイヤーピースのサイズを変えてください。それでも痛い場合はShokz（骨伝導）を検討してください。'),('iPhoneとAndroid両方で使えますか？','Bluetooth接続なのでOS問わず使用可。ただしAirPods ProはiPhone専用と考えてください。')],
    },
    {
        'title': '1万円以下コスパ最強ワイヤレスイヤホン',
        'cat': 'イヤホン',
        'kw_short': 'ワイヤレスイヤホン 1万円以下',
        'keywords': ['Anker Soundcore A3i', 'JVC HA-A30T', 'EDIFIER TWS330NB', 'Belkin SoundForm Bolt', 'Anker Soundcore Life P3'],
        'must': ['イヤホン','Buds','TWS','Life','Soundcore'],
        'exclude': ['ケース','カバー','イヤーパッド','交換','充電ケーブル'],
        'lead': '「AirPodsは高すぎる」「でも安物買いの銭失いはしたくない」という方向けに、1万円以下で本当に使えるモデルだけ厳選しました。',
        'problem': ['AirPodsが高すぎる','安いイヤホンを買って音質に失望した','充電切れが早くて困った','Androidで使えるいいイヤホンが見つからない'],
        'conclusion': 'コスパNo.1 → Anker Soundcore A3i｜音質重視 → EDIFIER TWS330NB｜長時間使用 → JVC HA-A30T',
        'decision': '1万円以下はAnkerとEDIFIERとJVCの3ブランドから選べばまず失敗しない',
        'personas': [('💰','予算1万円以内','AirPodsの代わりを探している大学生・20代'),('📱','Androidユーザー','iOSに縛られずに使えるワイヤレスイヤホンを探している'),('🎵','音質重視','安くても音質を妥協したくない'),('🔋','長時間使用','電池持ちを最優先で選びたい')],
        'criteria': [('連続使用時間を確認する','1万円以下でも8〜10時間使えるモデルが増えています。ケース込みの時間ではなく本体単体の時間で選ぶこと。'),('ノイキャンの有無を確認する','1万円以下でもノイキャン搭載モデルがあります。ただし効果は3万円台の半分以下が目安です。'),('Bluetooth バージョンを確認する','Bluetooth 5.0以上を選ぶと遅延・接続安定性が改善されます。')],
        'faq': [('1万円以下でも音質は大丈夫ですか？','Anker・EDIFIER・JVCなど信頼ブランドなら十分満足できる音質。ハイレゾ対応モデルも増えています。'),('AirPodsと何が違いますか？','音質は同等以上のモデルも存在。Androidユーザーならむしろコスパ系の方が機能が豊富なことも。'),('保証は何年ですか？','Ankerは18ヶ月保証。国内正規品を購入すれば安心して使えます。'),('iPhoneでもAndroidでも使えますか？','Bluetooth接続なのでOS問わず使用可。iOS専用機能はAirPodsのみです。'),('ノイキャンはついていますか？','Anker Soundcore Life P3などノイキャン搭載モデルがあります。効果は高額機より劣りますが十分実用的。')],
    },
    {
        'title': 'スポーツ・ランニング向けワイヤレスイヤホン',
        'cat': 'イヤホン',
        'kw_short': 'イヤホン ランニング おすすめ',
        'keywords': ['Jabra Elite Active 75t', 'Shokz OpenRun', 'Anker Soundcore Sport X10', 'Sony LinkBuds S', 'JVC HA-ET45T'],
        'must': ['イヤホン','Buds','OpenRun','Sport','LinkBuds'],
        'exclude': ['ケース','カバー','交換','イヤーパッド'],
        'lead': '走っても落ちない・汗で壊れない・外音も聞こえる。スポーツ中に本当に使えるイヤホンだけ厳選しました。',
        'problem': ['走るとイヤホンが外れてストレス','汗で壊れた経験がある','交通量の多い道を走るとき車の音が聞こえなくて怖い','運動中に耳が蒸れて不快'],
        'conclusion': '落ちない固定力 → Jabra Elite Active｜耳をふさがない安全性 → Shokz OpenRun｜コスパ → Anker Sport X10',
        'decision': 'IPX4以上の防水・固定方法・外音取り込み機能の3点で絞り込む',
        'personas': [('🏃','週3回ランニング','落ちない・汗に強い・外音も聞こえる'),('🚴','自転車通勤・サイクリング','車の音が聞こえて安全に走りたい'),('🏋️','ジム・筋トレ','耳が蒸れない・激しい動きでもズレない'),('💰','初めてのスポーツ用','コスパ重視で試してみたい')],
        'criteria': [('防水性能：IPX4以上を選ぶ','IPX4は汗・小雨OK。水泳するならIPX7以上。ランニングの汗ならIPX4〜5で十分です。'),('固定方法：イヤーフック・ウイングチップが必須','普通のイヤホンは走ると外れます。スポーツ向けは固定パーツ付きを選びましょう。'),('外音取り込み機能：交通量が多い道なら必須','車の音を聞きながら音楽を楽しめます。特に公道を走るランナーには必須です。')],
        'faq': [('スポーツ中にイヤホンが外れないか心配です','イヤーフックやウイングチップ付きのモデルを選びましょう。Jabraは固定力に定評があります。'),('骨伝導イヤホンは音が悪いですか？','低音は劣りますが中高音はクリア。耳をふさがないので安全性・長時間装着では骨伝導が優秀です。'),('バッテリーはどれくらいもちますか？','本体6〜10時間が目安。フルマラソンも余裕でカバーできます。'),('水洗いできるモデルはありますか？','Shokz OpenRunはIP67防水で水洗いOK。衛生面が気になる方にもおすすめです。'),('外音取り込み機能は必要ですか？','公道を走る場合は必須。車の音を聞きながら音楽が楽しめます。')],
    },
    {
        'title': 'テレワーク・在宅ワーク向けヘッドセット',
        'cat': 'イヤホン',
        'kw_short': 'ヘッドセット テレワーク おすすめ',
        'keywords': ['Jabra Evolve2 Buds テレワーク', 'Sony WH-1000XM5 ヘッドホン', 'Logicool Zone Wireless ヘッドセット', 'Plantronics Voyager Focus ヘッドセット', 'Anker PowerConf H700 ヘッドセット'],
        'must': ['ヘッドセット','ヘッドホン','Wireless','WH-'],
        'exclude': ['イヤーパッド','クッション','ケーブル','交換','補修'],
        'lead': '家族の声・生活音をシャットアウトしてWeb会議に集中したい在宅ワーカー向けの記事です。',
        'problem': ['家族の声が会議中に入る','マイクの音質が悪くて相手に聞き返される','長時間装着すると耳が痛い','イヤホンと違いヘッドセットは何を選べばいいかわからない'],
        'conclusion': '音質・NC最強 → Sony WH-1000XM5｜マイク品質最強 → Jabra Evolve2 Buds｜コスパ → Anker H700',
        'decision': 'ノイキャン性能・マイクNC・長時間装着の快適さの3点で選ぶ',
        'personas': [('💻','週4日以上在宅','子どもの声でWeb会議に集中できない'),('🎙️','マイク品質重視','声が鮮明に届くことを最優先したい'),('🎵','音楽も楽しみたい','会議もエンタメも1台でこなしたい'),('💰','コスパ重視','1万円台で実用的なヘッドセットが欲しい')],
        'criteria': [('マイクのNC性能が最重要','音楽用NCとマイク用NCは別物。マイクNCが弱いと相手に雑音が聞こえます。Jabra・Logicoolが特に優秀。'),('長時間装着の快適さ','側圧の強さ・クッションの柔らかさ・重量（300g以下）を確認。1日8時間使えるかどうかが重要。'),('有線か無線かを決める','在宅メインなら有線でも不便なし。外出も想定するなら無線モデルを選びましょう。')],
        'faq': [('ヘッドセットとヘッドホンの違いは何ですか？','ヘッドセットはマイク内蔵、ヘッドホンはマイクなし。Web会議ではヘッドセットまたはマイク内蔵ヘッドホンが必要です。'),('長時間つけていると耳が痛くなります','側圧の強さとイヤーカップの素材が重要。300g以下・柔らかいクッション付きを選んでください。'),('MacとWindowsどちらでも使えますか？','Bluetooth・USB接続のモデルはどちらでも使用可能です。'),('Zoomで音声が遅延します','Bluetooth接続は遅延が発生することがあります。Web会議専用なら有線接続が安定します。'),('眼鏡をしていても使えますか？','側圧の強いモデルは眼鏡のフレームに当たることがあります。試着できる場合は必ず確認を。')],
    },
    {
        'title': '骨伝導イヤホン完全ガイド',
        'cat': 'イヤホン',
        'kw_short': '骨伝導イヤホン おすすめ',
        'keywords': ['Shokz OpenRun Pro 本体', 'Shokz OpenSwim', 'Shokz OpenFit', 'AfterShokz Aeropex 本体', 'Panasonic 骨伝導 ヘッドホン'],
        'must': ['骨伝導','OpenRun','OpenSwim','OpenFit','Aeropex'],
        'exclude': ['ケース','カバー','交換','充電ケーブル'],
        'lead': '耳の穴をふさがずに音楽が聴ける骨伝導イヤホン。自転車・ランニング・長時間装着に最適な理由を解説します。',
        'problem': ['普通のイヤホンは耳をふさいで危ない','長時間つけると耳が痛い','メガネと干渉する','カナル型で耳が蒸れる'],
        'conclusion': 'ランニング → Shokz OpenRun Pro｜水泳対応 → Shokz OpenSwim｜開放感重視 → Shokz OpenFit',
        'decision': 'Shokz（旧AfterShokz）一択。用途に合わせてモデルを選ぶだけ',
        'personas': [('🏃','ランニング・サイクリング','外音が聞こえて安全に使いたい'),('🏊','水泳','プールや海で音楽を楽しみたい'),('💼','テレワーク','1日8時間以上装着しても耳が痛くない'),('👓','メガネユーザー','イヤホンとメガネの干渉が気になる')],
        'criteria': [('用途で選ぶ','ランニングはOpenRun Pro、水泳はOpenSwim、日常・テレワークはOpenFit。用途を先に決めてください。'),('防水性能を確認する','ランニングの汗ならIP55、水泳するならIP68対応のOpenSwimが必要です。'),('バッテリー持ちを確認する','OpenRun Proは10時間、OpenSwimは8時間。用途に合わせて確認しましょう。')],
        'faq': [('普通のイヤホンより音が悪いですか？','低音は劣りますが中高音はクリア。通話品質は特に優秀です。'),('メガネをしていても使えますか？','Shokzはメガネとの干渉が少ない設計です。'),('防水性能はどれくらいですか？','OpenRunはIP67、OpenSwimはIP68防水です。'),('テレワークのWeb会議でも使えますか？','マイク内蔵でNC付き。会議用として評価が高いです。'),('耳の穴をふさがないと音が漏れませんか？','静かな場所では多少聞こえます。電車の中などでの使用は音量に注意が必要です。')],
    },

    # ===== スマートウォッチ系 (4テーマ) =====
    {
        'title': '健康管理に使えるスマートウォッチ',
        'cat': 'スマートウォッチ',
        'kw_short': 'スマートウォッチ 健康管理 おすすめ',
        'keywords': ['Garmin Venu 3 本体', 'Apple Watch SE 第2世代 本体', 'Samsung Galaxy Watch 6 本体', 'Fitbit Charge 6', 'Amazfit GTR 4'],
        'must': ['Watch','ウォッチ','Venu','Fitbit','Amazfit','Charge','Galaxy'],
        'exclude': ['バンド','ベルト','充電','ケース','フィルム','交換','スタンド','保護'],
        'lead': '睡眠・心拍・血中酸素・ストレスを毎日記録して自分の体の変化を数値で把握したい方向けです。',
        'problem': ['体調が悪い日の原因がわからない','睡眠の質を改善したいが何をすればいいかわからない','Apple WatchとGarminどっちがいいか決められない','スマートウォッチを買って充電が面倒で使わなくなった'],
        'conclusion': 'バッテリー・GPS重視 → Garmin Venu 3｜iPhoneユーザーの入門 → Apple Watch SE｜コスパ → Amazfit GTR 4',
        'decision': 'バッテリー持ち・GPS精度・健康データの詳細さで選ぶ。Garminは5日以上、Apple Watchは毎日充電前提',
        'personas': [('❤️','健康診断で引っかかった40代','血圧・心拍・睡眠を毎日数値で把握したい'),('🏅','ランニング・マラソン','GPS精度・ルート記録・トレーニング分析'),('📱','iPhoneユーザーの入門','Apple Watchを試してみたい・使いやすさ重視'),('💰','コスパ重視・Android','1〜2万円台・バッテリー長持ち')],
        'criteria': [('バッテリー持ちで選ぶ','Apple Watchは1〜2日で要充電。GarminのVenuは5〜7日持つ。毎日充電が面倒な人はGarminを選んでください。'),('健康データの詳細さで選ぶ','睡眠ステージ・ストレス・血中酸素まで詳しく知りたいならGarminが圧倒的。Apple Watchは心電図が強み。'),('iPhoneかAndroidかで選ぶ','Apple WatchはiPhone専用。AndroidユーザーはGarmin・Samsung・Amazfitから選んでください。')],
        'faq': [('血圧は正確に測れますか？','医療機器ではないため参考値です。傾向把握・異常値アラートとしては十分活用できます。'),('Apple WatchとGarminどっちがいいですか？','iPhoneユーザーで決済機能も使いたいならApple Watch。バッテリー持ち・GPS精度を重視するならGarmin。'),('睡眠の質はどうやって計測しますか？','心拍数・血中酸素・体動から睡眠ステージを自動判定します。'),('防水性能はありますか？','ほとんどのモデルが5ATM防水でシャワーや水泳にも対応しています。'),('バッテリーはどれくらいもちますか？','Apple Watchは1〜2日、GarminのVenuは5〜7日、Amazfitは最大14日が目安です。')],
    },
    {
        'title': 'ランニング・マラソン向けGPSスマートウォッチ',
        'cat': 'スマートウォッチ',
        'kw_short': 'スマートウォッチ ランニング GPS',
        'keywords': ['Garmin Forerunner 265 本体', 'Garmin Forerunner 55 本体', 'Coros Pace 3 本体', 'Apple Watch Ultra 2 本体', 'Polar Pacer Pro 本体'],
        'must': ['Watch','ウォッチ','Forerunner','Coros','Polar','Pacer'],
        'exclude': ['バンド','ベルト','充電','ケース','フィルム','交換'],
        'lead': 'タイムを縮めたいランナーに必要なのは、GPS精度・心拍ゾーン・リカバリー分析が揃ったスマートウォッチです。',
        'problem': ['スマホでランニングを管理していたがGPSがズレる','トレーニング強度の適正がわからない','マラソン完走後の回復にどれだけかかるか知りたい','フルマラソン中にバッテリーが切れた'],
        'conclusion': 'コスパ最強 → Garmin Forerunner 265｜入門向け → Garmin Forerunner 55｜本格派 → Apple Watch Ultra 2',
        'decision': 'GPS精度・バッテリー持ち（GPS使用時）・トレーニング分析機能の3点で選ぶ',
        'personas': [('🏃','週3〜5回ランニング','タイムを縮めたい市民ランナー'),('🏁','フルマラソン初挑戦','完走を目標に練習を管理したい'),('🌲','トレイルランニング','山道でのGPS精度と長時間バッテリーが必要'),('💰','コスパ重視','2〜3万円台で本格的なGPSウォッチが欲しい')],
        'criteria': [('GPS使用時のバッテリー持ちを確認する','フルマラソン（4〜6時間）を走りきれるか確認。Garmin Forerunner 265はGPS使用で約20時間。'),('心拍ゾーン機能を確認する','正確な心拍ゾーン管理があるとトレーニングの質が上がります。光学式心拍計の精度も重要。'),('リカバリー・VO2max機能を確認する','トレーニング後のリカバリー時間表示があると過負荷を防げます。')],
        'faq': [('スマホのランニングアプリと何が違いますか？','GPS精度・心拍計・ランニングダイナミクスの精度が格段に上がります。腕時計型なのでスマホを持たずに走れます。'),('バッテリーはフルマラソン中もちますか？','Garmin Forerunner 265はGPS使用で約20時間。フルマラソン（6時間以内）なら問題なし。'),('防水性能はありますか？','5ATM防水でシャワー・水泳にも対応しています。'),('Apple Watch Ultra 2はランニングに向いていますか？','GPS精度・バッテリーともに優秀ですが、価格が約10万円と高額です。本格派向けです。'),('Garmin ConnectとStrava、どちらが使いやすいですか？','Garmin ConnectはGarmin特化で詳細分析が得意。StravaはSNS要素が強く仲間とシェアできます。')],
    },
    {
        'title': 'スマートウォッチ初心者の選び方ガイド',
        'cat': 'スマートウォッチ',
        'kw_short': 'スマートウォッチ 初心者 選び方',
        'keywords': ['Apple Watch SE 第2世代 本体', 'Fitbit Versa 4 本体', 'Samsung Galaxy Watch 6 本体', 'Amazfit Bip 5 本体', 'Garmin Vivoactive 5 本体'],
        'must': ['Watch','ウォッチ','Fitbit','Amazfit','Bip','Vivoactive','Versa'],
        'exclude': ['バンド','ベルト','充電','ケース','フィルム','交換'],
        'lead': '「スマートウォッチって何が便利なの？」という方向けに、初めて買う人が失敗しない選び方を解説します。',
        'problem': ['スマートウォッチの機能が多すぎて何を選べばいいかわからない','高いものを買って使いこなせなかったら困る','毎日充電が必要なら面倒くさい','文字盤が見づらいと困る'],
        'conclusion': 'iPhoneユーザーの入門 → Apple Watch SE｜Android入門 → Amazfit Bip 5｜コスパ最強 → Amazfit GTR 4',
        'decision': 'まずiPhoneかAndroidかを確認してから選ぶ。初めてなら3万円以下で試してみるのが正解',
        'personas': [('📱','スマホはiPhone派','シームレスに連携して使いたい'),('🤖','Androidユーザー','iOSに縛られない選択肢を探している'),('💰','初めてなので安く試したい','2万円以内で体験してから高いものを検討したい'),('👔','ビジネスマン','スーツに合うデザインで通知管理がしたい')],
        'criteria': [('まずiPhoneかAndroidかを確認する','Apple WatchはiPhone専用。AndroidユーザーはGarmin・Samsung・AmazfitからOS問わず選べます。'),('バッテリー持ちを最初に確認する','毎日充電が苦にならない人はApple Watch。充電回数を減らしたい人はGarmin・Amazfitを選んでください。'),('まず安いモデルで試す','初めてのスマートウォッチは2〜3万円台で十分。使い慣れてから高機能モデルに移行するのがおすすめ。')],
        'faq': [('スマートウォッチは何歳から使えますか？','年齢制限はありませんが、子ども向けには専用のキッズスマートウォッチがあります。'), ('毎日充電が必要なのは面倒ではないですか？','Apple Watchは1〜2日で要充電。Garmin・Amazfitは5〜14日持ちます。生活スタイルに合わせて選んでください。'),('スマートウォッチで電話はできますか？','Bluetoothを通じて通話できるモデルと、SIM内蔵で単体通話できるモデルがあります。'),('文字盤はカスタマイズできますか？','多くのモデルで数百種類の文字盤から選択可能。表示する情報も変更できます。'),('スマートウォッチを付けたまま寝られますか？','睡眠計測のため付けたまま寝ることを推奨するモデルもあります。ただし毎日充電が必要なモデルは就寝中に充電することが多いです。')],
    },

    # ===== モバイルバッテリー系 (4テーマ) =====
    {
        'title': '毎日持ち歩けるコスパ最強モバイルバッテリー',
        'cat': 'モバイル',
        'kw_short': 'モバイルバッテリー 軽量 おすすめ',
        'keywords': ['Anker PowerCore 10000 PD Redux', 'CIO SMARTCOBY PRO SLIM', 'Belkin BoostCharge 10000', 'UGREEN Nexode Power 10000', 'Anker Nano Power Bank'],
        'must': ['バッテリー','モバイル','PowerCore','SMARTCOBY','BoostCharge','Nexode'],
        'exclude': ['ケース','カバー','ケーブル'],
        'lead': '重いモバイルバッテリーを買ったら結局カバンに入れなくなった、という失敗をしないための記事です。',
        'problem': ['重くて持ち歩くのが面倒でカバンに入れなくなった','スマホが夕方に切れそうで不安','軽くて急速充電対応のモデルが見つからない','どのブランドが信頼できるかわからない'],
        'conclusion': '毎日持ち歩き → Anker PowerCore 10000 PD（180g）｜デザイン重視 → CIO SMARTCOBY PRO（170g）｜コスパ → Anker Nano',
        'decision': '毎日使うなら200g以下が絶対条件。急速充電対応（18W以上PD）かどうかを次に確認する',
        'personas': [('👔','毎日通勤するビジネスマン','カバンに入れても重くない・スマホ1回分あればOK'),('📱','スマホヘビーユーザー','一日中使うから夕方に切れる前に補充したい'),('💰','コスパ重視','3000〜4000円台で十分な機能が欲しい'),('✈️','出張が多い','飛行機持ち込みOKで急速充電対応のものが欲しい')],
        'criteria': [('毎日持ち歩くなら200g以下が目安','300gを超えると「今日は重いからいいや」と持ち歩かなくなります。継続して使えることが最重要。'),('急速充電対応（PD 18W以上）を選ぶ','急速充電非対応は充電時間が倍以上かかる場合があります。PD表記のあるモデルを選んでください。'),('飛行機持ち込みはWh（ワットアワー）で確認する','100Wh以下なら機内持ち込みOK。mAhだけでなくWhの確認が重要です。')],
        'faq': [('毎日持ち歩くなら何mAhがいいですか？','スマホ1回分なら5000〜10000mAh。200g以下を選べば重さを感じません。'),('急速充電対応かどうかの確認方法は？','PD（Power Delivery）18W以上と書かれているものが急速充電対応です。'),('飛行機に持ち込めますか？','2026年4月24日以降、機内持ち込みは2個まで・160Wh以下・手元保管。機内での充電・給電は禁止です。'),('充電しながら使えますか？','パススルー充電対応モデルとそうでないものがあります。商品ページの仕様欄で確認しましょう。'),('Anker以外に信頼できるブランドはありますか？','CIO（日本製）・UGREEN・Belkin・エレコムも信頼性が高いブランドです。')],
    },
    {
        'title': 'ノートPC対応・大容量モバイルバッテリー',
        'cat': 'モバイル',
        'kw_short': 'モバイルバッテリー ノートPC 65W',
        'keywords': ['Anker Prime 20000 Power Bank', 'UGREEN Nexode Power Bank 25000', 'Anker PowerCore III Elite 25600 PD', 'CIO NovaPort POWER 20000', 'Baseus Blade 20000'],
        'must': ['バッテリー','モバイル','Prime','Nexode','PowerCore','NovaPort'],
        'exclude': ['ケース','カバー','ケーブル'],
        'lead': '「MacBookも充電したい」「旅行3泊以上でコンセントを使わずに過ごしたい」という方向けの大容量モデルを比較します。',
        'problem': ['出張先でMacBookのバッテリーが切れた','旅行中にホテルのコンセントが少なくて困った','65W以上のPD出力対応モデルがわからない','重すぎて持ち歩きたくない'],
        'conclusion': 'ノートPC充電最強 → Anker Prime（200W）｜旅行・大容量 → UGREEN Nexode 25000（100W）｜コスパ → Anker 25600 PD',
        'decision': 'MacBook Airには65W以上・MacBook Pro 14には96W以上・16インチには140W以上のPD出力が必要',
        'personas': [('💻','MacBookユーザー','外出先でもMacBookをフル充電したい'),('✈️','出張・旅行3泊以上','ホテルのコンセントを使わずに3日過ごしたい'),('📱','複数デバイス持ち','スマホ・タブレット・ノートPCを同時充電したい'),('🏕️','アウトドア好き','キャンプや登山で複数デバイスを充電したい')],
        'criteria': [('必要なW数をノートPCで確認する','MacBook Air（M2）は67W、MacBook Pro 14インチは96W、16インチは140Wが目安。不足すると充電されないことも。'),('容量と重さのバランスを考える','20000〜25000mAhは350〜480gが目安。旅行専用と割り切るなら重さより容量を優先してください。'),('飛行機持ち込みはWhで確認する','2026年4月24日以降、機内での充電・給電は禁止。持ち込みは2個まで・160Wh以下・手元保管が条件。')],
        'faq': [('MacBook Airを充電するには何W必要ですか？','MacBook Air（M2）には65W以上のPD出力対応モデルが必要です。'),('スマホを何回充電できますか？','20000mAhならiPhone換算で約5回。変換効率を考慮すると実際は4回程度です。'),('旅行3泊4日に何mAhあれば足りますか？','スマホ＋タブレットなら20000mAhで十分。ノートPCも使うなら25000mAhが安心です。'),('複数ポートで同時充電すると出力は下がりますか？','下がります。重要なデバイスを1ポートで充電するか、同時使用時の出力仕様を事前に確認しましょう。'),('飛行機に2個持ち込めますか？','2026年4月24日以降のルールで2個まで可（160Wh以下、手元保管）。ただし機内での使用は禁止です。')],
    },
    {
        'title': 'GaN充電器でデスクをスッキリ整理',
        'cat': 'モバイル',
        'kw_short': 'GaN充電器 おすすめ MacBook',
        'keywords': ['Anker 735 GaN 充電器 65W', 'CIO NovaPort QUAD GaN 充電器', 'Anker 747 GaN 充電器 150W', 'Belkin BoostCharge Pro GaN 充電器', 'Anker Nano 3 GaN 30W'],
        'must': ['充電器','GaN','Charger','NovaPort','BoostCharge'],
        'exclude': ['ケーブル','カバー','アダプタ','延長'],
        'lead': 'MacBook・iPhone・iPadをひとつの充電器でまとめたい方向けに、GaN充電器の選び方を正直に解説します。',
        'problem': ['コンセントが足りなくてタコ足になっている','アダプタが大きくてデスクがごちゃごちゃ','MacBookとスマホを同時充電したい','旅行に充電器を何個も持っていくのが面倒'],
        'conclusion': 'MacBookメイン → Anker 735 65W GaN｜複数デバイス同時 → Anker 747 150W｜コスパ → CIO NovaPort',
        'decision': '何を充電するかで選ぶW数が決まる。MacBook Air=65W、MacBook Pro 16=140W、スマホのみ=30W',
        'personas': [('💻','MacBook Airユーザー','1つの充電器でMacとiPhoneを同時充電'),('🖥️','MacBook Pro 16ユーザー','高出力でMacを急速充電'),('📱','スマホ・タブレットのみ','小さい・軽い・旅行に最適'),('🧳','海外旅行が多い','100-240V対応・変圧器不要')],
        'criteria': [('必要なW数は「最大消費電力の機器」で決まる','MacBook Air 15インチは70W、iPhone急速充電は25W。同時使用するなら合計W数を計算しましょう。'),('複数ポートで同時充電すると出力が下がる','仕様書の「同時使用時出力」を確認しましょう。'),('海外対応（100-240V）かどうかを確認','対応モデルなら変圧器不要で世界中で使えます。')],
        'faq': [('GaN充電器とは何ですか？','ガリウムナイトライドという素材を使った充電器。従来より小型・軽量で発熱が少ないのが特徴です。'),('MacBook Proの充電に使えますか？','MacBook Pro 14インチは65W以上、16インチは140W以上を推奨します。'),('熱くなりませんか？','GaN採用により発熱が少ないのが特徴。ただし高負荷時はある程度温かくなります。'),('海外旅行でも使えますか？','100〜240V対応モデルなら変圧器不要で世界中で使えます。プラグ形状のみ要確認。'),('従来の充電器と何が違いますか？','同じ出力でも30〜50%小さく・軽くなります。旅行のカバンに入れても全然邪魔になりません。')],
    },

    # ===== ゲーミング系 (4テーマ) =====
    {
        'title': 'FPS向け軽量ゲーミングマウス選び方',
        'cat': 'ゲーミング',
        'kw_short': 'ゲーミングマウス 軽量 FPS',
        'keywords': ['Logicool G Pro X Superlight 2 マウス', 'Razer Viper V3 HyperSpeed', 'Logicool G304 マウス', 'Finalmouse Starlight-12', 'SteelSeries Aerox 3 マウス'],
        'must': ['マウス','Mouse','Superlight','Viper','Aerox'],
        'exclude': ['パッド','グリップ','交換','ソール','マウスソール','マウスパッド'],
        'lead': 'マウスを変えてエイムが改善した、というのは本当です。FPSで上位を目指すための軽量マウス選び方を解説します。',
        'problem': ['重いマウスで長時間プレイすると腕が疲れる','クリック感が悪い','有線と無線どっちがいいかわからない','センサー精度って何が違うの？'],
        'conclusion': 'プロ御用達 → Logicool G Pro X Superlight 2｜コスパ → Logicool G304｜有線最軽量 → Razer Viper V3',
        'decision': '60g以下・高精度センサー・持ち方に合った形状の3点で選ぶ',
        'personas': [('🎯','FPS上位ランク目指す','エイム精度を上げたい・軽量マウスを試したい'),('💰','入門・コスパ重視','5000円台で本格的なゲーミングマウスを使いたい'),('📡','無線派','ケーブルの抵抗なしで自由に動きたい'),('✋','かぶせ持ち','大型・重めが合っている持ち方')],
        'criteria': [('60g以下が軽量の目安','プロゲーマーの多くは55〜70gを使用。長時間プレイで腕が疲れる方は60g以下を選んでください。'),('センサーより持ち方との相性が重要','HERO・FOCUS Proなど上位センサーなら精度差は僅か。グリップスタイルに合った形状を優先しましょう。'),('有線と無線の差はほぼない','最新無線（LogicoolのLIGHTSPEED等）は遅延がほぼゼロ。ケーブルの取り回しが気になるなら無線を選んで問題なし。')],
        'faq': [('軽量マウスは何グラム以下がいいですか？','60g以下が軽量の目安。プロゲーマーの多くは55〜70gのモデルを使用しています。'),('有線と無線どちらがいいですか？','最新の無線技術は遅延がほぼゼロで実用上の差はありません。ケーブルの取り回しが気になる方は無線を選んでください。'),('DPIはいくつに設定すればいいですか？','FPSは400〜1600DPIが一般的。ゲームと画面サイズに合わせて調整しましょう。'),('グリップスタイルで選び方は変わりますか？','かぶせ持ちは大型・重め、つかみ・つまみ持ちは小型・軽量が向いています。'),('マウスパッドも一緒に変えた方がいいですか？','ゲーミングマウスパッドと組み合わせることでセンサーの性能を最大限発揮できます。')],
    },
    {
        'title': 'ゲーミングヘッドセット完全比較',
        'cat': 'ゲーミング',
        'kw_short': 'ゲーミングヘッドセット おすすめ FPS',
        'keywords': ['SteelSeries Arctis Nova Pro ヘッドセット 本体', 'HyperX Cloud III ゲーミングヘッドセット 本体', 'Logicool G733 ゲーミングヘッドセット 本体', 'Razer BlackShark V2 ゲーミングヘッドセット 本体', 'Corsair HS65 ゲーミングヘッドセット 本体'],
        'must': ['ヘッドセット'],
        'exclude': ['イヤーパッド','クッション','交換','補修','ケーブル','パーツ','ソール'],
        'lead': '敵の足音が聞こえるかどうかはヘッドセット次第です。FPS・RPG用途別に正直なレビューをお届けします。',
        'problem': ['敵の足音の方向が全然わからない','ボイチャで声が聞き取りにくいと言われる','長時間プレイで頭が痛くなる','有線と無線どっちにすればいいかわからない'],
        'conclusion': 'FPS足音把握 → SteelSeries Arctis Nova Pro｜マイク音質 → HyperX Cloud III｜コスパ → Corsair HS65',
        'decision': 'サラウンド対応・マイク品質・重量（300g以下）の3点で選ぶ',
        'personas': [('🎯','FPS・TPS重視','敵の足音・銃声の方向を正確に聞き取りたい'),('🎙️','ボイチャ重視','声が鮮明に届くマイク品質が最重要'),('💰','コスパ重視・入門','初めてゲーミングヘッドセットを買う'),('📡','無線でスッキリ','ケーブルなしで自由に動きたい')],
        'criteria': [('7.1chサラウンドの必要性を考える','FPSなら足音の方向把握に有効。ただしステレオでも高品質なモデルなら十分。'),('マイクのNC性能を確認する','安いモデルはマイクが弱く、ゲーム音を拾います。SteelSeriesとHyperXはマイク品質が特に高評価。'),('重量は300g以下を選ぶ','300g超えると長時間プレイで首が疲れます。')],
        'faq': [('ゲーミングヘッドセットと普通のヘッドホンの違いは？','マイク内蔵・サラウンド対応・ゲーム向けチューニングが主な違いです。'),('PS5やSwitchでも使えますか？','3.5mmジャック・USB接続対応モデルならほとんどのゲーム機で使用可。'),('有線と無線どちらがいいですか？','遅延を極限まで減らしたいなら有線。最新の無線モデルは遅延がほぼなく実用上の差はありません。'),('長時間プレイで頭が痛くなります','ヘッドバンドの締め付け調整と柔らかいイヤーパッドのモデルを選んでください。'),('マイクがPC・PS5に対応しているか確認方法は？','接続方式（USB/3.5mm）を確認。PS5はUSBとBluetoothに対応しています。')],
    },

    # ===== テレワーク・PC周辺機器系 (5テーマ) =====
    {
        'title': 'テレワーク・在宅ワーク向けガジェット',
        'cat': 'PC周辺機器',
        'kw_short': 'テレワーク ガジェット おすすめ',
        'keywords': ['Logicool C920s ウェブカメラ', 'Blue Yeti Nano USB マイク', 'Anker 552 USBハブ Type-C', 'Anker 735 GaN 充電器 65W', 'Logicool MX Keys キーボード'],
        'must': ['カメラ','ハブ','マイク','充電器','キーボード','C920','Yeti','GaN','MX'],
        'exclude': ['ケーブル','交換','パーツ','カバー','延長'],
        'lead': '在宅ワーク歴4年が「本当に買って良かった」と思うガジェットを正直に紹介します。',
        'problem': ['Web会議でカメラの画質が悪くて映りが気になる','MacBookのポートが足りなくてドングルだらけ','デスクのケーブルが多すぎてぐちゃぐちゃ','マイクの音質が悪くて会議中に聞き返される'],
        'conclusion': 'Web会議の映り → Logicool C920s｜マイク音質 → Blue Yeti Nano｜ポート不足 → Anker USBハブ',
        'decision': '在宅ワーク環境は「マイク→カメラ→ハブ」の順番で投資すると費用対効果が高い',
        'personas': [('📹','Web会議が多いビジネスマン','カメラの映りを改善して印象を良くしたい'),('💻','MacBookユーザー','ポート不足を解消してすっきりしたデスクにしたい'),('🎙️','配信・ポッドキャスト','マイクの音質をプロレベルに上げたい'),('⚡','ガジェット好き','充電器1つで全デバイスをまとめたい')],
        'criteria': [('カメラは最低フルHD（1080p）を選ぶ','720pのカメラはWeb会議でぼやけて見えます。1080p以上なら顔の表情まで鮮明に映ります。'),('USBハブはPD対応・ポート数で選ぶ','MacBook充電しながら他のデバイスも使うには「PD対応」が必須。HDMIポートも必要かどうか確認しましょう。'),('マイクはコンデンサー型を選ぶ','イヤホン付属マイクより圧倒的に音がクリア。Web会議・配信・録音すべてで効果を実感できます。')],
        'faq': [('ウェブカメラはどれくらいの価格から良くなりますか？','5000円台のLogicool C270でも改善を感じられます。1万円台のC920sなら顔の表情まで鮮明に映ります。'),('USBハブは何を基準に選べばいいですか？','HDMI出力・PD充電対応・ポート数の3点。Ankerの7-in-1か11-in-1が最もバランスが良いです。'),('マイクとウェブカメラ、先に買うならどちら？','マイクを先に買ってください。音声品質の方が映像より相手への印象に直結します。'),('GaN充電器に変えると何が変わりますか？','同じ出力でも30〜50%小さく軽くなります。デスクがすっきりして旅行のカバンにも楽に入ります。'),('ノートPCスタンドは本当に必要ですか？','Web会議が多い方には必須です。PCを目線の高さに上げるだけでカメラアングルが改善し印象が変わります。')],
    },
    {
        'title': 'ウェブカメラおすすめ比較',
        'cat': 'PC周辺機器',
        'kw_short': 'ウェブカメラ おすすめ テレワーク',
        'keywords': ['Logicool C920s ウェブカメラ', 'Logicool C270n ウェブカメラ', 'Logicool BRIO 500 ウェブカメラ', 'Anker PowerConf C302 ウェブカメラ', 'Razer Kiyo Pro ウェブカメラ'],
        'must': ['カメラ','ウェブカメラ','C920','C270','BRIO','Kiyo','PowerConf'],
        'exclude': ['ライト','スタンド','ケーブル','交換','カバー'],
        'lead': '「内蔵カメラが暗い・画質が悪い」というWeb会議の悩みは、ウェブカメラを変えるだけで解決します。',
        'problem': ['Web会議でカメラが暗くて映りが悪い','内蔵カメラだと顔が見えにくいと言われる','Zoomで画面がぼやけて見える','高品質なウェブカメラが高そうで踏み出せない'],
        'conclusion': 'バランス最強 → Logicool C920s（1万円台）｜コスパ入門 → Logicool C270n（3000円台）｜4K本格派 → Logicool BRIO 500',
        'decision': '1080p以上・自動露出補正・AIフレーミングの3点で選ぶ。まずC920sを試せば間違いない',
        'personas': [('💼','Web会議が1日3回以上','映りを改善して仕事の印象を良くしたい'),('📸','配信・YouTube','4K対応・AIフレーミングで本格配信したい'),('💰','コスパ重視','5000円以下で内蔵カメラより改善したい'),('🌙','暗い部屋での作業が多い','低照度でもきれいに映る自動露出補正が必要')],
        'criteria': [('最低フルHD（1080p）を選ぶ','720pの製品はWeb会議でぼやけて見えます。1080p以上が最低限のラインです。'),('自動露出補正・HDR機能を確認する','部屋が暗い・逆光環境でも顔が明るく映るHDR機能付きを選ぶと環境に左右されません。'),('AIオートフレーミングは便利だが必須ではない','話している間に自動で追跡する機能。配信・プレゼンでは便利ですが、通常の会議では不要です。')],
        'faq': [('ウェブカメラとノートPCの内蔵カメラは何が違いますか？','画角・解像度・低照度性能が大きく異なります。内蔵カメラは720p以下のモデルが多く、暗い部屋ではノイズが目立ちます。'),('MacとWindowsどちらでも使えますか？','USB接続のウェブカメラはドライバー不要でMac・Windowsどちらでも使えます。'),('Zoom・Teams・Meetで設定が必要ですか？','アプリの映像設定でウェブカメラを選択するだけです。追加のドライバーは通常不要。'),('三脚に取り付けられますか？','多くのウェブカメラは三脚穴（1/4インチ）が付いており、三脚やモニターアームに取り付けられます。'),('画角は何度がいいですか？','Web会議は70〜80度が顔がきれいに映る範囲。広角（90度以上）は背景が映りすぎる場合があります。')],
    },
    {
        'title': 'USBマイクおすすめ比較【配信・テレワーク向け】',
        'cat': 'PC周辺機器',
        'kw_short': 'USBマイク おすすめ 配信',
        'keywords': ['Blue Yeti Nano USB マイク', 'Anker PowerConf M300 マイク', 'Blue Yeti X USB マイク', 'HyperX QuadCast マイク', 'RODE NT-USB Mini マイク'],
        'must': ['マイク','Yeti','QuadCast','PowerConf','RODE','NT-USB'],
        'exclude': ['ケーブル','スタンド','ポップガード','交換','ケース'],
        'lead': 'イヤホン付属マイクとUSBマイクの差は歴然。Web会議の印象を変えたい・配信を始めたいなら最初の投資はマイクです。',
        'problem': ['Web会議で「声が聞き取りにくい」と言われる','配信を始めたいがマイクの選び方がわからない','ゲームの音や部屋の騒音が会議に入る','イヤホンマイクから卒業したい'],
        'conclusion': 'テレワーク入門 → Anker PowerConf M300｜コスパバランス → Blue Yeti Nano｜本格配信 → Blue Yeti X',
        'decision': 'まずコンデンサー型・単一指向性・ノイズキャンセリング付きの3点を満たすモデルを選ぶ',
        'personas': [('💼','テレワーク・Web会議重視','声のクリアさを改善して会議の印象を変えたい'),('🎮','ゲーム配信・YouTube','配信音質をプロレベルに上げたい'),('🎙️','ポッドキャスト','クリアな音声でコンテンツを録音したい'),('💰','コスパ重視','5000円以内でイヤホンマイクから卒業したい')],
        'criteria': [('コンデンサー型を選ぶ','ダイナミック型より感度が高く、クリアな音声を収録できます。テレワーク・配信どちらにもコンデンサー型がおすすめ。'),('単一指向性（カーディオイド）を選ぶ','正面の声だけを拾い、周囲の雑音を抑えます。会議・配信用なら単一指向性が最適。'),('ノイズキャンセリング機能を確認する','キーボード音・エアコン音・生活音を自動でカット。在宅ワークの環境に大きく貢献します。')],
        'faq': [('USBマイクとコンデンサーマイクの違いは何ですか？','コンデンサーマイクはマイクの種類（感度が高い）、USBマイクは接続方式（PCに直接挿せる）です。USB接続のコンデンサーマイクが最もポピュラーです。'),('ノートPC内蔵マイクと何が違いますか？','感度・指向性・ノイズキャンセリング性能が格段に上がります。Web会議で「声がクリアになった」と言われるようになります。'),('スタンドは別途買う必要がありますか？','多くのUSBマイクにはスタンドが付属しています。マイクアームで口元に近づけるとさらに音質が向上します。'),('Macでも使えますか？','USB接続なのでドライバー不要でMac・Windows・iPadどちらでも使えます。'),('配信用とWeb会議用で選び方は違いますか？','配信は音質重視でBlue Yeti X・RODE NT-USB Miniを。テレワークはコスパと使いやすさ重視でAnker PowerConf M300・Blue Yeti Nanoをおすすめします。')],
    },

    # ===== スマートホーム系 (3テーマ) =====
    {
        'title': 'マッピングロボット掃除機比較',
        'cat': 'スマートホーム',
        'kw_short': 'ロボット掃除機 おすすめ マッピング',
        'keywords': ['iRobot Roomba j7 ロボット掃除機', 'Ecovacs DEEBOT T20 ロボット掃除機', 'Roborock S7 ロボット掃除機', 'Panasonic ロボット掃除機 本体', 'SwitchBot ロボット掃除機 本体'],
        'must': ['ロボット','掃除機','Roomba','DEEBOT','Roborock'],
        'exclude': ['フィルター','ブラシ','交換','バッテリー','部品','パーツ','消耗品'],
        'lead': '「帰宅したら部屋がきれいになっている」という生活を実現した。ロボット掃除機歴3年の正直レビューです。',
        'problem': ['共働きで帰宅後に掃除する体力も時間もない','ペットの毛が毎日気になる','ロボット掃除機って本当に使えるのか半信半疑','間取りが複雑でちゃんと掃除できるか不安'],
        'conclusion': 'ペット毛 → iRobot Roomba j7｜水拭き同時 → Roborock S7｜コスパ → Ecovacs DEEBOT',
        'decision': 'マッピング機能・水拭き対応・ペット毛対応の3点で用途に合わせて選ぶ',
        'personas': [('🐱','ペット（犬・猫）がいる家庭','ペットの毛を毎日自動で掃除したい'),('🏠','水拭きもしたい','掃除機がけと床拭きを同時にやってほしい'),('💰','初めてのロボット掃除機','3万円台から試してみたい'),('👶','子どもがいる家庭','細かいゴミ・食べこぼしを毎日自動で')],
        'criteria': [('マッピング機能：間取りが複雑なら必須','間取りをスキャンして最短ルートで掃除。複数部屋がある家庭には必須機能です。'),('ゴミ自動収集：週1の掃除が月1になる','ダストステーションがあれば本体のゴミ捨ては月1回程度でOK。'),('ペット毛対応：ブラシの種類を確認','ゴム製ブラシはペットの毛が絡まりにくい設計。毛が多い家庭はiRobot Roomba j7+一択。')],
        'faq': [('部屋が散らかっていても使えますか？','ケーブルや小さなおもちゃは事前に片付けが必要。それ以外は自動で避けながら掃除してくれます。'),('うるさいですか？','50〜65dBが目安。外出中に動かすのが理想です。'),('ペットの毛は吸えますか？','iRobot Roomba j7はペット毛に特化した設計。ゴム製ブラシで絡まりを防いでいます。'),('Wi-FiやアプリなしでもOKですか？','アプリなしでもボタン1つで動きます。ただしスケジュール設定にはアプリが必要です。'),('水拭き対応モデルはどれがいいですか？','Roborock S7シリーズは吸引＋水拭きを同時に行い、カーペットを自動で避ける機能も搭載。')],
    },
    {
        'title': '賃貸でもできるスマートホーム入門',
        'cat': 'スマートホーム',
        'kw_short': 'スマートホーム 賃貸 SwitchBot',
        'keywords': ['SwitchBot Lock スマートロック 本体', 'Philips Hue スターターキット', 'SwitchBot Hub Mini 本体', 'Amazon Echo Dot 本体', 'SwitchBot カーテン 本体'],
        'must': ['スマートロック','Lock','Hue','Hub','Echo','カーテン'],
        'exclude': ['交換','部品','キー','スペア','ケーブル','アダプタ'],
        'lead': '賃貸・工事不要で始められるスマートホーム。月3000円からできる生活の自動化を紹介します。',
        'problem': ['鍵を閉めたか不安で引き返したことがある','帰宅したときに部屋が真っ暗で電気をつけるのが面倒','賃貸なので工事できずスマートホームを諦めていた','何から始めればいいかわからない'],
        'conclusion': '最初に買うなら → SwitchBot Hub Mini（全デバイスの司令塔）｜鍵の閉め忘れ対策 → SwitchBot Lock',
        'decision': 'スマートホームは「SwitchBot Hub Mini」から始めるのが最短ルート。工事不要・賃貸OK',
        'personas': [('🔑','鍵の閉め忘れが不安','外出先からスマホで鍵の確認・施錠がしたい'),('💡','帰宅時の電気が面倒','玄関を開けたら自動で電気がつくようにしたい'),('🎙️','声で家電を操作したい','Amazon EchoでエアコンやTVを音声操作'),('🌅','毎朝カーテンを自動で開けたい','起床時間に合わせてカーテンが自動開閉')],
        'criteria': [('まずSwitchBot Hub Miniを買う','すべてのSwitchBot製品をWi-Fi経由でスマホから操作できるようになる「司令塔」。これがないと外出先からの操作ができません。'),('賃貸対応：取り付け工事が不要かを確認','SwitchBot製品は両面テープ・挟み込みが基本。退去時も原状回復できます。'),('Amazon Echo（Alexa）との連携を検討する','SwitchBotとAlexaを連携させると「アレクサ、電気消して」の音声操作が実現します。')],
        'faq': [('賃貸に取り付けても問題ありませんか？','両面テープで取り付けるため原状回復が可能。退去時に取り外しできます。'),('Wi-Fiがなくても動きますか？','Bluetooth接続ならWi-Fiなしでも動作可。ただし外出先からの遠隔操作にはHub Miniが必要です。'),('スマートホームにするのに費用はいくらかかりますか？','SwitchBot Lockのみなら約1万円から。Hub Mini込みでも2万円以下でスタートできます。'),('停電したらスマートロックはどうなりますか？','バッテリー式なので停電に影響されません。ただしバッテリー切れには注意が必要です。'),('iPhoneとAndroid両方に対応していますか？','SwitchBot・Philips Hue・Amazon EchoはいずれもiOSとAndroid両方に対応しています。')],
    },

    # ===== カメラ系 (2テーマ) =====
    {
        'title': '4Kアクションカメラ完全比較',
        'cat': 'カメラ',
        'kw_short': 'アクションカメラ おすすめ GoPro',
        'keywords': ['GoPro HERO 12 Black 本体', 'DJI Osmo Action 4 本体', 'Insta360 ONE RS 本体', 'Sony FDR-X3000 アクションカメラ', 'DJI Pocket 3 本体'],
        'must': ['カメラ','Camera','GoPro','Action','Pocket','Insta360','FDR'],
        'exclude': ['ケース','マウント','バッテリー','充電','交換','アクセサリー','ハウジング','保護'],
        'lead': 'スマホカメラでは撮れない映像をGoPro・DJIで撮った経験をもとに、正直比較します。',
        'problem': ['スマホで撮ると手ブレがひどくて見ていられない','GoProとDJIどっちがいいかわからない','旅行動画をSNSに上げたいが素人っぽく見える','水中で撮影したい'],
        'conclusion': '防水・過酷環境 → GoPro HERO 12｜旅行・Vlog → DJI Osmo Action 4｜360度撮影 → Insta360',
        'decision': '水中・アウトドアの過酷環境ならGoPro、旅行・日常のVlogならDJIが向いている',
        'personas': [('🏄','サーフィン・ダイビング','水中で使える・落としても壊れない'),('🌍','旅行・海外Vlog','きれいな映像で思い出を残したい'),('🚴','サイクリング・バイク','ヘルメット装着・手ブレなし・長時間録画'),('🎿','スキー・スノボ','寒冷地でも動く・防水・広角')],
        'criteria': [('GoProかDJIかの選び方','水中・超過酷環境ならGoPro（10m防水単体）、旅行・Vlogの映像美ならDJI。迷ったら用途を先に決めてください。'),('手ブレ補正は全モデル必須','最新モデルはほぼすべて電子式手ブレ補正搭載。ただしDJIのRockSteady補正はGoPro比でも滑らかです。'),('バッテリーと保護ケースは初日に買う','アクションカメラの本体バッテリーは60〜90分。予備バッテリー2本・専用ケースはセットで揃えましょう。')],
        'faq': [('GoProとDJIどちらを選べばいいですか？','水中・アウトドアの過酷環境ならGoPro、旅行・Vlog中心ならDJI Osmo Actionがおすすめです。'),('スマホのカメラとどう違いますか？','手ブレ補正・超広角・耐衝撃・防水が最大の違いです。'),('4Kで撮影するとデータはどれくらい？','4K60fpsで1時間あたり約30GB。大容量のmicroSDカード（128GB以上）を準備しましょう。'),('初心者でも使いこなせますか？','最近のモデルは自動設定が優秀。電源ONで録画ボタンを押すだけで高品質な映像が撮れます。'),('寒い場所でも使えますか？','GoProとDJIは-10〜-20℃でも動作しますが、バッテリー持ちが大幅に落ちます。予備バッテリー必須です。')],
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

# ===== 記事HTML生成（理想の記事構成：悩み→結論→用途別→比較表→レビュー→FAQ→CTA） =====
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
    kw_short = theme_obj.get('kw_short', theme)
    today    = datetime.now().strftime('%Y年%m月%d日')
    year     = datetime.now().year

    num_class = ['gold','silver','bronze','normal','normal']
    rank_label= ['1位','2位','3位','4位','5位']

    # ===== ① TOP3クイック選択 =====
    top3_html = ''
    for i, item in enumerate(products[:3]):
        p     = item.get('Item',{})
        name  = p.get('itemName','')[:32]
        price = p.get('itemPrice',0)
        url   = p.get('affiliateUrl', p.get('itemUrl','#'))
        amz   = f"https://www.amazon.co.jp/s?k={requests.utils.quote(name[:25])}"
        yah   = f"https://shopping.yahoo.co.jp/search?p={requests.utils.quote(name[:25])}"
        labels= ['🏆 総合No.1','💰 コスパNo.1','🎯 用途別No.1']
        borders=['border:2px solid #e63900;background:#fff9f7','border:2px solid #333','border:2px solid #666']
        top3_html += f'''
<div style="{borders[i]};border-radius:8px;padding:14px">
  <div style="font-size:10px;font-weight:700;color:#e63900;margin-bottom:4px">{labels[i]}</div>
  <div style="font-size:13px;font-weight:900;margin-bottom:8px;line-height:1.3">{name}...</div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:5px">
    <a href="{url}" target="_blank" rel="noopener sponsored" style="display:block;background:#e63900;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:6px 2px;border-radius:4px">🛍️楽天</a>
    <a href="{amz}" target="_blank" rel="noopener" style="display:block;background:#FF9900;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:6px 2px;border-radius:4px">🛒Amazon</a>
    <a href="{yah}" target="_blank" rel="noopener" style="display:block;background:#FF0033;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:6px 2px;border-radius:4px">🟡Yahoo!</a>
  </div>
</div>'''

    # ===== ② 悩みリスト =====
    problem_li = ''.join(f'<li>{p}</li>' for p in problems)

    # ===== ③ 用途別ペルソナ =====
    persona_html = ''
    for emoji, label, desc, rec in personas:
        persona_html += f'''
<div style="border:1px solid #e8e8e8;border-radius:8px;padding:12px;text-align:center">
  <div style="font-size:22px;margin-bottom:5px">{emoji}</div>
  <div style="font-weight:700;font-size:12px;margin-bottom:3px">{label}</div>
  <div style="font-size:11px;color:#666;margin-bottom:6px;line-height:1.45">{desc}</div>
  <div style="font-size:11px;font-weight:700;color:#e63900">→ {rec}</div>
</div>'''

    # ===== ④ 選び方 =====
    criteria_html = ''
    for i, (ctitle, cdesc) in enumerate(criteria):
        icon = ['①','②','③','④','⑤'][i]
        criteria_html += f'''
<h3 style="font-size:15px;font-weight:700;margin:18px 0 8px;padding-left:12px;border-left:4px solid #111">{icon} {ctitle}</h3>
<p style="font-size:14px;color:#333;line-height:1.9;margin-bottom:4px">{cdesc}</p>'''

    # ===== ⑤ 比較表 =====
    table_rows = ''
    for i, item in enumerate(products[:5]):
        p     = item.get('Item',{})
        name  = p.get('itemName','')[:28]
        price = p.get('itemPrice',0)
        ra    = float(p.get('reviewAverage',0))
        rc    = int(p.get('reviewCount',0))
        url   = p.get('affiliateUrl', p.get('itemUrl','#'))
        amz   = f"https://www.amazon.co.jp/s?k={requests.utils.quote(name[:22])}"
        si    = int(ra); stars = '★'*si+'☆'*(5-si)
        best  = ' style="color:#e63900;font-weight:700"' if i==0 else ''
        table_rows += f'''<tr>
<td><strong>{name}</strong></td>
<td{best}>¥{price:,}</td>
<td>{stars} {ra:.1f}</td>
<td><a href="https://review.rakuten.co.jp/search/?k={requests.utils.quote(name[:20])}" target="_blank" rel="noopener" style="color:#e63900">{rc:,}件</a></td>
<td>
  <a href="{url}" target="_blank" rel="noopener sponsored" style="display:block;background:#e63900;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:4px 6px;border-radius:3px;margin-bottom:3px">楽天</a>
  <a href="{amz}" target="_blank" rel="noopener" style="display:block;background:#FF9900;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:4px 6px;border-radius:3px">Amazon</a>
</td></tr>'''

    # ===== ⑥ 詳細レビューカード =====
    cards_html = ''
    exp_cats = {
        'イヤホン': ['を1ヶ月使い続けた結果、通勤中の集中力が上がりました。','を試した中で、装着感と音質のバランスが最も優れています。','を使い始めてから、Web会議での「聞き返し」がなくなりました。','の最大の強みは、同価格帯の競合と比べた際の音質の差です。','を選んだ理由は用途との相性の良さ。値段以上の満足感があります。'],
        'スマートウォッチ': ['を3ヶ月使って気づいたこと：睡眠データが改善のヒントになっています。','の健康管理機能は、体調の波を数値で把握したい人に刺さります。','を使い始めてから、自分の体調の変化が数値でわかるようになりました。','を選んだ理由：バッテリーが長持ちで充電を忘れることがなくなりました。'],
        'モバイル': ['は毎日のカバンの中に入れても重さを感じない軽量設計が決め手でした。','を導入してから、外出先でバッテリー残量を気にしなくなりました。','の最大の利点は急速充電。30分で大幅に回復します。'],
        'PC周辺機器': ['を導入してからWeb会議での映りが明らかに改善しました。','を使い始めてデスクのケーブルが減り、作業効率が上がりました。'],
        'ゲーミング': ['を使い始めてから、敵の足音の方向が聞き取れるようになりました。','に変えてからボイチャで「声がクリアになった」と言われました。'],
        'スマートホーム': ['を導入してから「鍵を閉めたか不安で引き返す」ことがゼロになりました。','で生活が自動化されて、毎朝の手間がなくなりました。'],
        'カメラ': ['を使ってから旅行動画のクオリティが別次元になりました。','は「スマホカメラで後悔した経験がある人」に特にすすめたいモデルです。'],
    }
    comments = exp_cats.get(cat, ['を実際に使ったレビューをお届けします。'])

    for i, item in enumerate(products[:5]):
        p         = item.get('Item',{})
        name      = p.get('itemName','')[:60]
        price     = p.get('itemPrice',0)
        shop      = p.get('shopName','')[:16]
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
        amz_url   = f"https://www.amazon.co.jp/s?k={requests.utils.quote(name[:25])}"
        yah_url   = f"https://shopping.yahoo.co.jp/search?p={requests.utils.quote(name[:25])}"
        si        = int(ra)
        stars_h   = f'<span style="color:#f5a623;font-size:16px">{"★"*si}{"☆"*(5-si)}</span>'
        bar_w     = int(ra/5*100)
        exp       = comments[i % len(comments)]
        img_html  = f'<img src="{img}" alt="{name}" loading="lazy" style="width:100%;max-height:180px;object-fit:contain">' if img else f'<div style="font-size:48px;text-align:center;opacity:.3">{["🎧","⌚","🔋","💻","🎮","📷"][i%6]}</div>'

        cards_html += f'''
<div class="rank-card">
  <div class="rank-header">
    <span class="rank-num {num_class[i]}">{i+1}</span>
    <span class="rank-label">{rank_label[i]}</span>
    <span class="rank-shop-name">{shop}</span>
  </div>
  <div style="display:grid;grid-template-columns:200px 1fr">
    <div style="background:#fafafa;border-right:1px solid #f0f0f0;display:flex;align-items:center;justify-content:center;padding:16px;min-height:200px">
      {img_html}
    </div>
    <div style="padding:16px 18px;display:flex;flex-direction:column;gap:10px">
      <div style="font-size:14px;font-weight:700;line-height:1.5;color:#111">{name}</div>
      <div style="font-size:13px;color:#555;line-height:1.8;background:#f8f8f8;border-left:3px solid #e63900;padding:10px 14px;border-radius:0 4px 4px 0">
        このモデル{exp}
      </div>
      <div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px">
          {stars_h}
          <strong style="font-size:18px;color:#111">{ra:.1f}</strong>
          <span style="font-size:13px;color:#aaa">/ 5.0</span>
          <a href="{rev_url}" target="_blank" rel="noopener" style="font-size:12px;color:#e63900">楽天口コミ{rc:,}件を読む →</a>
        </div>
        <div style="background:#f0f0f0;border-radius:4px;height:6px;width:160px">
          <div style="background:#f5a623;height:6px;border-radius:4px;width:{bar_w}%"></div>
        </div>
      </div>
      <div style="margin-top:auto;padding-top:10px;border-top:1px solid #f0f0f0">
        <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:10px;flex-wrap:wrap">
          <div style="font-size:26px;font-weight:900;color:#e63900">¥{price:,}</div>
          <small style="font-size:11px;color:#aaa">税込（楽天市場参照）※変動あり</small>
        </div>
        <a href="{url}" target="_blank" rel="noopener sponsored" class="btn-buy">🛍️ 楽天で今すぐ確認する →</a>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
          <a href="{amz_url}" target="_blank" rel="noopener" style="display:block;background:#FF9900;color:#fff;text-align:center;font-size:11px;font-weight:700;padding:7px;border-radius:4px">🛒 Amazonで見る</a>
          <a href="{yah_url}" target="_blank" rel="noopener" style="display:block;background:#FF0033;color:#fff;text-align:center;font-size:11px;font-weight:700;padding:7px;border-radius:4px">🟡 Yahoo!で見る</a>
        </div>
        <a href="{rev_url}" target="_blank" rel="noopener" class="btn-review" style="margin-top:6px">口コミ（{rc:,}件）を読んでから決める →</a>
      </div>
    </div>
  </div>
</div>'''

    # ===== ⑦ FAQ =====
    faq_html = ''
    if faq:
        faq_items = ''.join(f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>' for q,a in faq)
        faq_html  = f'<section id="faq"><h2 class="section-title">よくある質問（FAQ）</h2><div class="faq-wrap">{faq_items}</div></section>'

    faq_ld = ','.join(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}' for q,a in faq)

    # ===== ⑧ まとめ =====
    summary_top3 = ''
    for i, item in enumerate(products[:3]):
        p    = item.get('Item',{})
        name = p.get('itemName','')[:30]
        url  = p.get('affiliateUrl', p.get('itemUrl','#'))
        amz  = f"https://www.amazon.co.jp/s?k={requests.utils.quote(name[:22])}"
        icons= ['🏆','💰','🎯']
        summary_top3 += f'''
<div style="border:1px solid #e8e8e8;border-radius:8px;padding:14px">
  <div style="font-size:20px;margin-bottom:4px">{icons[i]}</div>
  <div style="font-size:12px;font-weight:900;margin-bottom:8px;line-height:1.4">{name}...</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px">
    <a href="{url}" target="_blank" rel="noopener sponsored" style="display:block;background:#e63900;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:6px;border-radius:4px">楽天で見る</a>
    <a href="{amz}" target="_blank" rel="noopener" style="display:block;background:#FF9900;color:#fff;text-align:center;font-size:10px;font-weight:700;padding:6px;border-radius:4px">Amazonで見る</a>
  </div>
</div>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>【{year}年】{theme}おすすめ5選｜用途別に徹底比較 | ガジェット天国</title>
<meta name="description" content="{year}年最新。{theme}を用途別に比較。{lead[:55]}楽天・Amazon・Yahoo!の3社比較リンク付き。">
<link rel="canonical" href="{SITE_URL}/">
<meta property="og:title" content="【{year}年】{theme}おすすめ5選｜用途別に徹底比較">
<meta property="og:type" content="article">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"【{year}年】{theme}おすすめ5選","datePublished":"{datetime.now().strftime('%Y-%m-%d')}","dateModified":"{datetime.now().strftime('%Y-%m-%d')}","author":{{"@type":"Organization","name":"ガジェット天国編集部","url":"{SITE_URL}/about.html"}},"publisher":{{"@type":"Organization","name":"ガジェット天国","url":"{SITE_URL}/"}}}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
<style>
.faq-item{{border-bottom:1px solid #f0f0f0;padding:14px 0}}
.faq-item:last-child{{border-bottom:none}}
.faq-q{{font-weight:700;color:#111;margin-bottom:6px;font-size:14px;display:flex;align-items:flex-start;gap:8px}}
.faq-q::before{{content:'Q';background:#e63900;color:#fff;font-size:10px;font-weight:900;padding:1px 6px;border-radius:3px;flex-shrink:0;margin-top:2px}}
.faq-a{{font-size:13px;color:#555;line-height:1.85;padding-left:26px}}
.faq-wrap{{background:#fafafa;border:1px solid #e8e8e8;border-radius:8px;padding:0 20px}}
@media(max-width:600px){{
  .rank-card>div:last-child{{grid-template-columns:1fr!important}}
  .rank-card>div:last-child>div:first-child{{border-right:none!important;border-bottom:1px solid #f0f0f0;min-height:140px}}
}}
</style>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="{SITE_URL}/" class="logo">Gadget<span>天国</span></a>
    <nav>
      <a href="{SITE_URL}/earphone.html">イヤホン</a>
      <a href="{SITE_URL}/smartwatch.html">スマートウォッチ</a>
      <a href="{SITE_URL}/battery.html">バッテリー</a>
      <a href="{SITE_URL}/gaming.html">ゲーミング</a>
      <a href="{SITE_URL}/telework.html">テレワーク</a>
      <a href="{SITE_URL}/archive.html">記事一覧</a>
    </nav>
  </div>
</header>

<div class="article-hero">
  <div class="article-hero-inner">
    <div class="article-cat">{cat}</div>
    <h1>【{year}年】{theme}おすすめ5選<br>用途別に徹底比較</h1>
    <div class="article-meta">
      <span>📅 {today} 更新</span>
      <span>⏱ 読了約6分</span>
      <span>✍️ 編集部調査</span>
    </div>
  </div>
</div>

<div class="container">

  <!-- ① 悩み共感 -->
  <div style="background:#fff8f0;border-left:4px solid #e63900;padding:14px 18px;margin-bottom:16px;border-radius:0 6px 6px 0">
    <div style="font-size:12px;color:#e63900;font-weight:700;margin-bottom:6px">こんな悩みはありませんか？</div>
    <ul style="font-size:14px;color:#333;line-height:2.2;padding-left:20px">{problem_li}</ul>
    <div style="font-size:14px;color:#111;font-weight:700;margin-top:8px">→ この記事を読めば15分で自分に合った1本が選べます。</div>
  </div>

  <!-- ② 結論（PREP） -->
  <div class="result-box">
    <div class="result-box-label">✅ 結論：迷ったらこの3択</div>
    <div class="result-box-text">{conc}</div>
  </div>

  <!-- ③ クイック選択 TOP3 -->
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:20px">
    {top3_html}
  </div>

  <div class="intro-box">{lead}</div>

  <!-- 価格変動注意 -->
  <div style="background:#fff8e7;border:1px solid #f5d78b;border-radius:6px;padding:10px 14px;margin-bottom:16px;font-size:12px;color:#7a5800">
    ⚠️ 掲載価格は{today}時点の楽天市場参照価格です。<strong>価格・在庫は変動します。購入前に必ず各サイトでご確認ください。</strong>
  </div>

  <nav class="toc">
    <div class="toc-title">この記事の目次</div>
    <ol>
      <li><a href="#persona">用途別診断</a></li>
      <li><a href="#howto">失敗しない選び方</a></li>
      <li><a href="#compare">スペック比較表</a></li>
      <li><a href="#ranking">詳細レビュー5選</a></li>
      <li><a href="#faq">よくある質問（FAQ）</a></li>
      <li><a href="#summary">まとめ・最終結論</a></li>
    </ol>
  </nav>

  <!-- ④ 用途別診断 -->
  <section id="persona">
    <h2 class="section-title">あなたに合うのはどれ？用途別診断</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin-bottom:24px">
      {persona_html}
    </div>
  </section>

  <!-- ⑤ 選び方 -->
  <section id="howto">
    <h2 class="section-title">失敗しない選び方｜{len(criteria)}つの基準だけ見ればいい</h2>
    <p style="font-size:14px;color:#333;line-height:1.9;margin-bottom:14px"><strong>{decision}</strong></p>
    {criteria_html}
  </section>

  <!-- ⑥ 比較表 -->
  <section id="compare">
    <h2 class="section-title">スペック比較表｜一気に比較</h2>
    <div style="overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid #e8e8e8;border-radius:6px">
      <table style="width:100%;border-collapse:collapse;font-size:13px;min-width:520px">
        <thead><tr style="background:#111;color:#fff">
          <th style="padding:10px 12px;text-align:left;font-size:12px">商品名</th>
          <th style="padding:10px 12px;text-align:center;font-size:12px">価格</th>
          <th style="padding:10px 12px;text-align:center;font-size:12px">評価</th>
          <th style="padding:10px 12px;text-align:center;font-size:12px">口コミ</th>
          <th style="padding:10px 12px;text-align:center;font-size:12px">購入</th>
        </tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
    <p style="font-size:11px;color:#aaa;margin-top:8px">※{today}時点の楽天市場参照価格。価格・在庫は変動します。</p>
  </section>

  <!-- ⑦ 詳細レビュー -->
  <section id="ranking">
    <h2 class="section-title">詳細レビュー5選｜選ぶ理由を正直に書く</h2>
    <p style="font-size:12px;color:#aaa;margin-bottom:14px">
      ※参照：<a href="https://www.rakuten.co.jp/" target="_blank" rel="noopener" style="color:#e63900">楽天市場</a>（{today}時点）。<strong style="color:#c00">価格・在庫は変動します。購入前に必ず各サイトでご確認ください。</strong>
    </p>
    {cards_html}
  </section>

  {faq_html}

  <!-- ⑧ おすすめしない人 -->
  <section style="margin-top:28px">
    <h2 class="section-title">こんな方にはおすすめしません</h2>
    <div style="background:#fff5f5;border:1px solid #ffcccc;border-radius:6px;padding:16px 20px;font-size:14px;line-height:2.1;color:#555">
      <ul style="padding-left:20px">
        <li>目的が「なんとなく」の方（用途を明確にしてから選んでください）</li>
        <li>最安値のみを重視して信頼ブランド以外から選ぶ方（安全性の観点からおすすめしません）</li>
        <li>口コミを確認せずに即決したい方（楽天・Amazonのレビューを必ず確認してください）</li>
        <li>予算を決めていない方（まず予算を決めてから選んでください）</li>
      </ul>
    </div>
  </section>

  <!-- ⑨ 最終CTA -->
  <section id="summary" style="margin-top:28px">
    <h2 class="section-title">まとめ・最終結論</h2>
    <div style="background:#111;color:#fff;border-radius:8px;padding:18px 20px;margin-bottom:20px">
      <div style="font-size:12px;color:#e63900;font-weight:700;margin-bottom:8px">✅ 用途別おすすめまとめ</div>
      <div style="font-size:14px;line-height:1.9">{conc}</div>
      <div style="font-size:13px;color:#aaa;margin-top:8px">迷ったら楽天市場の口コミを読んでから決めましょう。Amazon・Yahoo!ショッピングとの価格比較もおすすめです。</div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:20px">
      {summary_top3}
    </div>
  </section>

  <!-- ⑩ 運営者ボックス -->
  <div style="display:flex;align-items:flex-start;gap:14px;background:#fafafa;border:1px solid #e8e8e8;border-radius:8px;padding:16px 18px;margin-top:20px">
    <div style="width:44px;height:44px;background:#111;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">🎧</div>
    <div>
      <div style="font-size:13px;font-weight:700;margin-bottom:3px">ガジェット天国 編集部</div>
      <div style="font-size:12px;color:#666;line-height:1.7">公式スペック・楽天市場データ・編集部調査をもとに記事を作成しています。価格・スペックは変動します。購入前に必ず各サイトでご確認ください。</div>
      <a href="{SITE_URL}/about.html" style="font-size:12px;color:#e63900;font-weight:700;display:inline-block;margin-top:5px">運営者情報・検証方針を見る →</a>
    </div>
  </div>

  <!-- ⑪ 関連記事 -->
  <section style="margin-top:28px">
    <h2 class="section-title">この記事を読んだ方はこちらも読んでいます</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:12px">
      <a href="{SITE_URL}/earphone.html" style="display:block;border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;text-decoration:none;color:#111">
        <div style="height:70px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:28px">🎧</div>
        <div style="padding:8px 10px"><div style="font-size:10px;color:#e63900;font-weight:700;margin-bottom:3px">イヤホン</div><div style="font-size:11px;font-weight:700;line-height:1.4">ノイキャンイヤホンおすすめ5選</div></div>
      </a>
      <a href="{SITE_URL}/smartwatch.html" style="display:block;border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;text-decoration:none;color:#111">
        <div style="height:70px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:28px">⌚</div>
        <div style="padding:8px 10px"><div style="font-size:10px;color:#e63900;font-weight:700;margin-bottom:3px">スマートウォッチ</div><div style="font-size:11px;font-weight:700;line-height:1.4">Apple Watch vs Garmin 徹底比較</div></div>
      </a>
      <a href="{SITE_URL}/battery.html" style="display:block;border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;text-decoration:none;color:#111">
        <div style="height:70px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:28px">🔋</div>
        <div style="padding:8px 10px"><div style="font-size:10px;color:#e63900;font-weight:700;margin-bottom:3px">バッテリー</div><div style="font-size:11px;font-weight:700;line-height:1.4">モバイルバッテリーおすすめ5選</div></div>
      </a>
      <a href="{SITE_URL}/gaming.html" style="display:block;border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;text-decoration:none;color:#111">
        <div style="height:70px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:28px">🎮</div>
        <div style="padding:8px 10px"><div style="font-size:10px;color:#e63900;font-weight:700;margin-bottom:3px">ゲーミング</div><div style="font-size:11px;font-weight:700;line-height:1.4">ゲーミングデバイス完全ガイド</div></div>
      </a>
    </div>
  </section>

</div><!-- /container -->

<footer>
  <div class="footer-inner">
    <div class="footer-logo">Gadget<span>天国</span></div>
    <div class="footer-links">
      <a href="{SITE_URL}/">トップ</a>
      <a href="{SITE_URL}/earphone.html">イヤホン</a>
      <a href="{SITE_URL}/smartwatch.html">スマートウォッチ</a>
      <a href="{SITE_URL}/battery.html">バッテリー</a>
      <a href="{SITE_URL}/gaming.html">ゲーミング</a>
      <a href="{SITE_URL}/telework.html">テレワーク</a>
      <a href="{SITE_URL}/archive.html">記事一覧</a>
      <a href="{SITE_URL}/about.html">運営者情報</a>
      <a href="{SITE_URL}/privacy.html">プライバシーポリシー</a>
    </div>
  </div>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。掲載価格は{today}時点の楽天市場参照価格です。価格・在庫は変動します。購入前に必ず各サイトでご確認ください。</p>
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
        try: used = {a.get('theme_key','') for a in json.loads(content)[:60]}
        except: pass
    available = [t for t in ALL_THEMES if t['title'] not in used] or ALL_THEMES
    # AM枠：イヤホン・スマートウォッチ（検索ボリューム高）
    am_cats = ['イヤホン','スマートウォッチ']
    # PM枠：モバイル・ゲーミング・PC周辺機器・スマートホーム・カメラ
    pm_cats = ['モバイル','ゲーミング','PC周辺機器','スマートホーム','カメラ']
    target_cats = am_cats if SLOT=='am' else pm_cats
    pool = [t for t in available if t['cat'] in target_cats] or available
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
