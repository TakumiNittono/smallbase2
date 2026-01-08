# RLSエラー修正ガイド

## 問題の原因

エラーメッセージ「new row violates row-level security policy」が発生する主な原因：

1. **サービスロールキーが正しく設定されていない**
   - `SUPABASE_SERVICE_KEY`がanonキーになっている可能性
   - サービスロールキーは`eyJ`で始まるJWTトークン

2. **RLSポリシーが設定されていない**
   - SupabaseのテーブルにRLSポリシーが必要

## 解決方法

### ステップ1: サービスロールキーを確認・設定

1. Supabaseダッシュボードにアクセス
2. 「Settings」→「API」を開く
3. 「Project API keys」セクションを確認
4. **`service_role`キー**をコピー（⚠️ これは秘密鍵です）
   - 通常`eyJ`で始まるJWTトークン
   - `sb_publishable_`で始まるものはanonキー（公開キー）です

5. `backend/.env`ファイルを編集：
   ```env
   SUPABASE_SERVICE_KEY=eyJ...（サービスロールキーを貼り付け）
   ```

### ステップ2: サーバーを再起動

環境変数を変更したら、サーバーを再起動してください：

```bash
# サーバーを停止（Ctrl+C）
# その後、再起動
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

### ステップ3: RLSポリシーを設定（オプション）

サービスロールキーを使う場合は不要ですが、セキュリティのため設定を推奨：

1. Supabaseダッシュボードの「SQL Editor」を開く
2. `docs/setup_rls.sql`の内容を実行

## 確認方法

環境変数が正しく設定されているか確認：

```bash
cd backend
source venv/bin/activate
python check_env.py
```

`SUPABASE_SERVICE_KEY`が`eyJ`で始まっていることを確認してください。

## よくある間違い

❌ **間違い**: `SUPABASE_SERVICE_KEY=sb_publishable_...`（これはanonキー）
✅ **正しい**: `SUPABASE_SERVICE_KEY=eyJ...`（サービスロールキー）

## トラブルシューティング

### まだエラーが発生する場合

1. **サーバーを完全に再起動**
   - ターミナルでCtrl+Cで停止
   - 再度起動

2. **環境変数の確認**
   ```bash
   python check_env.py
   ```

3. **Supabaseの設定確認**
   - サービスロールキーが正しいか確認
   - プロジェクトがアクティブか確認

4. **サーバーのログを確認**
   - エラーの詳細を確認
   - スタックトレースを確認

