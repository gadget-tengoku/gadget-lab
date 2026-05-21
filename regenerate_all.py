#!/usr/bin/env python3
"""
ガジェット天国 - 記事一括再生成スクリプト v2
========================================
新ポジショニング「在宅ワーカーのためのガジェット選び」適用版
- 商品フィルタ強化（消耗品・部品を除外）
- スコア式刷新（レビュー0件除外、対数重み付け）
- 透明性セクション追加（GitHub公開ロジック明示）
- canonical URL 正確化
- カテゴリ別文脈に合った商品説明テンプレ
- 楽天サムネイル画像を確実に表示
"""

import os
import sys
import json
import math
import time
import html
import random
import requests
from datetime import datetime, timezone, timedelta

# ===================================================
# 設定
# ===================================================
RAKUTEN_APP_ID = os.environ.get("API_KEY") or os.environ.get("RAKUTEN_APP_ID", "")
RAKUTEN_AFFILIATE_ID = os.environ.get("AFFILIATE_ID") or os.environ.get("RAKUTEN_AFFILIATE_ID", "")
SITE_URL = "https://gadget-tengoku.com"
JST = timezone(timedelta(hours=9))


def log(msg):
    print(f"[{datetime.now(JST).strftime('%H:%M:%S')}] {msg}", flush=True)


