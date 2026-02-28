# ポケモンチャンピオンズ バトルロガー 計画書

## プロジェクト概要

ポケモンチャンピオンズの対戦データを自動で記録・分析するアプリケーション。
既存の poke_battle_logger (ポケモンSV向け) の知見を活かしつつ、新規リポジトリとして構築する。

**主な設計方針**:
- Python で完結する構成（Node.js ランタイム不要）
- ローカル実行を前提とし、配布しやすい形にする
- クラウド依存を排除し、SQLite + ローカルファイルで動作する

---

## アーキテクチャ

### 技術スタック

| レイヤー | 技術 | 備考 |
|---------|------|------|
| Web フレームワーク | FastAPI | 既存プロジェクトと同じ |
| テンプレートエンジン | Jinja2 | FastAPI 組み込み |
| フロントエンド | HTMX + Tailwind CSS | サーバーサイドレンダリング、JS 最小限 |
| チャート | Chart.js | 勝率推移・順位推移など。HTMX で部分更新 |
| DB | SQLite (デフォルト) | SQLModel + Alembic。PostgreSQL もオプション対応 |
| CV | OpenCV (テンプレートマッチング) | 既存アプローチを踏襲 |
| 画像検索 | FAISS | ポケモン画像の類似検索 |
| OCR | EasyOCR (`ja+en` / `ch_tra+en` 2 Reader構成) | 検証済み。Tesseract より高精度かつ配布容易 |
| パッケージ管理 | Poetry or uv | uv のほうが配布向きか検討 |

### 構成図

```
[ブラウザ]
    ↕ HTML (HTMX で部分更新)
[FastAPI + Jinja2]
    ├── /pages/* → HTML テンプレート返却
    ├── /api/* → JSON API (必要に応じて)
    ├── /htmx/* → HTML フラグメント返却 (HTMX 用)
    ↕
[SQLite] + [ローカルファイルシステム]
    ├── battle_data.db
    ├── template_images/
    └── videos/ (ローカルファイル入力時)
```

### ディレクトリ構成案

```
poke_champions_logger/
├── poke_champions_logger/
│   ├── app.py                  # FastAPI エントリーポイント
│   ├── api/                    # JSON API エンドポイント
│   ├── pages/                  # HTML ページルーティング
│   ├── htmx/                   # HTMX 用 HTML フラグメントルーティング
│   ├── batch/                  # 動画処理パイプライン
│   │   ├── video_downloader.py
│   │   ├── frame_detector.py
│   │   ├── pokemon_extractor.py
│   │   └── ocr_processor.py
│   ├── database/
│   │   └── handler.py          # SQLModel ベース
│   ├── models/                 # SQLModel データモデル
│   └── cv/                     # コンピュータビジョン関連
│       ├── template_matcher.py
│       └── faiss_index.py
├── templates/                  # Jinja2 テンプレート
│   ├── base.html
│   ├── pages/
│   │   ├── dashboard.html
│   │   ├── analytics.html
│   │   ├── battle_log.html
│   │   ├── process_video.html
│   │   └── settings.html
│   └── fragments/              # HTMX 部分更新用
│       ├── battle_table.html
│       ├── chart_section.html
│       └── ...
├── static/
│   ├── css/                    # Tailwind ビルド済み CSS
│   └── js/                     # Chart.js 等、最小限の JS
├── template_images/            # テンプレートマッチング用画像
├── data/
│   └── pokemon_names.csv
├── alembic/                    # DB マイグレーション
├── tests/
├── pyproject.toml
├── Dockerfile
└── Makefile
```

---

## 既存プロジェクトからの流用・変更

### そのまま流用できるもの
- **テンプレートマッチング基盤** (`frame_detector.py`, `pokemon_extractor.py` の設計)
- **FAISS インデックス構築・検索**のロジック
- **SQLModel データモデル**の設計（Battle, BattleSummary 等の構造）
- **Alembic マイグレーション**の仕組み
- **動画ダウンロード** (yt-dlp 連携)
- **ポケモン名辞書** (`pokemon_names.csv`) ※チャンピオンズ向けに更新が必要

