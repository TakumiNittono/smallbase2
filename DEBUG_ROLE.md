# 管理者ロール設定のデバッグガイド

## 問題: 「管理者権限が必要です」エラー

ログインは成功しているが、管理者画面にアクセスできない場合、ユーザーのロールが正しく設定されていない可能性があります。

## 確認手順

### 1. ブラウザのコンソールを確認

1. ブラウザで http://localhost:8001/admin/login を開く
2. 開発者ツールを開く（F12 または 右クリック → 検証）
3. 「Console」タブを開く
4. ログインを実行
5. コンソールに以下のようなログが表示されます：
   ```
   ログイン成功: {access_token: "...", user: {...}}
   ユーザー情報: {id: "...", email: "...", role: "..."}
   ロール: "user" または "admin"
   ```

### 2. サーバーのログを確認

ターミナルでサーバーのログを確認：
```
DEBUG - user_metadata: {...}
DEBUG - raw_user_meta_data: {...}
DEBUG - 取得したロール: user または admin
```

### 3. Supabaseでユーザーメタデータを確認

1. Supabaseダッシュボードにアクセス
2. 「Authentication」→「Users」を開く
3. ログインに使用したユーザーをクリック
4. 「User Metadata」セクションを確認

## 解決方法

### 方法1: Supabaseダッシュボードから設定（推奨）

1. Supabaseダッシュボードでユーザーを開く
2. 「User Metadata」セクションの「Edit」をクリック
3. 以下のJSONを入力：
   ```json
   {
     "role": "admin"
   }
   ```
4. 「Save」をクリック
5. 再度ログインを試す

### 方法2: SQLで直接設定

SupabaseのSQL Editorで以下のSQLを実行：

```sql
-- ユーザーのUUIDを確認（SupabaseダッシュボードのUsersから）
-- 例: '123e4567-e89b-12d3-a456-426614174000'

UPDATE auth.users 
SET raw_user_meta_data = '{"role": "admin"}'::jsonb 
WHERE email = 'your-email@example.com';
```

### 方法3: ユーザー作成時に設定

新しいユーザーを作成する際に、最初からメタデータを設定：

1. 「Add user」をクリック
2. ユーザー情報を入力
3. 「User Metadata」に以下を入力：
   ```json
   {
     "role": "admin"
   }
   ```
4. 「Create user」をクリック

## 確認方法

ロールが正しく設定されたか確認：

1. ブラウザのコンソールでログイン時のログを確認
2. `role: "admin"` と表示されていればOK
3. 管理画面にアクセスできるはずです

## トラブルシューティング

### ロールが "user" のままの場合

- Supabaseのメタデータが正しく保存されていない可能性があります
- ユーザーを一度削除して再作成するか、SQLで直接更新してください

### メタデータが空の場合

- Supabaseのバージョンや設定によって、`user_metadata`と`raw_user_meta_data`のどちらを使うかが異なる場合があります
- サーバーのログでどちらに値が入っているか確認してください

