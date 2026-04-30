#!/usr/bin/env python3
import os, re, requests, base64, json, random, time
from datetime import datetime

WORKER_URL           = 'https://rakuten-proxy.sobamoripaya.workers.dev'
GITHUB_TOKEN         = os.environ['GITHUB_TOKEN']
GITHUB_REPO          = 'gadget-tengoku/gadget-lab'
SITE_URL             = 'https://gadget-tengoku.com'
SLOT                 = os.environ.get('SLOT', 'am')

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
    'beats','soundcore','edifier','final','jvc','kenwood','pioneer',
    'パナソニック','シャープ','ソニー','アンカー','エレコム','バッファロー',
    'キヤノン','ニコン','富士フイルム','ダイソン','フィリップス','ケンウッド',
]

# ===== テーマ（SEO強化版：購入意図ワード・FAQ・CTA・ペルソナ付き） =====
ALL_THEMES = [
    {
        'kw':      'Sony WH-1000XM5 ワイヤレスイヤホン',
        'title':   '通勤向けノイキャンイヤホン',
        'cat':     'イヤホン',
        'must':    ['イヤホン','ヘッドホン'],
        'exclude': ['ケース','ポーチ','カバー','クッション','交換','イヤーパッド'],
        'persona': '毎日満員電車で通勤し、雑音をシャットアウトしたい30代ビジネスマン',
        'pain':    '電車の騒音でリモート会議の内容が聞き取れない、音楽に集中できない',
        'faq': [
            ('ノイキャンイヤホンは飛行機でも使えますか？', 'はい、飛行機のエンジン音に非常に効果的です。国際線での長時間フライトにも最適です。'),
            ('ワイヤレスイヤホンの音切れが心配です', '最新モデルはBluetooth 5.3を採用しており、10m以内なら安定した接続が可能です。'),
            ('長時間つけると耳が痛くなりませんか？', 'イヤーピースのサイズ選びが重要です。S/M/Lから自分の耳に合うサイズを選びましょう。'),
            ('iPhoneとAndroid、両方で使えますか？', 'はい、Bluetooth接続なのでOS問わず使用可能。ただし一部機能はメーカーアプリが必要です。'),
            ('防水性能は？雨の日も使えますか？', 'IPX4以上のモデルは小雨程度なら問題なし。ジョギング中の汗にも対応しています。'),
        ],
    },
    {
        'kw':      'Jabra Elite ワイヤレスイヤホン スポーツ',
        'title':   'スポーツ・ランニング向けワイヤレスイヤホン',
        'cat':     'イヤホン',
        'must':    ['イヤホン'],
        'exclude': ['ケース','ポーチ','カバー','交換'],
        'persona': '週3回ランニングする健康意識の高い30代。運動中に落ちない・汗に強いイヤホンを探している',
        'pain':    '走っているとイヤホンがずれる、汗で壊れた経験がある',
        'faq': [
            ('ランニング中にイヤホンが外れないか心配です', 'スポーツ向けモデルはイヤーフックやウイングチップで固定されます。試走してみることをおすすめします。'),
            ('IPX5とIPX7の違いは何ですか？', 'IPX5は防水、IPX7は水没OK。ランニング程度なら IPX5で十分です。'),
            ('バッテリーはどれくらいもちますか？', '本体のみで6〜8時間、ケース込みで24〜32時間が目安です。'),
            ('外音取り込み機能は必要ですか？', '交通量の多い道を走る方には必須です。車の音を聞きながら音楽を楽しめます。'),
            ('骨伝導イヤホンとどちらが向いていますか？', '音質重視ならインイヤー型、安全性・長時間装着ならShokzなどの骨伝導がおすすめです。'),
        ],
    },
    {
        'kw':      'Anker Soundcore Liberty ワイヤレスイヤホン',
        'title':   '1万円以下コスパ最強ワイヤレスイヤホン',
        'cat':     'イヤホン',
        'must':    ['イヤホン'],
        'exclude': ['ケース','ポーチ','カバー','交換'],
        'persona': '予算1万円以内でAirPodsの代わりを探している大学生・20代社会人',
        'pain':    'AirPodsは高すぎる。でも安いと音質が心配',
        'faq': [
            ('1万円以下でも音質は大丈夫ですか？', 'AnkerやEarFunなど信頼ブランドなら十分な音質を確保。ハイレゾ対応モデルも増えています。'),
            ('AirPodsと比べてどうですか？', '音質は同等以上のモデルも。Androidユーザーならむしろコスパ系の方が使いやすいです。'),
            ('ノイキャンはついていますか？', '1万円以下でもAnker Soundcoreなら搭載モデルあり。効果は高額機より劣りますが十分実用的です。'),
            ('楽天で買うのと家電量販店で買うのはどちらがお得ですか？', '楽天ポイント還元を考えると楽天が有利なケースが多いです。'),
            ('保証期間はどれくらいですか？', 'Ankerは18ヶ月保証。国内正規品を購入すれば安心です。'),
        ],
    },
    {
        'kw':      'Shokz OpenRun 骨伝導イヤホン',
        'title':   '骨伝導イヤホン完全ガイド',
        'cat':     'イヤホン',
        'must':    ['骨伝導','イヤホン','Shokz'],
        'exclude': ['ケース','カバー','交換'],
        'persona': '交通安全が気になるランナー・自転車通勤者。耳をふさがずに音楽を聴きたい',
        'pain':    '普通のイヤホンをしていると車の音が聞こえず危ない',
        'faq': [
            ('骨伝導イヤホンは普通のイヤホンより音が悪いですか？', '低音は劣りますが、クリアな中高音域は十分。通話品質は特に優秀です。'),
            ('耳穴に何も入らないので衛生的ですか？', 'はい、耳の穴を使わないので耳の蒸れや痛みがなく、長時間装着に向いています。'),
            ('メガネをしていても使えますか？', 'Shokzはメガネとの干渉が少ない設計。ただし一部モデルは調整が必要な場合があります。'),
            ('防水性能はありますか？', 'Shokz OpenRunはIP67防水で、雨天や汗も問題なし。水洗いもできます。'),
            ('テレワークのWeb会議でも使えますか？', 'マイク内蔵モデルなら通話品質も良好。ノイズキャンセリングマイク搭載モデルもあります。'),
        ],
    },
    {
        'kw':      'Sony WH-1000XM5 ノイキャン ヘッドホン',
        'title':   '在宅ワーク向けノイキャンヘッドホン',
        'cat':     'オーディオ',
        'must':    ['ヘッドホン'],
        'exclude': ['イヤーパッド','クッション','ケーブル','交換','補修'],
        'persona': '週4日在宅勤務のエンジニア。家族の騒音を遮断してWeb会議に集中したい',
        'pain':    '子どもの声や生活音でWeb会議に集中できない',
        'faq': [
            ('長時間つけていると疲れませんか？', '重量と側圧が重要。Sony WH-1000XM5は250gで長時間装着を想定した設計です。'),
            ('マイクの音質はどうですか？', 'ビームフォーミングマイク搭載で周囲のノイズを拾いにくく、Web会議で重宝します。'),
            ('折りたたんでカバンに入れられますか？', 'ほとんどの有線モデルは折りたたみ可能。専用ポーチも付属するモデルが多いです。'),
            ('有線と無線どちらがいいですか？', '在宅なら有線でも不便なし。外出も想定するなら無線モデルの方が使い勝手がいいです。'),
            ('眼鏡をかけていても快適に使えますか？', '側圧の強さとイヤーカップの形状が重要。実際に試着するか、返品保証のある店舗での購入をおすすめします。'),
        ],
    },
    {
        'kw':      'Garmin Venu スマートウォッチ 健康管理',
        'title':   '健康管理に特化したスマートウォッチ',
        'cat':     'スマートウォッチ',
        'must':    ['スマートウォッチ','ウォッチ'],
        'exclude': ['バンド','ベルト','充電','ケース','フィルム','交換'],
        'persona': '健康診断で血圧・睡眠を指摘された40代。毎日の健康データを記録したい',
        'pain':    '体の状態を可視化したい。病院に行くほどじゃないけど気になる',
        'faq': [
            ('血圧は正確に測れますか？', '医療機器ではないため参考値です。傾向を把握するのに有効で、異常値のアラート機能もあります。'),
            ('睡眠の質はどうやって計測しますか？', '心拍数・血中酸素・体動から睡眠ステージ（深い/浅い/REM）を自動判定します。'),
            ('バッテリーはどれくらいもちますか？', 'Garmin Venuは通常使用で5日間。GPS使用時は約20時間が目安です。'),
            ('Apple Watchと何が違いますか？', 'Garminはバッテリー持ち・GPS精度・健康データの詳細さが強み。Apple WatchはiPhoneとの連携と決済機能が優れています。'),
            ('防水性能はありますか？', '5ATM防水で水泳にも対応。シャワーを浴びながら装着しても問題ありません。'),
        ],
    },
    {
        'kw':      'Apple Watch SE Series9 本体',
        'title':   '失敗しないApple Watch選び方ガイド',
        'cat':     'スマートウォッチ',
        'must':    ['Apple Watch'],
        'exclude': ['バンド','ベルト','充電','ケース','フィルム','カバー','交換'],
        'persona': 'iPhone使いで初めてスマートウォッチを買う30代。何を選べばいいかわからない',
        'pain':    'Apple WatchのSE・Series9・Ultraの違いがわからない',
        'faq': [
            ('SEとSeries 9はどちらを選べばいいですか？', '機能差より価格差（約2万円）を重視。初めてならSEで十分です。Series 9は心電図・血中酸素計が必要な方向け。'),
            ('アンドロイドでも使えますか？', 'Apple WatchはiPhone専用です。Androidユーザーはガーミンやサムスンが選択肢になります。'),
            ('バンドはいくつか種類がありますが、どれが使いやすいですか？', 'スポーツバンドが最も汎用的。公式以外の社外品でも安価に手に入ります。'),
            ('文字盤はカスタマイズできますか？', '数百種類の文字盤から選択可能。complicationsで表示する情報も自由に変更できます。'),
            ('楽天とApple Store、どちらで買うのがお得ですか？', '楽天ポイントを考慮すると楽天が有利なことが多いです。セール時期を狙いましょう。'),
        ],
    },
    {
        'kw':      'Anker PowerCore モバイルバッテリー 軽量 薄型',
        'title':   '毎日持ち歩ける軽量モバイルバッテリー',
        'cat':     'モバイル',
        'must':    ['バッテリー','モバイル'],
        'exclude': ['ケース','カバー'],
        'persona': '毎日通勤するビジネスパーソン。スマホが夕方に切れそうで不安',
        'pain':    '重いモバイルバッテリーを持ち歩きたくない。でも容量も欲しい',
        'faq': [
            ('毎日持ち歩くのに何mAhが適切ですか？', 'スマホ1回分なら5000〜10000mAh。200g以下を選べば重さを感じません。'),
            ('急速充電対応かどうかの確認方法は？', 'PD（Power Delivery）対応と書かれているものが急速充電対応です。18W以上を目安に選びましょう。'),
            ('飛行機に持ち込めますか？', '100Wh（約27000mAh）以下なら機内持ち込み可。スーツケースへの収納はNGです。'),
            ('複数のデバイスを同時充電できますか？', 'ポート数を確認。USB-C×2などのモデルならスマホとイヤホンを同時充電できます。'),
            ('充電しながら使えますか？（パススルー充電）', '対応モデルとそうでないものがあります。商品ページの仕様欄で確認しましょう。'),
        ],
    },
    {
        'kw':      'Anker PowerCore 20000 モバイルバッテリー 大容量',
        'title':   '旅行・出張に使える大容量モバイルバッテリー',
        'cat':     'モバイル',
        'must':    ['バッテリー','モバイル'],
        'exclude': ['ケース','カバー'],
        'persona': '月2〜3回出張がある営業マン。ホテルのコンセント争いから解放されたい',
        'pain':    '出張先でスマホもノートPCも充電できるバッテリーを探している',
        'faq': [
            ('ノートPCも充電できますか？', '65W以上のPD出力対応モデルならMacBook Airの充電も可能です。'),
            ('何回スマホを充電できますか？', '20000mAhならiPhone14換算で約5回。変換効率を考慮すると実際は4回程度です。'),
            ('満充電にどれくらいかかりますか？', '入力もPD対応なら約4時間。非対応だと8〜10時間かかる場合があります。'),
            ('重さはどれくらいですか？', '20000mAhクラスは350〜450gが一般的。スーツケースに入れる用途なら許容範囲です。'),
            ('ソーラー充電対応のモデルはありますか？', 'アウトドア向けにはソーラーパネル付きモデルもあります。ただし充電速度は遅め。'),
        ],
    },
    {
        'kw':      'Anker GaN充電器 65W コンパクト',
        'title':   'GaN充電器でデスクをスッキリさせる',
        'cat':     'モバイル',
        'must':    ['充電器','GaN'],
        'exclude': ['ケーブル','カバー'],
        'persona': 'MacBook・iPhone・iPadを使うクリエイター。充電器だらけのデスクを整理したい',
        'pain':    'デバイスが多くてコンセントが足りない。アダプタが大きすぎる',
        'faq': [
            ('GaN充電器とは何ですか？', 'ガリウムナイトライドという素材を使った充電器。従来より小型・軽量で発熱が少ないのが特徴です。'),
            ('MacBook Proの充電に使えますか？', 'MacBook Pro 14インチには65W以上、16インチには140W以上を推奨します。'),
            ('複数ポートで同時充電すると出力は下がりますか？', '下がります。重要なデバイスを1ポートで充電するか、出力分配の仕様を事前に確認しましょう。'),
            ('海外旅行でも使えますか？', '100〜240V対応のモデルなら変圧器不要で世界中で使えます。プラグ形状のみ要確認。'),
            ('熱くなりませんか？', 'GaN採用により発熱が少ないのが特徴。ただし高負荷時はある程度温かくなります。'),
        ],
    },
    {
        'kw':      'Logicool G PRO ゲーミングマウス 本体',
        'title':   'FPSゲーマーのための軽量ゲーミングマウス選び',
        'cat':     'ゲーミング',
        'must':    ['マウス'],
        'exclude': ['パッド','グリップ','交換','マウスソール','ソール'],
        'persona': 'FPSゲームで上位を目指す大学生。エイム精度を上げたい',
        'pain':    'マウスが重くて長時間プレイすると疲れる',
        'faq': [
            ('軽量マウスは何グラム以下を選べばいいですか？', '60g以下が軽量の目安。プロゲーマーの多くは55〜70gのモデルを使用しています。'),
            ('センサーはどれを選べばいいですか？', 'HERO・FOCUS Pro・TrueMove Proなど各社上位センサーを搭載したモデルなら精度の差は僅か。持ち方との相性を優先しましょう。'),
            ('有線と無線どちらがいいですか？', '遅延を極限まで減らしたいなら有線。使い勝手重視なら最新の無線モデルも遅延はほぼありません。'),
            ('DPIはいくつに設定すればいいですか？', 'FPSは400〜1600DPIが一般的。ゲームと画面解像度に合わせて調整しましょう。'),
            ('グリップスタイルで選び方は変わりますか？', 'かぶせ持ちは大型・重め、つかみ・つまみ持ちは小型・軽量が向いています。'),
        ],
    },
    {
        'kw':      'SteelSeries Arctis HyperX Cloud ゲーミングヘッドセット 本体',
        'title':   'ゲームの没入感が変わるゲーミングヘッドセット',
        'cat':     'ゲーミング',
        'must':    ['ヘッドセット'],
        'exclude': ['イヤーパッド','クッション','交換','補修','ケーブル','パーツ'],
        'persona': 'FPS・RPGを本格的に楽しみたいゲーマー。敵の足音を正確に聞き取りたい',
        'pain':    '敵の位置が音で把握できない。ボイチャの声が聞き取りにくい',
        'faq': [
            ('ゲーミングヘッドセットと普通のヘッドホンの違いは？', 'マイク内蔵・サラウンド対応・ゲーム向けチューニングが主な違い。ゲームと通話を両立できます。'),
            ('7.1chサラウンドは必要ですか？', 'FPSでは足音の方向を掴むのに有効。ただしステレオでも十分楽しめます。'),
            ('PS5やSwitchでも使えますか？', '3.5mmジャックまたはUSB接続対応モデルならほとんどのゲーム機で使用可。Bluetooth対応なら更に便利。'),
            ('マイクの音質はどうですか？', 'ゲーミングヘッドセットのマイクは通話品質に特化。ノイズキャンセリング付きモデルが特におすすめ。'),
            ('長時間つけていても疲れませんか？', '重量300g以下・イヤーカップの素材・ヘッドバンドのクッション性が重要。試着できる場合は必ず試しましょう。'),
        ],
    },
    {
        'kw':      'iRobot Roomba ロボット掃除機 本体',
        'title':   'ロボット掃除機で毎日の掃除を自動化する',
        'cat':     'スマートホーム',
        'must':    ['ロボット','掃除機'],
        'exclude': ['フィルター','ブラシ','交換','バッテリー','部品','パーツ'],
        'persona': '共働き夫婦。帰宅後に掃除する時間と体力がない',
        'pain':    '毎日掃除機をかけたいけど時間がない。ペットの毛が気になる',
        'faq': [
            ('部屋が散らかっていても使えますか？', 'ケーブルや小さなおもちゃは事前に片付けが必要。ルンバはその上で最大限効率化してくれます。'),
            ('段差はどれくらい乗り越えられますか？', '多くのモデルは2cm程度の段差をクリア。ラグの厚みによっては乗り越えられない場合も。'),
            ('マッピング機能は必要ですか？', '間取りが複雑・複数部屋をカバーしたいならマッピング機能付きが便利。シンプルな1Kなら不要です。'),
            ('うるさいですか？', '50〜65dBが目安。在宅勤務中に動かすのは気になる場合も。外出時に動かすのがおすすめです。'),
            ('ペットの毛は吸えますか？', 'ルンバはペットの毛に特化したモデルあり。ブラシの絡まりを防ぐゴム製ブラシを採用しています。'),
        ],
    },
    {
        'kw':      'SwitchBot スマートロック 後付け 本体',
        'title':   '賃貸でもできるスマートロック後付け完全ガイド',
        'cat':     'スマートホーム',
        'must':    ['スマートロック','ロック','SwitchBot'],
        'exclude': ['交換','部品','キー','スペア'],
        'persona': '賃貸マンション住まいで鍵の閉め忘れが不安な一人暮らし',
        'pain':    '外出後に「鍵閉めたっけ？」と不安になる',
        'faq': [
            ('賃貸に取り付けても問題ありませんか？', '多くのスマートロックは両面テープで取り付けるため、原状回復が可能。退去時に取り外しできます。'),
            ('既存の鍵はそのまま使えますか？','はい、既存の鍵の上に取り付ける後付けタイプなので、管理会社への届け出も不要なケースがほとんどです。'),
            ('バッテリーが切れたらどうなりますか？', '切れると施錠・解錠できなくなります。低残量アラートで事前に通知が来るのでこまめな交換を。'),
            ('Wi-Fiがなくても使えますか？', 'Bluetooth接続なら Wi-Fiなしでもスマホから操作可。ただし外出先からの遠隔操作はWi-Fi必須。'),
            ('取り付けに工事は必要ですか？', '多くのモデルは工具不要で10分以内に設置可能。ただし一部のシリンダー形状には非対応の場合も。'),
        ],
    },
    {
        'kw':      'GoPro HERO アクションカメラ 本体',
        'title':   'GoPro vs DJI アクションカメラ徹底比較',
        'cat':     'カメラ',
        'must':    ['カメラ','GoPro'],
        'exclude': ['ケース','マウント','バッテリー','充電','交換','アクセサリ'],
        'persona': 'アウトドア・旅行が好きな30代。ダイナミックな映像を残したい',
        'pain':    'スマホカメラでは手ブレがひどい。激しい動きも綺麗に撮りたい',
        'faq': [
            ('GoProとDJIどちらを選べばいいですか？', '水中・過酷な環境ならGoPro、日常・旅行動画の安定性ならDJI Osmo Actionが優秀です。'),
            ('防水はどれくらい対応していますか？', 'GoPro HERO12は単体で10mまで防水対応。ダイビングには専用ハウジングが必要。'),
            ('4Kで撮影するとデータ容量はどれくらいですか？', '4K60fpsで約1時間あたり約30GB。大容量のmicroSDカードを事前に準備しましょう。'),
            ('スマホで撮った映像と何が違いますか？', '手ブレ補正・超広角・耐衝撃・防水が最大の違い。動きのある場面での安定性が圧倒的です。'),
            ('初心者でも使いこなせますか？', '最近のモデルは自動設定が優秀。「電源ON→撮影ボタン」だけで高品質な映像が撮れます。'),
        ],
    },
]