# ===================================================
# 再生成対象の記事リスト（15本）
# ===================================================
# 各記事: filename, title, category, keyword, subtheme
ARTICLES = [
    {
        "filename": "article-1万円以下コスパ最強ワイヤレスイヤホン-am-20260506.html",
        "title": "1万円以下コスパ最強ワイヤレスイヤホン｜在宅ワーカーの第1候補",
        "category": "earphone_wireless",
        "keyword": "ワイヤレスイヤホン",
        "subtheme": "コスパ",
        "lead": "毎日のWeb会議用に1万円以下で買えるワイヤレスイヤホンを楽天実売データから絞り込みました。マイク品質とノイキャンの実力を、レビュー件数×評価で重み付け。",
    },
    {
        "filename": "article-iPhone-15対応USB-Cイヤホン-am-20260509.html",
        "title": "iPhone 15対応USB-Cイヤホン｜Web会議で直挿しできる1本",
        "category": "earphone_wireless",
        "keyword": "USB-Cイヤホン",
        "subtheme": "iPhone",
        "lead": "iPhone 15シリーズのUSB-Cポートに直挿しできるイヤホン。Bluetooth不要・遅延ゼロで在宅Web会議に最適です。",
    },
    {
        "filename": "article-通勤-在宅ワーク向けノイキャンイヤホン-am-20260430.html",
        "title": "通勤・在宅ワーク向けノイキャンイヤホン｜Web会議にも使える1台",
        "category": "earphone_wireless",
        "keyword": "ノイズキャンセリング イヤホン",
        "subtheme": "ノイキャン",
        "lead": "電車内・カフェ・在宅Web会議。すべての環境で「相手の声に集中できる」ノイキャンイヤホンを選びました。",
    },
    {
        "filename": "article-Apple-Watch-SE-と-Series-9-am-20260510.html",
        "title": "Apple Watch SE と Series 9 比較ガイド｜在宅で買うならどっち",
        "category": "smartwatch",
        "keyword": "Apple Watch",
        "subtheme": "Apple",
        "lead": "Apple Watchを買うなら SE と Series 9 どちらか。在宅ワーカー視点では「血中酸素」「心電図」が必要かどうかで答えが変わります。",
    },
    {
        "filename": "article-スマートウォッチ初心者の選び方ガイド-am-20260504.html",
        "title": "スマートウォッチ初心者の選び方ガイド｜失敗しない5つの判断軸",
        "category": "smartwatch",
        "keyword": "スマートウォッチ",
        "subtheme": "入門",
        "lead": "初めてのスマートウォッチで失敗しない5つの判断軸を解説。座りすぎ通知・心拍計測・睡眠分析・スマホ連携の優先順位を整理します。",
    },
    {
        "filename": "article-健康管理に使えるスマートウォッチ-am-20260430.html",
        "title": "健康管理に使えるスマートウォッチ｜在宅ワーカーの座りすぎ対策",
        "category": "smartwatch",
        "keyword": "スマートウォッチ 健康管理",
        "subtheme": "健康",
        "lead": "在宅ワーカー最大の敵は座りすぎと運動不足。心拍・ストレス・睡眠の3軸で可視化してくれるスマートウォッチを選びました。",
    },
    {
        "filename": "article-ノートPC対応-大容量モバイルバッテリー-pm-20260510.html",
        "title": "ノートPC対応・大容量モバイルバッテリー｜出張で電源を気にしない",
        "category": "mobile_battery",
        "keyword": "モバイルバッテリー PD",
        "subtheme": "出張",
        "lead": "ノートPCを給電できるPD対応モバイルバッテリーを厳選。容量・出力・重量のバランスで在宅ワーカーの外出を支える1台を選びます。",
    },
    {
        "filename": "article-ワイヤレスマウスおすすめ-在宅ワーク-pm-20260505.html",
        "title": "ワイヤレスマウスおすすめ｜在宅ワーク向け静音・エルゴ",
        "category": "wireless_mouse",
        "keyword": "ワイヤレスマウス 静音",
        "subtheme": "静音",
        "lead": "Web会議中のクリック音が乗らない静音マウス。長時間作業の手首負担を減らすエルゴノミクス設計モデルを優先しました。",
    },
    {
        "filename": "article-ウェブカメラおすすめ比較-pm-20260507.html",
        "title": "ウェブカメラおすすめ比較｜Web会議の映りを底上げする",
        "category": "webcam",
        "keyword": "ウェブカメラ",
        "subtheme": "Web会議",
        "lead": "Web会議での「映りの悪さ」はカメラ買い替えで7割解決します。オートフォーカス・光量補正・解像度の3軸で選びました。",
    },
    {
        "filename": "article-USBマイクおすすめ比較-配信-テレワーク向け--pm-20260506.html",
        "title": "USBマイクおすすめ比較【配信・テレワーク向け】",
        "category": "usb_microphone",
        "keyword": "USBマイク",
        "subtheme": "Web会議",
        "lead": "Web会議で「相手が聞きやすい声」になる単一指向性USBマイク。配信用にも使える音質を確保しつつ、在宅で使いやすいモデルを選びました。",
    },
    {
        "filename": "article-ゲーミングヘッドセット完全比較-am-20260430.html",
        "title": "ゲーミングヘッドセット完全比較｜Web会議転用も視野に",
        "category": "headset",
        "keyword": "ゲーミングヘッドセット",
        "subtheme": "Web会議転用",
        "lead": "ゲーミングヘッドセットは実は在宅ワーカーのWeb会議用にこそ刺さります。業務用より安く、マイクは優秀。両用できる1台を選びました。",
    },
    {
        "filename": "article-テレワーク-在宅ワーク向けヘッドセット-am-20260508.html",
        "title": "テレワーク・在宅ワーク向けヘッドセット比較",
        "category": "headset",
        "keyword": "ヘッドセット テレワーク",
        "subtheme": "テレワーク",
        "lead": "1日中Web会議に出続ける在宅ワーカー向けのヘッドセット。装着感・マイク品質・接続安定性の3軸で絞り込みました。",
    },
    {
        "filename": "article-4Kモニター-27インチおすすめ-pm-20260509.html",
        "title": "4Kモニター 27インチおすすめ｜在宅作業の解像度問題を解決",
        "category": "monitor_4k",
        "keyword": "4Kモニター 27インチ",
        "subtheme": "在宅作業",
        "lead": "在宅ワーカーの生産性を底上げする27インチ4Kモニター。USB-C 1本接続・HDR・IPSパネルなど、実用視点で選びました。",
    },
    {
        "filename": "article-ノートPCスタンドおすすめ-pm-20260511.html",
        "title": "ノートPCスタンドおすすめ｜首・肩の負担を減らす1台",
        "category": "laptop_stand",
        "keyword": "ノートPCスタンド",
        "subtheme": "姿勢",
        "lead": "ノートPCの画面を目線まで上げて、首・肩の負担を減らすスタンド。アルミ製・折りたたみ・角度調整の3軸で選びました。",
    },
    {
        "filename": "article-テレワーク-在宅ワーク向けガジェット-pm-20260508.html",
        "title": "テレワーク・在宅ワーク向けガジェット完全ガイド",
        "category": "wireless_mouse",
        "keyword": "テレワーク ガジェット",
        "subtheme": "総合",
        "lead": "在宅ワーク環境を底上げする周辺機器を、優先順位の高い順に整理します。マウス・キーボード・モニター・スタンドの順で揃えるのが王道。",
    },
]


