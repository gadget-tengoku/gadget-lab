#!/usr/bin/env python3
import os, re, requests, base64, json, random, time
from datetime import datetime

RAKUTEN_APP_ID     = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO  = 'gadget-tengoku/gadget-lab'
SITE_URL     = 'https://gadget-tengoku.com'
SLOT         = os.environ.get('SLOT', 'am')

TWITTER_API_KEY          = os.environ.get('API_KEY', '')
TWITTER_API_SECRET       = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN     = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

ALL_THEMES = [
    {'kw':'ワイヤレスイヤホン ノイキャン 通勤','title':'通勤・テレワーク向けノイキャンイヤホン','cat':'イヤホン'},
    {'kw':'ワイヤレスイヤホン スポーツ 防水','title':'スポーツ向けワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'ワイヤレスイヤホン 高音質 LDAC','title':'音質重視ハイレゾイヤホン','cat':'イヤホン'},
    {'kw':'ワイヤレスイヤホン 安い コスパ','title':'5000円以下コスパイヤホン','cat':'イヤホン'},
    {'kw':'骨伝導イヤホン','title':'骨伝導イヤホン完全ガイド','cat':'イヤホン'},
    {'kw':'ヘッドホン ノイズキャンセリング','title':'テレワーク向けNCヘッドホン','cat':'オーディオ'},
    {'kw':'Bluetoothスピーカー 防水 アウトドア','title':'アウトドア向け防水スピーカー','cat':'オーディオ'},
    {'kw':'スマートウォッチ 健康管理 血圧','title':'健康管理スマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'スマートウォッチ GPS ランニング','title':'ランニング向けGPSウォッチ','cat':'スマートウォッチ'},
    {'kw':'スマートウォッチ ビジネス メンズ','title':'ビジネス向けスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'キッズ スマートウォッチ 子供 GPS','title':'キッズ向けスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'Apple Watch SE Series','title':'Apple Watch全モデル比較','cat':'スマートウォッチ'},
    {'kw':'Garmin スマートウォッチ ランニング','title':'Garmin完全比較ガイド','cat':'スマートウォッチ'},
    {'kw':'モバイルバッテリー 軽量 薄型 10000','title':'超軽量モバイルバッテリー','cat':'モバイル'},
    {'kw':'モバイルバッテリー 大容量 20000 旅行','title':'旅行向け大容量バッテリー','cat':'モバイル'},
    {'kw':'モバイルバッテリー ノートPC 65W PD','title':'ノートPC対応急速充電バッテリー','cat':'モバイル'},
    {'kw':'GaN充電器 コンパクト 65W 100W','title':'GaN超コンパクト充電器','cat':'モバイル'},
    {'kw':'ワイヤレス充電器 MagSafe iPhone','title':'MagSafe対応ワイヤレス充電器','cat':'モバイル'},
    {'kw':'ゲーミングマウス 軽量 FPS','title':'FPS向け軽量ゲーミングマウス','cat':'ゲーミング'},
    {'kw':'ゲーミングキーボード メカニカル 青軸','title':'メカニカルゲーミングキーボード','cat':'ゲーミング'},
    {'kw':'ゲーミングヘッドセット サラウンド','title':'サラウンドゲーミングヘッドセット','cat':'ゲーミング'},
    {'kw':'ゲーミングモニター 144Hz 27インチ','title':'144Hzゲーミングモニター','cat':'PC周辺機器'},
    {'kw':'4Kモニター テレワーク 27インチ','title':'テレワーク向け4Kモニター','cat':'PC周辺機器'},
    {'kw':'ウェブカメラ フルHD 配信','title':'配信・テレワーク向けウェブカメラ','cat':'PC周辺機器'},
    {'kw':'USBハブ Type-C MacBook 7in1','title':'MacBook向けUSB-Cハブ','cat':'PC周辺機器'},
    {'kw':'マイク USB コンデンサー 配信','title':'配信向けUSBマイク','cat':'PC周辺機器'},
    {'kw':'ロボット掃除機 マッピング 水拭き','title':'マッピング水拭きロボット掃除機','cat':'スマートホーム'},
    {'kw':'スマートLED 電球 Alexa Google','title':'Alexa対応スマートLED電球','cat':'スマートホーム'},
    {'kw':'防犯カメラ 屋外 ワイヤレス','title':'屋外対応ワイヤレス防犯カメラ','cat':'スマートホーム'},
    {'kw':'空気清浄機 花粉 PM2.5 静音','title':'花粉PM2.5対策空気清浄機','cat':'スマートホーム'},
    {'kw':'小型プロジェクター ホームシアター','title':'小型ホームシアタープロジェクター','cat':'スマートホーム'},
    {'kw':'アクションカメラ 4K 防水 GoProクラス','title':'4K防水アクションカメラ','cat':'カメラ'},
    {'kw':'スマホ ジンバル スタビライザー','title':'スマホ動画向けジンバル','cat':'カメラ'},
    {'kw':'ドライブレコーダー 前後 4K 駐車監視','title':'前後4Kドライブレコーダー','cat':'カメラ'},
    {'kw':'電動歯ブラシ 音波 ホワイトニング','title':'音波電動歯ブラシ比較','cat':'生活家電'},
    {'kw':'マッサージガン 筋膜リリース 静音','title':'筋膜リリースマッサージガン','cat':'生活家電'},
    {'kw':'スマートロック 後付け 指紋認証','title':'後付け対応スマートロック','cat':'スマートホーム'},
]

# ===== GitHub API =====
def gh_get(path):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
    h   = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    r   = requests.get(url, headers=h)
    if r.status_code == 200:
        d = r.json()
        return base64.b64decode(d['content']).decode('utf-8'), d['sha']
    return None, None

def gh_put(path, content, msg, sha=None):
    url  = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
    h    = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    data = {'message': msg, 'content': base64.b64encode(content.encode()).decode()}
    if sha: data['sha'] = sha
    r = requests.put(url, headers=h, json=data)
    ok = r.status_code in [200, 201]
    print(f"  {'✅' if ok else '❌'} {path}")
    return ok

# ===== 楽天API =====
def fetch_products(keyword, hits=5):
    url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'
    params = {
        'format': 'json',
        'keyword': keyword,
        'applicationId': RAKUTEN_APP_ID,
        'affiliateId': RAKUTEN_AFFILIATE_ID,
        'hits': hits,
        'imageFlag': 1,
        'sort': '-reviewCount',
    }
    headers = {'Referer': 'https://gadget-tengoku.com'}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get('Items', [])
        print(f"  楽天API {r.status_code}: {r.text[:100]}")
        return []
    except Exception as e:
        print(f"  楽天APIエラー: {e}")
        return []

# ===== HTML生成 =====
def build_html(title, theme, products):
    today = datetime.now().strftime('%Y年%m月%d日')
    year  = datetime.now().year

    colors = ['gold','silver','bronze','normal','normal']
    labels = ['🥇 編集部イチオシ','🥈 コスパ優秀','🥉 人気急上昇','4位','5位']

    cards = ''
    rows  = ''

    for i, item in enumerate(products[:5]):
        p    = item.get('Item', {})
        name = p.get('itemName', '')[:55]
        price= p.get('itemPrice', 0)
        shop = p.get('shopName', '')[:18]
        ra   = float(p.get('reviewAverage', 0))
        rc   = int(p.get('reviewCount', 0))
        url  = p.get('affiliateUrl', p.get('itemUrl', '#'))
        imgs = p.get('mediumImageUrls', [])
        # 画像URLを大きく（128→400px）
        img  = ''
        if imgs:
            raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            img = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)
        stars = '★' * int(ra) + '☆' * (5 - int(ra))

        img_html = f'<img src="{img}" alt="{name}" loading="lazy" onerror="this.style.display=\'none\'">' if img else '<div style="font-size:48px;text-align:center;opacity:.2;padding:20px">📦</div>'

        cards += f'''
<div class="rank-card">
  <div class="rank-header {colors[i]}">
    <span class="rank-num {colors[i]}">{i+1}</span>
    <span class="rank-label">{labels[i]}</span>
    <span class="rank-shop-name">{shop}</span>
  </div>
  <div class="rank-layout">
    <div class="rank-img-col">{img_html}</div>
    <div class="rank-info-col">
      <div class="rank-name">{name}</div>
      <div class="rank-review">
        <span class="stars">{stars}</span>
        <strong>{ra:.1f}</strong>（{rc:,}件のレビュー）
      </div>
      <div class="price-buy">
        <div class="price">¥{price:,} <small>税込</small></div>
        <a href="{url}" class="btn-buy" target="_blank" rel="noopener sponsored">楽天市場で購入する</a>
      </div>
    </div>
  </div>
</div>'''

        rows += f'<tr><td><span class="rank-no">{i+1}位</span>{name[:25]}</td><td>¥{price:,}</td><td>{stars} {ra:.1f}</td><td>{rc:,}件</td><td><a href="{url}" target="_blank" rel="noopener sponsored" style="color:#BF0000;font-weight:700">購入→</a></td></tr>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新！{theme}のおすすめTOP5を楽天実売データで比較。レビュー数・評価点つき。({today}更新)">
<link rel="canonical" href="{SITE_URL}/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Oswald:wght@600;700&display=swap" rel="stylesheet">
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
  <h1>{title}</h1>
  <p class="hero-sub">楽天市場の実売データ・レビュー数をもとに厳選</p>
</div>

<div class="container">
  <div class="intro-box">
    この記事では楽天市場の実際の売れ筋・レビュー数をもとに<strong>{theme} TOP5</strong>を厳選しました。気になった商品はリンク先でレビューもご確認ください。
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
    <p style="font-size:12px;color:#999;margin-bottom:16px">※楽天市場のレビュー数順。価格は{today}時点。</p>
    {cards}
  </section>

  <section id="compare">
    <h2 class="section-title">📊 スペック比較表</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </section>

  <section id="guide">
    <h2 class="section-title">🔍 選び方のポイント</h2>
    <div class="guide-grid">
      <div class="guide-item"><div class="guide-item-icon">💰</div><div class="guide-item-title">予算を決める</div><div class="guide-item-desc">価格帯によっておすすめモデルが変わります。まず予算を決めましょう。</div></div>
      <div class="guide-item"><div class="guide-item-icon">⭐</div><div class="guide-item-title">レビュー数を確認</div><div class="guide-item-desc">1,000件以上のレビューがある商品は実績十分で安心です。</div></div>
      <div class="guide-item"><div class="guide-item-icon">🔄</div><div class="guide-item-title">用途に合わせる</div><div class="guide-item-desc">日常使い・スポーツ・ビジネスなど用途で最適モデルが変わります。</div></div>
      <div class="guide-item"><div class="guide-item-icon">🛡️</div><div class="guide-item-title">保証を確認</div><div class="guide-item-desc">国内正規品は保証が充実。長く安心して使えます。</div></div>
    </div>
  </section>
</div>

<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。</p>
  <p style="margin-top:8px;font-size:11px">© {year} ガジェット天国</p>
</footer>

</body>
</html>'''

# ===== articles.json 更新 =====
def update_articles_json(theme, filename, img_url, today):
    content, _ = gh_get('articles.json')
    articles   = json.loads(content) if content else []
    year       = datetime.now().year
    new = {
        'title':     f"【{year}年最新】{theme['title']} おすすめランキングTOP5",
        'filename':  filename,
        'img_url':   img_url,
        'category':  theme['cat'],
        'theme_key': theme['title'],
        'date':      today.strftime('%Y年%m月%d日'),
        'description': f"楽天実売データで{theme['title']}TOP5を比較。",
    }
    updated = False
    for i, a in enumerate(articles):
        if a['filename'] == filename:
            articles[i] = new
            updated = True
            break
    if not updated:
        articles.insert(0, new)
    articles = articles[:50]
    _, sha = gh_get('articles.json')
    gh_put('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), 'Auto: 記事一覧更新', sha)
    return articles

# ===== アーカイブ生成 =====
def build_archive(articles):
    cards = ''
    for a in articles:
        img     = a.get('img_url', '')
        img_tag = f'<img src="{img}" alt="{a["title"]}" style="width:100%;height:160px;object-fit:contain;background:#f5f5f5;padding:8px">' if img else f'<div style="height:160px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;font-size:48px">📱</div>'
        cards  += f'''
<a href="{a["filename"]}" style="display:block;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #eee;text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s" onmouseover="this.style.transform=\'translateY(-4px)\';this.style.boxShadow=\'0 8px 24px rgba(0,0,0,.1)\'" onmouseout="this.style.transform=\'\';this.style.boxShadow=\'\'">
  {img_tag}
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
<meta name="description" content="ガジェット天国の全記事一覧。家電・ガジェットの最新比較記事。">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&family=Oswald:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
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
  <h1>記事アーカイブ</h1>
  <p class="hero-sub">毎日更新中 | 全{len(articles)}記事</p>
</div>
<div class="container">
  <div class="archive-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px">
    {cards}
  </div>
</div>
<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">© {datetime.now().year} ガジェット天国</p>
</footer>
</body>
</html>'''

# ===== 既存記事を新レイアウトで再生成 =====
def regenerate_existing():
    """articles.jsonの既存記事を全て新フォーマットで再生成"""
    print('\n🔄 既存記事を新レイアウトで再生成中...')
    content, _ = gh_get('articles.json')
    if not content:
        return
    articles = json.loads(content)

    # theme_key → keyword の対応表
    kw_map = {t['title']: t['kw'] for t in ALL_THEMES}

    for a in articles:
        filename  = a.get('filename', '')
        theme_key = a.get('theme_key', '')
        title     = a.get('title', '')
        keyword   = kw_map.get(theme_key)

        if not keyword:
            # ALL_THEMESにない場合はスキップ
            print(f'  ⏭ スキップ（テーマ不明）: {theme_key}')
            continue

        print(f'  🔄 {theme_key}')
        products = fetch_products(keyword, hits=5)
        if not products:
            print(f'  ⚠ 商品取得失敗、スキップ')
            time.sleep(1)
            continue

        html = build_html(title, theme_key, products)
        _, sha = gh_get(filename)
        gh_put(filename, html, f'Regenerate: {theme_key}', sha)

        # img_url を最新に更新
        imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
        if imgs:
            raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            a['img_url'] = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)

        time.sleep(1.2)  # API制限対策

    # articles.json を img_url 更新で保存
    _, sha = gh_get('articles.json')
    gh_put('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), 'Auto: img_url更新', sha)
    print('✅ 既存記事の再生成完了')

# ===== サイトマップ =====
def build_sitemap(extra_files):
    today = datetime.now().strftime('%Y-%m-%d')
    bases = ['', 'earphone.html', 'smartwatch.html', 'battery.html', 'archive.html', 'privacy.html']
    urls  = [f'  <url>\n    <loc>{SITE_URL}/{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>{"1.0" if u=="" else "0.8"}</priority>\n  </url>' for u in bases]
    for f in extra_files:
        urls.append(f'  <url>\n    <loc>{SITE_URL}/{f}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'

# ===== Twitter =====
def post_twitter(text):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        return
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        tweepy.API(auth).update_status(text)
        print('✅ Twitter投稿成功')
    except Exception as e:
        print(f'Twitter投稿エラー: {e}')

# ===== テーマ選択 =====
def select_theme():
    content, _ = gh_get('articles.json')
    used = set()
    if content:
        try:
            used = set(a.get('theme_key','') for a in json.loads(content)[:40])
        except:
            pass
    available = [t for t in ALL_THEMES if t['title'] not in used]
    if not available:
        available = ALL_THEMES

    am_cats = ['イヤホン','オーディオ','スマートウォッチ']
    pm_cats = ['ゲーミング','PC周辺機器','スマートホーム','カメラ','モバイル','生活家電']
    pref    = am_cats if SLOT == 'am' else pm_cats
    pool    = [t for t in available if t['cat'] in pref] or available
    return random.choice(pool)

# ===== メイン =====
def main():
    today = datetime.now()
    print(f"📅 {today.strftime('%Y年%m月%d日')} [{SLOT.upper()}]")

    # 1. 新記事生成
    theme = select_theme()
    print(f"📝 テーマ: {theme['title']}")

    products = fetch_products(theme['kw'], hits=5)
    if not products:
        products = fetch_products('ガジェット 人気', hits=5)
    print(f"✅ {len(products)}件取得")

    title = f"【{today.year}年最新】{theme['title']} おすすめランキングTOP5"
    html  = build_html(title, theme['title'], products)

    date_str = today.strftime('%Y%m%d')
    safe     = re.sub(r'[^\w]', '-', theme['title'])[:25]
    filename = f"article-{safe}-{SLOT}-{date_str}.html"

    _, sha = gh_get(filename)
    gh_put(filename, html, f"Auto: {theme['title']} [{SLOT.upper()}]", sha)

    # サムネイル画像
    img_url = ''
    if products:
        imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
        if imgs:
            raw     = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            img_url = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)

    articles = update_articles_json(theme, filename, img_url, today)

    # 2. 既存記事を新レイアウトで一括再生成
    regenerate_existing()

    # 3. アーカイブ更新
    print('\n📚 アーカイブ更新中...')
    content, _ = gh_get('articles.json')
    if content:
        articles = json.loads(content)
        _, sha = gh_get('archive.html')
        gh_put('archive.html', build_archive(articles), 'Auto: アーカイブ更新', sha)

    # 4. サイトマップ更新
    _, sha = gh_get('sitemap.xml')
    gh_put('sitemap.xml', build_sitemap([filename]), 'Auto: サイトマップ更新', sha)

    # 5. Twitter投稿
    tweet = f"{'🆕' if SLOT=='am' else '🌙'} 新着記事！\n{title}\n\n楽天実売データで比較📊\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット #楽天"
    post_twitter(tweet)

    print(f"\n🎉 完了！ {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