# ===== CTA文パターン（ランダムで使用） =====
CTA_PATTERNS = [
    '楽天で最安値をチェックする',
    '在庫確認・最新価格を見る',
    '楽天の口コミを読んで購入する',
    '今すぐ楽天で購入する',
    '詳細スペックと価格を確認する',
    '楽天公式ページで購入する',
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
    print(f"  {'🗑️削除' if ok else '❌削除失敗'} {path}")
    return ok

# ===== 楽天商品取得 =====
WH = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gadget-tengoku.com/',
}

def fetch_products(keyword, hits=20, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(WORKER_URL, params={'keyword': keyword, 'hits': hits}, headers=WH, timeout=20)
            if r.ok:
                items = r.json().get('Items', [])
                if items:
                    return items
        except Exception as e:
            print(f"  Workerエラー: {e}")
        time.sleep(2)
    return []

def filter_items(items, theme):
    must_words    = theme.get('must', [])
    exclude_words = theme.get('exclude', [])
    result        = []
    for item in items:
        p    = item.get('Item', {})
        name = p.get('itemName', '')
        shop = p.get('shopName', '')
        if any(ex in name for ex in exclude_words):
            continue
        if must_words and not any(m in name for m in must_words):
            continue
        text = (name + ' ' + shop).lower()
        if not any(b.lower() in text for b in TRUSTED_BRANDS):
            continue
        result.append(item)
    return result

def fetch_trusted(theme, need=5):
    items    = fetch_products(theme['kw'], hits=30)
    filtered = filter_items(items, theme)
    print(f"  '{theme['kw'][:35]}' → 全{len(items)}件 / フィルタ後{len(filtered)}件")
    if len(filtered) >= 3:
        return filtered[:need]
    soft = [i for i in items if not any(ex in i.get('Item',{}).get('itemName','') for ex in theme.get('exclude',[]))]
    return soft[:need] if soft else items[:need]

# ===== 記事HTML生成（PREP + セールスライティング + FAQ） =====
def build_html(title, theme_obj, products):
    theme   = theme_obj['title'] if isinstance(theme_obj, dict) else theme_obj
    persona = theme_obj.get('persona', '') if isinstance(theme_obj, dict) else ''
    pain    = theme_obj.get('pain', '') if isinstance(theme_obj, dict) else ''
    faq     = theme_obj.get('faq', []) if isinstance(theme_obj, dict) else []
    today   = datetime.now().strftime('%Y年%m月%d日')
    year    = datetime.now().year
    num_class = ['gold','silver','bronze','normal','normal']
    cta = random.choice(CTA_PATTERNS)

    cards = ''
    rows  = ''

    for i, item in enumerate(products[:5]):
        p         = item.get('Item', {})
        name      = p.get('itemName', '')[:60]
        price     = p.get('itemPrice', 0)
        shop      = p.get('shopName', '')[:20]
        ra        = float(p.get('reviewAverage', 0))
        rc        = int(p.get('reviewCount', 0))
        url       = p.get('affiliateUrl', p.get('itemUrl', '#'))
        imgs      = p.get('mediumImageUrls', [])
        img       = ''
        if imgs:
            raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            img = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)
        item_code  = p.get('itemCode', '')
        review_url = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':', '/')}/1.1/" if item_code else url
        stars_int  = int(ra)
        stars_html = f'<span style="color:#f5a623;font-size:16px">{"★"*stars_int}{"☆"*(5-stars_int)}</span>'
        bar_w      = int(ra / 5 * 100)

        img_html = f'<img src="{img}" alt="{name}" loading="lazy">' if img else '<div style="color:#ccc;font-size:12px;text-align:center">No Image</div>'

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
      <div style="margin:8px 0">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px">
          {stars_html}
          <strong style="font-size:18px;color:#111">{ra:.1f}</strong>
          <span style="font-size:13px;color:#aaa">/ 5.0</span>
          <a href="{review_url}" target="_blank" rel="noopener"
             style="font-size:12px;color:#e63900">楽天の口コミを見る（{rc:,}件）→</a>
        </div>
        <div style="background:#f0f0f0;border-radius:4px;height:6px;width:160px">
          <div style="background:#f5a623;height:6px;border-radius:4px;width:{bar_w}%"></div>
        </div>
      </div>
      <div class="price-area">
        <div class="price">¥{price:,} <small>税込</small></div>
        <a href="{url}" class="btn-buy" target="_blank" rel="noopener sponsored">{cta}</a>
      </div>
    </div>
  </div>
