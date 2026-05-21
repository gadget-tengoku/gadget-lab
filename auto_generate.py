#!/usr/bin/env python3
"""
ガジェット天国 - 日次記事自動生成 v2
==========================================
- 在宅ワーカー特化のトピックキューから未生成のものを選んで1本生成
- 公開スコアリングロジック(scoring.py)を使用
- 新デザインテンプレで出力
- archive.html / sitemap.xml も毎回自動更新

【動作】
GitHub Actions が10:00 JST / 21:00 JST に呼ぶ。
1回の実行で1記事生成。トピックキューが尽きたら何もしない。
"""

import os
import sys
import json
import math
import time
import html
import requests
from datetime import datetime, timezone, timedelta

# 公開スコアリングロジック
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from scoring import calculate_score, is_valid_product
except ImportError:
    print("ERROR: scoring.py が見つかりません。リポジトリのルートに配置してください。")
    sys.exit(1)


# ===========================================================
# 設定
# ===========================================================
RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID", "") or os.environ.get("API_KEY", "")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID", "") or os.environ.get("AFFILIATE_ID", "")
SITE_URL = "https://gadget-tengoku.com"
JST = timezone(timedelta(hours=9))


def log(msg):
    print(f"[{datetime.now(JST).strftime('%H:%M:%S')}] {msg}", flush=True)