### 大きく変わるもの
- **フロントエンド全体**: Next.js → Jinja2 + HTMX に書き換え
- **認証**: Auth0 → 不要（ローカルアプリ前提）。初回起動時にトレーナー名設定のみ
- **クラウド連携**: GCS / Firestore / Cloud Batch → すべて排除。ローカル完結
- **テンプレート画像**: ポケモンチャンピオンズのUI向けに全て新規作成が必要
- **フレーム検出ロジック**: ゲームUIの画面遷移パターンに合わせて再実装

### 改善するもの
- **動画入力**: YouTube URL に加えて、ローカル mp4 ファイルの直接入力にも対応
- **分析機能強化**: パーティ相性マトリクス、技選択傾向分析の追加
- **対戦メモ**: テキストに加えてタグ付け機能

---

## 動画入力フロー

### YouTube URL 入力（既存踏襲）
```
YouTube URL 入力 → yt-dlp でダウンロード → フレーム解析 → データ抽出 → DB 保存
```

### ローカルファイル入力（新規追加）
```
mp4 ファイルアップロード → フレーム解析 → データ抽出 → DB 保存
```

- ローカルファイルの場合、動画は `videos/` ディレクトリに保存し、対戦振り返り時に参照可能にする
- 1080p / 30fps のバリデーションはどちらの入力でも実施

---

## OCR 比較検証結果（2026-02-28 実施）

SV + チャンピオンズ先行画像（計92枚）で Tesseract / EasyOCR / RapidOCR を比較。
テストデータ・ベンチマークスクリプトは `tests/ocr_benchmark.py`, `tests/ocr_benchmark_easyocr_tuning.py` に保存。

### 結論: **EasyOCR を採用。Tesseract は捨てる。**

### エンジン比較（OVERALL 92枚）

| Engine | Exact Match | Avg EditDist | Avg Time |
|--------|------------|-------------|----------|
| Tesseract | 17.6% | 1.71 | 0.901s |
| **EasyOCR** | **39.1%** | **1.28** | **0.144s** |
| RapidOCR | 12.1% | 2.95 | 0.502s |

- **RapidOCR は候補外**。カタカナを中国語漢字に誤変換する問題が致命的
- Tesseract は battle_messages（日本語長文）で EasyOCR より良いが、他カテゴリで劣る
- EasyOCR は pip 完結・PyInstaller 同梱可能で配布面でも圧倒的に有利

### EasyOCR チューニング結果

コストゼロの改善策を8バリアント比較した結果:

| Variant | Exact Match | Avg ED | Avg Time | 効果 |
|---------|-----------|--------|----------|------|
| baseline (`ja+en`) | 39.1% | 1.28 | 0.144s | — |
| **+ch_tra** | **46.7%** | **1.11** | 0.521s | **中国語画像の認識が大幅改善** |
| upscale2x | 40.2% | 1.21 | 0.456s | 小さい文字の改善 |
| **up2x+ch_tra** | **47.8%** | **0.98** | 1.141s | **最高精度** |
| CLAHE | 38.0% | 1.41 | 0.143s | 逆効果 |
| white_ext (HSV) | 27.2% | 1.72 | 0.140s | 明確に悪化 |
| low_contrast | 39.1% | 1.27 | 0.140s | 効果なし |

**推奨構成**: `+ch_tra`（ja+en Reader と ch_tra+en Reader の2本立て、best pick）
- 速度重視なら `+ch_tra` のみ（0.5s/画像）
- 精度重視なら `up2x+ch_tra`（1.1s/画像）
- いずれも既存の編集距離マッチングと組み合わせれば実用的な精度に到達見込み

### 注意点
- EasyOCR は `ja` と `ch_tra` を同一 Reader に混在不可（別 Reader が必要）
- battle_messages でふりがな（ルビ）を誤って拾う問題あり → GPT 補正パイプラインは引き続き有効
- Fine-tuning も可能（deep-text-recognition-benchmark ベース）だが、まずは上記構成で十分な見込み

### ゲーム内フォント特定（2026-02-28 実施）

LikeFont でテスト画像を解析し、ゲーム内フォントを特定。

| 用途 | 特定フォント | 一致率 | 備考 |
|------|------------|--------|------|
| 英語テキスト（バトルメッセージ等） | **FOT-UD角ゴC80 Pro DB** (Fontworks) | 86.0% | UDKakuGo Condensed 80。上位候補がすべて UD角ゴファミリー |
| 日本語テキスト（ポケモン名等） | **FOT-Rodin NTLG DB** (Fontworks) | — | LikeFont では一致率が低い（69%）が、Fontendo の解析で確定済み |

