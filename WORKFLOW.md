# 作業手順書

## 概要
本ドキュメントは、MVP要件定義書に基づいた実装作業の進め方を説明します。

---

## 開発環境セットアップ

### 1. 必要なツール・アカウント
- [ ] Python 3.11以上
- [ ] Node.js 18以上（フロントエンドビルド用）
- [ ] Git
- [ ] Supabaseアカウント
- [ ] Azureアカウント
- [ ] OpenAI APIキー

### 2. プロジェクト構成
```
smallbase/
├── backend/          # FastAPI
├── frontend/         # 静的HTML + Bootstrap
├── docs/            # ドキュメント
│   ├── mvp.md       # 要件定義書
│   ├── WORKFLOW.md  # 本ファイル
│   └── PROGRESS.md  # 進捗管理
└── README.md
```

---

## Phase 1: 基盤構築

### 1.1 Supabaseプロジェクト作成・設定

#### 手順
1. Supabaseダッシュボードで新規プロジェクト作成
2. プロジェクトURLとAPIキーを取得
3. 環境変数ファイル（`.env`）に設定を保存

#### 確認事項
- [ ] プロジェクトが作成されている
- [ ] APIキーが取得できている
- [ ] 環境変数が設定されている

### 1.2 データベーステーブル作成

#### SQL実行
```sql
-- filesテーブル作成
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- chunksテーブル作成
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);

-- pgvector拡張有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- ベクトル検索用インデックス作成
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
```

#### 確認事項
- [ ] `files`テーブルが作成されている
- [ ] `chunks`テーブルが作成されている
- [ ] pgvector拡張が有効になっている
- [ ] インデックスが作成されている
- [ ] 外部キー制約（CASCADE削除）が設定されている

### 1.3 FastAPIプロジェクト作成

#### 手順
1. `backend/`ディレクトリ作成
2. `requirements.txt`作成
3. 仮想環境作成・有効化
4. 依存パッケージインストール

#### requirements.txt例
```
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
supabase==2.0.0
openai==1.3.0
python-multipart==0.0.6
pypdf2==3.0.1
python-docx==1.1.0
```

#### 確認事項
- [ ] FastAPIプロジェクトが作成されている
- [ ] 依存パッケージがインストールされている
- [ ] サーバーが起動できる

### 1.4 認証機能実装

#### 手順
1. Supabaseクライアント初期化
2. ログインエンドポイント実装（`POST /auth/login`）
3. JWTトークン検証ミドルウェア作成
4. 管理者ロールチェック関数作成

#### 実装ポイント
- JWTトークンの検証
- ユーザーメタデータから`role`を取得
- 管理者以外のアクセスを403で拒否

#### 確認事項
- [ ] ログインエンドポイントが動作する
- [ ] JWTトークンが正しく検証される
- [ ] 管理者ロールチェックが機能する

---

## Phase 2: 管理者機能

### 2.1 ログイン画面実装

#### 手順
1. `frontend/admin/login.html`作成
2. Bootstrapでフォーム作成
3. ログインAPI呼び出し実装
4. トークンをlocalStorageに保存
5. ログイン成功時に`/admin`へリダイレクト

#### 確認事項
- [ ] ログイン画面が表示される
- [ ] ログインが成功する
- [ ] トークンが保存される
- [ ] リダイレクトが動作する

### 2.2 ファイル一覧表示機能

#### 手順
1. `GET /admin/files`エンドポイント実装
2. 認証ミドルウェア適用
3. `frontend/admin/index.html`作成
4. 一覧取得API呼び出し実装
5. テーブル表示実装

#### 確認事項
- [ ] ファイル一覧が取得できる
- [ ] テーブルに正しく表示される
- [ ] 認証なしアクセスが拒否される

### 2.3 ファイルアップロード機能

#### 手順
1. `POST /admin/upload`エンドポイント実装
2. ファイル形式チェック（PDF/TXT/DOCX）
3. Supabase Storageにファイル保存
4. データベースにファイル情報保存
5. フロントエンドにアップロードフォーム追加

#### 確認事項
- [ ] ファイルがアップロードできる
- [ ] ファイル形式チェックが機能する
- [ ] Storageに保存される
- [ ] データベースに記録される

### 2.4 ファイル削除機能

#### 手順
1. `DELETE /admin/files/{id}`エンドポイント実装
2. ファイル削除処理実装
3. 関連チャンク・embedding削除処理実装（CASCADE）
4. Storageからファイル削除
5. フロントエンドに削除ボタン追加

#### 確認事項
- [ ] ファイルが削除できる
- [ ] 関連チャンクも削除される
- [ ] Storageからも削除される
- [ ] 一覧が更新される

---

## Phase 3: RAG機能

### 3.1 テキスト抽出・チャンク分割実装

