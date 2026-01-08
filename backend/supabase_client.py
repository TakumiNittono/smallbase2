"""
Supabaseクライアント設定
"""
from supabase import create_client, Client
from config import settings


def get_supabase_client() -> Client:
    """Supabaseクライアントを取得"""
    return create_client(settings.supabase_url, settings.supabase_key)


def get_supabase_service_client() -> Client:
    """Supabaseサービスロールクライアントを取得（管理者操作用）"""
    if not settings.supabase_service_key:
        raise ValueError("SUPABASE_SERVICE_KEYが設定されていません。.envファイルを確認してください。")
    
    # サービスロールキーの形式確認（eyJで始まるJWTトークン、またはsb_secret_で始まる新しい形式）
    if not (settings.supabase_service_key.startswith("eyJ") or settings.supabase_service_key.startswith("sb_secret_")):
        print(f"警告: SUPABASE_SERVICE_KEYの形式が標準的ではありません。")
        print(f"現在の値: {settings.supabase_service_key[:30]}...")
        print("動作確認が必要です。")
    
    return create_client(settings.supabase_url, settings.supabase_service_key)

