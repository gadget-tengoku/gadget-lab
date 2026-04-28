#!/usr/bin/env python3
import os
import re
import requests
import base64
import json
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
    {'keyword': 'ワイヤレスイヤホン ノイキャン 人気', 'title': 'ワイヤレスイヤホン', 'filename': 'earphone-ranking', 'category': 'イヤホン', 'emoji': '🎧'},
    {'keyword': 'スマートウォッチ 健康管理 人気', 'title': 'スマートウォッチ', 'filename': 'smartwatch-ranking', 'category': 'スマートウォッチ', 'emoji': '⌚'},
    {'keyword': 'モバイルバッテリー 軽量 急速充電', 'title': 'モバイルバッテリー', 'filename': 'battery-ranking', 'category': 'モバイル', 'emoji': '🔋'},
    {'keyword': 'スマートホーム LED 人気', 'title': 'スマートホームガジェット', 'filename': 'smarthome-ranking', 'category': 'スマートホーム', 'emoji': '💡'},
    {'keyword': 'ゲーミングマウス 高性能', 'title': 'ゲーミングマウス', 'filename': 'gaming-mouse-ranking', 'category': 'PC周辺機器', 'emoji': '🖱️'},
    {'keyword': 'Bluetoothスピーカー 防水', 'title': 'Bluetoothスピーカー', 'filename': 'speaker-ranking', 'category': 'オーディオ', 'emoji': '🔊'},
    {'keyword': 'USB充電器 GaN 急速充電', 'title': 'USB急速充電器', 'filename': 'charger-ranking', 'category': 'モバイル', 'emoji': '⚡'},
]

HTML_TEMPLATE_START = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="article-style.css">
</head>
<body>
<header>
  <div class="header-inner">
    <div class="logo">Gadget<span>天国</span></div>
    <nav><a href="{site_url}/index.html">トップ</a></nav>
  </div>
</header>
"""

HTML_TEMPLATE_END = """
<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{site_url}/index.html">← トップページに戻る</a>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。<br>記事内のリンクから購入された場合、運営者に報酬が発生することがあります。</p>
  <p style="margin-top:10px;font-size:.75rem">© 2026 ガジェット天国</p>
</footer>
</body>
</html>"""

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

def generate_article_body(theme, products):
    product_info = ""
    for i, item in enumerate(products[:5], 1):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:50]
        price = p.get('itemPrice', 0)
        shop = p.get('shopName', '')
        review_avg = p.get('reviewAverage', 0)
        review_count = p.get('reviewCount', 0)
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        product_info += f"\n{i}位: {name} / 価格:¥{price:,} / ショップ:{shop} / 評価:{review_avg}点({review_count}件) / URL:{affiliate_url}\n"

    if not product_info:
        product_info = "商品データなし。一般的な情報で記事を生成してください。"

    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year

    prompt = f"""ガジェット専門アフィリエイトライターとして、HTMLの<body>内コンテンツのみを生成してください。

テーマ:【{year}年最新】{theme['title']} おすすめランキングTOP5
更新日:{today}
商品データ:{product_info}

出力ルール:
- <body>タグや<html>タグは不要。divやsectionのみ出力
- CSSクラスは以下を使用:hero, hero-badge, container, section-title, intro-box, toc, guide-grid, guide-item, guide-item-icon, guide-item-title, guide-item-desc, rank-card, rank-header(gold/silver/bronze), rank-number, rank-label, rank-body, rank-name, rank-shop, rank-review, pros-cons, pros, cons, price-buy, price, btn-buy, table-wrap, faq, faq-item, faq-q, faq-a
- マークダウン記法は使わない
- 購入ボタン: <a href="商品URL" class="btn-buy" target="_blank">🛒 楽天で購入する</a>

構成:
1. ヒーローセクション(class="hero")
2. 導入文(class="intro-box")
3. 目次(class="toc")
4. 選び方ガイド(class="guide-grid" 4項目)
5. ランキングTOP5(class="rank-card" 各商品)
6. 比較表(class="table-wrap")
7. FAQ(class="faq" 3問)"""

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
        content = re.sub(r'```html\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        return content.strip()
    except Exception as e:
        print(f"Claude API エラー: {e}")
        return None

def build_html(theme, body_content):
    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year
    title = f"【{year}年最新】{theme['title']} おすすめ人気ランキングTOP5"
    description = f"{year}年最新の{theme['title']}おすすめランキングTOP5を徹底比較！選び方・比較表・FAQも充実。楽天市場の人気商品を専門家が厳選紹介。({today}更新)"
    start = HTML_TEMPLATE_START.format(title=title, description=description, site_url=SITE_URL)
    end = HTML_TEMPLATE_END.format(site_url=SITE_URL)
    return start + body_content + end

def get_github_file(filename):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return content, data['sha']
    return None, None

def upload_to_github(filename, content, commit_message):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
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
        print(f"✅ アップロード成功: {filename}")
        return True
    print(f"❌ アップロード失敗: {res.status_code}")
    return False

def update_articles_json(theme, filename, today):
    """記事一覧JSONを更新してトップページに反映"""
    articles_json, sha = get_github_file('articles.json')
    if articles_json:
        articles = json.loads(articles_json)
    else:
        articles = []

    year = datetime.now().year
    new_article = {
        'title': f"【{year}年最新】{theme['title']} おすすめ人気ランキングTOP5",
        'filename': filename,
        'category': theme['category'],
        'emoji': theme.get('emoji', '📱'),
        'date': today.strftime('%Y年%m月%d日'),
        'description': f"{theme['title']}のおすすめをランキング形式で徹底比較。選び方・比較表・FAQも充実。"
    }

    # 同じファイル名があれば更新、なければ先頭に追加
    exists = False
    for i, a in enumerate(articles):
        if a['filename'] == filename:
            articles[i] = new_article
            exists = True
            break
    if not exists:
        articles.insert(0, new_article)

    # 最新20件のみ保持
    articles = articles[:20]

    upload_to_github('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), f"Auto: 記事一覧更新 ({today.strftime('%Y/%m/%d')})")
    print(f"✅ articles.json更新完了")

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
        return False
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        tweepy.API(auth).update_status(text)
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
    body = generate_article_body(theme, products)
    if not body:
        print("❌ 記事生成失敗")
        return

    article_html = build_html(theme, body)
    print("✅ 記事生成完了")

    date_str = today.strftime('%Y%m%d')
    filename = f"{theme['filename']}-{date_str}.html"

    upload_to_github(filename, article_html, f"Auto: {theme['title']}記事生成 ({today.strftime('%Y/%m/%d')})")
    upload_to_github('sitemap.xml', update_sitemap([filename]), "Auto: サイトマップ更新")
    update_articles_json(theme, filename, today)

    tweet_text = f"🆕 新着記事！\n【{today.year}年最新】{theme['title']} おすすめランキングTOP5\n\n{SITE_URL}/{filename}\n\n#{theme['category']} #ガジェット #楽天"
    post_to_twitter(tweet_text)
    print(f"\n🎉 完了！ {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