#### 手順
1. PDFテキスト抽出ライブラリ統合（PyPDF2）
2. DOCXテキスト抽出ライブラリ統合（python-docx）
3. TXTファイル読み込み実装
4. チャンク分割ロジック実装（500文字程度、オーバーラップあり）

#### 実装ポイント
- チャンクサイズ: 500文字
- オーバーラップ: 100文字
- ファイル形式ごとの抽出処理

#### 確認事項
- [ ] PDFからテキストが抽出できる
- [ ] DOCXからテキストが抽出できる
- [ ] TXTが読み込める
- [ ] チャンクが適切に分割される

### 3.2 Embedding生成・保存実装

#### 手順
1. OpenAI APIクライアント設定
2. Embedding生成関数実装（`text-embedding-ada-002`）
3. チャンクごとにEmbedding生成
4. pgvectorに保存

#### 実装ポイント
- モデル: `text-embedding-ada-002`
- ベクトル次元: 1536
- バッチ処理で効率化

#### 確認事項
- [ ] Embeddingが生成される
- [ ] pgvectorに保存される
- [ ] アップロード時に自動実行される

### 3.3 類似度検索実装

#### 手順
1. 質問文のEmbedding生成
2. pgvectorでコサイン類似度検索
3. 上位N件のチャンク取得（N=5程度）

#### SQL例
```sql
SELECT 
    c.id,
    c.content,
    c.file_id,
    f.filename,
    1 - (c.embedding <=> $1::vector) AS similarity
FROM chunks c
JOIN files f ON c.file_id = f.id
ORDER BY c.embedding <=> $1::vector
LIMIT 5;
```

#### 確認事項
- [ ] 類似度検索が動作する
- [ ] 関連チャンクが取得できる
- [ ] 検索結果が適切にソートされる

### 3.4 質問回答機能実装

#### 手順
1. `POST /chat`エンドポイント実装
2. 質問文のEmbedding生成
3. 類似度検索で関連チャンク取得
4. プロンプト構築（質問 + コンテキスト）
5. OpenAI Chat APIで回答生成
6. 回答とソース情報を返却
7. フロントエンドに質問画面実装

#### プロンプト例
```
以下のコンテキストを参考に、質問に回答してください。

コンテキスト:
{関連チャンク1}
{関連チャンク2}
...

質問: {ユーザーの質問}

回答:
```

#### 確認事項
- [ ] 質問に回答が生成される
- [ ] 関連チャンクが参照される
- [ ] ソース情報が返される
- [ ] フロントエンドで表示される

---

## Phase 4: デプロイ

### 4.1 Azure Static Web Apps設定

#### 手順
1. Azure PortalでStatic Web Appsリソース作成
2. GitHubリポジトリ連携
3. ビルド設定（`azure-static-web-apps.yml`）作成
4. 環境変数設定

#### 確認事項
- [ ] Static Web Appsが作成されている
- [ ] GitHub連携が完了している
- [ ] ビルドが成功する

### 4.2 本番環境デプロイ

#### 手順
1. FastAPIをAzure FunctionsまたはApp Serviceにデプロイ
2. 環境変数を本番環境に設定
3. CORS設定
4. 動作確認

#### 確認事項
- [ ] APIがデプロイされている
- [ ] 環境変数が設定されている
- [ ] CORSが正しく設定されている

### 4.3 動作確認

#### 確認項目
- [ ] 管理者ログインが動作する
- [ ] ファイルアップロードが動作する
- [ ] ファイル削除が動作する
- [ ] RAG質問が動作する
- [ ] エラーハンドリングが適切

---

## 開発のコツ

### 1. 段階的に実装
- 各Phaseを順番に進める
- 1つの機能が完成してから次へ進む
- 動作確認をこまめに行う

### 2. エラーハンドリング
- 各APIで適切なエラーレスポンスを返す
- フロントエンドでエラーメッセージを表示
- ログを残す

### 3. テスト
- 各機能を手動でテスト
- エッジケースも確認
- 本番環境でも動作確認

### 4. ドキュメント更新
- 実装した機能は`PROGRESS.md`を更新
- 問題が発生したら記録
- 解決方法も記録

---

## トラブルシューティング

### よくある問題

#### 1. pgvectorが動作しない
- PostgreSQLのバージョンを確認（12以上）
- 拡張機能が有効になっているか確認

#### 2. Embedding生成が遅い
- バッチ処理を実装
- 非同期処理を検討

#### 3. 認証が通らない
- JWTトークンの有効期限を確認
- ロール設定を確認

#### 4. CORSエラー
- FastAPIのCORS設定を確認
- 許可するオリジンを正しく設定

---

## 参考リソース

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Supabase公式ドキュメント](https://supabase.com/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)

