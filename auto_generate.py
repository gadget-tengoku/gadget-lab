#!/usr/bin/env python3
import os
import re
import requests
import base64
import json
import random
from datetime import datetime

RAKUTEN_APP_ID = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
CLAUDE_API_KEY = os.environ['CLAUDE_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = 'gadget-tengoku/gadget-lab'
SITE_URL = 'https://gadget-tengoku.com'
SLOT = os.environ.get('SLOT', 'am')

TWITTER_API_KEY = os.environ.get('API_KEY', '')
TWITTER_API_SECRET = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

ALL_THEMES = [
    {'kw':'ワイヤレスイヤホン ノイキャン 通勤','title':'通勤・テレワーク向けノイキャンイヤホン','cat':'イヤホン','emoji':'🎧'},
    {'kw':'ワイヤレスイヤホン スポーツ 防水','title':'スポーツ・ランニング向けイヤホン','cat':'イヤホン','emoji':'🏃'},
    {'kw':'ワイヤレスイヤホン 高音質 LDAC','title':'音質重視ハイレゾイヤホン','cat':'イヤホン','emoji':'🎵'},
    {'kw':'ワイヤレスイヤホン 安い 5000円','title':'5000円以下コスパイヤホン','cat':'イヤホン','emoji':'💰'},
    {'kw':'骨伝導イヤホン 開放型','title':'骨伝導イヤホン完全ガイド','cat':'イヤホン','emoji':'🦴'},
    {'kw':'ゲーミングイヤホン 低遅延','title':'ゲーム向け低遅延イヤホン','cat':'ゲーミング','emoji':'🎮'},
    {'kw':'ヘッドホン ノイズキャンセリング','title':'テレワーク向けNCヘッドホン','cat':'オーディオ','emoji':'🎧'},
    {'kw':'Bluetoothスピーカー 防水 アウトドア','title':'アウトドア向け防水スピーカー','cat':'オーディオ','emoji':'🔊'},
    {'kw':'スマートウォッチ 血圧 健康管理','title':'健康管理スマートウォッチ','cat':'スマートウォッチ','emoji':'❤️'},
    {'kw':'スマートウォッチ GPS ランニング','title':'ランニング向けGPSウォッチ','cat':'スマートウォッチ','emoji':'🏅'},
    {'kw':'スマートウォッチ ビジネス','title':'ビジネス向けスマートウォッチ','cat':'スマートウォッチ','emoji':'💼'},
    {'kw':'スマートウォッチ 子供 キッズ','title':'キッズ向けスマートウォッチ','cat':'スマートウォッチ','emoji':'👦'},
    {'kw':'Apple Watch おすすめ 比較','title':'Apple Watch全モデル比較','cat':'スマートウォッチ','emoji':'⌚'},
    {'kw':'Garmin スマートウォッチ','title':'Garmin完全比較ガイド','cat':'スマートウォッチ','emoji':'🗺️'},
    {'kw':'モバイルバッテリー 軽量 薄型','title':'超軽量モバイルバッテリー','cat':'モバイル','emoji':'🔋'},
    {'kw':'モバイルバッテリー 大容量 旅行','title':'旅行向け大容量バッテリー','cat':'モバイル','emoji':'✈️'},
    {'kw':'モバイルバッテリー ノートPC 65W','title':'ノートPC対応急速充電バッテリー','cat':'モバイル','emoji':'💻'},
    {'kw':'GaN充電器 100W コンパクト','title':'GaN100W超コンパクト充電器','cat':'モバイル','emoji':'⚡'},
    {'kw':'ワイヤレス充電器 MagSafe','title':'MagSafe対応ワイヤレス充電器','cat':'モバイル','emoji':'🔌'},
    {'kw':'ゲーミングマウス 軽量 FPS','title':'FPS向け軽量ゲーミングマウス','cat':'ゲーミング','emoji':'🖱️'},
    {'kw':'ゲーミングキーボード メカニカル','title':'メカニカルゲーミングキーボード','cat':'ゲーミング','emoji':'⌨️'},
    {'kw':'ゲーミングヘッドセット サラウンド','title':'サラウンドゲーミングヘッドセット','cat':'ゲーミング','emoji':'🎮'},
    {'kw':'ゲーミングチェア 腰痛','title':'腰痛対策ゲーミングチェア','cat':'ゲーミング','emoji':'🪑'},
    {'kw':'モニター 144Hz ゲーミング','title':'144Hzゲーミングモニター','cat':'PC周辺機器','emoji':'🖥️'},
    {'kw':'モニター 4K テレワーク','title':'テレワーク向け4Kモニター','cat':'PC周辺機器','emoji':'📺'},
    {'kw':'ウェブカメラ 配信 テレワーク','title':'配信・テレワーク向けカメラ','cat':'PC周辺機器','emoji':'📸'},
    {'kw':'USBハブ Type-C MacBook','title':'MacBook向けUSB-Cハブ','cat':'PC周辺機器','emoji':'🔗'},
    {'kw':'ロボット掃除機 マッピング 水拭き','title':'マッピング水拭きロボット掃除機','cat':'スマートホーム','emoji':'🤖'},
    {'kw':'スマートLED 電球 Alexa','title':'Alexa対応スマートLED','cat':'スマートホーム','emoji':'💡'},
    {'kw':'防犯カメラ 屋外 AI検知','title':'AI検知屋外防犯カメラ','cat':'スマートホーム','emoji':'🔒'},
    {'kw':'空気清浄機 花粉 PM2.5','title':'花粉PM2.5対策空気清浄機','cat':'スマートホーム','emoji':'🌿'},
    {'kw':'プロジェクター 小型 ホームシアター','title':'小型ホームシアタープロジェクター','cat':'スマートホーム','emoji':'🎬'},
    {'kw':'アクションカメラ 4K 防水','title':'4K防水アクションカメラ','cat':'カメラ','emoji':'🏍️'},
    {'kw':'ジンバル スタビライザー スマホ','title':'スマホ動画向けジンバル','cat':'カメラ','emoji':'🎥'},
    {'kw':'ドライブレコーダー 前後 4K','title':'前後4Kドライブレコーダー','cat':'カメラ','emoji':'🚗'},
    {'kw':'電動歯ブラシ 音波','title':'音波電動歯ブラシ比較','cat':'生活家電','emoji':'🦷'},
    {'kw':'マッサージガン 筋膜リリース','title':'筋膜リリースマッサージガン','cat':'生活家電','emoji':'💪'},
    {'kw':'Switch アクセサリー ケース','title':'Nintendo Switchアクセサリー','cat':'ゲーミング','emoji':'🕹️'},
    {'kw':'スマートロック 後付け 指紋','title':'後付け対応スマートロック','cat':'スマートホーム','emoji':'🗝️'},
    {'kw':'マイク 配信 USB','title':'配信向けUSBマイク','cat':'PC周辺機器','emoji':'🎙️'},
]

def get_github_file(filename):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return base64.b64decode(data['content']).decode('utf-8'), data['sha']
    return None, None

def upload_to_github(filename, content, commit_message, binary=False):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    sha = None
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json().get('sha')
    if binary:
        encoded = base64.b64encode(content).decode('utf-8')
    else:
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

def get_used_themes():
    content, _ = get_github_file('articles.json')
    if not content:
        return set()
    try:
        articles = json.loads(content)
        return set(a.get('theme_key', '') for a in articles[:40])
    except:
        return set()

def select_theme(slot):
    used = get_used_themes()
    available = [t for t in ALL_THEMES if t['title'] not in used]
    if not available:
        available = ALL_THEMES
    am_cats = ['イヤホン', 'オーディオ', 'スマートウォッチ']
    pm_cats = ['ゲーミング', 'PC周辺機器', 'スマートホーム', 'カメラ', 'モバイル', '生活家電']
    preferred_cats = am_cats if slot == 'am' else pm_cats
    preferred = [t for t in available if t['cat'] in preferred_cats]
    return random.choice(preferred) if preferred else random.choice(available)

def fetch_rakuten_products(keyword, hits=5):
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
    params = {
        'format': 'json', 'keyword': keyword, 'genreId': 0,
        'applicationId': RAKUTEN_APP_ID, 'accessKey': RAKUTEN_ACCESS_KEY,
        'hits': hits, 'affiliateId': RAKUTEN_AFFILIATE_ID,
        'imageFlag': 1, 'sort': '-reviewCount'
    }
    headers = {'Referer': 'https://gadget-tengoku.com'}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        return res.json().get('Items', [])
    except Exception as e:
        print(f"楽天API エラー: {e}")
        return []

def build_article_html(theme, products):
    """画像左・情報右のサイドバイサイドレイアウトで記事生成"""
    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year
    title = f"【{year}年最新】{theme['title']} おすすめランキングTOP5"

    rank_colors = ['gold', 'silver', 'bronze', 'normal', 'normal']
    rank_labels = ['🥇 編集部イチオシ', '🥈 コスパ優秀', '🥉 人気急上昇', '4位', '5位']

    product_cards = ''
    for i, item in enumerate(products[:5]):
        p = item.get('Item', {})
        name = p.get('itemName', 'N/A')[:60]
        price = p.get('itemPrice', 0)
        shop = p.get('shopName', '')[:20]
        review_avg = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        img_url = p.get('mediumImageUrls', [{}])[0].get('imageUrl', '') if p.get('mediumImageUrls') else ''
        # 大きい画像URLを取得（mediumImageUrls → 画像サイズを128→400に変換）
        large_img_url = img_url.replace('?_ex=128x128', '?_ex=400x400') if img_url else ''
        item_code = p.get('itemCode', '')
        review_url = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':', '/')}/1.1/" if item_code else affiliate_url
        stars_full = int(review_avg)
        stars_html = '★' * stars_full + '☆' * (5 - stars_full)
        color = rank_colors[i]
        label = rank_labels[i]

        # 商品画像HTML（大きい画像を優先）
        display_img = large_img_url or img_url
        if display_img:
            img_html = f'<img src="{display_img}" alt="{name}" loading="lazy" onerror="this.src=\'{img_url}\'">'
        else:
            img_html = f'<div class="rank-img-placeholder">{theme["emoji"]}</div>'

        product_cards += f'''
<div class="rank-card" id="rank{i+1}">
  <div class="rank-header {color}">
    <span class="rank-number">{i+1}</span>
    <span class="rank-label">{label}</span>
    <span class="rank-shop-tag">{shop}</span>
  </div>
  <div class="rank-body">
    <div class="rank-layout">
      <div class="rank-img-col">
        {img_html}
      </div>
      <div class="rank-info-col">
        <div class="rank-name">{name}</div>
        <div class="rank-review">
          <span class="stars">{stars_html}</span>
          <strong>{review_avg:.1f}</strong>
          <a href="{review_url}" target="_blank" rel="noopener">（{review_count:,}件のレビューを見る →）</a>
        </div>
        <div class="price-buy">
          <div class="price">¥{price:,} <small>税込</small></div>
          <a href="{affiliate_url}" class="btn-buy" target="_blank" rel="noopener sponsored">楽天市場で購入する</a>
        </div>
      </div>
    </div>
  </div>
</div>'''

    # 比較表
    table_rows = ''
    for i, item in enumerate(products[:5]):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:28]
        price = p.get('itemPrice', 0)
        review_avg = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        stars = '★' * int(review_avg) + '☆' * (5 - int(review_avg))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        table_rows += f'''<tr>
<td><span class="rank-no">{i+1}位</span>{name}</td>
<td>¥{price:,}</td>
<td>{stars} {review_avg:.1f}</td>
<td>{review_count:,}件</td>
<td><a href="{affiliate_url}" target="_blank" rel="noopener sponsored" style="color:#BF0000;font-weight:700">購入→</a></td>
</tr>'''

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新の{theme["title"]}TOP5を楽天実売データで比較。実際のレビュー数・評価点つき。({today}更新)">
<link rel="canonical" href="{SITE_URL}/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
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

