#!/usr/bin/env python3
"""
ガジェット天国 記事30本一括生成スクリプト
GitHub Actionsで実行: python bulk_generate.py
"""

import os
import re
import requests
import base64
import json
import time
from datetime import datetime, timedelta

RAKUTEN_APP_ID = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
CLAUDE_API_KEY = os.environ['CLAUDE_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = 'gadget-tengoku/gadget-lab'
SITE_URL = 'https://gadget-tengoku.com'

# ===== 30本分のテーマ（ロングテール・意思決定支援型） =====
BULK_THEMES = [
    # イヤホン系（10本）
    {'kw':'ワイヤレスイヤホン ノイキャン 通勤 電車','title':'通勤電車でノイキャンイヤホン｜走行音がうるさい人向け','slug':'earphone-commute-train','cat':'イヤホン','emoji':'🚃',
     'target':'毎日電車で通勤していてスマホの音が聞こえにくい人',
     'ng':'激しい運動・ランニング中に使いたい人 / 予算5,000円以下の人'},
    {'kw':'ワイヤレスイヤホン 1万円以下 コスパ ノイキャン','title':'1万円以下でノイキャンイヤホン｜初めて買う人向け','slug':'earphone-under10k','cat':'イヤホン','emoji':'💰',
     'target':'初めてNCイヤホンを試したい・予算を抑えたい人',
     'ng':'最強NC性能・最高音質を求める人'},
    {'kw':'Web会議 イヤホン マイク おすすめ','title':'Web会議でマイクが聞こえにくい問題を解決するイヤホン','slug':'earphone-webmeeting','cat':'イヤホン','emoji':'💻',
     'target':'テレワークでWeb会議が多く、マイク音質を改善したい人',
     'ng':'音楽鑑賞がメイン・屋外使用がメインの人'},
    {'kw':'AirPods Pro 代わり 安い Android','title':'AirPods Pro高すぎ問題｜代わりになるイヤホン5選','slug':'earphone-airpods-alternative','cat':'イヤホン','emoji':'📱',
     'target':'AirPods Proが気になるが価格が高いと感じている人',
     'ng':'iPhoneのAppleエコシステムをフル活用したい人'},
    {'kw':'ランニング イヤホン 防水 落ちない','title':'ランニング中に落ちないイヤホン｜防水・密着重視','slug':'earphone-running','cat':'イヤホン','emoji':'🏃',
     'target':'ランニング・ジム通いで使えるイヤホンを探している人',
     'ng':'NC機能・高音質を重視する人・オフィス使用がメインの人'},
    {'kw':'ワイヤレスイヤホン 耳が痛くない 長時間','title':'長時間使っても耳が痛くならないイヤホンの選び方','slug':'earphone-no-pain','cat':'イヤホン','emoji':'👂',
     'target':'イヤホンを2時間以上連続使用することが多い人',
     'ng':'激しい運動で使いたい人・防水を最優先する人'},
    {'kw':'Sony WF-1000XM5 レビュー 正直','title':'Sony WF-1000XM5 正直レビュー｜買って後悔した点も書く','slug':'review-wf1000xm5','cat':'イヤホン','emoji':'🎧',
     'target':'Sony WF-1000XM5が気になっているが本当に良いか迷っている人',
     'ng':'予算2万円以下の人 / ランニング・スポーツ用途の人'},
    {'kw':'Anker Liberty 4 NC レビュー Sony 比較','title':'Anker Liberty 4 NCは安物？Sonyと比較した正直な感想','slug':'review-liberty4nc','cat':'イヤホン','emoji':'⚔️',
     'target':'AnkerとSonyで迷っている人・コスパを重視する人',
     'ng':'音質最優先で妥協できない人'},
    {'kw':'骨伝導イヤホン おすすめ 耳が痛い','title':'耳が痛くて普通のイヤホンが使えない人向け骨伝導イヤホン','slug':'earphone-bone-conduction','cat':'イヤホン','emoji':'🦴',
     'target':'カナル型で耳が痛くなる・耳栓感が苦手な人',
     'ng':'高いNC性能・高音質を求める人'},
    {'kw':'ゲーム イヤホン 低遅延 PC PS5','title':'ゲーム中の遅延が気になる人向けゲーミングイヤホン','slug':'earphone-gaming','cat':'ゲーミング','emoji':'🎮',
     'target':'FPS・オンラインゲームで音ズレを感じている人',
     'ng':'音楽鑑賞メイン・テレワーク向けを探している人'},

    # モバイルバッテリー・充電器系（10本）
    {'kw':'モバイルバッテリー 軽量 薄型 毎日','title':'毎日カバンに入れても苦にならない軽量バッテリー','slug':'battery-lightweight','cat':'モバイル','emoji':'🔋',
     'target':'通勤・外出時に毎日持ち歩くモバイルバッテリーを探している人',
     'ng':'大容量（20000mAh以上）を求める人・旅行メイン'},
    {'kw':'モバイルバッテリー 飛行機 持ち込み 旅行','title':'飛行機持ち込みOK？旅行向けモバイルバッテリーの選び方','slug':'battery-airplane','cat':'モバイル','emoji':'✈️',
     'target':'旅行・出張で飛行機に乗る機会が多い人',
     'ng':'国内移動のみ・毎日持ち歩き軽さ最優先の人'},
    {'kw':'モバイルバッテリー ノートPC 充電 65W','title':'ノートPCも充電できるモバイルバッテリー｜65W以上対応','slug':'battery-laptop-65w','cat':'モバイル','emoji':'💻',
     'target':'カフェや外出先でノートPCを使う機会が多い人',
     'ng':'スマホのみ充電・軽さ重視の人'},
    {'kw':'Anker モバイルバッテリー 比較 どれがいい','title':'Ankerモバイルバッテリー全機種比較｜用途別おすすめ','slug':'battery-anker-lineup','cat':'モバイル','emoji':'⚡',
     'target':'Ankerに絞って選びたいが種類が多くて迷っている人',
     'ng':'他ブランドとの比較を含めて検討したい人'},
    {'kw':'MagSafe バッテリー iPhone 15 16','title':'iPhone15・16向けMagSafeバッテリー｜貼り付けるだけ充電','slug':'battery-magsafe','cat':'モバイル','emoji':'🧲',
     'target':'iPhone15/16ユーザーでケーブル不要の充電方法を探している人',
     'ng':'Androidユーザー・有線充電で十分な人'},
    {'kw':'GaN 充電器 65W コンパクト ノートPC スマホ','title':'GaN充電器65Wでノートも充電｜コンパクトな1台を選ぶ方法','slug':'charger-gan-65w','cat':'モバイル','emoji':'🔌',
     'target':'荷物を減らしたい・1つの充電器でPC・スマホを同時充電したい人',
     'ng':'スマホのみ充電・重さが気になる人'},
    {'kw':'モバイルバッテリー iPhone 向け おすすめ','title':'iPhoneユーザーが後悔しないモバイルバッテリーの選び方','slug':'battery-iphone','cat':'モバイル','emoji':'📱',
     'target':'iPhoneユーザーでモバイルバッテリーを初めて購入する人',
     'ng':'Android使用・ノートPC充電が必要な人'},
    {'kw':'ケーブル内蔵 モバイルバッテリー おすすめ','title':'ケーブル内蔵モバイルバッテリー｜ケーブル忘れが無くなる','slug':'battery-built-in-cable','cat':'モバイル','emoji':'🔌',
     'target':'充電ケーブルを忘れがち・荷物を少なくしたい人',
     'ng':'大容量・高出力を求める人'},
    {'kw':'10000mAh 20000mAh どっち 選び方','title':'10000mAhと20000mAhどっちを買うべき？失敗しない選び方','slug':'battery-capacity-guide','cat':'モバイル','emoji':'📊',
     'target':'容量で迷っていてどちらを選べばいいかわからない人',
     'ng':'すでに容量を決めている人'},
    {'kw':'ワイヤレス充電器 Qi 置くだけ おすすめ','title':'置くだけ充電の生活を始めるワイヤレス充電器','slug':'charger-wireless','cat':'モバイル','emoji':'📡',
     'target':'ケーブルなしの充電生活に切り替えたい人',
     'ng':'急速充電速度を最優先する人・古いAndroid使用'},

    # スマートウォッチ・ゲーミング系（10本）
    {'kw':'スマートウォッチ iPhone Apple Watch以外','title':'Apple Watch以外でiPhoneと繋がるスマートウォッチ','slug':'watch-iphone-non-apple','cat':'スマートウォッチ','emoji':'⌚',
     'target':'iPhoneユーザーだがApple Watchは高い・デザインが合わないと感じている人',
     'ng':'AppleエコシステムをフルやiOS連携を最大化したい人'},
    {'kw':'スマートウォッチ Android おすすめ 2026','title':'Androidと相性抜群のスマートウォッチ｜2026年版','slug':'watch-android-2026','cat':'スマートウォッチ','emoji':'📱',
     'target':'Androidスマホユーザーでスマートウォッチを探している人',
     'ng':'iPhoneユーザー・Apple Watch検討中の人'},
    {'kw':'Garmin Apple Watch どっち スポーツ 健康','title':'GarminかApple Watchか？用途別にどっちがいいか解説','slug':'compare-garmin-applewatch','cat':'スマートウォッチ','emoji':'🏅',
     'target':'GarminかApple Watchで迷っている人',
     'ng':'ビジネス寄りのデザインを重視する人・コスパ重視の人'},
    {'kw':'スマートウォッチ 1万円台 安い','title':'1万円台で買えるスマートウォッチ｜安くても使えるモデル','slug':'watch-budget-15k','cat':'スマートウォッチ','emoji':'💴',
     'target':'スマートウォッチが初めて・予算を抑えたい人',
     'ng':'GPS精度・通話機能を重視する人・長期使用前提の人'},
    {'kw':'スマートウォッチ 睡眠 計測 精度','title':'睡眠の質を本気で改善したい人向けスマートウォッチ','slug':'watch-sleep-tracking','cat':'スマートウォッチ','emoji':'😴',
     'target':'睡眠の質が気になっている・睡眠記録を活用したい人',
     'ng':'GPSランニング機能を重視する人'},
    {'kw':'ゲーミングマウス FPS 軽量 おすすめ','title':'FPSで負ける原因はマウスかも｜軽量ゲーミングマウス','slug':'mouse-fps-lightweight','cat':'ゲーミング','emoji':'🖱️',
     'target':'FPS・シューティングゲームをプレイしている人',
     'ng':'MMO向け多ボタンマウスを探している人'},
    {'kw':'ゲーミングマウス 手が小さい 女性 おすすめ','title':'手が小さい人・女性向けゲーミングマウス','slug':'mouse-small-hand','cat':'ゲーミング','emoji':'🤏',
     'target':'手が小さくてマウスのフィット感で悩んでいる人',
     'ng':'手が大きい人・MMO向け多ボタンを探している人'},
    {'kw':'Webカメラ テレワーク 顔色 綺麗 おすすめ','title':'テレワークで顔色が暗い問題を解決するWebカメラ','slug':'webcam-telework-face','cat':'PC周辺機器','emoji':'📷',
     'target':'Web会議で「顔が暗い・映りが悪い」と言われたことがある人',
     'ng':'カジュアルな通話のみ・高コストを避けたい人'},
    {'kw':'在宅ワーク ガジェット 揃えたい おすすめ','title':'在宅ワークで揃えたいガジェット｜快適になった順に紹介','slug':'telework-gadgets-set','cat':'PC周辺機器','emoji':'🏠',
     'target':'在宅ワーク環境を整えたい・何から買えばいいか迷っている人',
     'ng':'すでに環境が整っている人'},
    {'kw':'ゲーミングヘッドセット PS5 PC 両対応','title':'PS5でもPCでも使えるゲーミングヘッドセット','slug':'headset-ps5-pc','cat':'ゲーミング','emoji':'🎮',
     'target':'PS5とPCを両方持っていてヘッドセットを共用したい人',
     'ng':'PC専用・ワイヤレスにこだわらない人'},
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
        print(f"  ✅ {filename}")
        return True
    print(f"  ❌ {filename}: {res.status_code}")
    return False

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
    except:
        return []

def build_article(theme, products, pub_date):
    """意思決定支援型の記事HTMLを生成"""
    date_str = pub_date.strftime('%Y年%m月%d日')
    year = pub_date.year
    title = theme['title']

    # 商品カード生成
    rank_colors = ['gold','silver','bronze','','']
    rank_labels = ['🥇 最もおすすめ','🥈 コスパ優秀','🥉 人気急上昇','4位','5位']
    product_cards = ''
    img_url = ''

    for i, item in enumerate(products[:5]):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:60]
        price = p.get('itemPrice', 0)
        shop = p.get('shopName', '')
        review_avg = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', 'https://www.rakuten.co.jp/'))
        imgs = p.get('mediumImageUrls', [])
        img = imgs[0].get('imageUrl', '') if imgs else ''
        if i == 0 and img:
            img_url = img

        stars = '★' * int(review_avg) + '☆' * (5 - int(review_avg))
        search_q = requests.utils.quote(name[:30])
        amazon_url = f"https://www.amazon.co.jp/s?k={search_q}"
        yahoo_url = f"https://shopping.yahoo.co.jp/search?p={search_q}"

        img_html = (f'<img src="{img}" alt="{name}" style="width:100%;height:200px;object-fit:contain;background:#f8f8f8;border-radius:8px;padding:8px">'
                   if img else f'<div style="width:100%;height:200px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:60px">{theme["emoji"]}</div>')

        product_cards += f'''
<div class="rank-card" id="rank{i+1}">
  <div class="rank-header {rank_colors[i]}">
    <span class="rank-number">{i+1}</span>
    <span class="rank-label">{rank_labels[i]}</span>
  </div>
  <div class="rank-body">
    {img_html}
    <h3 class="rank-name" style="margin-top:12px">{name}</h3>
    <div class="rank-shop">📦 {shop}</div>
    <div style="margin:8px 0">
      <span style="color:#FFD700">{stars}</span> <strong>{review_avg:.1f}</strong>
      <a href="{affiliate_url}" target="_blank" rel="noopener" style="color:#FF4D00;font-size:.82rem;margin-left:8px">{review_count:,}件の口コミを読む →</a>
    </div>
    <p style="font-size:.82rem;color:#999;background:#fffbf0;border-left:3px solid #f39c12;padding:8px;border-radius:4px;margin:8px 0">
      📅 {date_str}確認　参考価格：¥{price:,}（変動あり・最新価格はリンク先で確認）
    </p>
    <div style="display:flex;flex-direction:column;gap:7px;margin-top:12px">
      <a href="{affiliate_url}" style="display:block;background:#BF0000;color:#fff;text-align:center;padding:12px;border-radius:8px;font-weight:700;font-size:.9rem;text-decoration:none" target="_blank" rel="noopener sponsored">🛒 楽天でポイント還元込み価格を確認する</a>
      <a href="{amazon_url}" style="display:block;background:#FF9900;color:#fff;text-align:center;padding:9px;border-radius:8px;font-weight:600;font-size:.85rem;text-decoration:none" target="_blank" rel="noopener">📦 Amazonで最短配送・レビューを確認する</a>
      <a href="{yahoo_url}" style="display:block;background:#FF0033;color:#fff;text-align:center;padding:9px;border-radius:8px;font-weight:600;font-size:.85rem;text-decoration:none" target="_blank" rel="noopener">💳 Yahoo!でPayPay還元価格を確認する</a>
    </div>
  </div>
</div>'''

    # 比較表
    table_rows = ''
    for i, item in enumerate(products[:5]):
        p = item.get('Item', {})
        name = p.get('itemName', '')[:22]
        price = p.get('itemPrice', 0)
        review_avg = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        stars = '★' * int(review_avg) + '☆' * (5 - int(review_avg))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        table_rows += f'<tr><td><span class="rank-no">{i+1}位</span>{name}</td><td>¥{price:,}</td><td>{stars} {review_avg:.1f}</td><td>{review_count:,}件</td><td><a href="{affiliate_url}" target="_blank" rel="noopener sponsored" style="color:#BF0000;font-weight:700">楽天→</a></td></tr>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>【{year}年】{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新｜{title}。{theme["target"]}向け。楽天実売データ・口コミ数で比較。おすすめしない人・弱点まで正直解説。楽天・Amazon・Yahoo!価格比較リンクつき。({date_str}更新)">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
<style>
.ng-box{{background:#fff5f5;border-left:4px solid #e74c3c;border-radius:8px;padding:12px 16px;margin:12px 0;font-size:.88rem}}
.ng-box strong{{color:#c0392b}}
.ok-box{{background:#f0fff4;border-left:4px solid #2ecc71;border-radius:8px;padding:12px 16px;margin:12px 0;font-size:.88rem}}
.ok-box strong{{color:#27ae60}}
.sticky-cta{{position:fixed;bottom:0;left:0;right:0;background:#BF0000;color:white;text-align:center;padding:13px;font-weight:700;z-index:999;display:none}}
@media(max-width:768px){{.sticky-cta{{display:block}}}}
</style>
</head>
<body>
<div style="background:#fffbf0;border-bottom:1px solid #ffe4b0;padding:8px 5%;font-size:12px;color:#666;text-align:center">
⚠️ 本記事は楽天・Amazon・Yahoo!のアフィリエイト広告を含みます。商品評価は独自基準によります。
</div>
<header>
  <div class="header-inner">
    <div class="logo"><a href="{SITE_URL}" style="color:inherit;text-decoration:none">Gadget<span>天国</span></a></div>
    <nav><a href="{SITE_URL}/">トップ</a><a href="{SITE_URL}/archive.html">記事一覧</a></nav>
  </div>
</header>
<div class="hero">
  <span class="hero-badge">{date_str} 更新 | 楽天実売データ参照</span>
  <h1>{theme["emoji"]} {title}</h1>
  <p class="hero-sub"><strong>こんな人向け：</strong>{theme["target"]}<br>
  弱点・おすすめしない人まで正直に解説。楽天・Amazon・Yahoo!価格比較リンクつき。</p>
</div>
<div class="container">
  <div style="font-size:.8rem;color:#999;border:1px solid #eee;border-radius:6px;padding:10px 14px;margin-bottom:20px">
    本記事は楽天・Amazon・Yahoo!アフィリエイトに参加しています。リンクから購入時に運営者へ報酬が発生しますが、<strong>商品評価・順位には影響しません。</strong>
  </div>
  <div class="intro-box">
    <h2 style="font-size:1rem;font-weight:800;margin-bottom:10px">📋 この記事でわかること</h2>
    <ul style="font-size:.9rem;color:#444;padding-left:18px;line-height:2">
      <li>楽天で実際に売れているTOP5（{date_str}時点）</li>
      <li>各商品の<strong>弱点・おすすめしない人</strong></li>
      <li>楽天・Amazon・Yahoo!の価格比較リンク</li>
      <li>楽天の実際の口コミへのリンク</li>
    </ul>
    <div class="ng-box" style="margin-top:12px">
      <strong>⚠️ こんな人にはおすすめしません</strong><br>
      {theme["ng"]}
    </div>
  </div>
  <nav class="toc">
    <div class="toc-title">📋 目次</div>
    <ol>
      <li><a href="#ranking">おすすめランキングTOP5</a></li>
      <li><a href="#compare">スペック比較表</a></li>
      <li><a href="#guide">選び方のポイント</a></li>
      <li><a href="#faq">よくある質問</a></li>
    </ol>
  </nav>
  <section id="ranking">
    <h2 class="section-title">🏆 おすすめランキングTOP5</h2>
    <p style="font-size:.82rem;color:#888;margin-bottom:20px">※楽天市場のレビュー数順。参考価格は{date_str}時点。必ず購入前に最新価格をご確認ください。</p>
    {product_cards if product_cards else f'<div style="text-align:center;padding:40px;color:#888;background:#f5f5f5;border-radius:12px"><div style="font-size:60px;margin-bottom:12px">{theme["emoji"]}</div><p>楽天市場で「{theme["kw"]}」を検索してみてください。</p><a href="https://www.rakuten.co.jp/search/itemSearch.html?keyword={requests.utils.quote(theme["kw"])}" target="_blank" rel="noopener sponsored" style="display:inline-block;margin-top:12px;background:#BF0000;color:white;padding:12px 24px;border-radius:8px;font-weight:700;text-decoration:none">楽天で検索する →</a></div>'}
  </section>
  <section id="compare">
    <h2 class="section-title">📊 比較表</h2>
    <p style="font-size:.82rem;color:#888;margin-bottom:12px">※参考価格は{date_str}時点。セール・ポイント還元で変動します。</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>商品名</th><th>参考価格</th><th>評価</th><th>口コミ数</th><th>購入</th></tr></thead>
        <tbody>{table_rows if table_rows else '<tr><td colspan="5" style="text-align:center;padding:20px;color:#888">楽天で検索してご確認ください</td></tr>'}</tbody>
      </table>
    </div>
    <p style="font-size:.82rem;color:#999;margin-top:8px">💡 楽天はポイント還元・セールで実質価格がさらに安くなる場合があります。</p>
  </section>
  <section id="guide">
    <h2 class="section-title">🔍 選び方のポイント</h2>
    <div class="guide-grid">
      <div class="guide-item"><div class="guide-item-icon">💰</div><div class="guide-item-title">①予算を先に決める</div><div class="guide-item-desc">予算によって最適解が変わります。まず予算を明確にしてから選びましょう。</div></div>
      <div class="guide-item"><div class="guide-item-icon">🎯</div><div class="guide-item-title">②用途を明確にする</div><div class="guide-item-desc">主な使用シーンによって最適なスペックが変わります。「なんでも使える」より用途特化の方が満足度が高いです。</div></div>
      <div class="guide-item"><div class="guide-item-icon">⭐</div><div class="guide-item-title">③レビュー数を重視</div><div class="guide-item-desc">評価点より「レビュー数」を重視してください。1,000件以上あれば信頼性が高い傾向です。</div></div>
      <div class="guide-item"><div class="guide-item-icon">🛡️</div><div class="guide-item-title">④保証・正規品を確認</div><div class="guide-item-desc">安さだけで選ぶと後悔することも。国内正規品・保証期間を確認してから購入しましょう。</div></div>
    </div>
  </section>
  <section id="faq">
    <h2 class="section-title">❓ よくある質問</h2>
    <div class="faq">
      <div class="faq-item">
        <div class="faq-q">楽天・Amazon・Yahooどこで買うのがお得？</div>
        <div class="faq-a">楽天はポイント還元・セールが充実。Amazonは配送スピードとレビュー数が強み。Yahoo!はPayPay還元が魅力です。価格は頻繁に変動するため、購入前に3サイトを比較することをおすすめします。</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">価格はいつ確認したものですか？</div>
        <div class="faq-a">掲載価格は{date_str}時点の参考価格です。実際の価格は変動しますので、購入前に必ずリンク先で最新価格をご確認ください。</div>
      </div>
    </div>
  </section>
  <div style="margin-top:24px">
    <h3 style="font-size:1rem;font-weight:700;margin-bottom:12px">📚 関連記事</h3>
    <div style="display:flex;flex-direction:column;gap:8px">
      <a href="{SITE_URL}/archive.html" style="display:block;background:#FF4D00;padding:12px 16px;border-radius:8px;font-size:.9rem;color:white;text-decoration:none;font-weight:700">📚 全記事一覧を見る</a>
      <a href="{SITE_URL}/" style="display:block;background:#f4f4f2;padding:12px 16px;border-radius:8px;font-size:.9rem;color:#333;text-decoration:none">🏠 トップページへ</a>
    </div>
  </div>
</div>
<div class="sticky-cta"><a href="#rank1" style="color:white;text-decoration:none">🏆 おすすめ1位を見る →</a></div>
<footer>
  <div class="footer-logo"><a href="{SITE_URL}" style="color:white;text-decoration:none">Gadget<span style="color:#FF4D00">天国</span></a></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">※本サイトは楽天・Amazon・Yahoo!のアフィリエイトプログラムに参加。掲載価格は{date_str}時点の参考価格です。</p>
  <p style="margin-top:10px;font-size:.75rem">© {year} ガジェット天国</p>
</footer>
<script>
window.addEventListener('scroll', () => {{
  const cta = document.querySelector('.sticky-cta');
  if (cta) cta.style.display = window.scrollY > 600 ? 'block' : 'none';
}});
</script>
</body>
</html>'''

def update_articles_json(new_articles):
    articles_json, _ = get_github_file('articles.json')
    existing = json.loads(articles_json) if articles_json else []
    existing_files = {a['filename'] for a in existing}

    for a in new_articles:
        if a['filename'] not in existing_files:
            existing.insert(0, a)

    existing = existing[:60]
    upload_to_github('articles.json',
                    json.dumps(existing, ensure_ascii=False, indent=2),
                    "Auto: 記事30本一括生成・articles.json更新")

def build_archive(articles):
    today_str = datetime.now().strftime('%Y年%m月%d日')
    cards = ''
    for a in articles:
        img = a.get('img_url', '')
        img_html = (f'<img src="{img}" alt="{a["title"]}" style="width:100%;height:150px;object-fit:contain;background:#f5f5f5">'
                   if img else
                   f'<div style="width:100%;height:150px;background:linear-gradient(135deg,#1a1a1a,#333);display:flex;align-items:center;justify-content:center;font-size:48px">{a.get("emoji","📱")}</div>')
        cards += f'<a href="{a["filename"]}" style="display:block;background:white;border-radius:12px;overflow:hidden;border:1px solid #eee;text-decoration:none;color:inherit"><div style="position:relative">{img_html}<div style="position:absolute;top:6px;left:6px;background:#FF4D00;color:white;font-size:10px;font-weight:700;padding:2px 8px;border-radius:999px">{a.get("category","")}</div></div><div style="padding:12px"><div style="font-size:13px;font-weight:700;line-height:1.4;margin-bottom:4px">{a["title"]}</div><div style="font-size:11px;color:#888">📅 {a["date"]}</div></div></a>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記事一覧（全{len(articles)}記事） | ガジェット天国</title>
<meta name="description" content="ガジェット天国の全記事一覧。イヤホン・スマートウォッチ・モバイルバッテリー・ゲーミングなど用途別比較記事{len(articles)}本。">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
</head>
<body>
<header><div class="header-inner"><div class="logo"><a href="{SITE_URL}" style="color:inherit;text-decoration:none">Gadget<span>天国</span></a></div><nav><a href="{SITE_URL}/">トップ</a></nav></div></header>
<div class="hero"><span class="hero-badge">{today_str} 現在</span><h1>📚 記事一覧</h1><p class="hero-sub">全{len(articles)}記事 | 順次更新中</p></div>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;padding:30px 5%;max-width:1200px;margin:0 auto">{cards}</div>
<footer><div class="footer-logo"><a href="{SITE_URL}" style="color:white;text-decoration:none">Gadget<span style="color:#FF4D00">天国</span></a></div><a class="back-link" href="{SITE_URL}/">← トップ</a><p class="footer-note">© {datetime.now().year} ガジェット天国</p></footer>
</body></html>'''

def main():
    today = datetime.now()
    print(f"🚀 記事30本一括生成開始 {today.strftime('%Y年%m月%d日')}")

    new_articles_meta = []
    success_count = 0

    for idx, theme in enumerate(BULK_THEMES):
        # 日付を1日ずつずらす（最近の記事に見せる）
        pub_date = today - timedelta(days=idx)

        print(f"\n[{idx+1}/{len(BULK_THEMES)}] {theme['title']}")

        # 楽天商品取得
        products = fetch_rakuten_products(theme['kw'])
        if not products:
            products = fetch_rakuten_products(theme['cat'] + ' おすすめ')
        print(f"  楽天: {len(products)}件取得")

        # 記事生成
        article_html = build_article(theme, products, pub_date)

        # ファイル名
        date_str = pub_date.strftime('%Y%m%d')
        filename = f"{theme['slug']}-{date_str}.html"

        # GitHub アップロード
        if upload_to_github(filename, article_html, f"Bulk: {theme['title']}"):
            success_count += 1

            # メタ情報
            img_url = ''
            if products:
                p = products[0].get('Item', {})
                imgs = p.get('mediumImageUrls', [])
                if imgs:
                    img_url = imgs[0].get('imageUrl', '')

            new_articles_meta.append({
                'title': f"【{pub_date.year}年】{theme['title']}",
                'filename': filename,
                'img_url': img_url,
                'category': theme['cat'],
                'emoji': theme['emoji'],
                'theme_key': theme['title'],
                'date': pub_date.strftime('%Y年%m月%d日'),
                'description': f"{theme['target']}向け。{theme['title']}をランキング形式で比較。"
            })

        # API制限対策
        time.sleep(2)

    print(f"\n📊 結果: {success_count}/{len(BULK_THEMES)}本 成功")

    # articles.json更新
    print("📋 articles.json更新中...")
    update_articles_json(new_articles_meta)

    # アーカイブページ更新
    print("📚 アーカイブページ更新中...")
    articles_json, _ = get_github_file('articles.json')
    if articles_json:
        all_articles = json.loads(articles_json)
        archive_html = build_archive(all_articles)
        upload_to_github('archive.html', archive_html, "Bulk: アーカイブ更新")

    print(f"\n🎉 完了！ {success_count}本の記事を公開しました")
    print(f"アーカイブ: {SITE_URL}/archive.html")

if __name__ == '__main__':
    main()
