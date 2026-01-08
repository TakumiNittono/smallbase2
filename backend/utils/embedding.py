"""
Embedding生成ユーティリティ
"""
from openai import OpenAI
from config import settings
from typing import List
import numpy as np


def get_openai_client() -> OpenAI:
    """
    OpenAIクライアントを取得
    
    Returns:
        OpenAIクライアント
    """
    return OpenAI(api_key=settings.openai_api_key)


def generate_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    テキストからEmbeddingを生成
    
    Args:
        text: テキスト
        model: 使用するモデル名
        
    Returns:
        Embeddingベクトル（リスト）
    """
    try:
        client = get_openai_client()
        
        response = client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.data[0].embedding
    except Exception as e:
        raise ValueError(f"Embedding生成に失敗しました: {str(e)}")


def generate_embeddings_batch(texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
    """
    複数のテキストからEmbeddingを一括生成
    
    Args:
        texts: テキストのリスト
        model: 使用するモデル名
        
    Returns:
        Embeddingベクトルのリスト
    """
    try:
        client = get_openai_client()
        
        response = client.embeddings.create(
            model=model,
            input=texts
        )
        
        return [item.embedding for item in response.data]
    except Exception as e:
        raise ValueError(f"Embedding一括生成に失敗しました: {str(e)}")

