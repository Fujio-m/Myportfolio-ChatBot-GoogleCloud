# 1. 軽量な Python 3.11 のベースイメージを使用
FROM python:3.11-slim

# 2. 環境変数の設定 (Python のバッファリング無効化、バイトコードの非生成)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# 3. 作業ディレクトリの設定
WORKDIR /app

# 4. 依存関係のインストールに必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. requirements.txt をコピーしてライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. アプリケーションコード全体をコピー
COPY . .

# 7. コンテナが開放するポート番号の指定 (Cloud Run のデフォルトは 8080)
EXPOSE 8080

# 8. 起動コマンドの設定 (環境変数 $PORT を動的に読み込む設定)
CMD ["sh", "-c", "streamlit run main.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]
