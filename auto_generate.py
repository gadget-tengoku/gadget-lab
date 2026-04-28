#!/usr/bin/env python3
"""
ガジェット天国 完全自動化システム
- 楽天APIから売れ筋商品を取得
- Claude AIで記事を自動生成
- GitHubに記事を自動アップロード
- Twitterに自動投稿
"""

import os
import json
import random
import requests
import base64
from datetime import datetime

# ===== 設定 =====
RAKUTEN_APP_ID = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
CLAUDE_API_KEY = os.environ['CLAUDE_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = 'gadget-tengoku/gadget-lab'
SITE_URL = 'https://gadget-tengoku.github.io/gadget-lab'

# Twitter（オプション）
TWITTER_API_KEY = os.environ.get('API_KEY', '')
TWITTER_API_SECRET = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

# 記事テーマ（曜日ごと）
ARTICLE_THEMES = [
    {'keyword': 'ワイヤレスイヤホン ノイキャン 人気', 'title': 'ワイヤレスイヤホン', 'filename': 'earphone-ranking', 'category': 'イヤホン'},
    {'keyword': 'スマートウォッチ 健康管理 人気', 'title': 'スマートウォッチ', 'filename': 'smartwatch-ranking', 'category': 'スマートウォッチ'},
    {'keyword': 'モバイルバッテリー 軽量 急速充電', 'title': 'モバイルバッテリー', 'filename': 'battery-ranking', 'category': 'モバイル'},
    {'keyword': 'スマートホーム LED 人気', 'title': 'スマートホームガジェット', 'filename': 'smarthome-ranking', 'category': 'スマートホーム'},
    {'keyword': 'ゲーミングマウス 高性能', 'title': 'ゲーミングマウス', 'filename': 'gaming-mouse-ranking', 'category': 'PC周辺機器'},
    {'keyword': 'Bluetoothスピーカー 防水', 'title': 'Bluetoothスピーカー', 'filename': 'speaker-ranking', 'category': 'オーディオ'},
    {'keyword': 'USB充電器 GaN 急速充電', 'title': 'USB急速充電器', 'filename': 'charger-ranking', 'category': 'モバイル'},
]

def fetch_rakuten_products(keyword, hits=5):
    """楽天APIから商品を取得"""
    url = f"https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
    params = {
        'format': 'json',
        'keyword': keyword,
        'genreId': 0,
        'applicationId': RAKUTEN_APP_ID,
        'accessKey': RAKUTEN_ACCESS_KEY,
        'hits': hits,
        'affiliateId': RAKUTEN_AFFILIATE_ID,
        'imageFlag': 1,
        'sort': '-reviewCount'
    }
    headers = {
        'Referer': 'https://gadget-tengoku.github.io',
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()
        return data.get('Items', [])
    except Exception as e:
        print(f"楽天API エラー: {e}")
        return []

def generate_article_with_claude(theme, products):
    """Claude AIで記事を生成"""
    product_info = ""
    for i, item in enumerate(products[:5], 1):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:50]
        price = p.get('itemPrice', 0)
        shop = p.get('shopName', '')
        review_avg = p.get('reviewAverage', 0)
        review_count = p.get('reviewCount', 0)
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', ''))
        product_info += f"""
{i}位: {name}
- 価格: ¥{price:,}（税込）
- ショップ: {shop}
- 評価: {review_avg}点（{review_count}件）
- URL: {affiliate_url}
"""

    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year

    prompt = f"""あなたはガジェット・家電専門のアフィリエイトライターです。
以下の商品情報をもとに、SEOに強い日本語の商品ランキング記事をHTMLで生成してください。

テーマ: {theme['title']}のおすすめランキング
カテゴリ: {theme['category']}
更新日: {today}

【商品情報（楽天市場から取得）】
{product_info}

以下の構成でHTMLを生成してください：
- タイトル: 【{year}年最新】{theme['title']} おすすめ人気ランキングTOP5
- メタディスクリプション（160文字以内）
- 記事本文（選び方のポイント、各商品の詳細レビュー、比較表、FAQ）
- 各商品に楽天アフィリエイトリンクボタンを設置
- SEOキーワードを自然に盛り込む
- 文字数: 2000〜3000文字

スタイルは以下のCSSクラスを使用：
- ヘッダー: header（黒背景）
- 記事: article-hero（黒グラデーション）
- 商品カード: rank-card
- 購入ボタン: btn-buy（赤背景 #BF0000）
- フォント: Noto Sans JP

完全なHTMLファイルとして出力してください。
サイトURL: {SITE_URL}
トップページへのリンク: {SITE_URL}/index.html"""

    headers = {
        'x-api-key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }
    data = {
        'model': 'claude-sonnet-4-6',
        'max_tokens': 4000,
        'messages': [{'role': 'user', 'content': prompt}]
    }
    try:
        res = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=60
        )
        result = res.json()
        return result['content'][0]['text']
    except Exception as e:
        print(f"Claude API エラー: {e}")
        return None

def upload_to_github(filename, content, commit_message):
    """GitHubにファイルをアップロード"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # 既存ファイルのSHAを取得
    sha = None
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json().get('sha')

    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {
        'message': commit_message,
        'content': encoded,
    }
    if sha:
        data['sha'] = sha

    res = requests.put(url, headers=headers, json=data)
    if res.status_code in [200, 201]:
        print(f"✅ GitHubアップロード成功: {filename}")
        return True
    else:
        print(f"❌ GitHubアップロード失敗: {res.status_code} {res.text}")
        return False

def update_sitemap(new_files):
    """サイトマップを更新"""
    today = datetime.now().strftime('%Y-%m-%d')
    urls = [
        f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{SITE_URL}/earphone.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""",
        f"""  <url>
    <loc>{SITE_URL}/smartwatch.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""",
        f"""  <url>
    <loc>{SITE_URL}/battery.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""",
    ]
    for f in new_files:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/{f}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    return sitemap

