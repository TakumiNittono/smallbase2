"""
認証・認可機能
"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_client import get_supabase_client


security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    JWTトークンを検証し、ユーザー情報を返す
    
    Args:
        credentials: Bearerトークン
        
    Returns:
        ユーザー情報（id, email, role等）
        
    Raises:
        HTTPException: トークンが無効な場合
    """
    token = credentials.credentials
    
    try:
        # Supabaseクライアントを取得
        supabase = get_supabase_client()
        
        # トークンでセッションを設定してユーザー情報を取得
        # SupabaseのJWTトークンはaccess_tokenとして使用
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(
                status_code=401,
                detail="認証に失敗しました"
            )
        
        # ユーザーメタデータからロールを取得
        user_metadata = response.user.user_metadata or {}
        role = user_metadata.get("role", "user")
            
        return {
            "id": response.user.id,
            "email": response.user.email,
            "role": role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"認証に失敗しました: {str(e)}"
        )


async def verify_admin(
    user: dict = Depends(verify_token)
) -> dict:
    """
    管理者権限をチェック
    
    注意: 現在は認証済みユーザー全員を管理者として扱います
    
    Args:
        user: ユーザー情報
        
    Returns:
        ユーザー情報
        
    Raises:
        HTTPException: 認証に失敗した場合
    """
    # 一時的に認証済みユーザー全員を管理者として扱う
    # ロールチェックは行わない
    return user

