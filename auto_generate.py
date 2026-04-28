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
SLOT = os.environ.get('SLOT', 'am')  # am or pm

TWITTER_API_KEY = os.environ.get('API_KEY', '')
TWITTER_API_SECRET = os.environ.get('API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', '')

# ===== 大量テーマ定義（かぶらないよう多様化）=====
ALL_THEMES = [
    # イヤホン系
    {'kw':'ワイヤレスイヤホン ノイキャン 通勤','title':'通勤・テレワーク向けノイキャンイヤホン','cat':'イヤホン','emoji':'🎧','color':'#1a1a2e,#16213e'},
    {'kw':'ワイヤレスイヤホン スポーツ 防水','title':'スポーツ・ランニング向けイヤホン','cat':'イヤホン','emoji':'🏃','color':'#0f3460,#e94560'},
    {'kw':'ワイヤレスイヤホン 高音質 LDAC','title':'音質重視派のハイレゾイヤホン','cat':'イヤホン','emoji':'🎵','color':'#16213e,#0f3460'},
    {'kw':'ワイヤレスイヤホン 安い 5000円以下','title':'5000円以下コスパ最強イヤホン','cat':'イヤホン','emoji':'💰','color':'#1b1b2f,#2b2d42'},
    {'kw':'ワイヤレスイヤホン iPhone 14 15','title':'iPhone向けワイヤレスイヤホン','cat':'イヤホン','emoji':'📱','color':'#2c3e50,#3498db'},
    {'kw':'ワイヤレスイヤホン Android 長時間','title':'Android向け長時間バッテリーイヤホン','cat':'イヤホン','emoji':'⏰','color':'#1a1a2e,#4a4e69'},
    {'kw':'骨伝導イヤホン 開放型 安全','title':'骨伝導イヤホン完全ガイド','cat':'イヤホン','emoji':'🦴','color':'#2d3561,#c05c7e'},
    {'kw':'ゲーミングイヤホン 低遅延 PS5','title':'ゲーム向け低遅延イヤホン','cat':'ゲーミング','emoji':'🎮','color':'#0d0d0d,#39ff14'},
    {'kw':'ヘッドホン ノイズキャンセリング テレワーク','title':'テレワーク集中力アップヘッドホン','cat':'オーディオ','emoji':'🎧','color':'#1a1a1a,#c0392b'},
    {'kw':'ヘッドホン ハイレゾ 音楽鑑賞','title':'音楽鑑賞本格派ハイレゾヘッドホン','cat':'オーディオ','emoji':'🎼','color':'#2c2c54,#706fd3'},

    # スマートウォッチ系
    {'kw':'スマートウォッチ 血圧 心拍数 健康','title':'血圧・心拍数管理スマートウォッチ','cat':'スマートウォッチ','emoji':'❤️','color':'#c0392b,#922b21'},
    {'kw':'スマートウォッチ GPS ランニング','title':'ランニング・マラソン向けGPSウォッチ','cat':'スマートウォッチ','emoji':'🏅','color':'#1e8449,#145a32'},
    {'kw':'スマートウォッチ ビジネス スーツ','title':'ビジネスシーン映えスマートウォッチ','cat':'スマートウォッチ','emoji':'💼','color':'#1a1a1a,#2e4057'},
    {'kw':'スマートウォッチ 子供 キッズ','title':'子供・キッズ向けスマートウォッチ','cat':'スマートウォッチ','emoji':'👦','color':'#f39c12,#d35400'},
    {'kw':'スマートウォッチ 防水 登山 アウトドア','title':'登山・アウトドア向け防水ウォッチ','cat':'スマートウォッチ','emoji':'⛰️','color':'#1e8449,#0b5345'},
    {'kw':'Apple Watch 比較 おすすめ','title':'Apple Watch全モデル比較','cat':'スマートウォッチ','emoji':'⌚','color':'#1c1c1e,#636366'},
    {'kw':'Garmin スマートウォッチ スポーツ','title':'Garminスマートウォッチ完全比較','cat':'スマートウォッチ','emoji':'🗺️','color':'#003087,#0056d2'},

    # モバイル充電系
    {'kw':'モバイルバッテリー 軽量 100g 薄型','title':'100g以下超軽量モバイルバッテリー','cat':'モバイル','emoji':'🔋','color':'#0f2027,#203a43'},
    {'kw':'モバイルバッテリー 旅行 海外 大容量','title':'海外旅行に最強の大容量バッテリー','cat':'モバイル','emoji':'✈️','color':'#0f0c29,#302b63'},
    {'kw':'モバイルバッテリー ノートPC 65W','title':'ノートPC対応65W急速充電バッテリー','cat':'モバイル','emoji':'💻','color':'#232526,#414345'},
    {'kw':'ワイヤレス充電器 3in1 Apple','title':'iPhone・Watch・AirPods同時充電','cat':'モバイル','emoji':'⚡','color':'#1c1c1e,#48484a'},
    {'kw':'GaN充電器 100W コンパクト','title':'GaN100W超コンパクト充電器','cat':'モバイル','emoji':'🔌','color':'#0d0d0d,#ff6b35'},
    {'kw':'車載充電器 急速充電 シガーソケット','title':'車内急速充電カーチャージャー','cat':'モバイル','emoji':'🚗','color':'#1a1a2e,#e84393'},

    # PC周辺機器系
    {'kw':'ゲーミングマウス FPS 軽量 有線','title':'FPS最強軽量ゲーミングマウス','cat':'ゲーミング','emoji':'🖱️','color':'#0d0d0d,#ff0000'},
    {'kw':'ゲーミングマウス MMO 多ボタン','title':'MMO・MOBA向け多ボタンマウス','cat':'ゲーミング','emoji':'🎯','color':'#1a0533,#9b59b6'},
    {'kw':'ゲーミングキーボード 赤軸 青軸','title':'軸別おすすめメカニカルキーボード','cat':'ゲーミング','emoji':'⌨️','color':'#0d0d0d,#e74c3c'},
    {'kw':'ゲーミングキーボード 無線 ワイヤレス','title':'ワイヤレスゲーミングキーボード','cat':'ゲーミング','emoji':'📡','color':'#1a1a2e,#7f8c8d'},
    {'kw':'モニター 144Hz ゲーミング 27インチ','title':'144Hz 27インチゲーミングモニター','cat':'PC周辺機器','emoji':'🖥️','color':'#0d0d0d,#27ae60'},
    {'kw':'モニター 4K テレワーク USB-C','title':'テレワーク向け4K USB-Cモニター','cat':'PC周辺機器','emoji':'📺','color':'#2c3e50,#2980b9'},
    {'kw':'ウェブカメラ 1080p 配信 テレワーク','title':'配信・テレワーク向けウェブカメラ','cat':'PC周辺機器','emoji':'📸','color':'#1a1a1a,#3498db'},
    {'kw':'マイク 配信 ゲーム USB','title':'ゲーム配信向けUSBマイク','cat':'PC周辺機器','emoji':'🎙️','color':'#0d0d0d,#8e44ad'},
    {'kw':'USB ハブ Type-C MacBook','title':'MacBook向けUSB-Cハブ','cat':'PC周辺機器','emoji':'🔗','color':'#1c1c1e,#636366'},

    # スマートホーム系
    {'kw':'ロボット掃除機 マッピング 水拭き','title':'マッピング×水拭きロボット掃除機','cat':'スマートホーム','emoji':'🤖','color':'#1a1a2e,#4fc3f7'},
    {'kw':'スマートLED 電球 Alexa Google','title':'Alexa・Google対応スマートLED','cat':'スマートホーム','emoji':'💡','color':'#f39c12,#f1c40f'},
    {'kw':'スマートプラグ 電力モニター タイマー','title':'電力監視スマートプラグ','cat':'スマートホーム','emoji':'🔌','color':'#27ae60,#1e8449'},
    {'kw':'防犯カメラ 屋外 夜間 AI検知','title':'AI検知搭載屋外防犯カメラ','cat':'スマートホーム','emoji':'🔒','color':'#1a1a1a,#e74c3c'},
    {'kw':'空気清浄機 花粉 PM2.5 静音','title':'花粉・PM2.5対策空気清浄機','cat':'スマートホーム','emoji':'🌿','color':'#1b4332,#40916c'},
    {'kw':'スマートロック 後付け 指紋 スマホ','title':'後付け対応スマートロック','cat':'スマートホーム','emoji':'🗝️','color':'#2c3e50,#95a5a6'},
    {'kw':'プロジェクター 小型 ホームシアター','title':'小型ホームシアタープロジェクター','cat':'スマートホーム','emoji':'🎬','color':'#0d0d0d,#f39c12'},

    # カメラ・撮影系
    {'kw':'アクションカメラ 4K 防水 バイク','title':'バイク・スポーツ向けアクションカメラ','cat':'カメラ','emoji':'🏍️','color':'#1a1a1a,#f39c12'},
    {'kw':'スタビライザー ジンバル スマホ','title':'スマホ動画を滑らかにするジンバル','cat':'カメラ','emoji':'🎥','color':'#0d0d0d,#3498db'},
    {'kw':'三脚 軽量 旅行 スマホ カメラ','title':'旅行で使える軽量コンパクト三脚','cat':'カメラ','emoji':'📷','color':'#2c3e50,#7f8c8d'},
    {'kw':'リングライト LED 配信 YouTube','title':'YouTube配信向けリングライト','cat':'カメラ','emoji':'💫','color':'#f39c12,#e67e22'},
    {'kw':'ドライブレコーダー 前後 4K','title':'前後録画4Kドライブレコーダー','cat':'カメラ','emoji':'🚗','color':'#1a1a1a,#27ae60'},

    # 生活家電系
    {'kw':'電動歯ブラシ 音波 ホワイトニング','title':'ホワイトニング効果音波電動歯ブラシ','cat':'生活家電','emoji':'🦷','color':'#2980b9,#1a5276'},
    {'kw':'電気シェーバー 髭剃り 防水','title':'防水対応高性能電気シェーバー','cat':'生活家電','emoji':'🪒','color':'#1a1a1a,#7f8c8d'},
    {'kw':'マッサージガン 筋膜リリース 疲労回復','title':'筋膜リリースマッサージガン','cat':'生活家電','emoji':'💪','color':'#922b21,#641e16'},
    {'kw':'ネックスピーカー ウェアラブル 肩掛け','title':'肩掛けウェアラブルネックスピーカー','cat':'オーディオ','emoji':'🔊','color':'#1a1a2e,#2980b9'},
    {'kw':'スマートディスプレイ 卓上 フォトフレーム','title':'スマートフォトフレーム＆ディスプレイ','cat':'スマートホーム','emoji':'🖼️','color':'#2c3e50,#e74c3c'},

    # ゲーム系
    {'kw':'ゲーミングチェア 腰痛 テレワーク','title':'腰痛対策ゲーミングチェア','cat':'ゲーミング','emoji':'🪑','color':'#0d0d0d,#c0392b'},
    {'kw':'コントローラー PS5 Xbox 充電スタンド','title':'ゲームコントローラー充電スタンド','cat':'ゲーミング','emoji':'🎮','color':'#003791,#003791'},
    {'kw':'ゲーミングデスク 昇降 スタンディング','title':'昇降スタンディングゲーミングデスク','cat':'ゲーミング','emoji':'🖥️','color':'#1a1a1a,#2ecc71'},
    {'kw':'Switch アクセサリー ケース スタンド','title':'Nintendo Switchおすすめアクセサリー','cat':'ゲーミング','emoji':'🕹️','color':'#e4000f,#009ac7'},
]