<div class="hero">
  <div class="hero-badge">{today} 更新</div>
  <h1>{theme["emoji"]} {title}</h1>
  <p class="hero-sub">楽天市場の実売データ・レビュー数をもとに厳選</p>
</div>

<div class="container">

  <div class="intro-box">
    <p>この記事では楽天市場の実際の売れ筋・レビュー数をもとに<strong>{theme["title"]} TOP5</strong>を厳選しました。気になった商品はリンク先の楽天レビューもご確認ください。</p>
  </div>

  <nav class="toc">
    <div class="toc-title">この記事の目次</div>
    <ol>
      <li><a href="#ranking">おすすめランキングTOP5</a></li>
      <li><a href="#compare">スペック比較表</a></li>
      <li><a href="#guide">選び方のポイント</a></li>
    </ol>
  </nav>

  <section id="ranking">
    <h2 class="section-title">🏆 おすすめランキングTOP5</h2>
    <p style="font-size:.8rem;color:#999;margin-bottom:16px">※楽天市場のレビュー数順。価格は{today}時点のものです。</p>
    {product_cards}
  </section>

  <section id="compare">
    <h2 class="section-title">📊 スペック比較表</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
  </section>

  <section id="guide">
    <h2 class="section-title">🔍 選び方のポイント</h2>
    <div class="guide-grid">
      <div class="guide-item">
        <div class="guide-item-icon">💰</div>
        <div class="guide-item-title">予算を決める</div>
        <div class="guide-item-desc">まず予算を明確に。5,000円・1万円・3万円以上でおすすめモデルが変わります。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-icon">⭐</div>
        <div class="guide-item-title">レビュー数を確認</div>
        <div class="guide-item-desc">1,000件以上のレビューがあれば実績十分。安心して購入できます。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-icon">🔄</div>
        <div class="guide-item-title">用途に合わせる</div>
        <div class="guide-item-desc">日常使い・スポーツ・ビジネスなど用途で最適モデルが変わります。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-icon">🛡️</div>
        <div class="guide-item-title">保証・サポート</div>
        <div class="guide-item-desc">国内正規品は保証が充実。安心して長く使えます。</div>
      </div>
    </div>
  </section>

