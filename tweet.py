import tweepy
import random
import os
from datetime import datetime

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

auth = tweepy.OAuth1UserHandler(
    API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

SITE_URL = "https://gadget-tengoku.github.io/gadget-lab"

tweets = [
    f"🎧 ガジェット天国オープン！\n楽天市場の人気商品をリアルタイム紹介🔥\n✅ イヤホン比較\n✅ スマートウォッチ\n✅ バッテリー比較\n{SITE_URL}/\n#ガジェット #家電 #楽天",
    f"🎧 ワイヤレスイヤホンどれ買う？\nSony・Apple・Ankerを徹底比較👇\n{SITE_URL}/earphone.html\n#ワイヤレスイヤホン #ガジェット",
    f"⌚ スマートウォッチ おすすめTOP5\nApple Watch vs Galaxy Watch vs Garmin\n{SITE_URL}/smartwatch.html\n#スマートウォッチ #ガジェット",
    f"🔋 モバイルバッテリー選びで迷ったら\nAnker・CIOを徹底比較👇\n{SITE_URL}/battery.html\n#モバイルバッテリー #Anker",
    f"💡 今楽天で売れてるガジェットTOP3\n1位🎧イヤホン\n2位⌚スマートウォッチ\n3位🔋バッテリー\n{SITE_URL}/\n#ガジェット #楽天",
]

tweet_text = tweets[datetime.now().weekday() % len(tweets)]

try:
    api.update_status(tweet_text)
    print(f"✅ 投稿成功！")
except Exception as e:
    print(f"❌ エラー: {e}")
    raise
