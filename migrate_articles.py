#!/usr/bin/env python3
"""
migrate_articles.py
既存の自動生成記事を新レイアウト（画像左・情報右）で一括再生成する
使い方: CLAUDE_API_KEY=xxx GITHUB_TOKEN=xxx python migrate_articles.py
"""
import os
import re
import requests
import base64
import json
import time
from datetime import datetime

RAKUTEN_APP_ID     = '1693b6a4-2e07-4e04-b417-61ae0078af36'
RAKUTEN_ACCESS_KEY = 'pk_og9K73XUC5Pj2NMihItIkqjAvhhux8P80FmBjdp30PI'
RAKUTEN_AFFILIATE_ID = '533b373d.082b6dc2.533b3742.245bd56b'
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO  = 'gadget-tengoku/gadget-lab'
SITE_URL     = 'https://gadget-tengoku.com'

# ALL_THEMES と同じ定義（theme_key → keyword のマッピング用）
THEME_MAP = {
    '通勤・テレワーク向けノイキャンイヤホン': 'ワイヤレスイヤホン ノイキャン 通勤',
    'スポーツ・ランニング向けイヤホン':       'ワイヤレスイヤホン スポーツ 防水',
    '音質重視ハイレゾイヤホン':               'ワイヤレスイヤホン 高音質 LDAC',
    '5000円以下コスパイヤホン':               'ワイヤレスイヤホン 安い 5000円',
    '骨伝導イヤホン完全ガイド':               '骨伝導イヤホン 開放型',
    'ゲーム向け低遅延イヤホン':               'ゲーミングイヤホン 低遅延',
    'テレワーク向けNCヘッドホン':             'ヘッドホン ノイズキャンセリング',
    'アウトドア向け防水スピーカー':           'Bluetoothスピーカー 防水 アウトドア',
    '健康管理スマートウォッチ':               'スマートウォッチ 血圧 健康管理',
    'ランニング向けGPSウォッチ':              'スマートウォッチ GPS ランニング',
    'ビジネス向けスマートウォッチ':           'スマートウォッチ ビジネス',
    'キッズ向けスマートウォッチ':             'スマートウォッチ 子供 キッズ',
    'Apple Watch全モデル比較':                'Apple Watch おすすめ 比較',
    'Garmin完全比較ガイド':                   'Garmin スマートウォッチ',
    '超軽量モバイルバッテリー':               'モバイルバッテリー 軽量 薄型',
    '旅行向け大容量バッテリー':               'モバイルバッテリー 大容量 旅行',
    'ノートPC対応急速充電バッテリー':         'モバイルバッテリー ノートPC 65W',
    'GaN100W超コンパクト充電器':              'GaN充電器 100W コンパクト',
    'MagSafe対応ワイヤレス充電器':            'ワイヤレス充電器 MagSafe',
    'FPS向け軽量ゲーミングマウス':            'ゲーミングマウス 軽量 FPS',
    'メカニカルゲーミングキーボード':         'ゲーミングキーボード メカニカル',
    'サラウンドゲーミングヘッドセット':       'ゲーミングヘッドセット サラウンド',
    '腰痛対策ゲーミングチェア':               'ゲーミングチェア 腰痛',
    '144Hzゲーミングモニター':                'モニター 144Hz ゲーミング',
    'テレワーク向け4Kモニター':               'モニター 4K テレワーク',
    '配信・テレワーク向けカメラ':             'ウェブカメラ 配信 テレワーク',
    'MacBook向けUSB-Cハブ':                   'USBハブ Type-C MacBook',
    'マッピング水拭きロボット掃除機':         'ロボット掃除機 マッピング 水拭き',
    'Alexa対応スマートLED':                   'スマートLED 電球 Alexa',
    'AI検知屋外防犯カメラ':                   '防犯カメラ 屋外 AI検知',
    '花粉PM2.5対策空気清浄機':               '空気清浄機 花粉 PM2.5',
    '小型ホームシアタープロジェクター':       'プロジェクター 小型 ホームシアター',
    '4K防水アクションカメラ':                 'アクションカメラ 4K 防水',
    'スマホ動画向けジンバル':                 'ジンバル スタビライザー スマホ',
    '前後4Kドライブレコーダー':              'ドライブレコーダー 前後 4K',
    '音波電動歯ブラシ比較':                   '電動歯ブラシ 音波',
    '筋膜リリースマッサージガン':             'マッサージガン 筋膜リリース',
    'Nintendo Switchアクセサリー':            'Switch アクセサリー ケース',
    '後付け対応スマートロック':               'スマートロック 後付け 指紋',
    '配信向けUSBマイク':                      'マイク 配信 USB',
}

