"""
Smallbase MVP - FastAPI アプリケーション
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from routers import auth, admin, chat
import os

# 環境変数の読み込み
load_dotenv()

# 設定のインポート（環境変数が設定されていない場合でもエラーにならないように）
try:
    from config import settings
    cors_origins = settings.cors_origins
except Exception:
    # 環境変数が設定されていない場合はデフォルト値を使用
    cors_origins = ["http://localhost:3000", "http://localhost:8080"]

app = FastAPI(
    title="Smallbase MVP API",
    description="管理者画面付き・最小RAG構成のAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信（フロントエンド）
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ルーター登録
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "healthy"}


# フロントエンドルート
@app.get("/")
async def root_page():
    """ユーザー用RAG画面"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Smallbase MVP API", "status": "running"}


@app.get("/admin")
async def admin_page():
    """管理者画面"""
    admin_file = os.path.join(frontend_path, "admin", "index.html")
    if os.path.exists(admin_file):
        return FileResponse(admin_file)
    return {"error": "Admin page not found"}


@app.get("/admin/login")
async def admin_login_page():
    """管理者ログイン画面"""
    login_file = os.path.join(frontend_path, "admin", "login.html")
    if os.path.exists(login_file):
        return FileResponse(login_file)
    return {"error": "Login page not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

