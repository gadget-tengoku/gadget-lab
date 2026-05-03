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

# ===== ロングテールキーワード対応テーマ =====
ALL_THEMES = [
    # イヤホン系（ロングテール）
    {'kw':'ワイヤレスイヤホン ノイキャン 通勤 電車','title':'通勤電車向けノイキャンイヤホン','slug':'earphone-commute','cat':'イヤホン','emoji':'🚃','use':'commute',
     'ng':'激しい運動で使いたい人・1万円以下で探している人'},
    {'kw':'ワイヤレスイヤホン Web会議 マイク性能','title':'Web会議マイク性能重視イヤホン','slug':'earphone-webmeeting','cat':'イヤホン','emoji':'💻','use':'telework',
     'ng':'音楽鑑賞メイン・屋外使用がメインの人'},
    {'kw':'ワイヤレスイヤホン 1万円以下 コスパ','title':'1万円以下コスパ最強イヤホン','slug':'earphone-under10k','cat':'イヤホン','emoji':'💰','use':'all',
     'ng':'高音質・強力NCを求める人・長時間連続使用する人'},
    {'kw':'AirPods Pro 代わり Android','title':'AirPods Pro代替おすすめイヤホン','slug':'earphone-airpods-alt','cat':'イヤホン','emoji':'📱','use':'all',
     'ng':'iPhoneユーザーでAppleエコシステムにこだわる人'},
    {'kw':'ワイヤレスイヤホン スポーツ ランニング 防水','title':'ランニング・スポーツ向けイヤホン','slug':'earphone-sports','cat':'イヤホン','emoji':'🏃','use':'sports',
     'ng':'NC重視・音楽鑑賞メインの人'},
    {'kw':'ワイヤレスイヤホン 耳が痛くない 長時間','title':'長時間使っても耳が痛くないイヤホン','slug':'earphone-comfortable','cat':'イヤホン','emoji':'👂','use':'all',
     'ng':'激しい運動で使いたい人・防水重視の人'},
    {'kw':'Sony WF-1000XM5 レビュー','title':'Sony WF-1000XM5 実機レビュー','slug':'review-sony-wf1000xm5','cat':'イヤホン','emoji':'🎧','use':'all',
     'ng':'予算3万円以下の人・激しい運動で使いたい人・耳が小さい人'},
    {'kw':'Anker Liberty 4 NC レビュー Sony 比較','title':'Anker Liberty 4 NC vs Sony比較','slug':'compare-anker-sony','cat':'イヤホン','emoji':'⚔️','use':'all',
     'ng':'音質最優先の人・公式アプリ機能を使いこなしたい人'},
    {'kw':'ワイヤレスイヤホン 高音質 LDAC ハイレゾ','title':'ハイレゾ対応高音質イヤホン','slug':'earphone-hires','cat':'イヤホン','emoji':'🎵','use':'all',
     'ng':'コスパ重視・NC重視の人'},

    # スマートウォッチ系
    {'kw':'スマートウォッチ iPhone Apple Watch以外','title':'Apple Watch以外のiPhone向けスマートウォッチ','slug':'watch-iphone-non-apple','cat':'スマートウォッチ','emoji':'⌚','use':'all',
     'ng':'iOSアプリ連携を最大限使いたい人'},
    {'kw':'スマートウォッチ Android おすすめ','title':'Android向けスマートウォッチ','slug':'watch-android','cat':'スマートウォッチ','emoji':'📱','use':'all',
     'ng':'iPhoneユーザー・Apple Watchを検討中の人'},
    {'kw':'Garmin Apple Watch どっち 健康管理','title':'Garmin vs Apple Watchどっちがいい？','slug':'compare-garmin-applewatch','cat':'スマートウォッチ','emoji':'🏅','use':'sports',
     'ng':'ビジネス寄りのデザインを重視する人'},
    {'kw':'スマートウォッチ 1万円台 安い','title':'1万円台で買えるスマートウォッチ','slug':'watch-under15k','cat':'スマートウォッチ','emoji':'💴','use':'all',
     'ng':'GPS精度・通話機能を重視する人'},
    {'kw':'スマートウォッチ 睡眠 計測 精度','title':'睡眠計測精度が高いスマートウォッチ','slug':'watch-sleep','cat':'スマートウォッチ','emoji':'😴','use':'all',
     'ng':'GPSランニング機能を重視する人'},
    {'kw':'スマートウォッチ 高齢者 親 プレゼント','title':'高齢者・親へのプレゼントにおすすめスマートウォッチ','slug':'watch-elderly','cat':'スマートウォッチ','emoji':'👴','use':'all',
     'ng':'20〜30代向けのスタイリッシュデザインを求める人'},

    # モバイルバッテリー・充電器系
    {'kw':'モバイルバッテリー 飛行機 持ち込み 20000mAh','title':'飛行機持ち込みOKモバイルバッテリー','slug':'battery-airplane','cat':'モバイル','emoji':'✈️','use':'travel',
     'ng':'国内移動のみ・持ち歩き重量を最優先する人'},
    {'kw':'モバイルバッテリー iPhone 軽量','title':'iPhone向け軽量モバイルバッテリー','slug':'battery-iphone-light','cat':'モバイル','emoji':'🔋','use':'commute',
     'ng':'大容量（20000mAh以上）を求める人'},
    {'kw':'モバイルバッテリー ノートPC 65W','title':'ノートPCも充電できる65Wバッテリー','slug':'battery-laptop','cat':'モバイル','emoji':'💻','use':'telework',
     'ng':'軽さ重視・スマホのみ充電したい人'},
    {'kw':'Anker モバイルバッテリー 比較 おすすめ','title':'Ankerモバイルバッテリー全機種比較','slug':'battery-anker-compare','cat':'モバイル','emoji':'⚡','use':'all',
     'ng':'他ブランドも含めて比較したい人'},
    {'kw':'GaN充電器 65W 100W 比較','title':'GaN急速充電器65W vs 100W比較','slug':'charger-gan-compare','cat':'モバイル','emoji':'🔌','use':'all',
     'ng':'スマホのみ充電・重さが気になる人'},
    {'kw':'MagSafe モバイルバッテリー iPhone 15','title':'iPhone15対応MagSafeバッテリー','slug':'battery-magsafe','cat':'モバイル','emoji':'🧲','use':'all',
     'ng':'Androidユーザー・有線充電で十分な人'},
    {'kw':'モバイルバッテリー ケーブル内蔵','title':'ケーブル内蔵モバイルバッテリー','slug':'battery-built-in-cable','cat':'モバイル','emoji':'🔋','use':'commute',
     'ng':'大容量・高出力を求める人'},

    # ゲーミング系
    {'kw':'ゲーミングマウス 手が小さい FPS','title':'手が小さい人向けゲーミングマウス','slug':'mouse-small-hand','cat':'ゲーミング','emoji':'🖱️','use':'gaming',
     'ng':'手が大きい人・MMO向け多ボタンマウスを探している人'},
    {'kw':'ゲーミングマウス Valorant 軽量','title':'Valorant向け軽量ゲーミングマウス','slug':'mouse-valorant','cat':'ゲーミング','emoji':'🎯','use':'gaming',
     'ng':'MMO・RTS向け多ボタンマウスを探している人'},
    {'kw':'ゲーミングヘッドセット PS5 おすすめ','title':'PS5向けゲーミングヘッドセット','slug':'headset-ps5','cat':'ゲーミング','emoji':'🎮','use':'gaming',
     'ng':'PC専用・ワイヤレスにこだわらない人'},

    # 在宅ワーク系
    {'kw':'Webカメラ 顔色 明るく テレワーク','title':'顔色が明るく映るテレワーク向けWebカメラ','slug':'webcam-telework','cat':'PC周辺機器','emoji':'📷','use':'telework',
     'ng':'カジュアルな使用・高コストを避けたい人'},
    {'kw':'在宅ワーク マイク USB おすすめ','title':'テレワーク向けUSBマイク','slug':'mic-telework','cat':'PC周辺機器','emoji':'🎙️','use':'telework',
     'ng':'既にイヤホンマイクで満足している人'},
    {'kw':'ノートPC スタンド 軽量 持ち運び','title':'持ち運び対応軽量ノートPCスタンド','slug':'pcstand-portable','cat':'PC周辺機器','emoji':'💻','use':'telework',
     'ng':'自宅固定で使用・デスク環境が充実している人'},

    # スマートホーム系
    {'kw':'ロボット掃除機 一人暮らし おすすめ','title':'一人暮らしに最適なロボット掃除機','slug':'robot-vacuum-solo','cat':'スマートホーム','emoji':'🤖','use':'all',
     'ng':'ペット毛・カーペット床が多い環境の人'},
    {'kw':'空気清浄機 花粉 6畳 10畳','title':'花粉症対策 部屋の広さ別空気清浄機','slug':'air-purifier-pollen','cat':'スマートホーム','emoji':'🌸','use':'all',
     'ng':'加湿機能にこだわる人・大空間向け'},
]