</div>'''

        rows += f'<tr><td><span class="rank-no">{i+1}</span>{name[:28]}</td><td>¥{price:,}</td><td>{"★"*stars_int}{"☆"*(5-stars_int)} {ra:.1f}</td><td><a href="{review_url}" target="_blank" rel="noopener" style="color:#e63900">{rc:,}件</a></td><td><a href="{url}" target="_blank" rel="noopener sponsored" style="color:#e63900;font-weight:700">購入</a></td></tr>'

    # FAQ HTML
    faq_html = ''
    if faq:
        items_html = ''.join(f'''
<div style="border-bottom:1px solid #f0f0f0;padding:16px 0">
  <div style="font-weight:700;color:#111;margin-bottom:6px;font-size:14px">Q. {q}</div>
  <div style="color:#555;font-size:14px;line-height:1.8">A. {a}</div>
</div>''' for q, a in faq)
        faq_html = f'''
  <section id="faq" style="margin-top:32px">
    <h2 class="section-title">よくある質問（FAQ）</h2>
    <div style="background:#fafafa;border:1px solid #e8e8e8;border-radius:6px;padding:0 20px">
      {items_html}
    </div>
  </section>'''

    # ペルソナ・悩みブロック
    persona_html = ''
    if persona and pain:
        persona_html = f'''
  <div style="background:#fff8f0;border-left:4px solid #e63900;padding:14px 18px;margin-bottom:20px;border-radius:0 4px 4px 0">
    <div style="font-size:12px;color:#e63900;font-weight:700;margin-bottom:4px">こんな方におすすめ</div>
    <div style="font-size:14px;color:#333;margin-bottom:6px">{persona}</div>
    <div style="font-size:13px;color:#888">💬 よくある悩み：{pain}</div>
  </div>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新、{theme}のおすすめランキングTOP5。楽天市場の実売データ・口コミをもとに選出。失敗しない選び方のポイントも解説。">
