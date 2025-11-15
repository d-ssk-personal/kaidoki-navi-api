# Python 3.12ベースイメージ
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存パッケージをコピーしてインストール
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ /app/src/

# ポートを公開
EXPOSE 8080

# 環境変数
ENV PYTHONUNBUFFERED=1

# Flaskサーバーを起動
CMD ["python", "src/local_server.py"]