HTML_TEMPLATE_START = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{description}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
</head>
<body>
<header>
  <div class="header-inner">
    <div class="logo">Gadget<span>天国</span></div>
    <nav><a href="{site_url}/">トップ</a></nav>
  </div>
</header>
"""

HTML_TEMPLATE_END = """
<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{site_url}/">← トップページに戻る</a>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。<br>記事内のリンクから購入された場合、運営者に報酬が発生することがあります。</p>
  <p style="margin-top:10px;font-size:.75rem">© 2026 ガジェット天国</p>
</footer>
</body>
</html>"""

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

def get_used_themes():
    """使用済みテーマをarticles.jsonから取得"""
    content, _ = get_github_file('articles.json')
    if not content:
        return set()
    try:
        articles = json.loads(content)
        return set(a.get('theme_key', '') for a in articles[:30])
    except:
        return set()

def select_theme(slot):
    """かぶらないテーマを選択"""
    used = get_used_themes()
    available = [t for t in ALL_THEMES if t['title'] not in used]
    if not available:
        available = ALL_THEMES  # 全部使い切ったらリセット

    # AM/PMで異なるカテゴリを選ぶ
    am_cats = ['イヤホン', 'オーディオ', 'スマートウォッチ', 'ウェアラブル']
    pm_cats = ['ゲーミング', 'PC周辺機器', 'スマートホーム', 'カメラ', 'モバイル', '生活家電']

    preferred_cats = am_cats if slot == 'am' else pm_cats
    preferred = [t for t in available if t['cat'] in preferred_cats]

    if preferred:
        return random.choice(preferred)
    return random.choice(available)

def generate_thumbnail_svg(theme):
    """毎回違うサムネSVGを生成"""
    colors = theme.get('color', '#1a1a1a,#2c3e50').split(',')
    c1 = colors[0].strip()
    c2 = colors[1].strip() if len(colors) > 1 else '#333'
    emoji = theme.get('emoji', '📱')
    title = theme['title'][:20]

    # ランダムデザイン要素
    patterns = [
        f'<circle cx="280" cy="60" r="120" fill="{c2}" fill-opacity="0.3"/>',
        f'<rect x="200" y="0" width="200" height="200" rx="100" fill="{c2}" fill-opacity="0.2"/>',
        f'<polygon points="400,0 400,200 200,200" fill="{c2}" fill-opacity="0.2"/>',
        f'<circle cx="50" cy="150" r="80" fill="{c2}" fill-opacity="0.2"/>',
    ]
    pattern = random.choice(patterns)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="210">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1}"/>
      <stop offset="100%" style="stop-color:{c2}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="210" fill="url(#bg)"/>
  {pattern}
  <text x="200" y="95" font-family="Arial" font-size="60" text-anchor="middle">{emoji}</text>
  <text x="200" y="140" font-family="Arial" font-size="16" font-weight="bold" fill="white" text-anchor="middle">{title}</text>
  <text x="200" y="165" font-family="Arial" font-size="12" fill="rgba(255,255,255,0.7)" text-anchor="middle">ガジェット天国 | 2026年最新</text>
  <rect x="150" y="175" width="100" height="3" rx="1" fill="#FF4D00"/>
</svg>'''
    return svg

def fetch_rakuten_ranking():
    """楽天売れ筋ランキングを取得"""
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
    params = {
        'format': 'json', 'keyword': 'ガジェット 家電 人気',
        'genreId': 0, 'applicationId': RAKUTEN_APP_ID,
        'accessKey': RAKUTEN_ACCESS_KEY, 'hits': 10,
        'affiliateId': RAKUTEN_AFFILIATE_ID,
        'imageFlag': 1, 'sort': '-reviewCount'
    }
    headers = {'Referer': 'https://gadget-tengoku.com'}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        return res.json().get('Items', [])
    except Exception as e:
        print(f"楽天ランキング取得エラー: {e}")
        return []

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

def generate_article_body(theme, products, ranking_items):
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

    # 楽天売れ筋ランキング情報
    ranking_info = ""
    for i, item in enumerate(ranking_items[:5], 1):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:30]
        price = p.get('itemPrice', 0)
        ranking_info += f"{i}位: {name} ¥{price:,}\n"

    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year

    prompt = f"""ガジェット専門アフィリエイトライターとして、HTMLコンテンツのみを生成してください。