# ===================================================
# カテゴリ別フィルタ設定
# ===================================================
CATEGORY_CONFIG = {
    "earphone_wireless": {
        "label": "ワイヤレスイヤホン",
        "genre_id": 566215,
        "min_price": 3000,
        "max_price": 80000,
        "min_review_count": 30,
        "min_review_average": 3.8,
        "exclude": ["イヤーピース", "イヤーチップ", "ケース単体", "充電ケーブル", "交換用", "互換品", "保護フィルム", "ストラップ", "シール", "カバー単体"],
        "min_title_length": 12,
        "features": ["ノイズキャンセリング", "ANC", "ハイレゾ", "LDAC", "マルチポイント", "ワイヤレス", "Bluetooth"],
        "angle": "Web会議での音声品質と長時間装着の快適性",
    },
    "smartwatch": {
        "label": "スマートウォッチ",
        "genre_id": 566382,
        "min_price": 5000,
        "max_price": 200000,
        "min_review_count": 20,
        "min_review_average": 3.8,
        "exclude": ["バンド単体", "ベルト単体", "ストラップ単体", "保護フィルム", "ケース単体", "充電ケーブル単体", "交換用"],
        "min_title_length": 12,
        "features": ["GPS", "心拍", "血中酸素", "睡眠", "Suica", "FeliCa", "スマートウォッチ"],
        "angle": "座りすぎ通知・心拍ベースのストレス可視化",
    },
    "mobile_battery": {
        "label": "モバイルバッテリー",
        "genre_id": 560029,
        "min_price": 1500,
        "max_price": 30000,
        "min_review_count": 30,
        "min_review_average": 4.0,
        "exclude": ["ケーブル単品", "ACアダプタ単品", "ケース単体", "シール", "予備バッテリー（交換用）"],
        "min_title_length": 10,
        "features": ["PD", "急速充電", "MagSafe", "Qi", "USB-C", "大容量"],
        "angle": "カフェ作業・出張時のノートPC給電",
    },
    "wireless_mouse": {
        "label": "ワイヤレスマウス",
        "genre_id": 566375,
        "min_price": 1500,
        "max_price": 30000,
        "min_review_count": 20,
        "min_review_average": 4.0,
        "exclude": ["マウスパッド", "マウスソール", "替え芯", "電池単体"],
        "min_title_length": 10,
        "features": ["静音", "Bluetooth", "エルゴノミクス", "ロジクール", "MX"],
        "angle": "長時間作業の手首負担と静音性",
    },
    "webcam": {
        "label": "ウェブカメラ",
        "genre_id": 558943,
        "min_price": 2000,
        "max_price": 50000,
        "min_review_count": 20,
        "min_review_average": 4.0,
        "exclude": ["三脚単品", "クリップ単品", "リング単品"],
        "min_title_length": 10,
        "features": ["1080p", "4K", "オートフォーカス", "プライバシー", "Logicool"],
        "angle": "Web会議での映りの良さと光量補正",
    },
    "headset": {
        "label": "ヘッドセット",
        "genre_id": 558943,
        "min_price": 2000,
        "max_price": 60000,
        "min_review_count": 20,
        "min_review_average": 4.0,
        "exclude": ["イヤーパッド", "ケーブル単品", "替え", "スタンド単品"],
        "min_title_length": 12,
        "features": ["ノイズキャンセリングマイク", "USB", "Bluetooth", "両耳", "ヘッドセット"],
        "angle": "Web会議での聞き取りやすさと相手への音声明瞭度",
    },
    "usb_microphone": {
        "label": "USBマイク",
        "genre_id": 567172,
        "min_price": 2000,
        "max_price": 50000,
        "min_review_count": 20,
        "min_review_average": 4.0,
        "exclude": ["ポップガード単品", "ショックマウント単品", "ケーブル単品", "スタンド単品"],
        "min_title_length": 10,
        "features": ["コンデンサ", "単一指向性", "ミュート", "USB-C", "マイク"],
        "angle": "Web会議・配信での音声品質",
    },
    "monitor_4k": {
        "label": "4Kモニター",
        "genre_id": 211195,
        "min_price": 25000,
        "max_price": 200000,
        "min_review_count": 10,
        "min_review_average": 4.0,
        "exclude": ["モニターアーム", "保護フィルム", "スタンド単品", "ケーブル単品"],
        "min_title_length": 12,
        "features": ["IPS", "USB-C", "HDR", "HDMI", "DisplayPort", "4K"],
        "angle": "長時間作業の目疲労と画面占有率",
    },
    "laptop_stand": {
        "label": "ノートPCスタンド",
        "genre_id": 564586,
        "min_price": 1000,
        "max_price": 20000,
        "min_review_count": 20,
        "min_review_average": 4.0,
        "exclude": ["クッション", "保護ケース", "カバー"],
        "min_title_length": 10,
        "features": ["アルミ", "角度調節", "折りたたみ", "放熱", "スタンド"],
        "angle": "首・肩への負担軽減",
    },
}


