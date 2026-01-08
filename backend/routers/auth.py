"""
認証ルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_client import get_supabase_client


router = APIRouter(prefix="/auth", tags=["認証"])


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """ログインレスポンス"""
    access_token: str
    user: dict


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    ログインエンドポイント
    
    Args:
        request: ログイン情報（email, password）
        
    Returns:
        アクセストークンとユーザー情報
        
    Raises:
        HTTPException: ログインに失敗した場合
    """
    try:
        supabase = get_supabase_client()
        
        # Supabase Authでログイン
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=401,
                detail="メールアドレスまたはパスワードが正しくありません"
            )
        
        # ユーザーメタデータからロールを取得
        user_metadata = response.user.user_metadata or {}
        raw_user_meta_data = getattr(response.user, 'raw_user_meta_data', {}) or {}
        
        # user_metadataまたはraw_user_meta_dataからロールを取得
        # ロールが設定されていない場合は、認証済みユーザーをすべて管理者として扱う
        role = user_metadata.get("role") or raw_user_meta_data.get("role", "admin")
        
        return LoginResponse(
            access_token=response.session.access_token,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "role": role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ログイン処理でエラーが発生しました: {str(e)}"
        )