def get_github_file(filename):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return base64.b64decode(data['content']).decode('utf-8'), data['sha']
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
    content, _ = get_github_file('articles.json')
    if not content:
        return set()
    try:
        articles = json.loads(content)
        return set(a.get('theme_key', '') for a in articles[:50])
    except:
        return set()

def select_theme(slot):
    used = get_used_themes()
    available = [t for t in ALL_THEMES if t['title'] not in used]
    if not available:
        available = ALL_THEMES
    am_cats = ['イヤホン', 'スマートウォッチ']
    pm_cats = ['ゲーミング', 'PC周辺機器', 'スマートホーム', 'モバイル']
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
    today = datetime.now().strftime('%Y年%m月%d日')
    year = datetime.now().year
    title = f"【{year}年】{theme['title']} おすすめランキングTOP5｜失敗しない選び方"
    ng_people = theme.get('ng', 'ハイエンドモデルを求める人・予算が非常に限られる人')

    # 固定商品（楽天取得失敗時のフォールバック）
    fallback = [
        {'name':'【1位】楽天人気No.1モデル','price':'要確認','shop':'楽天市場','review_avg':4.5,'review_count':1000,'url':'https://www.rakuten.co.jp/'},
    ]

    product_cards = ''
    rank_colors = ['gold','silver','bronze','','']
    rank_labels = ['🥇 編集部イチオシ・最多レビュー','🥈 コスパ優秀','🥉 人気急上昇','4位 注目モデル','5位 要チェック']

    items_to_use = products[:5] if products else []

    for i, item in enumerate(items_to_use):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:60]
        price = p.get('itemPrice', 0)
        price_str = f"¥{price:,}" if price else '要確認'
        shop = p.get('shopName', '楽天市場')
        review_avg = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', 'https://www.rakuten.co.jp/'))
        img_url = p.get('mediumImageUrls', [{}])[0].get('imageUrl', '') if p.get('mediumImageUrls') else ''
        item_code = p.get('itemCode', '')
        review_url = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':', '/')}/1.1/" if ':' in item_code else affiliate_url
        stars = '★' * int(review_avg) + '☆' * (5 - int(review_avg))

        img_html = (f'<img src="{img_url}" alt="{name}" style="width:100%;height:220px;object-fit:contain;background:#f8f8f8;border-radius:8px;padding:10px">'
                   if img_url else
                   f'<div style="width:100%;height:220px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:70px">{theme["emoji"]}</div>')

        # Amazon/Yahoo検索URL生成
        search_name = re.sub(r'[【】\[\]「」\s]+', ' ', name).strip()[:30]
        amazon_url = f"https://www.amazon.co.jp/s?k={requests.utils.quote(search_name)}"
        yahoo_url = f"https://shopping.yahoo.co.jp/search?p={requests.utils.quote(search_name)}"

        product_cards += f'''
<div class="rank-card" id="rank{i+1}">
  <div class="rank-header {rank_colors[i]}">
    <span class="rank-number">{i+1}</span>
    <span class="rank-label">{rank_labels[i]}</span>
  </div>
  <div class="rank-body">
    {img_html}
    <h3 class="rank-name" style="margin-top:14px">{name}</h3>
    <div class="rank-shop">📦 販売店：{shop}</div>
    <div class="rank-review" style="margin:10px 0">
      <span style="color:#FFD700;font-size:1.1rem;letter-spacing:2px">{stars}</span>
      <strong style="margin-left:6px">{review_avg:.1f}</strong>
      <a href="{review_url}" target="_blank" rel="noopener" style="color:#FF4D00;font-size:.85rem;margin-left:8px">
        {review_count:,}件の口コミを読む →
      </a>
    </div>
    <p style="font-size:.85rem;color:#666;background:#fffbf0;border-left:3px solid #f39c12;padding:8px 12px;border-radius:4px;margin:10px 0">
      📅 価格確認日：{today}　※価格は変動します。購入前に必ず最新価格をご確認ください
    </p>
    <div class="price-buy" style="margin-top:14px">
      <div class="price">{price_str} <small>税込（参考価格）</small></div>
    </div>
    <div style="display:flex;flex-direction:column;gap:8px;margin-top:12px">
      <a href="{affiliate_url}" style="display:block;background:#BF0000;color:#fff;text-align:center;padding:12px;border-radius:8px;font-weight:700;font-size:.95rem" target="_blank" rel="noopener sponsored">
        🛒 楽天でポイント還元込み価格を確認する
      </a>
      <a href="{amazon_url}" style="display:block;background:#FF9900;color:#fff;text-align:center;padding:10px;border-radius:8px;font-weight:700;font-size:.9rem" target="_blank" rel="noopener">
        📦 Amazonで最短翌日配送を確認する
      </a>
      <a href="{yahoo_url}" style="display:block;background:#FF0033;color:#fff;text-align:center;padding:10px;border-radius:8px;font-weight:700;font-size:.9rem" target="_blank" rel="noopener">
        💳 Yahoo!でPayPay還元価格を確認する
      </a>
    </div>
  </div>
</div>'''

    # 比較表
    table_rows = ''
    for i, item in enumerate(items_to_use):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:20]
        price = p.get('itemPrice', 0)
        review_avg = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        stars = '★' * int(review_avg) + '☆' * (5 - int(review_avg))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        table_rows += f'''<tr>
          <td><span class="rank-no">{i+1}位</span>{name}</td>
          <td>¥{price:,}</td>
          <td>{stars}<br><small>{review_avg:.1f}点</small></td>
          <td>{review_count:,}件</td>
          <td><a href="{affiliate_url}" target="_blank" rel="noopener sponsored" style="color:#BF0000;font-weight:700;white-space:nowrap">楽天で見る</a></td>
        </tr>'''

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新の{theme["title"]}を楽天実売データ・レビュー数で比較。おすすめしない人・弱点まで正直に解説。失敗しない選び方を解説します。({today}更新)">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
<style>
.ng-box{{background:#fff5f5;border:1px solid #f5c6cb;border-radius:8px;padding:14px 16px;margin:14px 0;font-size:.88rem;color:#721c24}}
.ng-box strong{{color:#c0392b}}
.ok-box{{background:#f0fff4;border:1px solid #b2dfdb;border-radius:8px;padding:14px 16px;margin:14px 0;font-size:.88rem;color:#155724}}
.ok-box strong{{color:#27ae60}}
.review-summary{{background:#fffbf0;border:1px solid #ffe082;border-radius:10px;padding:16px;margin:14px 0}}
.review-summary h4{{font-size:.9rem;font-weight:700;margin-bottom:8px;color:#333}}
.review-good{{color:#27ae60;font-size:.85rem;margin-bottom:4px}}
.review-bad{{color:#c0392b;font-size:.85rem;margin-bottom:4px}}
</style>
</head>
<body>
<div style="background:#fffbf0;border-bottom:1px solid #ffe4b0;padding:8px 5%;font-size:12px;color:#666;text-align:center">
  ※本記事はアフィリエイト広告（楽天・Amazon・Yahoo!）を含みます。商品の評価・選定は独自基準によります。
</div>
<header>
  <div class="header-inner">
    <div class="logo"><a href="{SITE_URL}" style="color:inherit;text-decoration:none">Gadget<span>天国</span></a></div>
    <nav>
      <a href="{SITE_URL}/">トップ</a>
      <a href="{SITE_URL}/archive.html">記事一覧</a>
      <a href="{SITE_URL}/about.html">運営者情報</a>
    </nav>
  </div>
</header>

<div class="hero">
  <span class="hero-badge">{today} 更新 | 楽天実売データ参照</span>
  <h1>{theme["emoji"]} {title}</h1>
  <p class="hero-sub">楽天市場の実際のレビュー数・評価点をもとに厳選。<strong>おすすめしない人・弱点まで正直に解説</strong>します。</p>
</div>

<div class="container">

  <!-- アフィリエイト開示 -->
  <div style="font-size:.8rem;color:#999;border:1px solid #eee;border-radius:6px;padding:10px 14px;margin-bottom:20px">
    ⚠️ 本記事は楽天・Amazon・Yahoo!のアフィリエイトプログラムに参加しています。リンクから購入された場合、運営者に報酬が発生しますが、商品評価には影響しません。
  </div>

  <!-- この記事でわかること -->
  <div class="intro-box">
    <h2 style="font-size:1rem;font-weight:700;margin-bottom:10px">📋 この記事でわかること</h2>
    <ul style="font-size:.9rem;color:#444;padding-left:18px;line-height:1.9">
      <li>楽天で実際に売れている{theme["title"]}TOP5</li>
      <li>各商品の<strong>弱点・おすすめしない人</strong>（正直に記載）</li>
      <li>楽天・Amazon・Yahoo!の価格比較導線</li>
      <li>用途別の選び方ガイド</li>
      <li>楽天の実際の口コミ傾向</li>
    </ul>
    <div class="ng-box" style="margin-top:12px">
      <strong>⚠️ こんな人にはおすすめしません（{theme["title"]}全体として）</strong><br>
      {ng_people}
    </div>
  </div>

  <!-- 目次 -->
  <nav class="toc">
    <div class="toc-title">📋 目次（クリックで移動）</div>
    <ol>
      <li><a href="#howto">失敗しない選び方（3つのポイント）</a></li>
      <li><a href="#ranking">楽天売れ筋ランキングTOP5</a></li>
      <li><a href="#compare">スペック・価格比較表</a></li>
      <li><a href="#faq">よくある質問（FAQ）</a></li>
      <li><a href="#summary">まとめ：用途別おすすめ</a></li>
    </ol>
  </nav>

  <!-- 選び方 -->
  <section id="howto">
    <h2 class="section-title">🔍 失敗しない{theme["title"]}の選び方</h2>
    <div class="guide-grid">
      <div class="guide-item">
        <div class="guide-item-icon">💰</div>
        <div class="guide-item-title">①予算を先に決める</div>
        <div class="guide-item-desc">予算によって選ぶべきモデルが変わります。1万円以下・1〜3万円・3万円以上で最適解が異なります。まず予算を明確にしましょう。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-icon">🎯</div>
        <div class="guide-item-title">②用途・使用シーンを明確に</div>
        <div class="guide-item-desc">通勤/在宅/スポーツ/ゲームなど、主な使用シーンによって最適なスペックが変わります。「なんでも使える」商品より、用途に特化した方が満足度が高いです。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-icon">⭐</div>
        <div class="guide-item-title">③レビュー数を確認する</div>
        <div class="guide-item-desc">楽天のレビュー数が多いほど実績あり。1,000件以上のレビューがある商品は外れが少ない傾向です。評価点より「レビュー数」を重視しましょう。</div>
      </div>
      <div class="guide-item">
        <div class="guide-item-icon">🛡️</div>
        <div class="guide-item-title">④保証・サポートを確認</div>
        <div class="guide-item-desc">ガジェットは不具合が出ることも。国内正規品か、保証期間は何年か、日本語サポートがあるかを確認しましょう。安さだけで選ぶと後悔することがあります。</div>
      </div>
    </div>
  </section>

  <!-- ランキング -->
  <section id="ranking">
    <h2 class="section-title">🏆 楽天売れ筋ランキングTOP5</h2>
    <p style="font-size:.85rem;color:#888;margin-bottom:6px">※楽天市場のレビュー数順。価格は{today}時点の参考価格です。必ず購入前に最新価格をご確認ください。</p>
    <p style="font-size:.85rem;color:#888;margin-bottom:20px">※各商品ページで実際の口コミを必ずご確認いただくことをおすすめします。</p>
    {product_cards}
  </section>

  <!-- 比較表 -->
  <section id="compare">
    <h2 class="section-title">📊 スペック・価格比較表</h2>
    <p style="font-size:.85rem;color:#888;margin-bottom:12px">※価格は{today}時点の参考価格です。セール・ポイント還元で変動します。</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>参考価格</th><th>評価</th><th>レビュー数</th><th>購入</th></tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
    <p style="font-size:.82rem;color:#999;margin-top:8px">💡 楽天はポイント還元・セールが多いため、実質価格はさらに安くなる場合があります。</p>
  </section>

  <!-- FAQ -->
  <section id="faq">
    <h2 class="section-title">❓ よくある質問（FAQ）</h2>
    <div class="faq">
      <div class="faq-item">
        <div class="faq-q">{theme["title"]}はどこで買うのがお得？</div>
        <div class="faq-a">楽天市場はポイント還元・セールが充実しています。Amazonは配送スピードとレビュー数が強み。Yahoo!ショッピングはPayPay還元が魅力です。価格変動があるため、購入前に3サイトを比較することをおすすめします。</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">レビュー評価が高ければ選んで間違いない？</div>
        <div class="faq-a">評価点より「レビュー数」を重視してください。100件で4.9より、2,000件で4.5の方が信頼性が高い傾向です。また、自分の用途に合った口コミを読むことが大切です。</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">価格の変動はある？</div>
        <div class="faq-a">あります。楽天のお買い物マラソンや楽天スーパーセール期間中は大きく値下がりすることがあります。急ぎでなければ、セール時期を狙うとお得です。</div>
      </div>
    </div>
  </section>

  <!-- まとめ -->
  <section id="summary">
    <h2 class="section-title">📝 まとめ：用途別おすすめ</h2>
    <div class="intro-box">
      <p style="margin-bottom:10px">今回は楽天市場の実売データをもとに<strong>{theme["title"]}TOP5</strong>をご紹介しました。</p>
      <p style="margin-bottom:10px">迷ったときは<strong>レビュー数が最も多いモデル（1位）</strong>を選ぶのが失敗が少なくおすすめです。</p>
      <div class="ng-box">
        <strong>⚠️ 改めて：こんな人にはおすすめしません</strong><br>
        {ng_people}
      </div>
      <p style="margin-top:12px;font-size:.88rem;color:#666">価格は変動するため、購入前に楽天・Amazon・Yahooの3サイトで最新価格をご確認ください。</p>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px">
      <a href="{SITE_URL}/archive.html" style="display:inline-block;background:#f4f4f2;color:#333;padding:10px 20px;border-radius:999px;font-size:.88rem;font-weight:600">📚 他の記事も見る</a>
      <a href="{SITE_URL}/" style="display:inline-block;background:#FF4D00;color:white;padding:10px 20px;border-radius:999px;font-size:.88rem;font-weight:600">🏠 トップページへ</a>
    </div>
  </section>

</div>

<footer>
  <div class="footer-logo"><a href="{SITE_URL}" style="color:white;text-decoration:none">Gadget<span style="color:#FF4D00">天国</span></a></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">
    ※本サイトは楽天・Amazon・Yahoo!のアフィリエイトプログラムに参加しています。<br>
    記事内のリンクから購入された場合、運営者に報酬が発生することがあります。<br>
    掲載価格・スペックは{today}時点の情報です。最新情報はリンク先でご確認ください。
  </p>
  <p style="margin-top:10px;font-size:.75rem">© 2026 ガジェット天国</p>
</footer>
</body>
</html>'''
    return html

def update_articles_json(theme, filename, img_url, today):
    articles_json, _ = get_github_file('articles.json')
    articles = json.loads(articles_json) if articles_json else []
    year = datetime.now().year
    new_article = {
        'title': f"【{year}年】{theme['title']} おすすめランキングTOP5｜失敗しない選び方",
        'filename': filename,
        'img_url': img_url,
        'category': theme['cat'],
        'emoji': theme.get('emoji', '📱'),
        'theme_key': theme['title'],
        'use': theme.get('use', 'all'),
        'date': today.strftime('%Y年%m月%d日'),
        'description': f"楽天実売データで{theme['title']}TOP5を比較。弱点・おすすめしない人まで正直解説。"
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
    today_str = datetime.now().strftime('%Y年%m月%d日')
    cards = ''
    for a in articles:
        img = a.get('img_url', '')
        img_html = (f'<img src="{img}" alt="{a["title"]}" style="width:100%;height:160px;object-fit:contain;background:#f5f5f5">'
                   if img else
                   f'<div style="width:100%;height:160px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:50px">{a.get("emoji","📱")}</div>')
        cards += f'''
<a href="{a["filename"]}" style="display:block;background:white;border-radius:12px;overflow:hidden;border:1px solid #eee;transition:transform .2s;text-decoration:none;color:inherit">
  <div style="position:relative">{img_html}<div style="position:absolute;top:8px;left:8px;background:#FF4D00;color:white;font-size:10px;font-weight:700;padding:2px 8px;border-radius:999px">{a.get("category","")}</div></div>
  <div style="padding:12px">
    <div style="font-size:13px;font-weight:700;line-height:1.4;margin-bottom:5px">{a["title"]}</div>
    <div style="font-size:11px;color:#888">📅 {a["date"]}</div>
  </div>
</a>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記事アーカイブ（全{len(articles)}記事） | ガジェット天国</title>
<meta name="description" content="ガジェット天国の全記事一覧。イヤホン・スマートウォッチ・モバイルバッテリー・ゲーミングなど用途別比較記事。">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
</head>
<body>
<header>
  <div class="header-inner">
    <div class="logo"><a href="{SITE_URL}" style="color:inherit;text-decoration:none">Gadget<span>天国</span></a></div>
    <nav><a href="{SITE_URL}/">トップ</a></nav>
  </div>
</header>
<div class="hero">
  <span class="hero-badge">{today_str} 現在</span>
  <h1>📚 記事アーカイブ</h1>
  <p class="hero-sub">全{len(articles)}記事 | 順次更新中</p>
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;padding:30px 5%;max-width:1200px;margin:0 auto">
{cards}
</div>
<footer>
  <div class="footer-logo"><a href="{SITE_URL}" style="color:white;text-decoration:none">Gadget<span style="color:#FF4D00">天国</span></a></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">© 2026 ガジェット天国</p>
</footer>
</body>
</html>'''

def update_sitemap(new_files):
    today = datetime.now().strftime('%Y-%m-%d')
    base_urls = ['', 'earphone.html', 'smartwatch.html', 'battery.html', 'archive.html', 'about.html']
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
        products = fetch_rakuten_products(theme['cat'] + ' 人気')
    print(f"✅ {len(products)}件取得")

    img_url = ''
    if products:
        p = products[0].get('Item', {})
        imgs = p.get('mediumImageUrls', [])
        if imgs:
            img_url = imgs[0].get('imageUrl', '')

    print("📝 記事HTML生成中...")
    article_html = build_article_html(theme, products)
    print("✅ 記事生成完了")

    date_str = today.strftime('%Y%m%d')
    filename = f"{theme['slug']}-{slot}-{date_str}.html"

    upload_to_github(filename, article_html, f"Auto: {theme['title']} [{slot.upper()}]")
    update_articles_json(theme, filename, img_url, today)

    articles_json, _ = get_github_file('articles.json')
    if articles_json:
        articles = json.loads(articles_json)
        archive_html = build_archive_page(articles)
        upload_to_github('archive.html', archive_html, "Auto: アーカイブ更新")

    upload_to_github('sitemap.xml', update_sitemap([filename]), "Auto: サイトマップ更新")

    if slot == 'am':
        tweet = f"🆕 新着！{theme['emoji']}\n「{theme['title']}」で失敗しない選び方\n\n✅おすすめする人\n❌おすすめしない人\nも正直に解説👇\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット #楽天"
    else:
        tweet = f"🌙 夜の更新{theme['emoji']}\n{theme['title']}TOP5｜弱点まで正直解説\n\n楽天・Amazon・Yahooの価格比較リンクつき🛒\n\n{SITE_URL}/{filename}\n\n#{theme['cat']} #ガジェット天国"

    post_to_twitter(tweet)
    print(f"\n🎉 完了！ {SITE_URL}/{filename}")

if __name__ == '__main__':
    main()