いずれも **Fontworks の商用フォント**（Monotype 傘下）。合成データ用の無料代替:

| 実フォント | 合成データ用代替（OFL） | 入手先 |
|-----------|---------------------|--------|
| FOT-UD角ゴC80 Pro DB | **BIZ UDGothic** (Morisawa) | Google Fonts |
| FOT-Rodin NTLG DB | **Noto Sans JP** or **BIZ UDGothic** | Google Fonts |

BIZ UDGothic は同じ「UD（ユニバーサルデザイン）」設計思想で、字形的に最も近い無料フォント。

### 合成データ生成 PoC（2026-02-28 実施）

チャンピオンズ先行画像を背景テンプレートとして、Pillow で合成 OCR トレーニングデータを生成する PoC を実施。
スクリプト: `tests/synthetic_data_poc.py`、出力: `tests/synthetic_data_poc_output/`

**手法**:
1. 実ゲーム画像からテキスト領域を OpenCV inpaint で除去 → 背景テンプレート化
2. BIZ UDGothic / Noto Sans CJK JP フォントで新テキストを描画
3. augmentation（明度変動、ブラー、JPEG 圧縮）でバリエーション生成

**結果**:
- **技名**: ほぼ実画像と区別つかないレベル。背景が単色で再現性が高い
- **ポケモン名**: 良好。背景グラデーションの再現ができている
- **バトルメッセージ**: inpaint 後に元テキストの残影が残る課題あり。動画フレームから暗いシーンを切り出せば解決可能

**結論: 合成データ生成は実現可能。** フォントが商用版と微妙に異なるが、EasyOCR はニューラルネットベースの認識モデル（CNN + BiLSTM + CTC/Attention）のため、ピクセル単位の一致は不要。背景コントラスト・色味が近ければ fine-tuning に十分有効。

**本番の想定データ量**:
- ポケモン名: ~1,000種 × 5-10 バリエーション = 5,000-10,000枚
- 技名: ~800種 × 5 バリエーション = 4,000枚
- バトルメッセージ: テンプレート文 × バリエーション = 5,000枚

**EasyOCR fine-tuning パイプライン**: 合成画像 + labels.txt → LMDB 変換 → deep-text-recognition-benchmark で学習 → カスタムモデルとして EasyOCR に組み込み

---

## ポケモン画像認識の改善計画

### 現状（poke_battle_logger）

| 項目 | 内容 |
|------|------|
| 主モデル | SwinV2-base (`fufufukakaka/pokemon_image_classifier`) — 349MB, 93クラス |
| フォールバック | OpenCV テンプレートマッチング (TM_CCOEFF_NORMED, 閾値 0.78) |
| FAISS インデックス | `imgsim` ライブラリで埋め込み → IndexFlatL2（現パイプラインでは未使用） |
| 学習データ | 938枚 / 301クラス（平均 ~3枚/クラス） |
| テンプレート画像 | labeled: 107種 317枚 + user_labeled: 298種 746枚 = 合計 1,063枚 |
| eval accuracy | 88.3%（20エポック学習後、93クラスのみ） |

**課題**:
- SwinV2 は **93クラスしか学習していない** のにテンプレートは 301種以上 → モデルが古い
- 938枚 / 301クラスは **データ不足**（平均3枚/クラス）で過学習リスクあり
- SwinV2-base (349MB) + PyTorch (200MB) = **配布サイズが大きすぎる**
- **新ポケモン追加時に再学習が必要**（分類モデルの宿命）
- FAISS インデックスの `imgsim` ライブラリは埋め込み品質が低い

### 推奨アーキテクチャ: DINOv2-Small + FAISS（ONNX Runtime）

**DINOv2**（Meta, 自己教師あり Vision Transformer）を特徴抽出器とし、FAISS で類似検索するアプローチに移行。

**選定理由**:

