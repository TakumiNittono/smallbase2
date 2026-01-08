# ログイン方法ガイド

## 管理者ユーザーの作成手順

### 1. Supabaseダッシュボードでユーザーを作成

1. [Supabase](https://supabase.com/)にアクセスしてログイン
2. プロジェクトを選択
3. 左メニューから「Authentication」をクリック
4. 「Users」タブを選択
5. 「Add user」ボタンをクリック

### 2. ユーザー情報を入力

以下の情報を入力：
- **Email**: 管理者のメールアドレス（例: `admin@example.com`）
- **Password**: パスワード（8文字以上）
- **Auto Confirm User**: ✅ チェックを入れる（自動確認）

「Create user」をクリック

### 3. 管理者ロールを設定

作成したユーザーをクリックして詳細を開く

1. 「User Metadata」セクションを確認
2. 「Edit」ボタンをクリック
3. 以下のJSONを入力：

```json
{
  "role": "admin"
}
```

4. 「Save」をクリック

### 4. ログイン画面でログイン

1. ブラウザで http://localhost:8001/admin/login を開く
2. 作成したメールアドレスとパスワードを入力
3. 「ログイン」ボタンをクリック

## トラブルシューティング

### ログインに失敗する場合

#### 1. ユーザーが作成されているか確認
- Supabaseダッシュボードの「Authentication」→「Users」で確認

#### 2. 管理者ロールが設定されているか確認
- ユーザーの「User Metadata」に `{"role": "admin"}` が設定されているか確認
- 設定されていない場合は、上記の手順3を実行

#### 3. 環境変数が正しく設定されているか確認
- `backend/.env`ファイルに以下が設定されているか確認：
  ```
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your_anon_key_here
  ```

#### 4. サーバーが起動しているか確認
- ターミナルでサーバーが起動しているか確認
- http://localhost:8001/health にアクセスして確認

### エラーメッセージ別の対処法

#### "認証に失敗しました"
- メールアドレスとパスワードが正しいか確認
- Supabaseのプロジェクトがアクティブか確認

#### "管理者権限が必要です"
- ユーザーの`user_metadata`に`role: "admin"`が設定されているか確認
- Supabaseダッシュボードで再確認

#### CORSエラー
- ブラウザのコンソールでエラーを確認
- `backend/config.py`の`cors_origins`を確認

## テスト用ユーザー作成（SQL）

SupabaseのSQL Editorで以下のSQLを実行して、テスト用ユーザーを作成することもできます：

```sql
-- 注意: この方法は本番環境では推奨されません
-- テスト環境でのみ使用してください

-- ユーザーを作成（Supabase Authを使用する場合は、ダッシュボードから作成することを推奨）
-- ユーザーはSupabaseダッシュボードから作成し、以下のSQLでメタデータを更新

-- ユーザーのUUIDを取得（SupabaseダッシュボードのUsersから確認）
-- 例: UPDATE auth.users SET raw_user_meta_data = '{"role": "admin"}'::jsonb WHERE id = 'ユーザーのUUID';
```

## 確認チェックリスト

ログイン前に以下を確認してください：

- [ ] Supabaseプロジェクトが作成されている
- [ ] ユーザーが作成されている
- [ ] ユーザーの`user_metadata`に`{"role": "admin"}`が設定されている
- [ ] `backend/.env`ファイルにSupabaseの設定が記入されている
- [ ] サーバーが起動している（http://localhost:8001/health が動作する）
- [ ] ブラウザで http://localhost:8001/admin/login にアクセスできる