def post_to_twitter(text):
    """Twitterに投稿"""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        print("Twitter APIキーが設定されていません")
        return False
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        api.update_status(text)
        print("✅ Twitter投稿成功！")
        return True
    except Exception as e:
        print(f"Twitter投稿エラー: {e}")
        return False

def main():
    today = datetime.now()
    weekday = today.weekday()
    theme = ARTICLE_THEMES[weekday % len(ARTICLE_THEMES)]

    print(f"📅 {today.strftime('%Y年%m月%d日')} の記事テーマ: {theme['title']}")

    # 1. 楽天から商品取得
    print("🛒 楽天APIから商品を取得中...")
    products = fetch_rakuten_products(theme['keyword'])
    if not products:
        print("商品取得失敗。デフォルトキーワードで再試行...")
        products = fetch_rakuten_products('ガジェット 人気')

    print(f"✅ {len(products)}件の商品を取得")

    # 2. Claude AIで記事生成
    print("🤖 Claude AIで記事を生成中...")
    article_html = generate_article_with_claude(theme, products)
    if not article_html:
        print("❌ 記事生成失敗")
        return

    print("✅ 記事生成完了")

    # 3. GitHubにアップロード
    date_str = today.strftime('%Y%m%d')
    filename = f"{theme['filename']}-{date_str}.html"
    commit_msg = f"Auto: {theme['title']}記事を自動生成 ({today.strftime('%Y/%m/%d')})"

    print(f"📤 GitHubにアップロード中: {filename}")
    upload_to_github(filename, article_html, commit_msg)

    # 4. サイトマップ更新
    print("🗺️ サイトマップを更新中...")
    sitemap = update_sitemap([filename])
    upload_to_github('sitemap.xml', sitemap, f"Auto: サイトマップ更新 ({today.strftime('%Y/%m/%d')})")

    # 5. Twitter投稿
    tweet_text = f"""🆕 新着記事を公開しました！

【{today.year}年最新】{theme['title']} おすすめ人気ランキングTOP5

楽天市場の売れ筋を徹底比較👇

{SITE_URL}/{filename}

#{theme['category']} #ガジェット #楽天"""

    print("🐦 Twitterに投稿中...")
    post_to_twitter(tweet_text)

    print("\n🎉 全処理完了！")
    print(f"📄 新記事URL: {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