</div>

<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。商品情報・価格は楽天市場の情報に基づきます。</p>
  <p style="margin-top:8px;font-size:.72rem">© {year} ガジェット天国</p>
</footer>
</body>
</html>'''
    return html

def update_articles_json(theme, filename, img_url, today):
    articles_json, _ = get_github_file('articles.json')
    articles = json.loads(articles_json) if articles_json else []
    year = datetime.now().year
    new_article = {
        'title': f"【{year}年最新】{theme['title']} おすすめランキングTOP5",
        'filename': filename,
        'img_url': img_url,
        'category': theme['cat'],
        'emoji': theme.get('emoji', '📱'),
        'theme_key': theme['title'],
        'date': today.strftime('%Y年%m月%d日'),
        'description': f"楽天実売データで{theme['title']}TOP5を比較。レビュー数・評価点つき。"
    }
    exists = False
    for i, a in enumerate(articles):
        if a['filename'] == filename:
            articles[i] = new_article
            exists = True
            break
    if not exists:
        articles.insert(0, new_article)
    articles = articles[:50]
    upload_to_github('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), "Auto: 記事一覧更新")

def build_archive_page(articles):
    cards = ''
    for a in articles:
        img = a.get('img_url', '')
        img_html = f'<img src="{img}" alt="{a["title"]}" style="width:100%;height:160px;object-fit:contain;background:#f5f5f5;padding:8px">' if img else f'<div style="width:100%;height:160px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:50px">{a.get("emoji","📱")}</div>'
        cards += f'''