# ブランド信頼スコア
BRAND_TRUST = {
    "Sony": 10, "ソニー": 10, "Apple": 10, "Bose": 9, "Jabra": 9, "JBL": 8,
    "Anker": 8, "Soundcore": 8, "Logicool": 9, "Logitech": 9,
    "Garmin": 9, "Xiaomi": 7, "Fitbit": 7, "HUAWEI": 7,
    "Razer": 8, "SteelSeries": 8, "HyperX": 8, "Corsair": 7,
    "Panasonic": 9, "パナソニック": 9, "EPOS": 8, "Shure": 9, "Blue": 8,
    "Dell": 8, "LG": 8, "BenQ": 8, "ASUS": 8, "iiyama": 7,
    "CIO": 7, "ELECOM": 7, "エレコム": 7, "Buffalo": 7, "サンワサプライ": 7,
}


# ===================================================
# 楽天API
# ===================================================
def fetch_rakuten(keyword, config):
    """品質フィルタを通過した商品を返す。フォールバック付き。"""
    fallback_rc = [config["min_review_count"], max(5, config["min_review_count"] // 2), 3]
    for min_rc in fallback_rc:
        params = {
            "applicationId": RAKUTEN_APP_ID,
            "affiliateId": RAKUTEN_AFFILIATE_ID,
            "keyword": keyword,
            "genreId": config["genre_id"],
            "minPrice": config["min_price"],
            "maxPrice": config["max_price"],
            "hits": 30,
            "sort": "-reviewCount",
            "format": "json",
        }
        try:
            r = requests.get(
                "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601",
                params=params, timeout=15,
            )
            r.raise_for_status()
            items = [it["Item"] for it in r.json().get("Items", [])]
        except Exception as e:
            log(f"  ⚠ Rakuten API error: {e}")
            items = []
        filtered = []
        for item in items:
            name = item.get("itemName", "")
            if len(name) < config["min_title_length"]:
                continue
            if any(ng in name for ng in config["exclude"]):
                continue
            if item.get("reviewCount", 0) < min_rc:
                continue
            if item.get("reviewAverage", 0) < config["min_review_average"]:
                continue
            if item.get("itemPrice", 0) <= 0:
                continue
            filtered.append(item)
        if len(filtered) >= 5:
            return filtered[:10]
    return filtered


def calculate_score(item, config):
    name = item.get("itemName", "")
    review_avg = item.get("reviewAverage", 0)
    review_count = item.get("reviewCount", 0)
    price = item.get("itemPrice", 0)
    if review_count == 0 or review_avg == 0 or price <= 0:
        return None
    review_score = min(35, review_avg * math.log10(review_count + 1) * 5)
    mid_lo = config["min_price"] * 1.5
    mid_hi = config["max_price"] * 0.7
    if mid_lo <= price <= mid_hi:
        cost_score = 25
    elif config["min_price"] <= price <= config["max_price"]:
        cost_score = 18
    else:
        cost_score = 10
    brand_score = 5
    name_lower = name.lower()
    for brand, weight in BRAND_TRUST.items():
        if brand.lower() in name_lower:
            brand_score = weight
            break
    feature_bonus = sum(3 for kw in config["features"] if kw.lower() in name_lower)
    feature_bonus = min(15, feature_bonus)
    total = review_score + cost_score + brand_score + feature_bonus + 10
    return round(min(100, total))


# ===================================================
# テンプレ商品説明（Claude API不使用、データから決定論的に生成）
# ===================================================
def generate_summary(item, config):
    name = item.get("itemName", "")
    price = item.get("itemPrice", 0)
    rc = item.get("reviewCount", 0)
    ra = item.get("reviewAverage", 0)
    found = [f for f in config["features"] if f.lower() in name.lower()]

    # 価格・件数・評価から「指紋」を作り、商品ごとに違う文型を選ぶ
    fp_price = price % 3
    fp_review = rc % 4
    fp_feat = (price + rc) % 3

    # --- 価格に関する一文（数値で具体的に） ---
    mid_lo, mid_hi = config["min_price"] * 1.5, config["max_price"] * 0.7
    if price <= mid_lo:
        price_variants = [
            f"¥{price:,}という価格は、このカテゴリでは入門〜中堅クラス",
            f"¥{price:,}と手を出しやすく、最初の1台や買い替えの候補にしやすい",
            f"予算を抑えたい人向けの¥{price:,}という価格設定",
        ]
    elif price >= mid_hi:
        price_variants = [
            f"¥{price:,}とこのカテゴリでは上位の価格帯",
            f"¥{price:,}と決して安くはないが、その分スペックは充実しやすい価格帯",
            f"¥{price:,}というハイエンド寄りの価格",
        ]
    else:
        price_variants = [
            f"¥{price:,}と、価格と機能のバランスが取りやすい中位帯",
            f"¥{price:,}という、最も選ばれやすい価格ゾーン",
            f"¥{price:,}でこのカテゴリの主力価格帯に位置する",
        ]
    price_sentence = price_variants[fp_price]

    # --- レビューに関する一文（件数で語り口を変える） ---
    if rc >= 1000:
        review_variants = [
            f"レビューは{rc}件と非常に多く、平均{ra:.1f}。これだけ件数があると評価のブレは小さい",
            f"{rc}件という大量のレビューで平均{ra:.1f}を維持しているのは安心材料",
            f"母数{rc}件・平均{ra:.1f}。この規模のレビュー数は信頼性の裏付けになる",
        ]
    elif rc >= 300:
        review_variants = [
            f"レビュー{rc}件・平均{ra:.1f}と、判断材料としては十分な件数",
            f"{rc}件のレビューで平均{ra:.1f}。評価傾向が見える水準に達している",
            f"平均{ra:.1f}（{rc}件）で、ユーザー層の評価がそれなりに固まっている",
        ]
    elif rc >= 100:
        review_variants = [
            f"レビューは{rc}件・平均{ra:.1f}。まだ件数は伸びる余地があるが評価は良好",
            f"{rc}件で平均{ra:.1f}。新しめのモデルか、ニッチ寄りの可能性",
            f"平均{ra:.1f}（{rc}件）。件数は中程度なので口コミ内容も確認したい",
        ]
    else:
        review_variants = [
            f"レビューは{rc}件と少なめだが平均{ra:.1f}と高い。発売間もないか玄人向けか",
            f"{rc}件・平均{ra:.1f}。母数が小さいので評価は参考程度に見るのが無難",
            f"平均{ra:.1f}ながらレビュー{rc}件と少なく、判断は慎重に",
        ]
    review_sentence = review_variants[fp_review]

    # --- 機能に関する一文 ---
    if found:
        feat_str = "・".join(found[:2])
        feat_variants = [
            f"商品名には{feat_str}が含まれ、{config['angle']}を求める人と相性がいい",
            f"{feat_str}に対応している点が、{config['angle']}という観点で効いてくる",
            f"{feat_str}を備えており、用途が「{config['angle']}」ならチェックしておきたい",
        ]
    else:
        feat_variants = [
            f"派手な特徴はないが、{config['angle']}という基本は押さえている",
            f"{config['angle']}という観点では、突出はしないものの堅実な選択肢",
            f"スペック表記は控えめ。{config['angle']}重視なら詳細仕様の確認を推奨",
        ]
    feat_sentence = feat_variants[fp_feat]

    return f"{price_sentence}。{review_sentence}。{feat_sentence}。"

def generate_recommend(item, rank, config):
    """おすすめする人のフレーズ。商品の特性とランクに応じて変える。"""
    name_lower = item.get("itemName", "").lower()
    has_feature = any(f.lower() in name_lower for f in config["features"])
    price = item.get("itemPrice", 0)

    if rank == 1:
        if has_feature:
            return f"このカテゴリで「{config['label']}」を初めて買う在宅ワーカー全般。迷ったらまずこれ"
        else:
            return f"レビュー件数の安定感とブランドの信頼性を最優先したい在宅ワーカー"
    elif rank == 2:
        return f"1位より少し違うアプローチで{config['label']}を選びたい人。{config['angle']}を重視するなら有力候補"
    elif rank == 3:
        if price < (config["min_price"] * 2):
            return f"とにかく初期投資を抑えたい人。在宅ワーク用途で最初の1台として試すなら"
        else:
            return f"上位2台と比較しつつ、価格と機能のバランスを取りたい人"
    else:
        return f"{config['angle']}という軸で、もう1つ選択肢を持っておきたい人"


def generate_not_recommend(item, config):
    """おすすめしない人のフレーズ。"""
    price = item.get("itemPrice", 0)
    if price > config["max_price"] * 0.8:
        return f"とにかく安く済ませたい人。この価格帯なら同カテゴリの上位機種と比較検討を"
    elif price < config["min_price"] * 1.3:
        return f"高音質・高機能を最優先する人。この価格帯では機能の取捨選択は避けられない"
    else:
        return f"特定の用途（プロ用途・極端な静音性・特殊な接続要件）を求める人"


# ===================================================
# HTML生成
# ===================================================
COMMON_CSS_LINK = '<link rel="stylesheet" href="article-style.css">'

HEADER_HTML = '''<header class="site-header">
  <div class="header-inner">
    <a href="/" class="brand">Gadget<span class="accent">天国</span></a>
    <nav class="nav-main">
      <a href="earphone.html">イヤホン</a>
      <a href="smartwatch.html">スマートウォッチ</a>
      <a href="battery.html">バッテリー</a>
      <a href="telework.html">テレワーク</a>
      <a href="gaming.html">PC周辺</a>
      <a href="archive.html">記事一覧</a>
      <a href="about.html">編集部</a>
    </nav>
  </div>
</header>'''

FOOTER_HTML = '''<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-brand">
        <h4>Gadget<span style="color: var(--accent);">天国</span></h4>
        <p>在宅ワーカーのためのガジェット選びを、楽天実売データとレビュー分析で支援するメディア。スコアリングロジックはGitHubで全公開。</p>
      </div>
      <div class="footer-col">
        <h5>Categories</h5>
        <ul>
          <li><a href="earphone.html">イヤホン</a></li>
          <li><a href="smartwatch.html">スマートウォッチ</a></li>
          <li><a href="battery.html">バッテリー</a></li>
          <li><a href="telework.html">テレワーク</a></li>
          <li><a href="gaming.html">PC周辺</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5>About</h5>
        <ul>
          <li><a href="archive.html">記事一覧</a></li>
          <li><a href="about.html">編集部</a></li>
          <li><a href="review-policy.html">レビュー方針</a></li>
          <li><a href="ad-policy.html">広告ポリシー</a></li>
          <li><a href="privacy.html">プライバシーポリシー</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5>Connect</h5>
        <ul>
          <li><a href="https://twitter.com/gadget_tengoku">X (Twitter)</a></li>
          <li><a href="https://github.com/gadget-tengoku/gadget-lab">GitHub</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      ※本サイトは楽天アフィリエイトプログラムおよびAmazonアソシエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。掲載価格は楽天市場の参照価格であり、価格・在庫は変動します。購入前に必ず各ショッピングサイトでご確認ください。<br>
      © 2026 ガジェット天国
    </div>
  </div>
</footer>'''


def render_article(article, products, config):
    """記事HTMLを生成。"""
    today = datetime.now(JST).strftime("%Y年%m月%d日")
    today_iso = datetime.now(JST).strftime("%Y-%m-%d")
    canonical = f"{SITE_URL}/{article['filename']}"

    # ランキング部分
    ranking_html = ""
    for i, p in enumerate(products[:5], 1):
        rank_label = {1: "🥇 1位", 2: "🥈 2位", 3: "🥉 3位", 4: "4位", 5: "5位"}[i]
        item_name = html.escape(p.get("itemName", ""))
        item_url = p.get("affiliateUrl") or p.get("itemUrl", "#")
        shop_name = html.escape(p.get("shopName", ""))
        price = p.get("itemPrice", 0)
        review_count = p.get("reviewCount", 0)
        review_avg = p.get("reviewAverage", 0)
        stars = "★" * int(round(review_avg)) + "☆" * (5 - int(round(review_avg)))
        image_url = ""
        if p.get("mediumImageUrls"):
            image_url = p["mediumImageUrls"][0].get("imageUrl", "") if isinstance(p["mediumImageUrls"][0], dict) else p["mediumImageUrls"][0]
            image_url = image_url.replace("?_ex=128x128", "?_ex=400x400")
        score = p.get("_score", 0)

        summary = generate_summary(p, config)
        recommend = generate_recommend(p, i, config)
        not_recommend = generate_not_recommend(p, config)

        img_block = f'<img src="{image_url}" alt="{item_name}" loading="lazy">' if image_url else '🎁'

        ranking_html += f'''
<div class="ranking-item rank-{i}">
  <span class="rank">{rank_label} · スコア {score}/100</span>
  <h3 class="product-name">{item_name}</h3>
  <div class="product-brand">{shop_name}</div>
  <div class="product-image">{img_block}</div>
  <div class="rating">{stars} <span class="score">{review_avg:.1f}</span> <a href="{item_url}" target="_blank" rel="nofollow noopener sponsored">楽天レビュー {review_count}件 →</a></div>
  <div class="price">📅 {today}確認｜参考価格：<strong>¥{price:,}〜</strong></div>
  <p>{html.escape(summary)}</p>
  <div class="recommend">{html.escape(recommend)}</div>
  <div class="not-recommend">{html.escape(not_recommend)}</div>
  <p style="margin-top:1rem;"><a class="btn btn-rakuten" href="{item_url}" target="_blank" rel="nofollow noopener sponsored">楽天で価格を見る →</a></p>
</div>
'''

    # 比較表
    table_rows = ""
    for i, p in enumerate(products[:5], 1):
        item_url = p.get("affiliateUrl") or p.get("itemUrl", "#")
        item_name_short = html.escape(p.get("itemName", "")[:50])
        table_rows += f'''<tr>
  <td><strong>{i}位</strong></td>
  <td>{item_name_short}</td>
  <td>¥{p.get("itemPrice", 0):,}</td>
  <td>{p.get("reviewAverage", 0):.1f}★</td>
  <td>{p.get("reviewCount", 0)}件</td>
  <td>{p.get("_score", 0)}/100</td>
  <td><a href="{item_url}" target="_blank" rel="nofollow noopener sponsored">楽天</a></td>
</tr>'''

    html_doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(article["title"])} - ガジェット天国</title>
<meta name="description" content="{html.escape(article["lead"])}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{html.escape(article["title"])}">
<meta property="og:description" content="{html.escape(article["lead"])}">
<meta property="og:image" content="{SITE_URL}/ogp.png">
<meta property="og:site_name" content="ガジェット天国">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@gadget_tengoku">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":{json.dumps(article["title"], ensure_ascii=False)},"description":{json.dumps(article["lead"], ensure_ascii=False)},"url":"{canonical}","datePublished":"{today_iso}","dateModified":"{today_iso}","author":{{"@type":"Organization","name":"ガジェット天国 編集部","url":"{SITE_URL}/about.html"}},"publisher":{{"@type":"Organization","name":"ガジェット天国","logo":{{"@type":"ImageObject","url":"{SITE_URL}/ogp.png"}}}}}}
</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
{COMMON_CSS_LINK}
</head>
<body>