EMOJI_MAP = {
    'イヤホン':'🎧','オーディオ':'🔊','スマートウォッチ':'⌚','モバイル':'🔋',
    'ゲーミング':'🎮','PC周辺機器':'🖥️','スマートホーム':'🏠','カメラ':'📷',
    '生活家電':'🏠'
}

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
    print(f"  ❌ {filename} ({res.status_code}): {res.text[:100]}")
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
    except Exception as e:
        print(f"  楽天API エラー: {e}")
        return []

def build_article_html(title, theme_key, cat, emoji, products, filename_date):
    """新レイアウト（画像左・情報右）でHTML生成"""
    today = datetime.now().strftime('%Y年%m月%d日')
    year  = datetime.now().year

    rank_colors = ['gold', 'silver', 'bronze', 'normal', 'normal']
    rank_labels = ['🥇 編集部イチオシ', '🥈 コスパ優秀', '🥉 人気急上昇', '4位', '5位']

    product_cards = ''
    for i, item in enumerate(products[:5]):
        p = item.get('Item', {})
        name         = p.get('itemName', 'N/A')[:60]
        price        = p.get('itemPrice', 0)
        shop         = p.get('shopName', '')[:20]
        review_avg   = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        img_url      = p.get('mediumImageUrls', [{}])[0].get('imageUrl', '') if p.get('mediumImageUrls') else ''
        large_img    = img_url.replace('?_ex=128x128', '?_ex=400x400') if img_url else ''
        item_code    = p.get('itemCode', '')
        review_url   = f"https://review.rakuten.co.jp/item/1/{item_code.replace(':', '/')}/1.1/" if item_code else affiliate_url
        stars_html   = '★' * int(review_avg) + '☆' * (5 - int(review_avg))
        color        = rank_colors[i]
        label        = rank_labels[i]

        display_img = large_img or img_url
        if display_img:
            img_html = f'<img src="{display_img}" alt="{name}" loading="lazy" onerror="this.src=\'{img_url}\'">'
        else:
            img_html = f'<div style="font-size:64px;opacity:.2;text-align:center">{emoji}</div>'

        product_cards += f'''
<div class="rank-card" id="rank{i+1}">
  <div class="rank-header {color}">
    <span class="rank-number">{i+1}</span>
    <span class="rank-label">{label}</span>
    <span class="rank-shop-tag">{shop}</span>
  </div>
  <div class="rank-body">
    <div class="rank-layout">
      <div class="rank-img-col">{img_html}</div>
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

    table_rows = ''
    for i, item in enumerate(products[:5]):
        p = item.get('Item', {})
        name         = p.get('itemName', '')[:28]
        price        = p.get('itemPrice', 0)
        review_avg   = float(p.get('reviewAverage', 0))
        review_count = int(p.get('reviewCount', 0))
        stars        = '★' * int(review_avg) + '☆' * (5 - int(review_avg))
        affiliate_url = p.get('affiliateUrl', p.get('itemUrl', '#'))
        table_rows += f'''<tr>
<td><span class="rank-no">{i+1}位</span>{name}</td>
<td>¥{price:,}</td>
<td>{stars} {review_avg:.1f}</td>
<td>{review_count:,}件</td>
<td><a href="{affiliate_url}" target="_blank" rel="noopener sponsored" style="color:#BF0000;font-weight:700">購入→</a></td>
</tr>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | ガジェット天国</title>
<meta name="description" content="{year}年最新の{theme_key}TOP5を楽天実売データで比較。実際のレビュー数・評価点つき。({today}更新)">
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
  <h1>{emoji} {title}</h1>
  <p class="hero-sub">楽天市場の実売データ・レビュー数をもとに厳選</p>
