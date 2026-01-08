# 動作確認ガイド

## 前提条件

1. **Supabase設定完了**
   - プロジェクト作成済み
   - データベーステーブル作成済み（`docs/init_db.sql`実行済み）
   - Storageバケット「files」作成済み
   - 管理者ユーザー作成済み（`role: "admin"`）

2. **サーバー起動**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --port 8001
   ```

## 動作確認手順

### 1. API動作確認（自動テスト）

```bash
cd backend
source venv/bin/activate
python test_api.py
```

テストスクリプトが以下を確認します：
- ✅ ヘルスチェック
- ✅ ログイン
- ✅ ファイル一覧取得
- ✅ ファイルアップロード（オプション）
- ✅ ファイル削除（オプション）

### 2. APIドキュメント確認

ブラウザで以下にアクセス：
- http://localhost:8001/docs

各エンドポイントの詳細とテストが可能です。

### 3. フロントエンド動作確認

#### 3.1 ログイン画面

1. `frontend/admin/login.html` をブラウザで開く
2. 管理者のメールアドレスとパスワードを入力
3. 「ログイン」ボタンをクリック
4. 管理画面にリダイレクトされることを確認

#### 3.2 管理画面

1. ファイル一覧が表示されることを確認
2. 「ファイルを選択」でPDF/TXT/DOCXファイルを選択
3. 「アップロード」ボタンをクリック
4. アップロード成功メッセージが表示されることを確認
5. ファイル一覧に追加されたことを確認
6. 「削除」ボタンをクリック
7. 確認ダイアログで「OK」をクリック
8. ファイルが削除されることを確認

### 4. 手動APIテスト（curl）

#### 4.1 ログイン

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_password"}'
```

レスポンスから`access_token`を取得します。

#### 4.2 ファイル一覧取得

```bash
curl -X GET http://localhost:8001/admin/files \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4.3 ファイルアップロード

```bash
curl -X POST http://localhost:8001/admin/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/file.pdf"
```

#### 4.4 ファイル削除

```bash
curl -X DELETE http://localhost:8001/admin/files/FILE_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## トラブルシューティング

### ログインに失敗する

- Supabaseのユーザーが作成されているか確認
- ユーザーの`user_metadata`に`{"role": "admin"}`が設定されているか確認
- 環境変数（`.env`）が正しく設定されているか確認

### ファイルアップロードに失敗する

- Supabase Storageに「files」バケットが作成されているか確認
- ファイル形式がPDF/TXT/DOCXか確認
- Storageの権限設定を確認

### CORSエラーが発生する

- `backend/config.py`の`cors_origins`にフロントエンドのURLが含まれているか確認
- ブラウザのコンソールでエラーメッセージを確認

### ファイル削除後もStorageに残る

- データベースの削除は成功しているが、Storage削除でエラーが発生している可能性
- サーバーのログを確認

## 確認チェックリスト

- [ ] サーバーが起動している（http://localhost:8001/health）
- [ ] ログインが成功する
- [ ] ファイル一覧が取得できる
- [ ] ファイルがアップロードできる
- [ ] ファイルが削除できる
- [ ] フロントエンドのログイン画面が動作する
- [ ] フロントエンドの管理画面が動作する