# ===========================================================
# トピックキュー（30+本）
# ===========================================================
# 既に articles.json に同じ filename があるものはスキップされる。
# 新規追加するときは末尾に append。
TOPIC_QUEUE = [
    {"id": "anker-magsafe-battery", "category": "mobile_battery", "keyword": "MagSafe モバイルバッテリー iPhone", "title": "MagSafe対応モバイルバッテリーおすすめ｜iPhoneと相性最強", "lead": "iPhone利用者の在宅ワーカー向けに、ケーブル不要でくっつけて充電できるMagSafe対応モバイルバッテリーを選びました。"},
    {"id": "logicool-mx-master-3s", "category": "wireless_mouse", "keyword": "ロジクール MX Master", "title": "ロジクール MX Master 3S 比較｜在宅ワーカーの王道マウス", "lead": "在宅ワーカーの生産性ガジェットの代名詞、ロジクール MX Master シリーズを徹底比較。MX Master 3S か 3 で迷う方向け。"},
    {"id": "trackball-mouse-remote", "category": "wireless_mouse", "keyword": "トラックボール マウス", "title": "トラックボールマウスおすすめ｜手首が痛い在宅ワーカーへ", "lead": "手首を動かさずに使えるトラックボールマウス。長時間PC作業の腱鞘炎リスクを下げたい在宅ワーカー向けに選びました。"},
    {"id": "bluetooth-multi-mouse", "category": "wireless_mouse", "keyword": "Bluetooth マウス マルチペアリング", "title": "マルチペアリング対応 Bluetoothマウス｜PC・Mac・iPad切替", "lead": "ノートPC・Mac・iPadなど複数デバイスを使い分ける在宅ワーカー向けに、マルチペアリング対応のBluetoothマウスを比較。"},
    {"id": "ergonomic-mouse-pain", "category": "wireless_mouse", "keyword": "エルゴノミクスマウス", "title": "エルゴノミクスマウスおすすめ｜手首・腕の負担を減らす", "lead": "縦型グリップ・トラックボール型などの「人体工学」設計マウス。在宅で1日8時間以上PC作業をする人の必需品です。"},
    {"id": "4k-webcam-meeting", "category": "webcam", "keyword": "4K ウェブカメラ", "title": "4Kウェブカメラおすすめ｜Web会議の解像度を底上げ", "lead": "1080pでは満足できない在宅ワーカー向けの4Kウェブカメラ。商品紹介・採用面接・配信などの用途にも。"},
    {"id": "autofocus-webcam", "category": "webcam", "keyword": "オートフォーカス ウェブカメラ", "title": "オートフォーカス対応ウェブカメラ比較｜画面前後の動きにピント追従", "lead": "資料を見せたり身を乗り出したりしても自動でピントが合うオートフォーカス対応のウェブカメラを選びました。"},
    {"id": "1man-earphone-call-quality", "category": "earphone_wireless", "keyword": "ワイヤレスイヤホン 通話品質", "title": "通話品質重視ワイヤレスイヤホン｜Web会議でマイクが評価される1本", "lead": "音楽より「相手にどう聞こえるか」を最優先する在宅ワーカー向け。マイク評価が高いワイヤレスイヤホンに絞りました。"},
    {"id": "bose-earphone-noise", "category": "earphone_wireless", "keyword": "Bose ワイヤレスイヤホン", "title": "Boseワイヤレスイヤホン比較｜ノイキャンの効きを実データで検証", "lead": "ノイズキャンセリングといえば Bose の評判。各モデルの楽天レビューを分析して、在宅ワーカーが買うべき1本を絞ります。"},
    {"id": "anker-soundcore-cospa", "category": "earphone_wireless", "keyword": "Anker Soundcore", "title": "Anker Soundcore ワイヤレスイヤホンおすすめ｜コスパ重視", "lead": "Anker Soundcore シリーズの中でコスパ最強モデルを選定。在宅ワーカーの予備機にも本命にもなる価格帯です。"},
    {"id": "fitbit-watch-health", "category": "smartwatch", "keyword": "Fitbit スマートウォッチ", "title": "Fitbitスマートウォッチおすすめ｜健康管理特化型", "lead": "Apple Watch ほど多機能でなくていい、健康管理だけ強化したい在宅ワーカー向け。Fitbit シリーズを徹底比較。"},
    {"id": "huawei-watch-business", "category": "smartwatch", "keyword": "HUAWEI Watch", "title": "HUAWEI Watchおすすめ｜ビジネスで使えるスマートウォッチ", "lead": "スーツに合うクラシックなデザインのHUAWEI Watch。在宅ワーカーが商談・対面打合せで使える1本を選びました。"},
    {"id": "entry-smartwatch", "category": "smartwatch", "keyword": "スマートウォッチ 1万円以下", "title": "1万円以下スマートウォッチおすすめ｜入門用ベスト", "lead": "初めてのスマートウォッチで失敗したくない方へ。1万円以下で買える、座りすぎ通知と心拍計測が使える入門モデルを厳選。"},
    {"id": "suica-watch-commute", "category": "smartwatch", "keyword": "Suica対応 スマートウォッチ", "title": "Suica対応スマートウォッチおすすめ｜在宅勤務でもたまの通勤がラクに", "lead": "在宅メインでもたまに出社する人向け。改札・コンビニで手をかざすだけのSuica対応スマートウォッチを比較しました。"},
    {"id": "lightweight-battery-1man", "category": "mobile_battery", "keyword": "軽量 モバイルバッテリー 1万mAh", "title": "軽量モバイルバッテリーおすすめ｜10000mAh級で180g以下", "lead": "毎日持ち歩くなら200g切りが正義。10000mAhクラスで軽量・コンパクトなモバイルバッテリーに絞り込みました。"},
    {"id": "pd-battery-fast", "category": "mobile_battery", "keyword": "PD モバイルバッテリー 急速充電", "title": "急速充電PDモバイルバッテリーおすすめ｜30分で50%回復", "lead": "限られた時間で確実に充電したい在宅ワーカー向け。PD出力30W以上の急速充電対応モデルを優先しました。"},
    {"id": "100w-battery-large", "category": "mobile_battery", "keyword": "100W モバイルバッテリー", "title": "100W PD対応モバイルバッテリー｜ノートPC＋スマホ同時急速充電", "lead": "MacBook Pro クラスのノートPCも急速充電できる100W PD対応モバイルバッテリー。出張ヘビーユーザーの最終解。"},
    {"id": "ultrawide-monitor-remote", "category": "monitor_4k", "keyword": "ウルトラワイドモニター", "title": "ウルトラワイドモニターおすすめ｜在宅作業の生産性を底上げ", "lead": "21:9・32:9のウルトラワイドモニターは、エクセル・コード・動画編集すべてで生産性が変わる。在宅向けモデルを比較。"},
    {"id": "32inch-4k-monitor", "category": "monitor_4k", "keyword": "32インチ 4Kモニター", "title": "32インチ4Kモニターおすすめ｜在宅でゆったり作業したい人へ", "lead": "27インチでは少し狭い、35インチは置けない。中間サイズの32インチ4Kモニターを在宅ワーカー視点で選びました。"},
    {"id": "usbc-1cable-monitor", "category": "monitor_4k", "keyword": "USB-C モニター 65W", "title": "USB-C 1本接続モニターおすすめ｜ノートPCの電源・映像・USB全部1本", "lead": "ノートPC側のUSB-C 1本で映像・電源・USBハブを賄えるモニター。在宅デスクのケーブル激減が魅力。"},
    {"id": "aluminum-laptop-stand", "category": "laptop_stand", "keyword": "アルミ ノートPCスタンド", "title": "アルミ製ノートPCスタンドおすすめ｜放熱・安定感・高級感", "lead": "MacBookと相性のいいアルミ製のノートPCスタンド。放熱性・安定感・見た目の3点で高評価のモデルを選びました。"},
    {"id": "vertical-laptop-stand", "category": "laptop_stand", "keyword": "縦置き ノートPCスタンド", "title": "縦置きノートPCスタンドおすすめ｜デスクスペース節約", "lead": "ノートPCを閉じて縦に立てるクラムシェルモード向けスタンド。外部モニター利用時のデスクスペース確保に。"},
    {"id": "anc-mic-headset-wfh", "category": "headset", "keyword": "ノイズキャンセリングマイク ヘッドセット", "title": "ノイキャンマイク搭載ヘッドセット｜在宅で生活音をシャットアウト", "lead": "子供の声・宅配・空調音をマイクが拾わないノイズキャンセリングマイク搭載ヘッドセット。在宅Web会議の品質を上げる。"},
    {"id": "bluetooth-headset-meeting", "category": "headset", "keyword": "Bluetooth ヘッドセット Web会議", "title": "Bluetoothヘッドセットおすすめ｜Web会議で取り回しよく使える1本", "lead": "ケーブル無しでPC・スマホをまたいで使えるBluetoothヘッドセット。複数デバイスでWeb会議する在宅ワーカー向け。"},
    {"id": "lightweight-headset-1day", "category": "headset", "keyword": "軽量 ヘッドセット", "title": "軽量ヘッドセットおすすめ｜1日装着しても疲れない", "lead": "在宅でWeb会議が朝から晩まで続く日向けに、200g以下の軽量ヘッドセットを厳選。耳と首への負担を最小化。"},
    {"id": "1man-usbmic", "category": "usb_microphone", "keyword": "USBマイク 1万円以下", "title": "1万円以下USBマイクおすすめ｜配信・Web会議用ベストバイ", "lead": "ノートPC内蔵マイクからの卒業に。1万円以下で買えるUSBマイクの中で、音質・取り回しが両立した1本を選びました。"},
    {"id": "condenser-mic-streaming", "category": "usb_microphone", "keyword": "コンデンサーマイク USB-C", "title": "コンデンサーUSBマイクおすすめ｜配信レベルの音質を在宅で", "lead": "USB-C接続でPC・iPadにそのまま使えるコンデンサーマイク。配信・ポッドキャスト収録レベルの音質を在宅で。"},
    {"id": "directional-usbmic-noise", "category": "usb_microphone", "keyword": "単一指向性 USBマイク", "title": "単一指向性USBマイクおすすめ｜周囲の雑音を拾わない", "lead": "Web会議で「マイクの音、周りの音が気になりますね」と言われたくない在宅ワーカーへ。指向性の鋭いUSBマイクを選定。"},
    {"id": "garmin-watch-health", "category": "smartwatch", "keyword": "Garmin スマートウォッチ", "title": "Garminスマートウォッチおすすめ｜在宅ワーカーの健康管理に意外と効く", "lead": "ランナー向けというイメージが強いGarminですが、Body Battery・ストレス計測など在宅ワーカーにも刺さる機能が豊富です。"},
    {"id": "magnet-laptop-stand", "category": "laptop_stand", "keyword": "折りたたみ ノートPCスタンド 持ち運び", "title": "持ち運び対応ノートPCスタンド｜出張・カフェ作業向け", "lead": "薄く折りたためてカバンに入る軽量ノートPCスタンド。在宅メイン×たまに出社・出張する人の必需品。"},
]


