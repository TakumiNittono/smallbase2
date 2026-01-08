"""
環境変数の確認スクリプト
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("環境変数チェック")
print("=" * 50)

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")

print(f"SUPABASE_URL: {'設定済み' if supabase_url else '❌ 未設定'}")
if supabase_url:
    print(f"  → {supabase_url[:30]}...")

print(f"\nSUPABASE_KEY: {'設定済み' if supabase_key else '❌ 未設定'}")
if supabase_key:
    print(f"  → {supabase_key[:20]}...")

print(f"\nSUPABASE_SERVICE_KEY: {'設定済み' if supabase_service_key else '❌ 未設定'}")
if supabase_service_key:
    print(f"  → {supabase_service_key[:20]}...")
else:
    print("  ⚠️  サービスロールキーが設定されていません！")
    print("  Supabaseダッシュボードの「Settings」→「API」から取得してください。")

print(f"\nOPENAI_API_KEY: {'設定済み' if openai_api_key else '❌ 未設定'}")
if openai_api_key:
    print(f"  → {openai_api_key[:20]}...")

print("\n" + "=" * 50)
if not supabase_service_key:
    print("⚠️  SUPABASE_SERVICE_KEYが設定されていないため、RLSエラーが発生します。")
    print("   .envファイルに設定を追加してください。")
else:
    print("✅ すべての環境変数が設定されています。")

