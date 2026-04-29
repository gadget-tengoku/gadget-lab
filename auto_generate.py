#!/usr/bin/env python3
import os, re, requests, base64, json, random, time
from datetime import datetime

WORKER_URL           = 'https://rakuten-proxy.sobamoripaya.workers.dev'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
GITHUB_TOKEN         = os.environ['GITHUB_TOKEN']
GITHUB_REPO          = 'gadget-tengoku/gadget-lab'
SITE_URL             = 'https://gadget-tengoku.com'
SLOT                 = os.environ.get('SLOT', 'am')

TWITTER_API_KEY             = os.environ.get('API_KEY', '')
TWITTER_API_SECRET          = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN        = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

# ===== 信頼ブランドリスト =====
TRUSTED_BRANDS = [
    'anker','sony','apple','samsung','garmin','bose','jbl','panasonic','sharp',
    'dyson','philips','lg','dell','logicool','logitech','shokz','jabra',
    'sennheiser','audio-technica','asus','microsoft','google','gopro','dji',
    'canon','nikon','fujifilm','irobot','ecovacs','switchbot','qrio','buffalo',
    'elecom','belkin','cio','mophie','anker','hhkb','realforce','razer',
    'steelseries','hyperx','corsair','sennheiser','beats',
    # 日本語表記
    'パナソニック','シャープ','ソニー','アンカー','エレコム','バッファロー',
    'キヤノン','ニコン','富士フイルム','ダイソン','フィリップス',
]

def is_trusted(item):
    p    = item.get('Item', {})
    text = (p.get('itemName', '') + ' ' + p.get('shopName', '')).lower()
    return any(b.lower() in text for b in TRUSTED_BRANDS)

