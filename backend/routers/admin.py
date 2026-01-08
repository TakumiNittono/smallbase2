"""
管理者APIルーター
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel
from datetime import datetime
from auth import verify_admin
from supabase_client import get_supabase_client, get_supabase_service_client
from utils.text_extractor import extract_text, split_into_chunks
from utils.embedding import generate_embeddings_batch
import asyncio
import uuid
import os


router = APIRouter(prefix="/admin", tags=["管理者"])


class FileResponse(BaseModel):
    """ファイル情報レスポンス"""
    id: str
    filename: str
    created_at: datetime


class UploadResponse(BaseModel):
    """アップロードレスポンス"""
    id: str
    filename: str
    status: str


class DeleteResponse(BaseModel):
    """削除レスポンス"""
    status: str
    id: str


@router.get("/files", response_model=List[FileResponse])
async def get_files(
    user: dict = Depends(verify_admin)
):
    """
    ファイル一覧取得
    
    Args:
        user: 認証済みユーザー情報（管理者のみ）
        
    Returns:
        ファイル一覧
    """
    try:
        # サービスロールキーを使用してRLSをバイパス
        supabase = get_supabase_service_client()
        
        # filesテーブルから全件取得
        response = supabase.table("files").select("*").order("created_at", desc=True).execute()
        
        files = []
        for row in response.data:
            files.append(FileResponse(
                id=row["id"],
                filename=row["filename"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            ))
        
        return files
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ファイル一覧の取得に失敗しました: {str(e)}"
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(verify_admin)
):
    """
    ファイルアップロード
    
    Args:
        file: アップロードファイル
        user: 認証済みユーザー情報（管理者のみ）
        
    Returns:
        アップロード結果
    """
    # ファイル形式チェック
    allowed_extensions = {".pdf", ".txt", ".docx"}
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"サポートされていないファイル形式です。対応形式: PDF, TXT, DOCX"
        )
    
    try:
        supabase_service = get_supabase_service_client()
        
        # デバッグ: サービスロールキーが設定されているか確認
        from config import settings
        if not settings.supabase_service_key:
            raise HTTPException(
                status_code=500,
                detail="SUPABASE_SERVICE_KEYが設定されていません。.envファイルを確認してください。"
            )
        
        # ファイル内容を読み込み
        file_content = await file.read()
        
        # 重複チェック: 同じファイル名が既に存在するか確認
        existing_files = supabase_service.table("files").select("id, filename").eq("filename", file.filename).execute()
        if existing_files.data:
            raise HTTPException(
                status_code=400,
                detail=f"同じファイル名「{file.filename}」が既にアップロードされています。"
            )
        
        # Supabase Storageにアップロード
        # ファイル名をUUIDベースの安全な名前に変換（拡張子は保持）
        file_ext = os.path.splitext(file.filename)[1]  # 拡張子を取得
        safe_filename = f"{uuid.uuid4()}{file_ext}"  # UUID + 拡張子
        storage_path = f"files/{safe_filename}"
        try:
            storage_response = supabase_service.storage.from_("files").upload(
                storage_path,
                file_content,
                file_options={"content-type": file.content_type or "application/octet-stream"}
            )
            # レスポンスの確認（エラーがある場合は例外が発生する）
        except Exception as storage_error:
            # Storageアップロードエラーをキャッチ
            error_msg = str(storage_error)
            # 既に存在する場合は上書きを試みる
            if "duplicate" in error_msg.lower() or "already exists" in error_msg.lower():
                try:
                    supabase_service.storage.from_("files").update(
                        storage_path,
                        file_content,
                        file_options={"content-type": file.content_type or "application/octet-stream"}
                    )
                except Exception as update_error:
                    raise HTTPException(
                        status_code=500,
                        detail=f"ファイルのアップロードに失敗しました: {str(update_error)}"
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"ファイルのアップロードに失敗しました: {error_msg}"
                )
        
        # テキスト抽出
        try:
            text = extract_text(file_content, file.filename)
            if not text:
                raise HTTPException(
                    status_code=400,
                    detail="ファイルからテキストを抽出できませんでした"
                )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # チャンク分割
        chunks = split_into_chunks(text, chunk_size=500, overlap=100)
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="チャンク分割に失敗しました"
            )
        
        # データベースにファイル情報を保存（サービスロールキーを使用してRLSをバイパス）
        try:
            db_response = supabase_service.table("files").insert({
                "filename": file.filename
            }).execute()
        except Exception as e:
            # エラーの詳細をログ出力
            print(f"DEBUG - ファイル挿入エラー: {str(e)}")
            print(f"DEBUG - エラータイプ: {type(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"ファイル情報の保存に失敗しました: {str(e)}"
            )
        
        if not db_response.data:
            # データベース保存に失敗した場合、Storageからも削除
            try:
                supabase_service.storage.from_("files").remove([storage_path])
            except:
                pass
            raise HTTPException(
                status_code=500,
                detail="ファイル情報の保存に失敗しました"
            )
        
        file_id = db_response.data[0]["id"]
        
        # Embedding生成と保存（非同期で実行）
        try:
            # Embeddingを一括生成
            embeddings = generate_embeddings_batch(chunks)
            
            # チャンクとEmbeddingをデータベースに保存
            chunks_data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunks_data.append({
                    "file_id": file_id,
                    "content": chunk,
                    "embedding": embedding
                })
            
            # バッチで挿入（Supabaseの制限を考慮して100件ずつ）
            # サービスロールキーを使用してRLSをバイパス
            batch_size = 100
            for i in range(0, len(chunks_data), batch_size):
                batch = chunks_data[i:i + batch_size]
                supabase_service.table("chunks").insert(batch).execute()
            
        except Exception as e:
            # Embedding生成に失敗した場合、ファイルとチャンクを削除
            try:
                supabase_service.table("files").delete().eq("id", file_id).execute()
                supabase_service.storage.from_("files").remove([storage_path])
            except:
                pass
            raise HTTPException(
                status_code=500,
                detail=f"Embedding生成・保存に失敗しました: {str(e)}"
            )
        
        return UploadResponse(
            id=file_id,
            filename=file.filename,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ファイルのアップロード処理でエラーが発生しました: {str(e)}"
        )


@router.delete("/files/{file_id}", response_model=DeleteResponse)
async def delete_file(
    file_id: str,
    user: dict = Depends(verify_admin)
):
    """
    ファイル削除
    
    Args:
        file_id: ファイルID
        user: 認証済みユーザー情報（管理者のみ）
        
    Returns:
        削除結果
    """
    try:
        supabase_service = get_supabase_service_client()
        
        # ファイル情報を取得
        file_response = supabase_service.table("files").select("*").eq("id", file_id).execute()
        
        if not file_response.data:
            raise HTTPException(
                status_code=404,
                detail="ファイルが見つかりません"
            )
        
        filename = file_response.data[0]["filename"]
        storage_path = f"files/{filename}"
        
        # データベースから削除（CASCADEでchunksも自動削除）
        # サービスロールキーを使用してRLSをバイパス
        delete_response = supabase_service.table("files").delete().eq("id", file_id).execute()
        
        # Storageからも削除
        try:
            supabase_service.storage.from_("files").remove([storage_path])
        except Exception as e:
            # Storage削除に失敗してもデータベース削除は完了しているので警告のみ
            print(f"警告: Storageからのファイル削除に失敗しました: {str(e)}")
        
        return DeleteResponse(
            status="deleted",
            id=file_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ファイルの削除処理でエラーが発生しました: {str(e)}"
        )

