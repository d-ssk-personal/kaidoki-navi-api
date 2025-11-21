# Docker環境のトラブルシューティング

## 現在の状況について

`start-local.sh` を実行後、以下の症状が発生している場合の対処法です。

### 症状

1. **ポート8000にアクセスすると `400 Bad Request` エラーが出る**
2. **ポート8002が長時間読み込み中になり、開けない**

## 重要: ポート8000のエラーについて

**ポート8000で400エラーが出るのは正常な動作です！**

### なぜ400エラーが出るのか？

ポート8000は **DynamoDB Local のAPIエンドポイント** です。以下の特徴があります：

- ✅ **正しい使い方**: AWS CLIやSDK（boto3）から接続
- ❌ **間違った使い方**: ブラウザで直接アクセス

ブラウザでアクセスすると、DynamoDB Localは「これはAWS APIリクエストではない」と判断し、400エラーを返します。

### ポート8000が正常に動作しているか確認する方法

```bash
# AWS CLIを使用してテーブル一覧を取得
aws dynamodb list-tables \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

このコマンドでテーブル一覧が表示されれば、DynamoDB Local は正常に動作しています。

## ポート8002（DynamoDB Admin GUI）の問題を解決する

### クイックフィックス（推奨）

以下のスクリプトを実行してください：

```bash
./scripts/fix-admin-gui.sh
```

このスクリプトは自動的に：
1. ログを確認
2. DynamoDB Adminコンテナを再起動
3. 接続テストを実行

### 手動で修正する場合

#### Step 1: コンテナの状態を確認

```bash
docker ps -a | grep dynamodb
```

**期待される結果**:
- `dynamodb-local` と `dynamodb-admin` の両方が `Up` 状態

#### Step 2: ログを確認

```bash
# DynamoDB Localのログ
docker logs dynamodb-local

# DynamoDB Adminのログ
docker logs dynamodb-admin
```

**確認ポイント**:
- エラーメッセージがないか
- DynamoDB Adminが `dynamodb-local:8000` に接続できているか

#### Step 3: DynamoDB Adminを再起動

```bash
docker-compose restart dynamodb-admin

# 10秒待つ
sleep 10
```

#### Step 4: ブラウザでアクセス

```
http://localhost:8002
```

**ブラウザのキャッシュをクリアしてからアクセスしてください**:
- Chrome: `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)
- または、プライベートモード/シークレットモードで開く

### それでも解決しない場合

#### 完全に再起動

```bash
# コンテナを完全停止
docker-compose down

# 再起動
docker-compose up -d

# 起動を待つ
sleep 10

# テーブルを初期化（まだの場合）
cd scripts
./init-dynamodb.sh
cd ..
```

#### ポート競合の確認

```bash
# ポート8002を使用しているプロセスを確認
lsof -i :8002

# もし他のプロセスが使用している場合は終了させる
kill -9 <PID>
```

#### 別のブラウザで試す

- Chrome で開けない → Firefox や Safari で試す
- ブラウザの拡張機能が干渉している可能性があります

## 診断スクリプト

詳細な診断が必要な場合は、以下のスクリプトを実行してください：

```bash
./scripts/troubleshoot-docker.sh
```

このスクリプトは以下を確認します：
- コンテナの起動状態
- ポートバインディング
- 詳細なログ
- ネットワーク設定
- DynamoDB APIへの接続テスト

## よくある質問

### Q1: ポート8000で400エラーが出ますが、大丈夫ですか？

**A**: はい、正常です。ポート8000はAPIエンドポイントなので、ブラウザでアクセスすると400エラーが出ます。AWS CLIやSDKから接続できれば問題ありません。

### Q2: ポート8002が開けません

**A**: 以下を試してください：
1. `./scripts/fix-admin-gui.sh` を実行
2. ブラウザのキャッシュをクリア
3. 別のブラウザで試す
4. `docker logs dynamodb-admin` でエラーを確認

### Q3: データは永続化されていますか？

**A**: はい、Docker volumeに保存されています。`docker-compose down` でコンテナを削除してもデータは保持されます。データを削除したい場合は `docker-compose down -v` を実行してください。

### Q4: SAM Local APIを起動するにはどうすればいいですか？

**A**: DynamoDB Localが起動している状態で：
```bash
sam build
sam local start-api --docker-network lambda-local --env-vars env.json --parameter-overrides file://env.json
```

## まとめ

| ポート | 用途 | ブラウザでアクセス | 確認方法 |
|-------|------|------------------|----------|
| 8000 | DynamoDB API | ❌ 400エラー（正常） | AWS CLI |
| 8002 | DynamoDB Admin GUI | ✅ できる | ブラウザ |
| 3000 | SAM Local API | ✅ できる | curl/ブラウザ |

**重要**: ポート8000で400エラーが出ても心配不要です。これは正常な動作です。

DynamoDB Admin GUI（ポート8002）でテーブルを確認できれば、環境は正常に動作しています。
