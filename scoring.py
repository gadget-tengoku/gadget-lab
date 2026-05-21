"""
ガジェット天国 - 商品スコアリングロジック（公開版）
==========================================================

このファイルは https://gadget-tengoku.com の商品ランキングを算出している
スコアリング関数の全実装です。

【透明性方針】
当サイトは実機を所有していません。代わりに楽天市場の実売データ
（レビュー件数・評価点・価格・商品名）を機械的に加工してランキングを作成しています。
そのロジックを完全公開することで、ランキングの「ブラックボックス化」を避けています。

【スコア算出式】
total_score =
    review_score    # レビュー評価 × log10(レビュー件数+1) × 5 [上限35]
  + cost_score      # 価格帯マッチング                          [10-25]
  + brand_score     # ブランド信頼度                            [5-10]
  + feature_bonus   # 特徴キーワード含有                        [上限15]
  + baseline        # ベースライン                              [10]

【商品除外ルール】
- レビュー0件、評価0.0 の商品は計算対象外
- 価格0円の商品は計算対象外
- 商品名が短すぎる（カテゴリごとの下限未満）商品は計算対象外
- 商品名に消耗品・部品系キーワードを含む商品は計算対象外
  （例：「交換」「メンテナンス」「紙パック」「フィルター」など）

【何を計測していないか（限界明示）】
- 実機での吸引力・音質・装着感などの体感品質
- 長期使用での耐久性
- メーカーサポートの質
- 楽天以外の販売チャネルでの価格・在庫

これらの観点は本ロジックではカバーできません。
購入前にマイベスト・価格.com マガジン等の実機検証記事も併せてご確認ください。

Repository: https://github.com/gadget-tengoku/gadget-lab
License: 個人利用・参考目的での閲覧自由。コードの転載・再配布時は出典明記をお願いします。
"""

import math
from typing import Optional


# ===========================================================
# ブランド信頼度スコア
# ===========================================================
# 楽天市場での販売実績・ユーザー満足度・サポート品質を編集部が独自評価。
# 5（無名/不明）〜10（業界トップクラスの定評）の整数で重み付け。
# 商品名にブランド名が含まれていれば、その重みが brand_score として加算される。
BRAND_TRUST = {
    # オーディオ
    "Sony": 10, "ソニー": 10, "Apple": 10, "Bose": 9, "Jabra": 9, "JBL": 8,
    "Anker": 8, "Soundcore": 8, "Shure": 9, "Blue": 8, "EPOS": 8,
    # 入力機器
    "Logicool": 9, "Logitech": 9, "Razer": 8, "SteelSeries": 8,
    "HyperX": 8, "Corsair": 7,
    # ウェアラブル
    "Garmin": 9, "Xiaomi": 7, "Fitbit": 7, "HUAWEI": 7, "Amazfit": 7,
    # 家電・電源
    "Panasonic": 9, "パナソニック": 9, "CIO": 7,
    "ELECOM": 7, "エレコム": 7, "Buffalo": 7, "サンワサプライ": 7,
    # モニター
    "Dell": 8, "LG": 8, "BenQ": 8, "ASUS": 8, "iiyama": 7,
    "EIZO": 9, "ViewSonic": 7,
    # 掃除・スマートホーム
    "Roborock": 8, "iRobot": 9, "Ecovacs": 7,
}


# ===========================================================
# メインスコアリング関数
# ===========================================================
def calculate_score(item: dict, config: dict) -> Optional[int]:
    """
    商品スコアを 0〜100 の整数で返す。
    候補から除外すべき商品の場合は None を返す。

    Args:
        item: 楽天 API の Item オブジェクト
              必須キー: itemName, itemPrice, reviewAverage, reviewCount
        config: カテゴリ設定（CATEGORY_CONFIG の値）
              必須キー: min_price, max_price, features (list[str])

    Returns:
        スコア（0-100）、または除外対象なら None
    """
    name = item.get("itemName", "")
    review_avg = item.get("reviewAverage", 0)
    review_count = item.get("reviewCount", 0)
    price = item.get("itemPrice", 0)

    # 除外条件
    if review_count == 0 or review_avg == 0 or price <= 0:
        return None

    # ----- 1. レビュースコア (上限35) -----
    # 「件数の対数」×「評価点」で計算。
    # レビュー多い × 評価高い = スコア大、を実現しつつ、
    # 件数が非線形に効くので「★4.5（件数50）」 < 「★4.4（件数900）」になる。
    review_score = min(35, review_avg * math.log10(review_count + 1) * 5)

    # ----- 2. 価格帯マッチング (10-25) -----
    # カテゴリの「中位価格帯（min*1.5 〜 max*0.7）」に入る商品が最高評価。
    # ユーザーが買いやすい価格帯の商品を優先する。
    mid_lo = config["min_price"] * 1.5
    mid_hi = config["max_price"] * 0.7
    if mid_lo <= price <= mid_hi:
        cost_score = 25
    elif config["min_price"] <= price <= config["max_price"]:
        cost_score = 18
    else:
        cost_score = 10

    # ----- 3. ブランド信頼度 (5-10) -----
    # 商品名に含まれるブランド名から重みを取得。
    brand_score = 5  # デフォルト
    name_lower = name.lower()
    for brand, weight in BRAND_TRUST.items():
        if brand.lower() in name_lower:
            brand_score = weight
            break

    # ----- 4. 特徴キーワードボーナス (上限15) -----
    # カテゴリで重要な機能キーワードがタイトルに含まれていれば加算。
    # 例：イヤホンなら「ノイズキャンセリング」「マルチポイント」など。
    feature_bonus = sum(
        3 for kw in config["features"] if kw.lower() in name_lower
    )
    feature_bonus = min(15, feature_bonus)

    # ----- 5. ベースライン -----
    baseline = 10

    total = review_score + cost_score + brand_score + feature_bonus + baseline
    return round(min(100, total))