| 観点 | 現行 (SwinV2 分類器) | 推奨 (DINOv2 + FAISS) |
|------|--------------------|-----------------------|
| モデルサイズ | 349MB (PyTorch 200MB 別途) | **84MB** (ONNX Runtime 15MB) |
| 配布合計 | ~550MB | **~100MB** |
| 新ポケモン追加 | 再学習が必要 | **テンプレート画像追加 + インデックス再構築のみ** |
| 必要学習データ | クラスあたり数十枚推奨 | **1-3枚で十分** (few-shot) |
| fine-grained 認識 | 普通 | **非常に高い** (DINOv2 の強み) |
| CPU 推論速度 | ~200-400ms | **~50-100ms** |
| PyInstaller 互換 | PyTorch (大) | ONNX Runtime (軽量) |

**DINOv2 がベストな理由**:
- 自己教師あり学習で 142M 枚の画像から訓練 → 汎用的かつ高品質な視覚特徴量
- fine-grained (種の識別等) ベンチマークで CLIP の 5倍の精度 (70% vs 15%)
- ViT-Small (22M params, 84MB) でも k-NN のみで 93% の分類精度
- ポケモンアイコンは標準化されたスプライト → 少ないテンプレートで十分識別可能

**CLIP を採用しない理由**: テキスト-画像の対照学習は「意味的な類似性」に強いが、見た目が似たポケモン同士（ニドラン♂ vs ニドラン♀ 等）の fine-grained 識別では DINOv2 に劣る。

### 認識パイプライン（Champions 版）

```
ポケモンアイコン画像 (クロップ済み)
    │
    ▼
[前処理: 224x224 リサイズ, ImageNet 正規化]
    │
    ▼
[DINOv2-Small ONNX] → 384次元 埋め込みベクトル
    │
    ▼
[FAISS IndexFlatIP (コサイン類似度)] → Top-K 結果
    │
    ├── 閾値以上 → ポケモン名を返す
    └── 閾値未満 → unknown_templates/ に保存（手動アノテーション用）
```

### 新ポケモン対応フロー

```
1. テンプレート画像を labeled_pokemon_templates/{ポケモン名}/ に配置
2. make build-pokemon-faiss-index を実行
   → DINOv2 で埋め込み計算 → FAISS インデックス再構築
3. 完了（モデルの再学習は不要）
```

### 精度をさらに上げる場合（オプション）

DINOv2-Small の frozen 埋め込みで精度不足の場合:
1. DINOv2-Small バックボーン + **ArcFace ヘッド** でメトリック学習
2. 学習済みバックボーンを ONNX エクスポート
3. FAISS で引き続き検索

ArcFace は顔認識由来のメトリック学習手法で、open-set 認識（未知クラスへの対応）に強い。

### SV との互換性

ユーザーの確認により、チャンピオンズのポケモンアイコンは **SV とほぼ同じ**。
したがって:
- 既存の SV テンプレート画像（1,063枚）をそのまま流用可能
- チャンピオンズ固有のポケモンのみ新規テンプレート追加
- FAISS アプローチなら、テンプレート追加のみで対応完了

### 依存パッケージ（配布サイズ比較）

| パッケージ | 現行 | 新構成 |
|-----------|------|--------|
| torch | ~200MB | **不要** |
| transformers | ~300MB | **不要** |
| onnxruntime | — | **~15MB** |
| faiss-cpu | ~20MB | ~20MB |
| DINOv2 モデル | — | **~84MB (ONNX)** |
| SwinV2 モデル | ~349MB | **不要** |
| **合計** | **~870MB** | **~120MB** |

---

## 配布戦略

**ターゲットユーザー**: Python やシステムに詳しくないポケモン対戦プレイヤー。
「ダウンロードして起動するだけ」に近い体験を目指す。

### 配布形式の比較

| 形式 | ユーザー体験 | 開発コスト | 制約 |
|------|------------|-----------|------|
| **GUI インストーラ付きデスクトップアプリ** | ダブルクリックで起動。最も簡単 | 高い（OS 別ビルド、署名） | バイナリサイズ大（500MB〜1GB+） |
| **Docker Desktop + docker-compose** | ターミナル不要で GUI から起動可能 | 低い | Docker Desktop のインストールが必要（非技術者にはハードル） |
| **pip + ランチャースクリプト** | Python 必須。インストール手順書が要る | 低い | Python 環境構築が非技術者に厳しい |
| **GitHub Releases + 起動スクリプト** | OS 別の .zip をダウンロード → スクリプト実行 | 中程度 | Python 同梱 or 事前インストールが必要 |

### 推奨アプローチ: 段階的に拡充

#### Phase 1: PyInstaller で動くものを作る（開発初期）

