-- pgvector拡張有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- filesテーブル作成
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- chunksテーブル作成
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);

-- ベクトル検索用インデックス作成
-- 注意: データが少ない場合はエラーになる可能性があります
-- データが追加されてから作成することを推奨
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- file_idインデックス（削除時のパフォーマンス向上）
CREATE INDEX IF NOT EXISTS chunks_file_id_idx ON chunks(file_id);

-- 確認用クエリ
-- SELECT * FROM files;
-- SELECT * FROM chunks LIMIT 10;

