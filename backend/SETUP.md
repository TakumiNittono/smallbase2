# バックエンドセットアップガイド

## Phase 1: 基盤構築のセットアップ手順

### 1. Supabaseプロジェクト作成・設定

1. [Supabase](https://supabase.com/)にアクセスしてアカウントを作成（またはログイン）
2. 新しいプロジェクトを作成
3. プロジェクト設定から以下を取得：
   - **Project URL** (`SUPABASE_URL`)
   - **anon public key** (`SUPABASE_KEY`)
   - **service_role key** (`SUPABASE_SERVICE_KEY`) - 注意: これは秘密鍵です

### 2. データベーステーブル作成

1. Supabaseダッシュボードの「SQL Editor」を開く
2. `docs/init_db.sql`の内容をコピー＆ペースト
3. 「Run」ボタンをクリックして実行
4. テーブルが作成されたことを確認：
   - `files`テーブル
   - `chunks`テーブル
   - pgvector拡張が有効になっている

### 2.5 Supabase Storageバケット作成

1. Supabaseダッシュボードの「Storage」を開く
2. 「Create a new bucket」をクリック
3. バケット名: `files`
4. 「Public bucket」のチェックを外す（プライベートバケット）
5. 「Create bucket」をクリック
6. バケットが作成されたことを確認

### 3. 環境変数設定

`backend/.env`ファイルを作成（`.env.example`を参考に）：

```bash
cd backend
cp .env.example .env  # .env.exampleが存在する場合
```

`.env`ファイルを編集して、実際の値を設定：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 4. 仮想環境と依存パッケージ

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化（macOS/Linux）
source venv/bin/activate

# Windowsの場合
# venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt
```

### 5. サーバー起動と動作確認

```bash
# 開発サーバー起動
python main.py

# または
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

ブラウザで以下にアクセス：
- API: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs
- ヘルスチェック: http://localhost:8000/health

### 6. 認証機能のテスト

#### 6.1 Supabaseで管理者ユーザー作成

1. Supabaseダッシュボードの「Authentication」→「Users」を開く
2. 「Add user」で新しいユーザーを作成
3. ユーザーの「User Metadata」を編集：
   ```json
   {
     "role": "admin"
   }
   ```

#### 6.2 ログインAPIのテスト

APIドキュメント（http://localhost:8000/docs）から：

1. `/auth/login`エンドポイントを開く
2. 「Try it out」をクリック
3. 以下のリクエストボディを入力：
   ```json
   {
     "email": "admin@example.com",
     "password": "your_password"
   }
   ```
4. 「Execute」をクリック
5. `access_token`と`user`情報が返ってくることを確認

### 7. トラブルシューティング

#### 環境変数が読み込まれない
- `.env`ファイルが`backend/`ディレクトリに存在するか確認
- ファイル名が`.env`（先頭にドット）であることを確認

#### Supabase接続エラー
- `SUPABASE_URL`と`SUPABASE_KEY`が正しいか確認
- Supabaseプロジェクトがアクティブか確認

#### インポートエラー
- 仮想環境が有効になっているか確認
- `pip install -r requirements.txt`を再実行

#### pgvectorエラー
- PostgreSQLのバージョンが12以上であることを確認
- `CREATE EXTENSION vector;`が実行されているか確認

## 次のステップ

Phase 1が完了したら、`docs/PROGRESS.md`を更新して、Phase 2（管理者機能）に進みましょう。