</div>
<div class="container">
  <div class="intro-box">
    <p>この記事では楽天市場の実際の売れ筋・レビュー数をもとに<strong>{theme_key} TOP5</strong>を厳選しました。気になった商品はリンク先の楽天レビューもご確認ください。</p>
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
      <div class="guide-item"><div class="guide-item-icon">💰</div><div class="guide-item-title">予算を決める</div><div class="guide-item-desc">まず予算を明確に。価格帯でおすすめモデルが変わります。</div></div>
      <div class="guide-item"><div class="guide-item-icon">⭐</div><div class="guide-item-title">レビュー数を確認</div><div class="guide-item-desc">1,000件以上のレビューがあれば実績十分。安心して購入できます。</div></div>
      <div class="guide-item"><div class="guide-item-icon">🔄</div><div class="guide-item-title">用途に合わせる</div><div class="guide-item-desc">日常使い・スポーツ・ビジネスなど用途で最適モデルが変わります。</div></div>
      <div class="guide-item"><div class="guide-item-icon">🛡️</div><div class="guide-item-title">保証・サポート</div><div class="guide-item-desc">国内正規品は保証が充実。安心して長く使えます。</div></div>
    </div>
  </section>
</div>
<footer>
  <div class="footer-logo">Gadget<span>天国</span></div>
  <a class="back-link" href="{SITE_URL}/">← トップページに戻る</a>
  <p class="footer-note">※本サイトは楽天アフィリエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。</p>
  <p style="margin-top:8px;font-size:.72rem">© {year} ガジェット天国</p>
</footer>
</body>
</html>'''

def main():
    print("📖 articles.json を読み込み中...")
    content, _ = get_github_file('articles.json')
    if not content:
        print("❌ articles.json が取得できませんでした")
        return

    articles = json.loads(content)
    auto_articles = [a for a in articles if a.get('filename', '').startswith('article-')]
    print(f"✅ 自動生成記事 {len(auto_articles)} 件を検出")

    success = 0
    fail    = 0
    updated_img_urls = {}

    for i, article in enumerate(auto_articles):
        filename  = article['filename']
        theme_key = article.get('theme_key', '')
        title     = article.get('title', '')
        cat       = article.get('category', '')
        emoji     = article.get('emoji', EMOJI_MAP.get(cat, '📱'))

        # theme_key からキーワードを逆引き
        keyword = THEME_MAP.get(theme_key)
        if not keyword:
            # theme_keyがマップにない場合はタイトルから推測
            keyword = theme_key + ' おすすめ'
            print(f"  ⚠️ [{i+1}/{len(auto_articles)}] テーマ不明: {theme_key} → '{keyword}' で検索")
        else:
            print(f"  🔄 [{i+1}/{len(auto_articles)}] {theme_key}")

        # 楽天から商品取得
        products = fetch_rakuten_products(keyword, hits=5)
        if not products:
            print(f"  ⚠️ 商品取得失敗、スキップ: {filename}")
            fail += 1
            time.sleep(1)
            continue

        # サムネイル用画像URL更新
        first_item = products[0].get('Item', {})
        imgs = first_item.get('mediumImageUrls', [])
        if imgs:
            raw = imgs[0].get('imageUrl', '')
            updated_img_urls[filename] = raw.replace('?_ex=128x128', '?_ex=400x400') if raw else raw

        # HTML再生成
        new_html = build_article_html(title, theme_key, cat, emoji, products, filename)

        # GitHubにアップロード
        if upload_to_github(filename, new_html, f"Migrate: {theme_key} → 新レイアウト"):
            success += 1
        else:
            fail += 1

        # API制限対策：少し待つ
        time.sleep(1.5)

    # articles.json の img_url も更新
    if updated_img_urls:
        print("\n📝 articles.json の画像URLを更新中...")
        for article in articles:
            fn = article.get('filename', '')
            if fn in updated_img_urls:
                article['img_url'] = updated_img_urls[fn]
        upload_to_github('articles.json', json.dumps(articles, ensure_ascii=False, indent=2), "Migrate: articles.json 画像URL更新")

    print(f"\n🎉 完了！ 成功: {success}件 / 失敗: {fail}件")
    print("GitHub Pages の反映まで1〜2分お待ちください。")

if __name__ == '__main__':
    main()
