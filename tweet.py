import tweepy
import random
import os
from datetime import datetime

# 環境変数からAPIキーを取得
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

# Twitter API認証
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

SITE_URL = "https://gadget-tengoku.github.io/gadget-lab"

# ランダム投稿テンプレート
tweets = [
    # サイト紹介
    f"""🎧 ガジェット・家電専門サイト「ガジェット天国」

楽天市場の最新人気商品をリアルタイムで紹介中🔥

✅ イヤホン比較
✅ スマートウォッチランキング
✅ バッテリー比較

{SITE_URL}/

#ガジェット #家電 #楽天""",

    # イヤホン記事
    f"""🎧【2026年版】ワイヤレスイヤホン おすすめTOP5

SonyのWF-1000XM5が業界最強のNC性能で1位✨

コスパ重視ならAnkerが\u00a56,990〜でおすすめ👇

{SITE_URL}/earphone.html

#ワイヤレスイヤホン #ガジェット #楽天""",

    # スマートウォッチ記事
    f"""⌚【2026年版】スマートウォッチ おすすめTOP5

iPhoneユーザー→Apple Watch一択
AndroidユーザーはGalaxy Watchが最高峰📱

バッテリー重視ならGarminが最大13日間持ち！

{SITE_URL}/smartwatch.html

#スマートウォッチ #AppleWatch #ガジェット""",

    # バッテリー記事
    f"""🔋 モバイルバッテリー選びで迷ってる人へ

毎日持ち歩くなら→CIO 170g 超軽量
旅行・出張なら→Anker 20000mAh 200W出力

どちらも楽天で最安値チェック👇

{SITE_URL}/battery.html

#モバイルバッテリー #Anker #ガジェット""",

    # お得情報
    f"""💡 今楽天で売れてるガジェットTOP3

1位🎧 ワイヤレスイヤホン
2位⌚ スマートウォッチ
3位🔋 モバイルバッテリー

詳しいランキングはこちら👇

{SITE_URL}/

#ガジェット #楽天 #家電""",

    # NC特集
    f"""🔇 ノイズキャンセリングイヤホン比較

在宅ワーク・通勤に必須のNC機能🎧

性能最強: Sony WF-1000XM5
iPhone向け: AirPods Pro 2
コスパ最強: Anker Liberty 4 NC(\u00a56,990)

詳細レビューはこちら👇

{SITE_URL}/earphone.html

#ノイズキャンセリング #テレワーク""",

    # ランキング更新
    f"""📊 【本日更新】ガジェット天国ランキング

楽天市場の最新売れ筋をリアルタイム表示中📱

🥇 家電・ガジェット部門
🥈 イヤホン部門  
🥉 スマートウォッチ部門

今すぐチェック👇

{SITE_URL}/

#ガジェット #楽天市場 #家電""",

    # コスパ特集
    f"""💰 1万円以下で買えるおすすめガジェット

🎧 Anker イヤホン: \u00a56,990
🔋 CIO バッテリー: \u00a54,980
💡 スマートLED: \u00a53,280

コスパ最高の商品を厳選紹介中👇

{SITE_URL}/

#コスパ #ガジェット #楽天""",
]

# 曜日によって投稿を変える（毎日違う内容に）
weekday = datetime.now().weekday()  # 0=月曜〜6=日曜
tweet_index = weekday % len(tweets)

# ランダム要素も加える
if random.random() > 0.5:
    tweet_index = random.randint(0, len(tweets) - 1)

tweet_text = tweets[tweet_index]

# 投稿
try:
    response = client.create_tweet(text=tweet_text)
    print(f"✅ ツイート投稿成功！ ID: {response.data['id']}")
    print(f"内容: {tweet_text[:50]}...")
except Exception as e:
    print(f"❌ エラー: {e}")
    raise