<link rel="canonical" href="{SITE_URL}/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{",".join(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}' for q,a in faq)}]}}
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
      <span>⏱ 読了時間：約4分</span>
    </div>
  </div>
</div>

<div class="container">

  <!-- PREP: Point（結論先出し） -->
  <div style="background:#111;color:#fff;border-radius:6px;padding:16px 20px;margin-bottom:20px">
    <div style="font-size:12px;color:#e63900;font-weight:700;margin-bottom:6px">✅ この記事の結論</div>
    <div style="font-size:14px;line-height:1.8">楽天市場のレビュー数・評価点・価格を総合判断し、<strong style="color:#ffd700">{theme}</strong>のベストモデルを厳選しました。迷ったら<strong style="color:#ffd700">1位のモデル</strong>を選べば間違いありません。</div>
  </div>

  {persona_html}

  <div class="intro-box">
    「{theme}を選びたいけど種類が多くてわからない」という方向けに、楽天市場の実際の売れ筋・レビュー数をもとにTOP5を厳選しました。価格・評価・レビュー数を総合的に判断しています。
  </div>

  <nav class="toc">
    <div class="toc-title">目次</div>
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
      ※データ参照元：<a href="https://www.rakuten.co.jp/" target="_blank" rel="noopener" style="color:#e63900">楽天市場</a>（{today}時点・レビュー件数順・価格は変動する場合あり）
    </p>
    {cards}
  </section>

  <section id="compare">
    <h2 class="section-title">スペック比較表</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>順位</th><th>価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </section>

  <section id="guide">
    <h2 class="section-title">失敗しない選び方のポイント</h2>
    <div class="guide-grid">
      <div class="guide-item">
        <div class="guide-item-title">① まず予算を決める</div>
        <div class="guide-item-desc">価格帯によっておすすめモデルが変わります。1万円・3万円・5万円の区切りを意識しましょう。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-title">② レビュー件数を確認</div>
        <div class="guide-item-desc">1,000件以上なら実績十分。件数が多いほど信頼性が高く、外れが少ないです。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-title">③ 用途に合わせる</div>
        <div class="guide-item-desc">毎日使うシーンをイメージして機能を絞り込みましょう。多機能すぎるものは使いこなせないことも。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-title">④ 保証・サポートを確認</div>
        <div class="guide-item-desc">国内正規品はメーカー保証あり。楽天市場の公式ストアから購入すれば安心です。</div>
      </div>
    </div>
  </section>

  {faq_html}

  <!-- 最終CTA -->
  <div style="background:#f8f8f8;border:1px solid #e8e8e8;border-radius:6px;padding:20px;text-align:center;margin-top:28px">
    <div style="font-size:14px;font-weight:700;margin-bottom:8px">まだ迷っていますか？</div>
    <div style="font-size:13px;color:#555;margin-bottom:14px">楽天市場で実際のレビューを読んで決めましょう</div>
    <a href="https://www.rakuten.co.jp/search/{requests.utils.quote(theme)}/" target="_blank" rel="noopener"
       style="display:inline-block;background:#e63900;color:#fff;font-size:14px;font-weight:700;padding:12px 28px;border-radius:4px">
      楽天で「{theme}」を検索する →
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
        'description': f"{theme_obj['title']}のおすすめTOP5。{theme_obj.get('pain','')}を解決する選び方も解説。",
    }
    updated = False
    for i, a in enumerate(articles):
        if a['filename'] == filename:
            articles[i] = new; updated = True; break
    if not updated:
        articles.insert(0, new)
    articles = articles[:50]
    gh_put('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), 'Auto: 記事一覧更新', sha)
    return articles

# ===== 既存記事再生成・クリーンアップ =====
def regenerate_and_cleanup():
    print('\n既存記事を再生成中...')
    content, _ = gh_get('articles.json')
    if not content:
        return
    articles  = json.loads(content)
    theme_map = {t['title']: t for t in ALL_THEMES}
    keep      = []

    for a in articles:
        filename  = a.get('filename', '')
        theme_key = a.get('theme_key', '')
        title     = a.get('title', '')
        theme_obj = theme_map.get(theme_key)

        if not theme_obj:
            print(f'  テーマ不明 → 削除: {theme_key}')
            _, sha = gh_get(filename)
            if sha: gh_delete(filename, sha, f'Cleanup: {filename}')
            continue

        print(f'  再生成: {theme_key}')
        products = fetch_trusted(theme_obj, need=5)

        if not products:
            print(f'  商品0件 → 削除: {filename}')
            _, sha = gh_get(filename)
            if sha: gh_delete(filename, sha, f'Cleanup: 商品なし {filename}')
            continue

        html   = build_html(title, theme_obj, products)
        _, sha = gh_get(filename)
        if gh_put(filename, html, f'Regenerate: {theme_key}', sha):
            imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
            if imgs:
                raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
                a['img_url'] = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)
            keep.append(a)
        else:
            keep.append(a)
        time.sleep(1.5)

    _, sha = gh_get('articles.json')
    gh_put('articles.json', json.dumps(keep, ensure_ascii=False, indent=2), 'Auto: articles.json更新', sha)
    print(f'完了（残り{len(keep)}件）')