# ===========================================================
# 商品フィルタ関数
# ===========================================================
# 全カテゴリ共通のアクセサリ・消耗品除外ワード
# （本体商品を誤爆しないことを検証済み。"単体"等を付けず素のワードで弾く）
COMMON_EXCLUDE = [
    "保護フィルム", "保護シート", "保護ケース",
    "バンド", "ベルト", "ストラップ",
    "交換用", "互換品", "互換バッテリー",
    "ホルダー", "ポーチ", "収納ケース",
    "シール", "ステッカー", "スキンシール",
    "イヤーピース", "イヤーチップ", "イヤーパッド",
    "紙パック", "ダストパック", "メンテナンス",
    "替え", "スペア", "予備パーツ", "クリーナー",
]


def is_valid_product(item: dict, config: dict, min_review_count: int) -> bool:
    """
    商品が「本体商品」として有効か判定する。
    消耗品・部品・極端に情報の少ない商品を弾く。
    """
    name = item.get("itemName", "")

    # タイトル長チェック
    if len(name) < config["min_title_length"]:
        return False

    # 共通アクセサリ除外（全カテゴリ適用）
    if any(ng in name for ng in COMMON_EXCLUDE):
        return False

    # "ケース"・"カバー" の扱いはカテゴリで分岐
    if config.get("label") == "ワイヤレスイヤホン":
        # イヤホンは充電ケースが本体付属。ただし "ケース カバー" 等アクセサリ語が重なる場合は除外
        ear_accessory = ["シリコンケース", "ケースカバー", "保護ケース", "ケース 保護",
                         "カバー", "ケース シリコン", "ケース用", "用ケース"]
        if any(w in name for w in ear_accessory):
            return False
    else:
        # イヤホン以外は "ケース"・"カバー" を含めば原則アクセサリとして除外
        if "ケース" in name or "カバー" in name:
            return False

    # カテゴリ固有の除外キーワードチェック
    if any(ng in name for ng in config["exclude"]):
        return False

    # レビュー件数チェック
    if item.get("reviewCount", 0) < min_review_count:
        return False

    # 評価点チェック
    if item.get("reviewAverage", 0) < config["min_review_average"]:
        return False

    # 価格チェック
    price = item.get("itemPrice", 0)
    if price <= 0:
        return False

    return True


# ===========================================================
# 単体テスト用エントリポイント
# ===========================================================
if __name__ == "__main__":
    # ローカル検証用のサンプルテスト
    sample_config = {
        "min_price": 5000, "max_price": 80000,
        "min_review_count": 50, "min_review_average": 4.0,
        "exclude": ["イヤーピース", "ケース単体", "交換用"],
        "min_title_length": 12,
        "features": ["ノイズキャンセリング", "マルチポイント"],
    }

    test_items = [
        {
            "itemName": "Sony WF-1000XM5 ワイヤレスイヤホン ノイズキャンセリング",
            "itemPrice": 30000, "reviewAverage": 4.5, "reviewCount": 903,
        },
        {
            "itemName": "WF-1000XM5 交換用 イヤーピース",
            "itemPrice": 1500, "reviewAverage": 4.0, "reviewCount": 50,
        },
        {
            "itemName": "Generic Earphone",
            "itemPrice": 6000, "reviewAverage": 4.0, "reviewCount": 30,
        },
        {
            "itemName": "新発売イヤホン",
            "itemPrice": 8000, "reviewAverage": 0, "reviewCount": 0,
        },
    ]

    for item in test_items:
        valid = is_valid_product(item, sample_config, min_review_count=30)
        score = calculate_score(item, sample_config) if valid else None
        print(f"  {item['itemName'][:40]:40s} | valid={valid} | score={score}")