テーマ:【{year}年最新】{theme['title']}
ターゲット読者:{theme.get('cat','')}に興味がある人
更新日:{today}
商品データ:{product_info}
楽天売れ筋ランキング参考:{ranking_info}

出力ルール:
- <body>タグは不要。divとsectionのみ
- マークダウン(```)は使わない
- CSSクラス使用:hero,hero-badge,container,section-title,intro-box,toc,guide-grid,guide-item,rank-card,rank-header(gold/silver/bronze),rank-number,rank-label,rank-body,rank-name,rank-shop,rank-review,pros-cons,pros,cons,price-buy,price,btn-buy,table-wrap,faq,faq-item,faq-q,faq-a
- 購入ボタン:<a href="URL" class="btn-buy" target="_blank">🛒 楽天で購入する</a>

構成:ヒーロー→導入→目次→選び方4項目→ランキングTOP5→比較表→FAQ3問

楽天の売れ筋データを参考に、リアルな価格・評価を記事に反映してください。"""

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
    title = f"【{year}年最新】{theme['title']} おすすめランキングTOP5"
    description = f"{year}年最新の{theme['title']}を徹底比較！選び方・スペック比較表・FAQ充実。楽天市場の売れ筋をもとに専門家が厳選。({today}更新)"
    start = HTML_TEMPLATE_START.format(title=title, description=description, site_url=SITE_URL)
    end = HTML_TEMPLATE_END.format(site_url=SITE_URL)
    return start + body_content + end

def update_articles_json(theme, filename, thumbnail_filename, today):
    articles_json, _ = get_github_file('articles.json')
    articles = json.loads(articles_json) if articles_json else []

    year = datetime.now().year
    new_article = {
        'title': f"【{year}年最新】{theme['title']} おすすめランキングTOP5",
        'filename': filename,
        'thumbnail': thumbnail_filename,
        'category': theme['cat'],
        'emoji': theme.get('emoji', '📱'),
        'color': theme.get('color', '#1a1a1a,#333'),
        'theme_key': theme['title'],
        'date': today.strftime('%Y年%m月%d日'),
        'description': f"{theme['title']}のおすすめをランキング形式で徹底比較。楽天売れ筋連動。"
    }

    exists = False
    for i, a in enumerate(articles):
        if a['filename'] == filename:
            articles[i] = new_article
            exists = True
            break
    if not exists:
        articles.insert(0, new_article)

    articles = articles[:30]
    upload_to_github('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), f"Auto: 記事一覧更新")

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
    slot = SLOT  # am or pm
    print(f"📅 {today.strftime('%Y年%m月%d日')} [{slot.upper()}] 投稿")

    # かぶらないテーマ選択
    theme = select_theme(slot)
    print(f"📝 テーマ: {theme['title']} ({theme['cat']})")

    # 楽天売れ筋ランキング取得
    print("📊 楽天売れ筋ランキング取得中...")
    ranking_items = fetch_rakuten_ranking()
    print(f"✅ ランキング {len(ranking_items)}件取得")

    # 商品データ取得
    print("🛒 商品データ取得中...")
    products = fetch_rakuten_products(theme['kw'])
    if not products:
        products = fetch_rakuten_products('ガジェット 人気')
    print(f"✅ {len(products)}件取得")

    # サムネイル生成（毎回違うデザイン）
    print("🎨 サムネイル生成中...")
    svg_content = generate_thumbnail_svg(theme)
    date_str = today.strftime('%Y%m%d')
    thumb_filename = f"thumb-{theme['filename'] if 'filename' in theme else date_str}-{slot}-{date_str}.svg"
    # filenameキーがない場合は生成
    safe_title = re.sub(r'[^a-zA-Z0-9]', '-', theme['title'].lower())[:30]
    thumb_filename = f"thumb-{safe_title}-{slot}-{date_str}.svg"
    upload_to_github(f"thumbnails/{thumb_filename}", svg_content, f"Auto: サムネイル生成")

    # 記事生成
    print("🤖 Claude AIで記事生成中...")
    body = generate_article_body(theme, products, ranking_items)
    if not body:
        print("❌ 記事生成失敗")
        return

    article_html = build_html(theme, body)
    print("✅ 記事生成完了")

    # ファイル名生成（かぶらないよう日付+スロット）
    safe_title2 = re.sub(r'[^a-zA-Z0-9]', '-', theme['title'].lower())[:30]
    filename = f"article-{safe_title2}-{slot}-{date_str}.html"

    upload_to_github(filename, article_html, f"Auto: {theme['title']}記事生成 [{slot.upper()}]")
    upload_to_github('sitemap.xml', update_sitemap([filename]), "Auto: サイトマップ更新")
    update_articles_json(theme, filename, f"thumbnails/{thumb_filename}", today)

    # Twitter投稿（AM/PMで異なる文体）
    if slot == 'am':
        tweet_text = f"🆕 【朝の新着記事】\n\n{theme['emoji']}【{today.year}年最新】{theme['title']} おすすめランキングTOP5\n\n楽天売れ筋と連動した最新情報をお届け📊\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット #楽天"
    else:
        tweet_text = f"🌙 【夜の新着記事】\n\n{theme['emoji']}【{today.year}年最新】{theme['title']} 徹底比較\n\n今日の楽天人気商品をまとめました🛒\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット天国"

    post_to_twitter(tweet_text)
    print(f"\n🎉 完了！\n記事: {SITE_URL}/{filename}\nサムネ: {SITE_URL}/thumbnails/{thumb_filename}")

if __name__ == '__main__':
    main()