# ===========================================================
# カテゴリ別フィルタ設定（regenerate_all.py と同期）
# ===========================================================
CATEGORY_CONFIG = {
    "earphone_wireless": {"label": "ワイヤレスイヤホン", "genre_id": 566215, "min_price": 3000, "max_price": 80000, "min_review_count": 30, "min_review_average": 3.8, "exclude": ["イヤーピース", "イヤーチップ", "ケース単体", "充電ケーブル", "交換用", "互換品", "保護フィルム", "ストラップ", "シール", "カバー単体"], "min_title_length": 12, "features": ["ノイズキャンセリング", "ANC", "ハイレゾ", "LDAC", "マルチポイント", "ワイヤレス", "Bluetooth"], "angle": "Web会議での音声品質と長時間装着の快適性"},
    "smartwatch": {"label": "スマートウォッチ", "genre_id": 566382, "min_price": 5000, "max_price": 200000, "min_review_count": 20, "min_review_average": 3.8, "exclude": ["バンド単体", "ベルト単体", "ストラップ単体", "保護フィルム", "ケース単体", "充電ケーブル単体", "交換用"], "min_title_length": 12, "features": ["GPS", "心拍", "血中酸素", "睡眠", "Suica", "FeliCa", "スマートウォッチ"], "angle": "座りすぎ通知・心拍ベースのストレス可視化"},
    "mobile_battery": {"label": "モバイルバッテリー", "genre_id": 560029, "min_price": 1500, "max_price": 30000, "min_review_count": 30, "min_review_average": 4.0, "exclude": ["ケーブル単品", "ACアダプタ単品", "ケース単体", "シール"], "min_title_length": 10, "features": ["PD", "急速充電", "MagSafe", "Qi", "USB-C", "大容量"], "angle": "カフェ作業・出張時のノートPC給電"},
    "wireless_mouse": {"label": "ワイヤレスマウス", "genre_id": 566375, "min_price": 1500, "max_price": 30000, "min_review_count": 20, "min_review_average": 4.0, "exclude": ["マウスパッド", "マウスソール", "替え芯", "電池単体"], "min_title_length": 10, "features": ["静音", "Bluetooth", "エルゴノミクス", "ロジクール", "MX"], "angle": "長時間作業の手首負担と静音性"},
    "webcam": {"label": "ウェブカメラ", "genre_id": 558943, "min_price": 2000, "max_price": 50000, "min_review_count": 20, "min_review_average": 4.0, "exclude": ["三脚単品", "クリップ単品", "リング単品"], "min_title_length": 10, "features": ["1080p", "4K", "オートフォーカス", "プライバシー", "Logicool"], "angle": "Web会議での映りの良さと光量補正"},
    "headset": {"label": "ヘッドセット", "genre_id": 558943, "min_price": 2000, "max_price": 60000, "min_review_count": 20, "min_review_average": 4.0, "exclude": ["イヤーパッド", "ケーブル単品", "替え", "スタンド単品"], "min_title_length": 12, "features": ["ノイズキャンセリングマイク", "USB", "Bluetooth", "両耳", "ヘッドセット"], "angle": "Web会議での聞き取りやすさと相手への音声明瞭度"},
    "usb_microphone": {"label": "USBマイク", "genre_id": 567172, "min_price": 2000, "max_price": 50000, "min_review_count": 20, "min_review_average": 4.0, "exclude": ["ポップガード単品", "ショックマウント単品", "ケーブル単品", "スタンド単品"], "min_title_length": 10, "features": ["コンデンサ", "単一指向性", "ミュート", "USB-C", "マイク"], "angle": "Web会議・配信での音声品質"},
    "monitor_4k": {"label": "4Kモニター", "genre_id": 211195, "min_price": 25000, "max_price": 200000, "min_review_count": 10, "min_review_average": 4.0, "exclude": ["モニターアーム", "保護フィルム", "スタンド単品", "ケーブル単品"], "min_title_length": 12, "features": ["IPS", "USB-C", "HDR", "HDMI", "DisplayPort", "4K"], "angle": "長時間作業の目疲労と画面占有率"},
    "laptop_stand": {"label": "ノートPCスタンド", "genre_id": 564586, "min_price": 1000, "max_price": 20000, "min_review_count": 20, "min_review_average": 4.0, "exclude": ["クッション", "保護ケース", "カバー"], "min_title_length": 10, "features": ["アルミ", "角度調節", "折りたたみ", "放熱", "スタンド"], "angle": "首・肩への負担軽減"},
}


