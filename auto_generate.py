#!/usr/bin/env python3
import os
import re
import requests
import base64
from datetime import datetime

RAKUTEN_APP_ID = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
CLAUDE_API_KEY = os.environ['CLAUDE_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = 'gadget-tengoku/gadget-lab'
SITE_URL = 'https://gadget-tengoku.github.io/gadget-lab'

TWITTER_API_KEY = os.environ.get('API_KEY', '')
TWITTER_API_SECRET = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

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
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
    params = {
        'format': 'json', 'keyword': keyword, 'genreId': 0,
        'applicationId': RAKUTEN_APP_ID, 'accessKey': RAKUTEN_ACCESS_KEY,
        'hits': hits, 'affiliateId': RAKUTEN_AFFILIATE_ID,
        'imageFlag': 1, 'sort': '-reviewCount'
    }
    headers = {'Referer': 'https://gadget-tengoku.github.io'}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        return res.json().get('Items', [])
    except Exception as e:
        print(f"楽天API エラー: {e}")
        return []

def generate_article_with_claude(theme, products):
    product_info = ""
    for i, item in enumerate(products[:5], 1):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:50]
        price = p.get('itemPrice', 0)
        shop = p.get('shopName', '')
        review_avg = p.get('reviewAverage', 0)
        review_count = p.get('reviewCount', 0)
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', ''))
        product_info += f"\n{i}位: {name}\n価格:¥{price:,} ショップ:{shop} 評価:{review_avg}点({review_count}件)\nURL:{affiliate_url}\n"

    if not product_info:
        product_info = "商品データなし。一般的な情報で記事を生成してください。"

    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year

    prompt = f"""ガジェット専門アフィリエイトライターとして、完全なHTMLファイルを1つ生成してください。

テーマ:【{year}年最新】{theme['title']} おすすめランキングTOP5
更新日:{today}
商品:{product_info}

絶対ルール:
- 出力はHTMLのみ。```は使わない
- <!DOCTYPE html>で始まりる</html>で必ず終わる
- <style>タグは必ず</style>で閉じる
- CSSコメント/*は必ず*/で閉じる
- bodyタグ内にコンテンツを書く

デザイン:
- ヘッダー:背景#111、ロゴ「Gadget天国」文字色白、span要素を#FF4D00
- ヒーロー:グラデーション背景、白文字
- 商品カード:白背景、影あり、購入ボタンは背景#BF0000・白文字
- フッター:背景#111、アフィリエイト表記あり

構成:選び方(4項目)→ランキングTOP5→比較表→FAQ→フッター

トップページ:{SITE_URL}/index.html
サイトURL:{SITE_URL}

CSSは<style>内にまとめ、シンプルに書くこと。"""

    api_headers = {
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
        res = requests.post('https://api.anthropic.com/v1/messages', headers=api_headers, json=data, timeout=60)
        content = res.json()['content'][0]['text']
        # コードブロック除去
        content = re.sub(r'```html\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        # <!DOCTYPE>から始まるように
        if '<!DOCTYPE' in content and not content.startswith('<!DOCTYPE'):
            content = content[content.index('<!DOCTYPE'):]
        # </html>で終わるように
        if '</html>' in content:
            content = content[:content.rindex('</html>') + 7]
        return content
    except Exception as e:
        print(f"Claude API エラー: {e}")
        return None

def upload_to_github(filename, content, commit_message):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    sha = None
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json().get('sha')
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {'message': commit_message, 'content': encoded}
    if sha:
        data['sha'] = sha
    res = requests.put(url, headers=headers, json=data)
    if res.status_code in [200, 201]:
        print(f"✅ GitHubアップロード成功: {filename}")
        return True
    print(f"❌ GitHubアップロード失敗: {res.status_code}")
    return False

def update_sitemap(new_files):
    today = datetime.now().strftime('%Y-%m-%d')
    base_urls = ['', 'earphone.html', 'smartwatch.html', 'battery.html']
    urls = []
    for u in base_urls:
        priority = '1.0' if u == '' else '0.8'
        urls.append(f"  <url>\n    <loc>{SITE_URL}/{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>{priority}</priority>\n  </url>")
    for f in new_files:
        urls.append(f"  <url>\n    <loc>{SITE_URL}/{f}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'

def post_to_twitter(text):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        print("Twitter APIキーが未設定")
        return False
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        api.update_status(text)
        print("✅ Twitter投稿成功！")
        return True
    except Exception as e:
        print(f"Twitter投稿エラー: {e}")
        return False

def main():
    today = datetime.now()
    theme = ARTICLE_THEMES[today.weekday() % len(ARTICLE_THEMES)]
    print(f"📅 {today.strftime('%Y年%m月%d日')} テーマ: {theme['title']}")

    print("🛒 楽天APIから商品取得中...")
    products = fetch_rakuten_products(theme['keyword'])
    if not products:
        products = fetch_rakuten_products('ガジェット 人気')
    print(f"✅ {len(products)}件取得")

    print("🤖 Claude AIで記事生成中...")
    article_html = generate_article_with_claude(theme, products)
    if not article_html:
        print("❌ 記事生成失敗")
        return
    print("✅ 記事生成完了")

    date_str = today.strftime('%Y%m%d')
    filename = f"{theme['filename']}-{date_str}.html"
    upload_to_github(filename, article_html, f"Auto: {theme['title']}記事生成 ({today.strftime('%Y/%m/%d')})")

    sitemap = update_sitemap([filename])
    upload_to_github('sitemap.xml', sitemap, f"Auto: サイトマップ更新 ({today.strftime('%Y/%m/%d')})")

    tweet_text = f"🆕 新着記事！\n【{today.year}年最新】{theme['title']} おすすめランキングTOP5\n\n{SITE_URL}/{filename}\n\n#{theme['category']} #ガジェット #楽天"
    post_to_twitter(tweet_text)

    print(f"\n🎉 完了！ {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