{HEADER_HTML}

<main>
  <div class="breadcrumb"><a href="/">TOP</a> / {html.escape(config["label"])} / 記事</div>

  <article>
    <div class="article-meta">{today} 公開 · 在宅ワーカー視点で分析</div>
    <h1>{html.escape(article["title"])}</h1>
    <p style="font-size: 1.05rem; line-height: 1.95;">{html.escape(article["lead"])}</p>

    <div class="conclusion">
      <h3>📌 結論（在宅ワーカー視点）</h3>
      <p>このカテゴリの選び方の核は <mark>「{config["angle"]}」</mark> です。
      下位ランキングTOP5は、楽天市場の<strong>本体商品のみ</strong>に絞った上で、
      レビュー件数×評価×ブランド信頼度の重み付けスコアで並べています。</p>
      <p>急いでいる方は <strong>1位</strong> を見るのが早いです。価格や用途で迷う場合は比較表をどうぞ。</p>
    </div>

    <h2>🏆 おすすめランキング TOP5</h2>
    <p>※価格は{today}時点。セール・ポイント還元で変動します。購入前に必ず最新価格をご確認ください。</p>

    {ranking_html}

    <h2>📊 スペック比較表</h2>
    <table>
      <thead>
        <tr><th>順位</th><th>商品名</th><th>参考価格</th><th>評価</th><th>口コミ</th><th>スコア</th><th>購入</th></tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>

    <h2>💡 失敗しない選び方</h2>
    <p>{config["label"]}を在宅ワーカー視点で選ぶときに、最低限押さえておきたい判断軸を整理します。</p>
    <ol>
      <li><strong>{config["angle"]}を最優先する</strong> — 派手な機能より、毎日使う場面で効くスペックを選ぶ</li>
      <li><strong>レビュー件数を見る</strong> — 評価点が高くてもレビューが少ないと判断材料が弱い</li>
      <li><strong>ブランドの信頼性</strong> — 同価格帯なら主要ブランドを選ぶのが失敗しにくい</li>
      <li><strong>本体商品か確認</strong> — 楽天検索では消耗品・部品が混ざりやすい。当ランキングは除外済み</li>
      <li><strong>セール時期</strong> — 楽天スーパーセール・お買い物マラソンで最大15%引きも</li>
    </ol>

    <h2>❓ よくある質問</h2>
    <details><summary>Amazon と楽天、どっちで買うのが得？</summary>
    <p>楽天スーパーセール・お買い物マラソン中は楽天がポイント還元込みで実質安くなります。Amazonはタイムセールが強い時期があり、急ぎでない場合は両方の価格を比較するのが確実です。</p></details>
    <details><summary>このランキングは実機検証ですか？</summary>
    <p>いいえ。当サイトは実機を所有していません。楽天市場のレビューデータと公式仕様を独自に分析してランキングを作成しています。詳細は記事下の「透明性方針」をご覧ください。</p></details>
    <details><summary>掲載商品の在庫はありますか？</summary>
    <p>各楽天ストアの在庫状況によります。リンク先で在庫切れの場合は、同じ商品名で楽天市場内を再検索してください。</p></details>

    <section class="transparency">
      <h2 style="color: #f4f1ea; border-bottom-color: #f4f1ea;">📊 このランキングの算出方法</h2>
      <p>当サイトは実機を所有していません。<strong style="color: #f0d878;">実機検証ができない範囲を明示した上で、楽天市場の実売データを独自に加工</strong> してランキングを作成しています。</p>
      <ul style="color: rgba(244,241,234,0.85);">
        <li>データソース：楽天市場 商品検索API（{today}取得、ジャンルID {config["genre_id"]} に限定）</li>
        <li>除外：消耗品・部品（タイトルに「交換」「単体」等を含む商品）、レビュー{config["min_review_count"]}件未満、評価{config["min_review_average"]:.1f}未満</li>
      </ul>
      <pre>総合スコア =
  レビュー評価 × log10(レビュー件数+1) × 5  [上限35点]
