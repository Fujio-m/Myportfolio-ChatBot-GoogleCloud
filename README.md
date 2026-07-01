# 勤怠ルール AI チャットボット｜ポートフォリオ

> **Gemini API × RAG** で「就業規則を正確に答える」Q&A チャットボットを開発。
> ハルシネーション（AI の誤回答）を抑制し、実務運用を想定した PDCA 改善サイクルを組み込んだシステムです。
> ※本プロジェクトはポートフォリオ用に作成したデモアプリです。実際の企業データや社内就業規則等は一切使用しておりません。

## 🔗 デプロイ先リンク

- **ポートフォリオ紹介サイト（フロントエンド）**: [https://fujio-m-portfolio.web.app](https://fujio-m-portfolio.web.app)
- **勤怠ルールQ&Aチャットボットアプリ（バックエンド）**: [https://chatbot-app-70601432783.us-central1.run.app](https://chatbot-app-70601432783.us-central1.run.app)

---

## プロジェクト概要

### 開発の背景と目的
実務における「就業規則の参照コスト削減」および「自己解決率の向上」を目的としたRAG（検索拡張生成）チャットボットです。
開発者の実務経験（勤怠管理ツールの問い合わせ対応・エスカレーション業務）に基づき、定型的な問い合わせ対応時間（月約3時間相当）の削減と業務自動化を想定して構築しました。

### 解決された課題
- **自己解決率の向上**：従業員が質問を自己解決できる環境を構築。
- **対応工数の削減**：定型的な問い合わせを自動化し、担当者の対応時間を削減。
- **メンテナンス負荷の低減**：就業規則の改訂時はPDFを差し替えるだけでよく、プログラム改修を不要に。

### 再構築とサービスの選定理由
当初Streamlitで開発したプロトタイプをベースに、より実務に近い「フロントエンドとバックエンドの分離構成」へと再構築しました。
- **フロントエンド（Firebase Hosting）**：Google Cloudとの親和性が高く、無料枠で高速なWeb公開が可能。
- **バックエンド（Cloud Run）**：リクエスト時のみ起動（インスタンス数「0」に縮小）するコンテナ構成で、コスト最適化とスキル実践を実現。
※プロトタイプ版は [Streamlit Cloud](https://myportfolio-fujio-chatbot.streamlit.app/) でもご確認いただけます。

### 達成した成果
| 指標 | 結果 |
|:---|:---|
| 正答率 | **90.0%**（20 件中 18 件合格） |
| 改善サイクル | プロンプト修正による回答精度向上を実証 |
| デプロイ構成 | Firebase Hosting + Cloud Run（Dockerコンテナ） |
| メンテナンス性 | PDFの差し替えのみでルール更新が完結 |

---

## 設計におけるこだわり

### 1. ハルシネーション防止の徹底
就業規則PDF以外の「推測による回答」を禁じるシステムプロンプトを設定。
回答できない質問には「回答不可」と明示させることで、AIのハルシネーションの防止を徹底しました。

### 2. 機密情報の保護
Gemini APIキー等の認証情報は **Secret Manager** で一元管理し、ソースコードからの情報漏洩を徹底排除しています。
PDF原本もコンテナ内のメモリ上に配置し、外部露出を防ぐ設計にしました。

### 3. PDF更新によるPDCAサイクル
就業規則の改訂時は管理者がPDFを更新するだけでAIの回答が即座に最新化される設計にしました。
更新作業もあえて人間が行うことで、AIだけに任せた場合のリスクを排除しました。

### 4. ポートフォリオ全体のコスト運用
Cloud Run・Firebase Hosting・Secret Manager・Artifact Registryの各サービスを無料枠の範囲内で運用できるよう設計。
北米リージョン(us-central1)選択やインスタンスの自動縮小など、コストを意識した構成を徹底しています。

---

## 使用技術スタック

| カテゴリ | 技術 | バージョン | 採用理由 |
|:---|:---|:---|:---|
| 開発言語 | Python | 3.11 | AI ライブラリが豊富なため |
| フレームワーク | Streamlit | 1.55.0 | 素早く簡易的に AI モデル開発ができるため |
| AI モデル | Gemini 3.1 Flash-lite | - | 無料枠で最新かつ低コストで運用が可能なため |
| データ可視化 | Plotly | - | 動的なグラフが表示可能なため |
| データ処理 | Pandas | - | CSV の統計処理に必要なため |
| PDF 処理 | PyPDF | - | PDF テキスト抽出機能に必要なため |
| フロントエンド | HTML / CSS / JavaScript | - | ポートフォリオ紹介サイトの構築 |
| ホスティング | Firebase Hosting | - | Google Cloud との親和性が高く、無料枠で高速な静的サイト公開が可能なため |
| コンテナ | Docker | - | Cloud Run へのデプロイに使用 |
| クラウド | Google Cloud Run | - | リクエストが無いときはインスタンス数 0 にできるため、コスト削減が可能 |

---

## ディレクトリ構成

```
Myportfolio-ChatBot-GoogleCloud/
├── .github/
│   └── workflows/
│       ├── cloud-run-deploy.yml        # Cloud Run への自動デプロイ設定
│       ├── firebase-hosting-merge.yml  # Firebase への自動デプロイ設定
│       └── pytest.yml                  # テスト自動実行
│
├── frontend/                           # フロントエンド（ポートフォリオ紹介サイト）
│   ├── index.html                      # メインページ
│   ├── css/
│   │   └── style.css                   # メインページの装飾
│   ├── js/
│   │   └── main.js                     # メインページの操作ロジック
│   └── img/                            # 紹介用スクリーンショット・画像類
│
├── chatbot-app/                        # バックエンド（チャットボットアプリ）
│   ├── main.py                         # アプリのメインナビゲーション定義
│   ├── pages/
│   │   ├── 1_Chatbot.py                # AI チャットボット本体
│   │   └── 2_Evaluation.py             # 精度評価・テストダッシュボード
│   ├── utils/
│   │   ├── json_loader.py              # JSON ファイルから URL 読み込み処理
│   │   ├── responsive.py               # Web ページをレスポンシブデザイン化
│   │   └── rag_service.py              # RAG 処理・Gemini 接続の管理
│   ├── data/
│   │   ├── test_cases.csv              # テストケース CSV
│   │   └── kintai_rule.pdf             # 勤怠規定 PDF（RAG 参照元）
│   ├── assets/
│   │   ├── system_prompt.md            # Gemini API 用システムプロンプト
│   │   ├── usage_guide.md              # ユーザー向け利用ガイド
│   │   └── config.json                 # 外部フォーム URL 等の設定
│   ├── tests/
│   │   ├── test_chatbot.py             # チャット起動テスト・RAG機能 単体テスト
│   │   └── test_evaluation.py          # 精度評価ダッシュボード起動テスト
│   ├── .streamlit/
│   │   └── secrets.toml                # API キー設定（ローカル用・Git 管理外）
│   ├── Dockerfile                      # Cloud Run デプロイ用コンテナ定義
│   ├── .dockerignore                   # Docker ビルド時の除外ファイル設定
│   └── requirements.txt                # Python 依存ライブラリ一覧
│
├── firebase.json                       # Firebase 設定ファイル
├── .firebaserc                         # Firebase プロジェクト設定
└── README.md                           # 本ドキュメント
```

---

## ローカル環境のセットアップ方法

### 1. リポジトリのクローン

```bash
git clone https://github.com/Fujio-m/Myportfolio-ChatBot-GoogleCloud.git
cd Myportfolio-ChatBot-GoogleCloud
```

### 2. バックエンド（チャットボットアプリ）の起動

`chatbot-app` ディレクトリへ移動して実行します。

#### A. ローカルの仮想環境で直接起動する場合

```bash
cd chatbot-app

# 仮想環境の作成と有効化
python -m venv venv

# Windows の場合
venv\Scripts\activate

# macOS / Linux の場合
source venv/bin/activate

# 依存ライブラリのインストール
pip install -r requirements.txt
```

`.streamlit/secrets.toml` を新規作成し、Gemini API キーを設定します。

```toml
GEMINI_API_KEY = "あなたの API キー"
```

起動コマンドを実行します。

```bash
streamlit run main.py
```

#### B. Docker コンテナとして起動する場合

```bash
cd chatbot-app
docker build -t chatbot-app .
docker run -p 8501:8080 -e GEMINI_API_KEY="あなたの API キー" chatbot-app
```

### 3. フロントエンド（ポートフォリオ紹介サイト）の起動

Firebase CLI を使用してローカルでホスティング環境をテストできます。

```bash
# 準備: Node.js と Firebase CLI のインストールが必要です
npm install -g firebase-tools

# ログインとテスト起動
firebase login
firebase serve --only hosting
```

起動後、ブラウザで `http://localhost:5000` にアクセスするとポートフォリオサイトを確認できます。

---

*本プロジェクトはポートフォリオ用に作成したものです。実際の企業データは使用していません。*