まず PyInstaller で Python バックエンドを単一バイナリにまとめる。
これは Phase 2 の Tauri sidecar としても再利用するため、どの道必要な工程。

```bash
# 開発中の確認用。zip 展開 → 実行
./poke-champions-logger
# → FastAPI サーバー起動 → ブラウザが開く
```

- Docker Compose も並行して用意する（開発者・技術者向けの確実な動作手段として）
- この段階では自分と技術者向け。OS セキュリティ警告は手動で回避

**実現に必要なこと**:
- OCR は EasyOCR を採用する方が圧倒的に有利（Tesseract はシステム依存のため同梱が困難）
- OpenCV, FAISS, yt-dlp 等は PyInstaller で同梱可能
- GitHub Actions で Windows / macOS のビルドを自動化

**OCR 選定への影響**:
EasyOCR なら Python パッケージとして PyInstaller に同梱できる。
Tesseract はシステムバイナリ + 言語データの同梱が必要で、OS 別の対応が複雑になる。
**配布しやすさの観点では EasyOCR が明確に有利**。精度が同等以上であれば EasyOCR を採用する。

#### Phase 2: Tauri でネイティブアプリ化（一般配布・本命）

Phase 1 の PyInstaller バイナリを Tauri の「sidecar」として組み込み、
ネイティブインストーラ + ネイティブウィンドウのアプリにする。

```
[Windows]
PokéChampionsLogger_setup.msi を実行 → インストール → アプリ起動
  → ネイティブウィンドウで UI 表示
  → タスクトレイにアイコン（終了はここから）
  → アンインストールは「設定 → アプリ」から（OS 標準）

[macOS]
PokéChampionsLogger.dmg を開く → Applications にドラッグ → アプリ起動
  → ネイティブウィンドウで UI 表示
```

**PyInstaller 単体との違い**:

| | PyInstaller 単体 (Phase 1) | Tauri + sidecar (Phase 2) |
|---|---|---|
| ユーザーが受け取るもの | .zip（中に .exe / .app） | .msi / .dmg（インストーラ） |
| 起動後の見た目 | ブラウザのタブ | ネイティブウィンドウ |
| 「アプリっぽさ」 | 低い（Webページ感） | 高い（普通のアプリ感） |
| OS の警告 | 強め（生の実行ファイル） | やや緩和（インストーラ形式） |
| アンインストール | フォルダ削除 | OS 標準の手順 |

**実現に必要なこと**:
- Tauri の Rust ビルド環境（CI で自動化すれば開発マシンのみ）
- Tauri sidecar 設定（PyInstaller バイナリを Tauri に同梱する設定）
- macOS は署名なしだと Gatekeeper に引っかかるため、`xattr -cr` の手順 or Apple Developer 署名（$99/年）が必要
- Windows も EV コード署名があると SmartScreen 警告が消える（本格配布時に検討）
- バイナリサイズは 500MB〜1GB 程度になる見込み（許容範囲）

**Tauri の役割は薄いシェル**:
Tauri 側のコードは最小限（webview で `http://localhost:8000` を表示 + sidecar の起動/終了管理のみ）。
Python 側の開発が一通り完了してから着手しても遅くない。

#### Phase 3: 自動アップデート機能（将来）
- Tauri には組み込みのアップデーター機能がある
- 起動時に GitHub Releases の最新バージョンをチェック
- 新バージョンがあれば通知 → ダウンロード → 再起動

---

## 画面構成

### 1. ダッシュボード (`/`)
- 勝率・最新順位・直近の勝ちポケモン/負けポケモン
- 活動履歴ヒートマップ
- 最近の対戦履歴テーブル

### 2. ログ分析 (`/analytics`)
- 勝率推移チャート（Chart.js）
- 順位推移チャート（Chart.js）
- 自分/相手のポケモン選出統計テーブル
- ノックアウト統計テーブル
- **新規**: パーティ相性マトリクス
- **新規**: 技選択傾向

### 3. 対戦一覧 (`/battles`)
- 対戦カード一覧（ページネーション）
- 勝敗・順位・チーム構成の表示
- メモ編集（HTMX でインライン更新）
- **新規**: タグ付け・タグフィルタ

### 4. 対戦データ登録 (`/process`)
- YouTube URL 入力 + フォーマットチェック
- **新規**: ローカル mp4 ファイルアップロード
- 言語選択
- 処理状況表示（HTMX ポーリング or SSE で更新）