# ===========================================================
# 楽天API
# ===========================================================
def fetch_rakuten(keyword, config):
    fallback_rc = [config["min_review_count"], max(5, config["min_review_count"] // 2), 3]
    for min_rc in fallback_rc:
        params = {"applicationId": RAKUTEN_APP_ID, "affiliateId": RAKUTEN_AFFILIATE_ID, "keyword": keyword, "genreId": config["genre_id"], "minPrice": config["min_price"], "maxPrice": config["max_price"], "hits": 30, "sort": "-reviewCount", "format": "json"}
        try:
            r = requests.get("https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601", params=params, timeout=15)
            r.raise_for_status()
            items = [it["Item"] for it in r.json().get("Items", [])]
        except Exception as e:
            log(f"  ⚠ Rakuten error: {e}")
            items = []
        filtered = [it for it in items if is_valid_product(it, config, min_rc)]
        if len(filtered) >= 5:
            return filtered[:10]
    return filtered


# ===========================================================
# テンプレ文生成
# ===========================================================
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
    nl = item.get("itemName", "").lower()
    has_f = any(f.lower() in nl for f in config["features"])
    price = item.get("itemPrice", 0)
    if rank == 1:
        return f"このカテゴリで「{config['label']}」を初めて買う在宅ワーカー全般。迷ったらまずこれ" if has_f else f"レビュー件数の安定感とブランドの信頼性を最優先したい在宅ワーカー"
    elif rank == 2:
        return f"1位より少し違うアプローチで{config['label']}を選びたい人。{config['angle']}を重視するなら有力候補"
    elif rank == 3:
        return f"とにかく初期投資を抑えたい人。在宅ワーク用途で最初の1台として試すなら" if price < (config["min_price"] * 2) else f"上位2台と比較しつつ、価格と機能のバランスを取りたい人"
    else:
        return f"{config['angle']}という軸で、もう1つ選択肢を持っておきたい人"


def generate_not_recommend(item, config):
    p = item.get("itemPrice", 0)
    if p > config["max_price"] * 0.8:
        return "とにかく安く済ませたい人。この価格帯なら同カテゴリの上位機種と比較検討を"
    elif p < config["min_price"] * 1.3:
        return "高音質・高機能を最優先する人。この価格帯では機能の取捨選択は避けられない"
    return "特定の用途（プロ用途・極端な静音性・特殊な接続要件）を求める人"


# ===========================================================
# HTMLテンプレ（regenerate_all.py と同じ）
# ===========================================================
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
      <div class="footer-brand"><h4>Gadget<span style="color: var(--accent);">天国</span></h4><p>在宅ワーカーのためのガジェット選びを、楽天実売データとレビュー分析で支援するメディア。スコアリングロジックはGitHubで全公開。</p></div>
      <div class="footer-col"><h5>Categories</h5><ul><li><a href="earphone.html">イヤホン</a></li><li><a href="smartwatch.html">スマートウォッチ</a></li><li><a href="battery.html">バッテリー</a></li><li><a href="telework.html">テレワーク</a></li><li><a href="gaming.html">PC周辺</a></li></ul></div>
      <div class="footer-col"><h5>About</h5><ul><li><a href="archive.html">記事一覧</a></li><li><a href="about.html">編集部</a></li><li><a href="review-policy.html">レビュー方針</a></li><li><a href="ad-policy.html">広告ポリシー</a></li><li><a href="privacy.html">プライバシーポリシー</a></li></ul></div>
      <div class="footer-col"><h5>Connect</h5><ul><li><a href="https://twitter.com/gadget_tengoku">X (Twitter)</a></li><li><a href="https://github.com/gadget-tengoku/gadget-lab">GitHub</a></li></ul></div>
    </div>
    <div class="footer-bottom">※本サイトは楽天アフィリエイトプログラムおよびAmazonアソシエイトプログラムに参加しています。商品リンクから購入された場合、運営者に報酬が発生することがあります。掲載価格は楽天市場の参照価格であり、価格・在庫は変動します。購入前に必ず各ショッピングサイトでご確認ください。<br>© 2026 ガジェット天国</div>
  </div>
</footer>'''


def make_filename(topic_id, slot):
    """ファイル名生成: article-{topic_id}-{ampm}-{yyyymmdd}.html"""
    today = datetime.now(JST).strftime("%Y%m%d")
    return f"article-{topic_id}-{slot}-{today}.html"


def render_article(topic, products, config, filename):
    today = datetime.now(JST).strftime("%Y年%m月%d日")
    today_iso = datetime.now(JST).strftime("%Y-%m-%d")
    canonical = f"{SITE_URL}/{filename}"

    ranking_html = ""
    for i, p in enumerate(products[:5], 1):
        rank_label = {1: "🥇 1位", 2: "🥈 2位", 3: "🥉 3位", 4: "4位", 5: "5位"}[i]
        item_name = html.escape(p.get("itemName", ""))
        item_url = p.get("affiliateUrl") or p.get("itemUrl", "#")
        shop_name = html.escape(p.get("shopName", ""))
        price = p.get("itemPrice", 0)
        rc = p.get("reviewCount", 0)
        ra = p.get("reviewAverage", 0)
        stars = "★" * int(round(ra)) + "☆" * (5 - int(round(ra)))
        image_url = ""
        if p.get("mediumImageUrls"):
            first = p["mediumImageUrls"][0]
            image_url = first.get("imageUrl", "") if isinstance(first, dict) else first
            image_url = image_url.replace("?_ex=128x128", "?_ex=400x400")
        score = p.get("_score", 0)
        summary = generate_summary(p, config)
        rec = generate_recommend(p, i, config)
        nrec = generate_not_recommend(p, config)
        img = f'<img src="{image_url}" alt="{item_name}" loading="lazy">' if image_url else '🎁'
        ranking_html += f'''
<div class="ranking-item rank-{i}">
  <span class="rank">{rank_label} · スコア {score}/100</span>
  <h3 class="product-name">{item_name}</h3>
  <div class="product-brand">{shop_name}</div>
  <div class="product-image">{img}</div>
  <div class="rating">{stars} <span class="score">{ra:.1f}</span> <a href="{item_url}" target="_blank" rel="nofollow noopener sponsored">楽天レビュー {rc}件 →</a></div>
  <div class="price">📅 {today}確認｜参考価格：<strong>¥{price:,}〜</strong></div>
  <p>{html.escape(summary)}</p>
  <div class="recommend">{html.escape(rec)}</div>
  <div class="not-recommend">{html.escape(nrec)}</div>
  <p style="margin-top:1rem;"><a class="btn btn-rakuten" href="{item_url}" target="_blank" rel="nofollow noopener sponsored">楽天で価格を見る →</a></p>
</div>
'''

    table_rows = ""
    for i, p in enumerate(products[:5], 1):
        item_url = p.get("affiliateUrl") or p.get("itemUrl", "#")
        name_short = html.escape(p.get("itemName", "")[:50])
        table_rows += f'<tr><td><strong>{i}位</strong></td><td>{name_short}</td><td>¥{p.get("itemPrice", 0):,}</td><td>{p.get("reviewAverage", 0):.1f}★</td><td>{p.get("reviewCount", 0)}件</td><td>{p.get("_score", 0)}/100</td><td><a href="{item_url}" target="_blank" rel="nofollow noopener sponsored">楽天</a></td></tr>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(topic["title"])} - ガジェット天国</title>
<meta name="description" content="{html.escape(topic["lead"])}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{html.escape(topic["title"])}">
<meta property="og:description" content="{html.escape(topic["lead"])}">
<meta property="og:image" content="{SITE_URL}/ogp.png">
<meta property="og:site_name" content="ガジェット天国">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@gadget_tengoku">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":{json.dumps(topic["title"], ensure_ascii=False)},"description":{json.dumps(topic["lead"], ensure_ascii=False)},"url":"{canonical}","datePublished":"{today_iso}","dateModified":"{today_iso}","author":{{"@type":"Organization","name":"ガジェット天国 編集部","url":"{SITE_URL}/about.html"}},"publisher":{{"@type":"Organization","name":"ガジェット天国","logo":{{"@type":"ImageObject","url":"{SITE_URL}/ogp.png"}}}}}}
</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="stylesheet" href="article-style.css">
</head>
<body>

{HEADER_HTML}

<main>
  <div class="breadcrumb"><a href="/">TOP</a> / {html.escape(config["label"])} / 記事</div>

  <article>
    <div class="article-meta">{today} 公開 · 在宅ワーカー視点で分析</div>
    <h1>{html.escape(topic["title"])}</h1>
    <p style="font-size: 1.05rem; line-height: 1.95;">{html.escape(topic["lead"])}</p>

    <div class="conclusion">
      <h3>📌 結論（在宅ワーカー視点）</h3>
      <p>このカテゴリの選び方の核は <mark>「{config["angle"]}」</mark> です。下位ランキングTOP5は、楽天市場の<strong>本体商品のみ</strong>に絞った上で、レビュー件数×評価×ブランド信頼度の重み付けスコアで並べています。</p>
      <p>急いでいる方は <strong>1位</strong> を見るのが早いです。価格や用途で迷う場合は比較表をどうぞ。</p>
    </div>

    <h2>🏆 おすすめランキング TOP5</h2>
    <p>※価格は{today}時点。セール・ポイント還元で変動します。購入前に必ず最新価格をご確認ください。</p>
    {ranking_html}

    <h2>📊 スペック比較表</h2>
    <table>
      <thead><tr><th>順位</th><th>商品名</th><th>参考価格</th><th>評価</th><th>口コミ</th><th>スコア</th><th>購入</th></tr></thead>
      <tbody>{table_rows}</tbody>
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
    <details><summary>Amazon と楽天、どっちで買うのが得？</summary><p>楽天スーパーセール・お買い物マラソン中は楽天がポイント還元込みで実質安くなります。Amazonはタイムセールが強い時期があり、急ぎでない場合は両方の価格を比較するのが確実です。</p></details>
    <details><summary>このランキングは実機検証ですか？</summary><p>いいえ。当サイトは実機を所有していません。楽天市場のレビューデータと公式仕様を独自に分析してランキングを作成しています。詳細は記事下の「透明性方針」をご覧ください。</p></details>
    <details><summary>掲載商品の在庫はありますか？</summary><p>各楽天ストアの在庫状況によります。リンク先で在庫切れの場合は、同じ商品名で楽天市場内を再検索してください。</p></details>

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
      <p style="color: rgba(244,241,234,0.85);">ソースコードは <a href="https://github.com/gadget-tengoku/gadget-lab/blob/main/scoring.py">github.com/gadget-tengoku/gadget-lab/scoring.py</a> で公開。アルゴリズムの詳細は <a href="https://github.com/gadget-tengoku/gadget-lab/blob/main/scoring_README.md">こちら</a>。実機の使用感は <a href="https://my-best.com">マイベスト</a> や <a href="https://kakakumag.com">価格.comマガジン</a> もあわせてご確認ください。</p>
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
</html>'''


# ===========================================================
# articles.json / archive.html / sitemap.xml 更新
# ===========================================================
def load_articles_json():
    try:
        with open("articles.json", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_articles_json(articles):
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def regenerate_archive_html(articles):
    """archive.html を articles.json の内容に基づいて再生成"""
    items_html = ""
    for a in sorted(articles, key=lambda x: x.get("date", ""), reverse=True):
        cat_label = CATEGORY_CONFIG.get(a.get("category", ""), {}).get("label", a.get("category", ""))
        date_str = a.get("date", "").replace("-", ".")
        items_html += f'    <a href="{a["filename"]}" class="article-item">\n      <span class="article-date">{date_str}</span>\n      <span class="article-title">{html.escape(a.get("title", ""))}</span>\n      <span class="article-tag">{html.escape(cat_label)}</span>\n    </a>\n'

    archive_html = f'''<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記事一覧 - ガジェット天国</title>
<meta name="description" content="ガジェット天国の全記事一覧。在宅ワーカー向けの比較記事を更新中。">
<link rel="canonical" href="{SITE_URL}/archive.html">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}/archive.html">
<meta property="og:title" content="記事一覧 - ガジェット天国"><meta property="og:image" content="{SITE_URL}/ogp.png">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3514849475707540" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@500;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-style.css">
<style>
.site-header{{border-bottom:1px solid var(--line);background:var(--bg);position:sticky;top:0;z-index:100;}}
.header-inner{{max-width:1180px;margin:0 auto;padding:1rem 1.5rem;display:flex;align-items:center;justify-content:space-between;gap:2rem;flex-wrap:wrap;}}
.brand{{font-family:var(--serif);font-weight:900;font-size:1.45rem;}}.brand .accent{{color:var(--accent);}}
.nav-main{{display:flex;gap:1.6rem;font-size:0.9rem;flex-wrap:wrap;}}.nav-main a{{color:var(--ink-soft);font-weight:500;}}
.archive-hero{{max-width:1180px;margin:0 auto;padding:2.5rem 1.5rem;}}
.archive-hero h1{{font-family:var(--serif);font-size:clamp(2rem,4vw,2.6rem);font-weight:900;line-height:1.3;margin-bottom:1rem;}}
.archive-hero .em{{background:linear-gradient(transparent 65%,var(--highlight) 65%);padding:0 0.1em;}}
.archive-section{{max-width:1180px;margin:0 auto;padding:1rem 1.5rem 3rem;}}
.article-list{{display:grid;gap:0;border-top:1px solid var(--line);}}
.article-item{{display:grid;grid-template-columns:100px 1fr auto;gap:1.5rem;padding:1.4rem 0;border-bottom:1px solid var(--line);align-items:center;text-decoration:none;color:inherit;}}
.article-item:hover{{padding-left:1rem;}}.article-date{{font-family:var(--mono);font-size:0.78rem;color:var(--ink-muted);}}
.article-title{{font-weight:500;line-height:1.5;font-size:1rem;}}
.article-tag{{font-size:0.72rem;color:var(--accent);background:var(--accent-soft);padding:0.2rem 0.6rem;border-radius:3px;font-weight:600;white-space:nowrap;}}
@media(max-width:640px){{.article-item{{grid-template-columns:1fr;gap:0.5rem;}}}}
</style>
</head><body>

<header class="site-header"><div class="header-inner">
<a href="/" class="brand">Gadget<span class="accent">天国</span></a>
<nav class="nav-main">
<a href="earphone.html">イヤホン</a><a href="smartwatch.html">スマートウォッチ</a><a href="battery.html">バッテリー</a>
<a href="telework.html">テレワーク</a><a href="gaming.html">PC周辺</a><a href="archive.html">記事一覧</a><a href="about.html">編集部</a>
</nav></div></header>

<div style="max-width:1180px;margin:0 auto;padding:1.5rem 1.5rem 0;font-size:0.85rem;color:var(--ink-muted);font-family:var(--mono);"><a href="/" style="color:var(--ink-soft);">TOP</a> / 記事一覧</div>

<section class="archive-hero">
<span style="display:inline-block;font-family:var(--mono);font-size:0.75rem;color:var(--accent);background:var(--accent-soft);padding:0.35rem 0.8rem;border-radius:999px;letter-spacing:0.08em;margin-bottom:1.6rem;font-weight:600;">ARCHIVE · ALL ARTICLES</span>
<h1>すべての<span class="em">比較記事</span></h1>
<p style="font-size:1.05rem;color:var(--ink-soft);max-width:720px;line-height:1.85;">在宅ワーカー向けに、楽天実売データとレビュー分析で絞り込んだ比較記事の全リスト。公開日順に並べています。</p>
<div style="display:flex;gap:2rem;flex-wrap:wrap;margin-top:1.5rem;font-family:var(--mono);font-size:0.85rem;color:var(--ink-soft);">
<div><strong style="color:var(--accent);font-size:1.4rem;font-weight:700;">{len(articles)}</strong> 公開記事</div>
<div><strong style="color:var(--accent);font-size:1.4rem;font-weight:700;">9</strong> 分析カテゴリ</div>
<div><strong style="color:var(--accent);font-size:1.4rem;font-weight:700;">3K+</strong> 楽天レビュー分析</div>
</div>
</section>

<section class="archive-section">
<div class="article-list">
{items_html}</div>
</section>

{FOOTER_HTML}
</body></html>'''

    with open("archive.html", "w", encoding="utf-8") as f:
        f.write(archive_html)


def regenerate_sitemap(articles):
    today = datetime.now(JST).strftime("%Y-%m-%d")
    static_pages = ["", "earphone.html", "smartwatch.html", "battery.html", "telework.html", "gaming.html", "archive.html", "about.html", "privacy.html"]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path in static_pages:
        priority = "1.0" if path == "" else "0.9" if "html" in path and path not in ("archive.html", "about.html", "privacy.html") else "0.7" if path == "archive.html" else "0.5"
        xml += f'  <url><loc>{SITE_URL}/{path}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>\n'
    for a in articles:
        xml += f'  <url><loc>{SITE_URL}/{a["filename"]}</loc><lastmod>{a.get("date", today)}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
    xml += '</urlset>\n'

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml)


# ===========================================================
# メイン
# ===========================================================
def main():
    if not RAKUTEN_APP_ID or not RAKUTEN_AFFILIATE_ID:
        log("❌ RAKUTEN_APP_ID / RAKUTEN_AFFILIATE_ID not set")
        sys.exit(1)

    # 現在の時刻でAM/PM決定
    hour = datetime.now(JST).hour
    slot = "am" if hour < 15 else "pm"

    # 既存記事をロード
    existing_articles = load_articles_json()
    existing_ids = set()
    for a in existing_articles:
        fn = a.get("filename", "")
        # filename から topic_id を抽出（"article-{id}-{slot}-{date}.html"）
        if fn.startswith("article-"):
            existing_ids.add(fn.replace(".html", ""))

    # 未生成のトピックを探す
    target = None
    for topic in TOPIC_QUEUE:
        # 同じ topic_id がすでに articles.json にあるかチェック
        already_done = any(topic["id"] in existing_id for existing_id in existing_ids)
        if not already_done:
            target = topic
            break

    if not target:
        log("ℹ️ 全トピック生成済み。新規トピックを TOPIC_QUEUE に追加してください。")
        # 終了せず archive/sitemap だけ再生成
        regenerate_archive_html(existing_articles)
        regenerate_sitemap(existing_articles)
        log("✓ archive.html / sitemap.xml 更新済み")
        return

    log(f"🚀 生成対象: {target['id']} ({target['title']})")
    config = CATEGORY_CONFIG.get(target["category"])
    if not config:
        log(f"❌ 未知のカテゴリ: {target['category']}")
        sys.exit(1)

    # 楽天検索
    items = fetch_rakuten(target["keyword"], config)
    if len(items) < 3:
        log(f"⚠ 商品が {len(items)} 件しか見つからず、生成スキップ")
        sys.exit(0)

    # スコアリング
    scored = []
    for it in items:
        s = calculate_score(it, config)
        if s is None:
            continue
        it["_score"] = s
        scored.append(it)
    scored.sort(key=lambda x: x["_score"], reverse=True)

    if len(scored) < 3:
        log(f"⚠ 有効スコア商品が {len(scored)} 件、スキップ")
        sys.exit(0)

    # 重複排除
    seen, unique = set(), []
    for it in scored:
        head = it.get("itemName", "")[:20]
        if head not in seen:
            seen.add(head)
            unique.append(it)
    scored = unique[:10]

    # HTML生成
    filename = make_filename(target["id"], slot)
    html_doc = render_article(target, scored, config, filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_doc)
    log(f"✓ {filename} 生成完了 (top score: {scored[0]['_score']})")

    # articles.json に追加
    today = datetime.now(JST).strftime("%Y-%m-%d")
    existing_articles.append({
        "filename": filename,
        "title": target["title"],
        "category": target["category"],
        "lead": target["lead"],
        "date": today,
    })
    save_articles_json(existing_articles)
    log(f"✓ articles.json 更新")

    # archive.html / sitemap.xml 再生成
    regenerate_archive_html(existing_articles)
    log(f"✓ archive.html 更新")
    regenerate_sitemap(existing_articles)
    log(f"✓ sitemap.xml 更新")

    log("=== Done ===")


if __name__ == "__main__":
    main()