# ===== テーマ定義（シンプルなキーワードで確実にヒット） =====
ALL_THEMES = [
    {'kw':'Sony WH-1000XM5','title':'通勤向けノイキャンイヤホン','cat':'イヤホン'},
    {'kw':'Jabra ワイヤレスイヤホン スポーツ','title':'スポーツ向けワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'Sony LDAC ワイヤレスイヤホン','title':'音質重視ワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'Anker Soundcore イヤホン','title':'コスパ重視ワイヤレスイヤホン','cat':'イヤホン'},
    {'kw':'Shokz 骨伝導イヤホン','title':'骨伝導イヤホン','cat':'イヤホン'},
    {'kw':'Sony WH-1000XM5 ヘッドホン','title':'ノイキャンヘッドホン','cat':'オーディオ'},
    {'kw':'JBL Bluetoothスピーカー 防水','title':'防水Bluetoothスピーカー','cat':'オーディオ'},
    {'kw':'Garmin スマートウォッチ 健康管理','title':'健康管理スマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'Garmin Forerunner GPS ランニング','title':'ランニング向けGPSウォッチ','cat':'スマートウォッチ'},
    {'kw':'Samsung Galaxy Watch','title':'ビジネス向けスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'Apple Watch SE','title':'Apple Watch おすすめモデル','cat':'スマートウォッチ'},
    {'kw':'Garmin Venu スマートウォッチ','title':'Garminスマートウォッチ','cat':'スマートウォッチ'},
    {'kw':'Anker モバイルバッテリー 軽量','title':'軽量薄型モバイルバッテリー','cat':'モバイル'},
    {'kw':'Anker モバイルバッテリー 20000mAh','title':'大容量モバイルバッテリー','cat':'モバイル'},
    {'kw':'Anker GaN充電器 65W','title':'GaNコンパクト充電器','cat':'モバイル'},
    {'kw':'Anker Belkin MagSafe ワイヤレス充電器','title':'MagSafe対応ワイヤレス充電器','cat':'モバイル'},
    {'kw':'Logicool ゲーミングマウス G','title':'軽量ゲーミングマウス','cat':'ゲーミング'},
    {'kw':'Logicool ゲーミングキーボード G','title':'メカニカルゲーミングキーボード','cat':'ゲーミング'},
    {'kw':'SteelSeries HyperX ゲーミングヘッドセット','title':'ゲーミングヘッドセット','cat':'ゲーミング'},
    {'kw':'ASUS LG ゲーミングモニター 144Hz','title':'ゲーミングモニター','cat':'PC周辺機器'},
    {'kw':'LG Dell 4Kモニター','title':'テレワーク向け4Kモニター','cat':'PC周辺機器'},
    {'kw':'Logicool ウェブカメラ C920','title':'高画質ウェブカメラ','cat':'PC周辺機器'},
    {'kw':'Anker USBハブ Type-C','title':'MacBook向けUSB-Cハブ','cat':'PC周辺機器'},
    {'kw':'iRobot ロボット掃除機','title':'マッピングロボット掃除機','cat':'スマートホーム'},
    {'kw':'Philips Hue スマート電球','title':'スマートLED電球','cat':'スマートホーム'},
    {'kw':'Dyson Panasonic 空気清浄機','title':'高性能空気清浄機','cat':'スマートホーム'},
    {'kw':'Anker Nebula プロジェクター','title':'小型プロジェクター','cat':'スマートホーム'},
    {'kw':'GoPro アクションカメラ','title':'4Kアクションカメラ','cat':'カメラ'},
    {'kw':'DJI Osmo スマホ ジンバル','title':'スマホ向けジンバル','cat':'カメラ'},
    {'kw':'Philips 電動歯ブラシ ソニッケアー','title':'電動歯ブラシ','cat':'生活家電'},
    {'kw':'SwitchBot スマートロック','title':'スマートロック','cat':'スマートホーム'},
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

def gh_delete(path, sha, msg):
    url  = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
    h    = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    data = {'message': msg, 'sha': sha}
    r    = requests.delete(url, headers=h, json=data)
    ok   = r.status_code in [200, 204]
    print(f"  {'🗑' if ok else '❌削除失敗'} {path}")
    return ok

# ===== 楽天商品取得（Worker経由・ブラウザ偽装・リトライあり） =====
WORKER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gadget-tengoku.com/',
    'Origin':  'https://gadget-tengoku.com',
}

def fetch_products(keyword, hits=10, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(
                WORKER_URL,
                params={'keyword': keyword, 'hits': hits},
                headers=WORKER_HEADERS,
                timeout=20
            )
            if r.ok:
                items = r.json().get('Items', [])
                if items:
                    print(f"  '{keyword[:30]}' → {len(items)}件")
                    return items
            print(f"  Worker {r.status_code} (attempt {attempt+1})")
        except Exception as e:
            print(f"  Workerエラー: {e} (attempt {attempt+1})")
        time.sleep(2)
    return []

def fetch_trusted(keyword, need=5):
    """信頼ブランドのみ取得。足りなければ全件から補完"""
    items   = fetch_products(keyword, hits=20)
    trusted = [i for i in items if is_trusted(i)]
    if len(trusted) >= 3:
        return trusted[:need]
    # 信頼ブランドが少ない場合は全件から（空にしない）
    return items[:need]

# ===== 記事HTML生成 =====
def build_html(title, theme, products):
    today = datetime.now().strftime('%Y年%m月%d日')
    year  = datetime.now().year
    num_class = ['gold','silver','bronze','normal','normal']

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

        stars    = '★' * int(ra) + '☆' * (5 - int(ra))
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
      <div class="rank-review">
        <span class="stars">{stars}</span>
        <span>{ra:.1f}</span>
        <span class="review-count">({rc:,}件のレビュー)</span>
      </div>
      <div class="price-area">
        <div class="price">¥{price:,} <small>税込</small></div>
        <a href="{url}" class="btn-buy" target="_blank" rel="noopener sponsored">楽天市場で購入する</a>
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
    この記事では、楽天市場の実際の売れ筋・レビュー数をもとに<strong>{theme}</strong>のおすすめモデルをTOP5形式でご紹介します。価格・評価・レビュー数を総合的に判断して選出しています。
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
      <div class="guide-item"><div class="guide-item-title">予算を決める</div><div class="guide-item-desc">価格帯によっておすすめモデルが変わります。まず予算を明確にしましょう。</div></div>
      <div class="guide-item"><div class="guide-item-title">レビュー数を確認</div><div class="guide-item-desc">レビューが多いほど実績あり。1,000件以上なら安心して選べます。</div></div>
      <div class="guide-item"><div class="guide-item-title">用途に合わせる</div><div class="guide-item-desc">毎日の使い方をイメージして、必要な機能を絞り込みましょう。</div></div>
      <div class="guide-item"><div class="guide-item-title">保証を確認</div><div class="guide-item-desc">国内正規品は保証が充実。初期不良にも対応しやすいです。</div></div>
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
  <p style="text-align:center;margin-top:12px;font-size:11px;color:#444">© {year} ガジェット天国</p>
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

# ===== 既存記事を再生成・空記事削除 =====
def regenerate_and_cleanup():
    print('\n既存記事を再生成・クリーンアップ中...')
    content, _ = gh_get('articles.json')
    if not content:
        return
    articles = json.loads(content)
    kw_map   = {t['title']: t['kw'] for t in ALL_THEMES}

    keep     = []  # 残す記事
    updated  = False

    for a in articles:
        filename  = a.get('filename', '')
        theme_key = a.get('theme_key', '')
        title     = a.get('title', '')
        keyword   = kw_map.get(theme_key)

        if not keyword:
            print(f'  スキップ（テーマ不明）: {theme_key}')
            keep.append(a)
            continue

        print(f'  再生成: {theme_key}')
        products = fetch_trusted(keyword, need=5)

        if not products:
            # 商品取得できなかった → 記事をGitHubから削除
            print(f'  商品0件 → 記事を削除: {filename}')
            _, sha = gh_get(filename)
            if sha:
                gh_delete(filename, sha, f'Cleanup: 空記事を削除 {filename}')
            updated = True
            # keep に追加しない（articles.jsonから除外）
            continue

        html   = build_html(title, theme_key, products)
        _, sha = gh_get(filename)
        if gh_put(filename, html, f'Regenerate: {theme_key}', sha):
            # img_url 更新
            imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
            if imgs:
                raw = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
                a['img_url'] = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)
                updated = True
            keep.append(a)
        else:
            keep.append(a)  # 更新失敗でも残す

        time.sleep(1.5)

    if updated:
        _, sha = gh_get('articles.json')
        gh_put('articles.json', json.dumps(keep, ensure_ascii=False, indent=2), 'Cleanup: articles.json更新', sha)
        print(f'  articles.json 更新完了（{len(keep)}件）')

    print('再生成・クリーンアップ完了')

# ===== アーカイブ =====
def build_archive(articles):
    # サムネあり記事のみ
    articles = [a for a in articles if a.get('img_url', '').strip()]
    cards = ''
    for a in articles:
        img_tag = f'<img src="{a["img_url"]}" alt="{a["title"]}" style="width:100%;height:150px;object-fit:contain;padding:10px;background:#fafafa">'
        cards  += f'''
<a href="{a["filename"]}" style="display:block;border:1px solid #e8e8e8;border-radius:6px;overflow:hidden;text-decoration:none;color:#111;transition:box-shadow .2s" onmouseover="this.style.boxShadow=\'0 4px 16px rgba(0,0,0,.08)\'" onmouseout="this.style.boxShadow=\'\'">
  {img_tag}
  <div style="padding:12px;border-top:1px solid #f0f0f0">
    <div style="font-size:11px;color:#e63900;font-weight:700;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">{a.get("category","")}</div>
    <div style="font-size:13px;font-weight:700;line-height:1.45;margin-bottom:5px">{a["title"]}</div>
    <div style="font-size:11px;color:#bbb">{a["date"]}</div>
  </div>
</a>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記事一覧 | ガジェット天国</title>
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
<div style="border-bottom:1px solid #e8e8e8;padding:24px 20px">
  <div style="max-width:1000px;margin:0 auto">
    <h1 style="font-size:22px;font-weight:900">記事一覧</h1>
    <p style="font-size:13px;color:#aaa;margin-top:5px">全{len(articles)}記事 | 毎日更新</p>
  </div>
</div>
<div style="max-width:1000px;margin:0 auto;padding:24px 20px 56px">
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px">
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

# ===== サイトマップ =====
def build_sitemap(extra):
    today = datetime.now().strftime('%Y-%m-%d')
    bases = ['','earphone.html','smartwatch.html','battery.html','archive.html','privacy.html']
    urls  = [f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod><priority>{"1.0" if u=="" else "0.8"}</priority></url>' for u in bases]
    for f in extra:
        urls.append(f'  <url><loc>{SITE_URL}/{f}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'

# ===== Twitter投稿 =====
def post_twitter(title, url, cat):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        print('⚠ Twitter: Secrets未設定のためスキップ')
        return
    try:
        import tweepy
        auth   = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        client = tweepy.API(auth)
        text   = f"新着記事📱\n{title}\n\n楽天市場の実売データで厳選しました。\n\n{url}\n\n#{cat} #ガジェット #楽天 #家電"
        client.update_status(text[:280])
        print('✅ Twitter投稿成功')
    except Exception as e:
        print(f'❌ Twitter投稿失敗: {e}')

# ===== テーマ選択 =====
def select_theme():
    content, _ = gh_get('articles.json')
    used = set()
    if content:
        try: used = {a.get('theme_key','') for a in json.loads(content)[:40]}
        except: pass
    available = [t for t in ALL_THEMES if t['title'] not in used] or ALL_THEMES
    am_cats = ['イヤホン','オーディオ','スマートウォッチ']
    pm_cats = ['ゲーミング','PC周辺機器','スマートホーム','カメラ','モバイル','生活家電']
    pool    = [t for t in available if t['cat'] in (am_cats if SLOT=='am' else pm_cats)] or available
    return random.choice(pool)

# ===== メイン =====
def main():
    today = datetime.now()
    print(f"=== {today.strftime('%Y年%m月%d日')} [{SLOT.upper()}] ===")

    # 1. 新記事生成
    theme    = select_theme()
    print(f"テーマ: {theme['title']}")
    products = fetch_trusted(theme['kw'], need=5)

    if not products:
        print('❌ 商品取得失敗。処理を中断します。')
        return

    title    = f"【{today.year}年最新】{theme['title']} おすすめランキングTOP5"
    html     = build_html(title, theme['title'], products)
    date_str = today.strftime('%Y%m%d')
    safe     = re.sub(r'[^\w]', '-', theme['title'])[:25]
    filename = f"article-{safe}-{SLOT}-{date_str}.html"

    _, sha = gh_get(filename)
    gh_put(filename, html, f"Auto: {theme['title']}", sha)

    # サムネ画像URL
    img_url = ''
    if products:
        imgs = products[0].get('Item', {}).get('mediumImageUrls', [])
        if imgs:
            raw     = imgs[0].get('imageUrl', '') if isinstance(imgs[0], dict) else ''
            img_url = re.sub(r'\?_ex=\d+x\d+', '?_ex=400x400', raw)

    update_articles_json(theme, filename, img_url, today)

    # 2. 既存記事の再生成・空記事削除
    regenerate_and_cleanup()

    # 3. アーカイブ更新
    content, _ = gh_get('articles.json')
    if content:
        articles = json.loads(content)
        _, sha   = gh_get('archive.html')
        gh_put('archive.html', build_archive(articles), 'Auto: アーカイブ更新', sha)

    # 4. サイトマップ更新
    _, sha = gh_get('sitemap.xml')
    gh_put('sitemap.xml', build_sitemap([filename]), 'Auto: サイトマップ', sha)

    # 5. Twitter投稿
    article_url = f"{SITE_URL}/{filename}"
    post_twitter(title, article_url, theme['cat'])

    print(f"\n=== 完了: {article_url} ===")

if __name__ == '__main__':
    main()