<a href="{a["filename"]}" style="display:block;background:white;border-radius:12px;overflow:hidden;border:1px solid #eee;transition:transform .2s,box-shadow .2s;text-decoration:none;color:inherit">
  {img_html}
  <div style="padding:14px">
    <div style="font-size:11px;color:#FF4D00;font-weight:700;margin-bottom:4px">{a.get("category","")}</div>
    <div style="font-size:14px;font-weight:700;line-height:1.4;margin-bottom:6px">{a["title"]}</div>
    <div style="font-size:11px;color:#888">📅 {a["date"]}</div>
  </div>
</a>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記事アーカイブ | ガジェット天国</title>
<meta name="description" content="ガジェット天国の全記事一覧。イヤホン・スマートウォッチ・ゲーミングなど家電・ガジェットの最新比較記事。">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
<style>
.archive-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;margin-top:24px}}
.archive-grid a:hover{{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.1)}}
</style>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="{SITE_URL}/" class="logo">Gadget<span>天国</span></a>
    <nav><a href="{SITE_URL}/">トップ</a></nav>
  </div>
</header>
<div class="hero">
  <div class="hero-badge">全記事一覧</div>
  <h1>📚 記事アーカイブ</h1>
  <p class="hero-sub">毎日更新中 | 全{len(articles)}記事</p>
