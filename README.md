# Smallbase MVP

管理者画面付き・最小RAG構成（MVP）プロジェクト

## プロジェクト構成

```
smallbase/
├── backend/          # FastAPI
├── frontend/         # 静的HTML + Bootstrap
├── docs/            # ドキュメント
│   ├── mvp.md       # 要件定義書
│   ├── WORKFLOW.md  # 作業手順書
│   ├── PROGRESS.md  # 進捗管理
│   └── init_db.sql  # データベース初期化SQL
└── README.md
```

## セットアップ

### 1. 必要な環境

- Python 3.11以上
- Supabaseアカウント
- OpenAI APIキー

### 2. バックエンドセットアップ

```bash
# バックエンドディレクトリに移動
cd backend

# 仮想環境作成
python -m venv venv

# 仮想環境有効化（macOS/Linux）
source venv/bin/activate

# 依存パッケージインストール
pip install -r requirements.txt
```

### 3. 環境変数設定

`backend/.env`ファイルを作成し、以下の内容を設定してください：

```env
# Supabase設定
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# OpenAI設定
OPENAI_API_KEY=your_openai_api_key

# アプリケーション設定
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 4. データベース初期化

SupabaseダッシュボードのSQL Editorで、`docs/init_db.sql`の内容を実行してください。

### 5. サーバー起動

```bash
# 開発サーバー起動
python main.py

# または uvicorn を使用
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメントは `http://localhost:8000/docs` で確認できます。

## 開発状況

詳細は `docs/PROGRESS.md` を参照してください。

## ドキュメント

- [要件定義書](docs/mvp.md)
- [作業手順書](docs/WORKFLOW.md)
- [進捗管理](docs/PROGRESS.md)

