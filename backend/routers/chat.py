"""
RAG質問APIルーター
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from supabase_client import get_supabase_service_client
from utils.embedding import generate_embedding
from openai import OpenAI
from config import settings


router = APIRouter(prefix="/chat", tags=["RAG質問"])


class ChatRequest(BaseModel):
    """チャットリクエスト"""
    question: str


class Source(BaseModel):
    """参照元情報"""
    file_id: str
    filename: str
    chunk_id: str
    content: str


class ChatResponse(BaseModel):
    """チャットレスポンス"""
    answer: str
    sources: List[Source]


def get_openai_client() -> OpenAI:
    """OpenAIクライアントを取得"""
    return OpenAI(api_key=settings.openai_api_key)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG質問エンドポイント
    
    Args:
        request: 質問内容
        
    Returns:
        回答と参照元情報
    """
    try:
        # サービスロールキーを使用してRLSをバイパス
        supabase = get_supabase_service_client()
        
        # 質問文のEmbedding生成
        question_embedding = generate_embedding(request.question)
        
        # pgvectorで類似度検索（コサイン類似度）
        # SupabaseのPostgreSQLでベクトル検索を実行
        # 注意: SupabaseのPythonクライアントでは直接SQLを実行する必要がある
        
        # 類似度検索用のSQLクエリ
        # 1 - (embedding <=> question_embedding) でコサイン距離を計算
        # <=> はpgvectorのコサイン距離演算子
        
        # SupabaseのRPC（Remote Procedure Call）を使用するか、
        # または直接SQLを実行する必要があります
        # ここでは、SupabaseのPostgreSQL関数を使用する方法を採用
        
        # まず、一時的にすべてのチャンクを取得してPython側で類似度計算
        # 本番環境では、PostgreSQLの関数を使用することを推奨
        
        # 全チャンクを取得（サービスロールキーを使用してRLSをバイパス）
        # ファイル名も取得するためにfilesテーブルとJOIN
        chunks_response = supabase.table("chunks").select("id, file_id, content, embedding, files!inner(filename)").execute()
        
        if not chunks_response.data:
            raise HTTPException(
                status_code=404,
                detail="ナレッジベースが空です。まずファイルをアップロードしてください。"
            )
        
        # コサイン類似度を計算してソート
        import numpy as np
        import json
        
        similarities = []
        for chunk in chunks_response.data:
            chunk_embedding = chunk["embedding"]
            
            # embeddingが文字列の場合はリストに変換
            if isinstance(chunk_embedding, str):
                try:
                    chunk_embedding = json.loads(chunk_embedding)
                except:
                    # JSONパースに失敗した場合はスキップ
                    continue
            
            # リストをnumpy配列に変換
            chunk_embedding = np.array(chunk_embedding, dtype=np.float32)
            question_embedding_array = np.array(question_embedding, dtype=np.float32)
            
            # コサイン類似度を計算
            similarity = np.dot(question_embedding_array, chunk_embedding) / (
                np.linalg.norm(question_embedding_array) * np.linalg.norm(chunk_embedding)
            )
            similarities.append({
                "chunk": chunk,
                "similarity": float(similarity)
            })
        
        # 類似度でソート（降順）
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 上位3件を取得
        top_chunks = similarities[:3]
        
        if not top_chunks:
            raise HTTPException(
                status_code=404,
                detail="関連するチャンクが見つかりませんでした"
            )
        
        # プロンプトを構築
        context = "\n\n".join([
            f"[チャンク {i+1}]\n{chunk['chunk']['content']}"
            for i, chunk in enumerate(top_chunks)
        ])
        
        prompt = f"""以下のコンテキストを参考に、質問に回答してください。

コンテキスト:
{context}

質問: {request.question}

回答:"""
        
        # OpenAI Chat APIで回答生成
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは質問に対して、提供されたコンテキストを参考に正確で有用な回答を提供するアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # 参照元情報を構築
        sources = []
        for chunk in top_chunks:
            chunk_data = chunk["chunk"]
            file_id = chunk_data["file_id"]
            
            # ファイル名を取得
            filename = "不明"
            try:
                # filesテーブルからJOINで取得したファイル名を使用
                if "files" in chunk_data:
                    files_data = chunk_data["files"]
                    if isinstance(files_data, list) and len(files_data) > 0:
                        filename = files_data[0].get("filename", "不明")
                    elif isinstance(files_data, dict):
                        filename = files_data.get("filename", "不明")
                
                # ファイル名が取得できない場合は、別途取得を試みる
                if filename == "不明":
                    file_response = supabase.table("files").select("filename").eq("id", file_id).limit(1).execute()
                    if file_response.data and len(file_response.data) > 0:
                        filename = file_response.data[0].get("filename", "不明")
            except Exception as e:
                # エラーが発生した場合はファイル名を取得できないが続行
                print(f"ファイル名取得エラー: {str(e)}")
            
            sources.append(Source(
                file_id=file_id,
                filename=filename,
                chunk_id=chunk_data["id"],
                content=chunk_data["content"][:200] + "..." if len(chunk_data["content"]) > 200 else chunk_data["content"]
            ))
        
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"質問処理でエラーが発生しました: {str(e)}"
        )