# ===== アーカイブ =====
def build_archive(articles):
    arts  = [a for a in articles if a.get('img_url', '').strip()]
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
<div style="border-bottom:1px solid #e8e8e8;padding:24px 20px">
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
  <div class="footer-links">
    <a href="{SITE_URL}/">トップ</a>
    <a href="{SITE_URL}/privacy.html">プライバシーポリシー</a>
  </div>
</div>
<p class="footer-note">© {datetime.now().year} ガジェット天国</p>
</footer></body></html>'''

# ===== サイトマップ =====
def build_sitemap(extra):
    today = datetime.now().strftime('%Y-%m-%d')
    bases = ['','earphone.html','smartwatch.html','battery.html','archive.html','privacy.html']
    urls  = [f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod><priority>{"1.0" if u=="" else "0.8"}</priority></url>' for u in bases]
    for f in extra:
        urls.append(f'  <url><loc>{SITE_URL}/{f}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'

# ===== Twitter =====
def post_twitter(title, url, cat):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        print('⚠ Twitter: Secrets未設定')
        return
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        tweepy.API(auth).update_status(f"新着記事📱\n{title}\n\n楽天市場の実売データで厳選✅\nFAQ付きで選び方もわかる！\n\n{url}\n\n#{cat} #ガジェット #楽天")
        print('✅ Twitter投稿成功')
    except Exception as e:
        print(f'❌ Twitter失敗: {e}')

# ===== テーマ選択 =====
def select_theme():
    content, _ = gh_get('articles.json')
    used = set()
    if content:
        try: used = {a.get('theme_key','') for a in json.loads(content)[:40]}
        except: pass
    available = [t for t in ALL_THEMES if t['title'] not in used] or ALL_THEMES
    am = ['イヤホン','オーディオ','スマートウォッチ']
    pm = ['ゲーミング','PC周辺機器','スマートホーム','カメラ','モバイル','生活家電']
    pool = [t for t in available if t['cat'] in (am if SLOT=='am' else pm)] or available
    return random.choice(pool)

# ===== メイン =====
def main():
    today = datetime.now()
    print(f"=== {today.strftime('%Y年%m月%d日')} [{SLOT.upper()}] ===")

    theme = select_theme()
    print(f"テーマ: {theme['title']}")
    products = fetch_trusted(theme, need=5)

    if not products:
        print('❌ 商品取得失敗')
        return

    title    = f"【{today.year}年最新】{theme['title']} おすすめランキングTOP5"
    html     = build_html(title, theme, products)
    date_str = today.strftime('%Y%m%d')
    safe     = re.sub(r'[^\w]', '-', theme['title'])[:25]
    filename = f"article-{safe}-{SLOT}-{date_str}.html"

    _, sha = gh_get(filename)
    gh_put(filename, html, f"Auto: {theme['title']}", sha)

    img_url = ''
    if products:
        imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
        if imgs:
            raw     = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            img_url = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)

    update_articles_json(theme, filename, img_url, today)
    regenerate_and_cleanup()

    content, _ = gh_get('articles.json')
    if content:
        _, sha = gh_get('archive.html')
        gh_put('archive.html', build_archive(json.loads(content)), 'Auto: アーカイブ更新', sha)

    _, sha = gh_get('sitemap.xml')
    gh_put('sitemap.xml', build_sitemap([filename]), 'Auto: サイトマップ', sha)

    post_twitter(title, f"{SITE_URL}/{filename}", theme['cat'])
    print(f"\n=== 完了: {SITE_URL}/{filename} ===")

if __name__ == '__main__':
    main()