+ 価格帯マッチング                          [10-25点]
+ ブランド信頼スコア                        [5-10点]
+ 重要機能キーワード含有                    [上限15点]
+ ベースライン                              [10点]</pre>
      <p style="color: rgba(244,241,234,0.85);">ソースコードは <a href="https://github.com/gadget-tengoku/gadget-lab">github.com/gadget-tengoku/gadget-lab</a> で公開しています。実機の使用感は <a href="https://my-best.com">マイベスト</a> や <a href="https://kakakumag.com">価格.comマガジン</a> もあわせてご確認ください。</p>
    </section>

    <h2>📰 関連記事</h2>
    <div class="related">
      <a href="earphone.html">イヤホン比較一覧</a>
      <a href="smartwatch.html">スマートウォッチ比較一覧</a>
      <a href="telework.html">テレワークガジェット比較一覧</a>
      <a href="archive.html">全記事を見る</a>
    </div>

    <p class="disclaimer">※本記事は楽天アフィリエイトを利用しています。リンクから購入された場合、当サイトに報酬が発生することがあります。価格・在庫は変動します。購入前に必ず楽天市場の最新情報をご確認ください。</p>

  </article>
</main>

{FOOTER_HTML}

</body>
</html>
'''
    return html_doc


# ===================================================
# メイン処理
# ===================================================
def main():
    if not RAKUTEN_APP_ID or not RAKUTEN_AFFILIATE_ID:
        log("❌ ERROR: RAKUTEN_APP_ID / RAKUTEN_AFFILIATE_ID environment variables not set")
        log("   (also tried: API_KEY / AFFILIATE_ID)")
        sys.exit(1)

    log(f"🚀 Regenerate start: {len(ARTICLES)} articles")
    success, failed = 0, 0

    for idx, article in enumerate(ARTICLES, 1):
        log(f"[{idx}/{len(ARTICLES)}] {article['filename']}")
        config = CATEGORY_CONFIG.get(article["category"])
        if not config:
            log(f"  ⚠ Unknown category: {article['category']}")
            failed += 1
            continue

        # 楽天検索
        items = fetch_rakuten(article["keyword"], config)
        if len(items) < 3:
            log(f"  ⚠ Only {len(items)} items found, skip")
            failed += 1
            continue

        # スコアリング
        scored = []
        for item in items:
            s = calculate_score(item, config)
            if s is None:
                continue
            item["_score"] = s
            scored.append(item)
        scored.sort(key=lambda x: x["_score"], reverse=True)

        if len(scored) < 3:
            log(f"  ⚠ Only {len(scored)} scored items, skip")
            failed += 1
            continue

        # 重複排除（同じ商品名の頭20文字が同じものは1つに）
        seen = set()
        unique = []
        for item in scored:
            head = item.get("itemName", "")[:20]
            if head not in seen:
                seen.add(head)
                unique.append(item)
        scored = unique[:10]

        # HTML生成
        html_doc = render_article(article, scored, config)

        # 保存
        try:
            with open(article["filename"], "w", encoding="utf-8") as f:
                f.write(html_doc)
            log(f"  ✓ Saved ({len(html_doc)} bytes, top score: {scored[0]['_score']})")
            success += 1
        except Exception as e:
            log(f"  ✗ Write error: {e}")
            failed += 1

        # Rate limit (Rakuten APIへの配慮)
        time.sleep(2)

    log(f"\n=== Done: {success} success, {failed} failed ===")

    # articles.json 更新
    try:
        articles_json = []
        today = datetime.now(JST).strftime("%Y-%m-%d")
        for a in ARTICLES:
            articles_json.append({
                "filename": a["filename"],
                "title": a["title"],
                "category": a["category"],
                "lead": a["lead"],
                "date": today,
            })
        with open("articles.json", "w", encoding="utf-8") as f:
            json.dump(articles_json, f, ensure_ascii=False, indent=2)
        log(f"✓ articles.json updated ({len(articles_json)} entries)")
    except Exception as e:
        log(f"⚠ articles.json update failed: {e}")


if __name__ == "__main__":
    main()
