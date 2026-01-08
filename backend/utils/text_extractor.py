"""
テキスト抽出・チャンク分割ユーティリティ
"""
import PyPDF2
from docx import Document
from typing import List
import io


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    PDFからテキストを抽出
    
    Args:
        file_content: PDFファイルのバイト列
        
    Returns:
        抽出されたテキスト
    """
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise ValueError(f"PDFのテキスト抽出に失敗しました: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """
    DOCXからテキストを抽出
    
    Args:
        file_content: DOCXファイルのバイト列
        
    Returns:
        抽出されたテキスト
    """
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        raise ValueError(f"DOCXのテキスト抽出に失敗しました: {str(e)}")


def extract_text_from_txt(file_content: bytes) -> str:
    """
    TXTからテキストを抽出
    
    Args:
        file_content: TXTファイルのバイト列
        
    Returns:
        抽出されたテキスト
    """
    try:
        # UTF-8でデコードを試みる
        text = file_content.decode('utf-8')
        return text.strip()
    except UnicodeDecodeError:
        # UTF-8で失敗した場合はShift-JISを試す
        try:
            text = file_content.decode('shift-jis')
            return text.strip()
        except Exception as e:
            raise ValueError(f"TXTのテキスト抽出に失敗しました: {str(e)}")


def extract_text(file_content: bytes, filename: str) -> str:
    """
    ファイル形式に応じてテキストを抽出
    
    Args:
        file_content: ファイルのバイト列
        filename: ファイル名（拡張子から形式を判定）
        
    Returns:
        抽出されたテキスト
    """
    file_ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if file_ext == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_ext == "docx":
        return extract_text_from_docx(file_content)
    elif file_ext == "txt":
        return extract_text_from_txt(file_content)
    else:
        raise ValueError(f"サポートされていないファイル形式: {file_ext}")


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    テキストをチャンクに分割
    
    Args:
        text: 分割するテキスト
        chunk_size: チャンクサイズ（文字数）
        overlap: オーバーラップサイズ（文字数）
        
    Returns:
        チャンクのリスト
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # チャンクを取得
        chunk = text[start:end]
        
        # チャンクが空でない場合のみ追加
        if chunk.strip():
            chunks.append(chunk.strip())
        
        # 次の開始位置を計算（オーバーラップを考慮）
        start = end - overlap
        
        # 無限ループを防ぐ
        if start >= len(text):
            break
    
    return chunks