</div>
<div class="container">
  <div class="archive-grid">
    {cards}
  </div>
</div>
<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">© 2026 ガジェット天国</p>
</footer>
</body>
</html>'''

def update_sitemap(new_files):
    today = datetime.now().strftime('%Y-%m-%d')
    base_urls = ['', 'earphone.html', 'smartwatch.html', 'battery.html', 'archive.html']
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
    slot = SLOT
    print(f"📅 {today.strftime('%Y年%m月%d日')} [{slot.upper()}]")

    theme = select_theme(slot)
    print(f"📝 テーマ: {theme['title']} ({theme['cat']})")

    print("🛒 楽天商品取得中...")
    products = fetch_rakuten_products(theme['kw'])
    if not products:
        products = fetch_rakuten_products('ガジェット 人気')
    print(f"✅ {len(products)}件取得")

    # サムネイル用の画像URL（1番目商品の大きい画像）
    img_url = ''
    if products:
        p = products[0].get('Item', {})
        imgs = p.get('mediumImageUrls', [])
        if imgs:
            raw = imgs[0].get('imageUrl', '')
            img_url = raw.replace('?_ex=128x128', '?_ex=400x400') if raw else raw

    print("📝 記事HTML生成中...")
    article_html = build_article_html(theme, products)
    print("✅ 記事生成完了")

    date_str = today.strftime('%Y%m%d')
    safe_title = re.sub(r'[^\w]', '-', theme['title'])[:25]
    filename = f"article-{safe_title}-{slot}-{date_str}.html"

    upload_to_github(filename, article_html, f"Auto: {theme['title']} [{slot.upper()}]")
    update_articles_json(theme, filename, img_url, today)

    print("📚 アーカイブページ更新中...")
    articles_json, _ = get_github_file('articles.json')
    if articles_json:
        articles = json.loads(articles_json)
        archive_html = build_archive_page(articles)
        upload_to_github('archive.html', archive_html, "Auto: アーカイブ更新")

    upload_to_github('sitemap.xml', update_sitemap([filename]), "Auto: サイトマップ更新")

    if slot == 'am':
        tweet = f"🆕 新着！{theme['emoji']}\n【{today.year}年最新】{theme['title']}TOP5\n\n楽天実売データ・レビュー数で比較📊\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット #楽天"
    else:
        tweet = f"🌙 本日の夜更新！{theme['emoji']}\n【{today.year}年】{theme['title']}おすすめTOP5\n\n実際のレビュー数で厳選🛒\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット天国"

    post_to_twitter(tweet)
    print(f"\n🎉 完了！ {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
