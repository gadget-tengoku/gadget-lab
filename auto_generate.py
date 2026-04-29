#!/usr/bin/env python3
import os, re, requests, base64, json, random, time
from datetime import datetime

RAKUTEN_APP_ID       = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY   = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
GITHUB_TOKEN         = os.environ['GITHUB_TOKEN']
GITHUB_REPO          = 'gadget-tengoku/gadget-lab'
SITE_URL             = 'https://gadget-tengoku.com'
SLOT                 = os.environ.get('SLOT', 'am')

TWITTER_API_KEY             = os.environ.get('API_KEY', '')
TWITTER_API_SECRET          = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN        = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

ALL_THEMES = [
    {'kw':'ワイヤレスイヤホン ノイキャン 通勤 Sony Bose','title':'通勤向けノイキャンイヤホン','cat':'イヤホン'},
    {'kw':'ワイヤレスイヤホン スポーツ 防水 Jabra','title':'スポーツ向けワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'ワイヤレスイヤホン 高音質 LDAC Sony','title':'音質重視ワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'ワイヤレスイヤホン コスパ Anker Soundcore','title':'コスパ重視ワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'骨伝導イヤホン Shokz AfterShokz','title':'骨伝導イヤホン','cat':'イヤホン'},
    {'kw':'ノイズキャンセリング ヘッドホン Sony WH Bose','title':'ノイキャンヘッドホン','cat':'オーディオ'},
    {'kw':'Bluetoothスピーカー 防水 JBL Anker','title':'防水Bluetoothスピーカー','cat':'オーディオ'},
    {'kw':'スマートウォッチ 健康管理 血圧 Garmin','title':'健康管理スマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'スマートウォッチ GPS ランニング Garmin','title':'ランニング向けGPSウォッチ','cat':'スマートウォッチ'},
    {'kw':'スマートウォッチ ビジネス Samsung Galaxy Watch','title':'ビジネス向けスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'キッズ スマートウォッチ GPS 子供 見守り','title':'キッズ向けスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'Apple Watch SE Series 9','title':'Apple Watch おすすめモデル','cat':'スマートウォッチ'},
    {'kw':'Garmin Forerunner Venu スマートウォッチ','title':'Garminスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'モバイルバッテリー 軽量 薄型 Anker CIO','title':'軽量薄型モバイルバッテリー','cat':'モバイル'},
    {'kw':'モバイルバッテリー 大容量 20000mAh Anker','title':'大容量モバイルバッテリー','cat':'モバイル'},
    {'kw':'モバイルバッテリー ノートPC 65W PD Anker','title':'ノートPC対応モバイルバッテリー','cat':'モバイル'},
    {'kw':'GaN充電器 コンパクト 65W Anker CIO','title':'GaNコンパクト充電器','cat':'モバイル'},
    {'kw':'ワイヤレス充電器 MagSafe Anker Belkin','title':'MagSafe対応ワイヤレス充電器','cat':'モバイル'},
    {'kw':'ゲーミングマウス 軽量 Logicool Razer','title':'軽量ゲーミングマウス','cat':'ゲーミング'},
    {'kw':'ゲーミングキーボード メカニカル Logicool HHKB','title':'メカニカルゲーミングキーボード','cat':'ゲーミング'},
    {'kw':'ゲーミングヘッドセット SteelSeries HyperX','title':'ゲーミングヘッドセット','cat':'ゲーミング'},
    {'kw':'ゲーミングモニター 144Hz ASUS LG','title':'ゲーミングモニター144Hz','cat':'PC周辺機器'},
    {'kw':'4Kモニター テレワーク LG Dell','title':'テレワーク向け4Kモニター','cat':'PC周辺機器'},
    {'kw':'ウェブカメラ フルHD Logicool Anker','title':'高画質ウェブカメラ','cat':'PC周辺機器'},
    {'kw':'USBハブ Type-C MacBook Anker','title':'MacBook向けUSB-Cハブ','cat':'PC周辺機器'},
    {'kw':'コンデンサーマイク USB 配信 Blue Yeti','title':'配信向けUSBマイク','cat':'PC周辺機器'},
    {'kw':'ロボット掃除機 マッピング iRobot Ecovacs','title':'マッピングロボット掃除機','cat':'スマートホーム'},
    {'kw':'スマート電球 LED Alexa Google Philips Hue','title':'スマートLED電球','cat':'スマートホーム'},
    {'kw':'防犯カメラ 屋外 ワイヤレス Arlo','title':'屋外ワイヤレス防犯カメラ','cat':'スマートホーム'},
    {'kw':'空気清浄機 花粉 Dyson Panasonic','title':'高性能空気清浄機','cat':'スマートホーム'},
    {'kw':'小型プロジェクター Anker Nebula','title':'小型プロジェクター','cat':'スマートホーム'},
    {'kw':'アクションカメラ 4K GoPro DJI','title':'4Kアクションカメラ','cat':'カメラ'},
    {'kw':'スマホ ジンバル DJI Osmo','title':'スマホ向けジンバル','cat':'カメラ'},
    {'kw':'ドライブレコーダー 前後 4K Vantrue','title':'前後4Kドライブレコーダー','cat':'カメラ'},
    {'kw':'電動歯ブラシ 音波 Philips Oral-B','title':'電動歯ブラシ','cat':'生活家電'},
    {'kw':'マッサージガン Theragun Hyperice','title':'マッサージガン','cat':'生活家電'},
    {'kw':'スマートロック 後付け Qrio SwitchBot','title':'スマートロック','cat':'スマートホーム'},
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
    r  = requests.put(url, headers=h, json=data)
    ok = r.status_code in [200, 201]
    print(f"  {'✅' if ok else '❌'} {path}")
    return ok

# ===== 楽天API =====
def fetch_products(keyword, hits=5):
    url    = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'
    params = {
        'format': 'json', 'keyword': keyword,
        'applicationId': RAKUTEN_APP_ID,
        'affiliateId': RAKUTEN_AFFILIATE_ID,
        'hits': hits, 'imageFlag': 1, 'sort': '-reviewCount',
    }
    try:
        r = requests.get(url, params=params, headers={'Referer': SITE_URL}, timeout=15)
        if r.ok:
            return r.json().get('Items', [])
        print(f"  楽天API {r.status_code}")
    except Exception as e:
        print(f"  楽天APIエラー: {e}")
    return []

# ===== HTML生成 =====
def build_html(title, theme, products):
    today = datetime.now().strftime('%Y年%m月%d日')
    year  = datetime.now().year

    num_labels = ['1位','2位','3位','4位','5位']
    num_class  = ['gold','silver','bronze','normal','normal']

    cards = ''
    rows  = ''

    for i, item in enumerate(products[:5]):
        p     = item.get('Item', {})
        name  = p.get('itemName', '')[:60]
        price = p.get('itemPrice', 0)
        shop  = p.get('shopName', '')[:20]
        ra    = float(p.get('reviewAverage', 0))
        rc    = int(p.get('reviewCount', 0))
        url   = p.get('affiliateUrl', p.get('itemUrl', '#'))
        imgs  = p.get('mediumImageUrls', [])
        img   = ''
        if imgs:
            raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            img = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)

        stars = '★' * int(ra) + '☆' * (5 - int(ra))
        img_html = f'<img src="{img}" alt="{name}" loading="lazy">' if img else '<div style="width:100%;height:140px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#ccc;font-size:13px">画像なし</div>'

        cards += f'''
<div class="rank-card">
  <div class="rank-header">
    <span class="rank-num {num_class[i]}">{i+1}</span>
    <span class="rank-label">{num_labels[i]}</span>
    <span class="rank-shop-name">{shop}</span>
  </div>
  <div class="rank-layout">
    <div class="rank-img-col">{img_html}</div>
    <div class="rank-info-col">
      <div class="rank-name">{name}</div>
      <div class="rank-review">
        <span class="stars">{stars}</span>
        <span>{ra:.1f}</span>
        <span class="review-count">（{rc:,}件）</span>
      </div>
      <div class="price-area">
        <div class="price">¥{price:,} <small>税込</small></div>
        <a href="{url}" class="btn-buy" target="_blank" rel="noopener sponsored"></a>
      </div>
    </div>
  </div>
</div>'''

        rows += f'<tr><td><span class="rank-no">{i+1}</span>{name[:28]}</td><td>¥{price:,}</td><td>{stars} {ra:.1f}</td><td>{rc:,}件</td><td><a href="{url}" target="_blank" rel="noopener sponsored" style="color:#e63900;font-weight:700">購入</a></td></tr>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新、{theme}のおすすめランキングTOP5。楽天市場の実売データとレビュー数をもとに選出。">
<link rel="canonical" href="{SITE_URL}/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
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

<div class="article-hero">
  <div class="article-hero-inner">
    <div class="article-cat">{theme}</div>
    <h1>{title}</h1>
    <div class="article-meta">
      <span>{today} 更新</span>
      <span>楽天市場 実売データ</span>
    </div>
  </div>
</div>

<div class="container">

  <div class="intro-box">
    この記事では、楽天市場の実際の売れ筋・レビュー数をもとに<strong>{theme}</strong>のおすすめモデルをTOP5形式でご紹介します。価格・評価・レビュー数を総合的に判断しています。
  </div>

  <nav class="toc">
    <div class="toc-title">目次</div>
    <ol>
      <li><a href="#ranking">おすすめランキングTOP5</a></li>
      <li><a href="#compare">スペック比較表</a></li>
      <li><a href="#guide">選び方のポイント</a></li>
    </ol>
  </nav>

  <section id="ranking">
    <h2 class="section-title">おすすめランキングTOP5</h2>
    <p style="font-size:12px;color:#aaa;margin-bottom:16px">※価格は{today}時点の楽天市場最安値。レビュー件数順に掲載。</p>
    {cards}
  </section>

  <section id="compare">
    <h2 class="section-title">スペック比較表</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </section>

  <section id="guide">
    <h2 class="section-title">選び方のポイント</h2>
    <div class="guide-grid">
      <div class="guide-item">
        <div class="guide-item-title">予算を決める</div>
        <div class="guide-item-desc">価格帯によっておすすめモデルが変わります。まず予算を明確にしましょう。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-title">レビュー数を確認</div>
        <div class="guide-item-desc">レビューが多いほど実績あり。1,000件以上なら安心して選べます。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-title">用途に合わせる</div>
        <div class="guide-item-desc">毎日の使い方をイメージして、必要な機能を絞り込みましょう。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-title">メーカー保証を確認</div>
        <div class="guide-item-desc">国内正規品は保証が充実。初期不良にも対応しやすいです。</div>
      </div>
    </div>
  </section>

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
  <p style="text-align:center;margin-top:12px;font-size:11px;color:#555">© {year} ガジェット天国</p>
</footer>

</body>
</html>'''

# ===== articles.json 更新 =====
def update_articles_json(theme, filename, img_url, today):
    content, sha = gh_get('articles.json')
    articles     = json.loads(content) if content else []
    year         = datetime.now().year
    new = {
        'title':       f"【{year}年最新】{theme['title']} おすすめランキングTOP5",
        'filename':    filename,
        'img_url':     img_url,
        'category':    theme['cat'],
        'theme_key':   theme['title'],
        'date':        today.strftime('%Y年%m月%d日'),
        'description': f"{theme['title']}のおすすめTOP5。楽天実売データ・レビュー数で比較。",
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

# ===== アーカイブ =====
def build_archive(articles):
    cards = ''
    for a in articles:
        img     = a.get('img_url', '')
        img_tag = f'<img src="{img}" alt="{a["title"]}" style="width:100%;height:160px;object-fit:contain;padding:10px;background:#fafafa">' if img else f'<div style="height:160px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;color:#ccc;font-size:13px">画像なし</div>'
        cards  += f'''
<a href="{a["filename"]}" class="archive-card" style="display:block;text-decoration:none;color:#111">
  {img_tag}
  <div style="padding:14px;border-top:1px solid #f0f0f0">
    <div style="font-size:11px;color:#e63900;font-weight:700;margin-bottom:5px">{a.get("category","")}</div>
    <div style="font-size:13px;font-weight:700;line-height:1.45;margin-bottom:6px">{a["title"]}</div>
    <div style="font-size:11px;color:#aaa">{a["date"]}</div>
  </div>
</a>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記事アーカイブ | ガジェット天国</title>
<meta name="description" content="ガジェット天国の全記事一覧。イヤホン・スマートウォッチ・ガジェットの最新比較記事。">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
</head>
<body>
<header>
  <div class="header-inner">
    <a href="{SITE_URL}/" class="logo">Gadget<span>天国</span></a>
    <nav><a href="{SITE_URL}/">トップ</a></nav>
  </div>
</header>
<div style="border-bottom:1px solid #e0e0e0;padding:24px 20px">
  <div style="max-width:1000px;margin:0 auto">
    <h1 style="font-size:24px;font-weight:900;color:#111">記事一覧</h1>
    <p style="font-size:13px;color:#999;margin-top:6px">全{len(articles)}記事 | 毎日更新</p>
  </div>
</div>
<div style="max-width:1000px;margin:0 auto;padding:28px 20px 60px">
  <div class="archive-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px">
    {cards}
  </div>
</div>
<footer>
  <div class="footer-inner">
    <div class="footer-logo">Gadget<span>天国</span></div>
    <div class="footer-links">
      <a href="{SITE_URL}/">トップ</a>
      <a href="{SITE_URL}/privacy.html">プライバシーポリシー</a>
    </div>
  </div>
  <p class="footer-note">© {datetime.now().year} ガジェット天国</p>
</footer>
</body>
</html>'''

# ===== 既存記事を一括再生成 =====
def regenerate_existing():
    print('\n既存記事を再生成中...')
    content, _ = gh_get('articles.json')
    if not content:
        return
    articles = json.loads(content)
    kw_map   = {t['title']: t['kw'] for t in ALL_THEMES}
    updated  = False

    for a in articles:
        filename  = a.get('filename', '')
        theme_key = a.get('theme_key', '')
        title     = a.get('title', '')
        keyword   = kw_map.get(theme_key)

        if not keyword:
            print(f'  スキップ: {theme_key}')
            continue

        print(f'  {theme_key}')
        products = fetch_products(keyword, hits=5)
        if not products:
            print(f'  商品取得失敗')
            time.sleep(1)
            continue

        html    = build_html(title, theme_key, products)
        _, sha  = gh_get(filename)
        gh_put(filename, html, f'Regenerate: {theme_key}', sha)

        # img_url 更新
        imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
        if imgs:
            raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            a['img_url'] = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)
            updated = True

        time.sleep(1.2)

    if updated:
        _, sha = gh_get('articles.json')
        gh_put('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), 'Auto: img_url更新', sha)
    print('既存記事の再生成完了')

# ===== サイトマップ =====
def build_sitemap(extra):
    today = datetime.now().strftime('%Y-%m-%d')
    bases = ['','earphone.html','smartwatch.html','battery.html','archive.html','privacy.html']
    urls  = [f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod><priority>{"1.0" if u=="" else "0.8"}</priority></url>' for u in bases]
    for f in extra:
        urls.append(f'  <url><loc>{SITE_URL}/{f}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'

# ===== Twitter =====
def post_twitter(text):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        return
    try:
        import tweepy
        auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        tweepy.API(auth).update_status(text)
        print('Twitter投稿成功')
    except Exception as e:
        print(f'Twitter投稿エラー: {e}')

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
    print(f"{today.strftime('%Y年%m月%d日')} [{SLOT.upper()}]")

    # 新記事生成
    theme    = select_theme()
    print(f"テーマ: {theme['title']}")
    products = fetch_products(theme['kw'], hits=5) or fetch_products('ガジェット 人気', hits=5)
    print(f"{len(products)}件取得")

    title    = f"【{today.year}年最新】{theme['title']} おすすめランキングTOP5"
    html     = build_html(title, theme['title'], products)
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

    articles = update_articles_json(theme, filename, img_url, today)

    # 既存記事を新レイアウトで再生成
    regenerate_existing()

    # アーカイブ更新
    content, _ = gh_get('articles.json')
    if content:
        _, sha = gh_get('archive.html')
        gh_put('archive.html', build_archive(json.loads(content)), 'Auto: アーカイブ更新', sha)

    # サイトマップ
    _, sha = gh_get('sitemap.xml')
    gh_put('sitemap.xml', build_sitemap([filename]), 'Auto: サイトマップ', sha)

    # Twitter
    post_twitter(f"新着記事\n{title}\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット")
    print(f"\n完了: {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
