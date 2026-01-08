-- Row Level Security (RLS) ポリシー設定
-- SupabaseのRLSを有効化し、適切なポリシーを設定

-- filesテーブルのRLS設定
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- filesテーブル: 認証済みユーザーは全員読み取り可能
CREATE POLICY "認証済みユーザーは全員読み取り可能"
ON files FOR SELECT
TO authenticated
USING (true);

-- filesテーブル: 認証済みユーザーは全員挿入可能
CREATE POLICY "認証済みユーザーは全員挿入可能"
ON files FOR INSERT
TO authenticated
WITH CHECK (true);

-- filesテーブル: 認証済みユーザーは全員削除可能
CREATE POLICY "認証済みユーザーは全員削除可能"
ON files FOR DELETE
TO authenticated
USING (true);

-- chunksテーブルのRLS設定
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

-- chunksテーブル: 認証済みユーザーは全員読み取り可能
CREATE POLICY "認証済みユーザーは全員読み取り可能"
ON chunks FOR SELECT
TO authenticated
USING (true);

-- chunksテーブル: 認証済みユーザーは全員挿入可能
CREATE POLICY "認証済みユーザーは全員挿入可能"
ON chunks FOR INSERT
TO authenticated
WITH CHECK (true);

-- chunksテーブル: 認証済みユーザーは全員削除可能
CREATE POLICY "認証済みユーザーは全員削除可能"
ON chunks FOR DELETE
TO authenticated
USING (true);

-- 注意: サービスロールキーを使用している場合は、RLSをバイパスできます
-- しかし、セキュリティのため、認証済みユーザー用のポリシーも設定することを推奨します