### 5. 設定 (`/settings`)
- トレーナー名設定
- テンプレート画像管理（unknown → labeled のアノテーション）

---

## HTMX 設計パターン

```html
<!-- 例: シーズン切り替えで分析データを部分更新 -->
<select name="season"
        hx-get="/htmx/analytics/charts"
        hx-target="#charts-section"
        hx-swap="innerHTML">
  <option value="0">通算</option>
  <option value="1">シーズン1</option>
</select>

<div id="charts-section">
  {% include "fragments/chart_section.html" %}
</div>
```

```html
<!-- 例: メモのインライン編集 -->
<div hx-target="this" hx-swap="outerHTML">
  <p>{{ battle.memo }}</p>
  <button hx-get="/htmx/battles/{{ battle.id }}/memo-edit">編集</button>
</div>
```

---

## データモデル（初期設計）

既存モデルをベースに、以下を初期モデルとする。
ポケモンチャンピオンズのゲームシステムに応じて調整が必要。

- **Trainer** - プレイヤー情報（ローカルでは基本1人）
- **Season** - シーズン情報
- **Battle** - 対戦メタデータ（日時、勝敗、順位変動）
- **BattlePokemonTeam** - チーム構成（自分6体 + 相手6体）
- **InBattlePokemonLog** - 選出ポケモンログ
- **SelectedMove** - 技選択ログ
- **FaintedLog** - ひんしログ
- **MessageLog** - バトルメッセージログ
- **BattleVideo** - 動画参照（YouTube URL or ローカルパス）
- **BattleTag** - **新規**: 対戦タグ（多対多）

---

## 開発ロードマイク

### マイルストーン 1: 基盤構築
- [ ] リポジトリ作成・プロジェクト初期設定（Poetry/uv, FastAPI, SQLModel）
- [ ] Jinja2 + HTMX + Tailwind の基本レイアウト構築
- [ ] SQLite + Alembic のセットアップ
- [ ] データモデル定義・マイグレーション作成

### マイルストーン 2: 動画処理パイプライン
- [ ] yt-dlp による動画ダウンロード
- [ ] ローカル mp4 ファイルアップロード対応
- [ ] フレーム検出ロジック（ポケモンチャンピオンズ UI 向け）
- [ ] テンプレートマッチングによるポケモン認識
- [ ] OCR によるテキスト抽出（EasyOCR 採用決定済み）
- [ ] FAISS インデックス構築

### マイルストーン 3: ダッシュボード・分析画面
- [ ] ダッシュボードページ
- [ ] ログ分析ページ（チャート + テーブル）
- [ ] 対戦一覧ページ（ページネーション + メモ）
- [ ] 対戦データ登録ページ

### マイルストーン 4: 配布準備
- [ ] PyInstaller でのバイナリビルド（Windows / macOS）
- [ ] GitHub Actions で OS 別ビルドの自動化
- [ ] Dockerfile + `docker-compose.yml`（技術者向け）
- [ ] Tauri シェル構築（sidecar として PyInstaller バイナリを組み込み）
- [ ] .msi / .dmg インストーラの生成
- [ ] コード署名の検討（配布が本格化したタイミングで）

### マイルストーン 5: 機能拡充
- [ ] タグ付け機能
- [ ] パーティ相性マトリクス
- [ ] 技選択傾向分析
- [ ] 対戦検索の強化

---

## 前提条件

- **対戦フォーマット**: シングルバトル
- **動画入力**: 1920x1080 (1080p) の動画を前提。Switch のキャプチャが主だが、同一フォーマットであればプラットフォームは問わない
- **ターゲットユーザー**: Python やシステムに詳しくない一般のポケモン対戦プレイヤーにも使ってもらえることを目指す

## 未確定事項（ポケモンチャンピオンズ情報待ち）

- ゲーム画面のUI配置 → テンプレート画像とフレーム検出ロジックに影響
- ランクシステムの仕様 → 順位追跡ロジックに影響
- ゲーム内 API や公式連携の有無 → CV/OCR が不要になる可能性
- ~~OCR 精度比較（Tesseract vs EasyOCR）~~ → **検証完了。EasyOCR 採用決定**（詳細は「OCR 比較検証結果」セクション参照）
