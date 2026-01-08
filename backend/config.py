"""
設定管理
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Supabase設定
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    
    # OpenAI設定
    openai_api_key: str = ""
    
    # アプリケーション設定
    environment: str = "development"
    cors_origins: Union[str, List[str]] = "http://localhost:3000,http://localhost:8080"
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """CORS originsを文字列からリストに変換"""
        if isinstance(v, str):
            # カンマで分割して、空白を削除
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 設定インスタンス
settings = Settings()

