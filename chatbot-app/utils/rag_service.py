import os
from typing import Optional, List, Any
from pypdf import PdfReader
from google import genai
from google.genai import types
import streamlit as st

class RAGChatService:
    """
    RAG (Retrieval-Augmented Generation) チャットボットのデータ処理とAPI連携を管理するサービス。
    """
    def __init__(self, pdf_path: str, model_name: str):
        self.pdf_path = pdf_path
        self.model_name = model_name
        self.client = self._init_ai_client()
        self.pdf_content = self._load_pdf_text()
        self.max_pages = self._load_pdf_page_count()

    def _init_ai_client(self) -> genai.Client:
        # 1. 環境変数 (Docker/Cloud Run用) から取得を試みる
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # 2. なければ Streamlit Secrets (ローカル開発用) から取得を試みる
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
                
        if not api_key:
            st.error("APIキーが見つかりません。環境変数 'GEMINI_API_KEY'を設定してください。")
            st.stop()
            
        return genai.Client(api_key=api_key)

    def _load_pdf_text(self) -> Optional[str]:
        try:
            text = ""
            reader = PdfReader(self.pdf_path)
            for i, page in enumerate(reader.pages):
                page_num = i + 1
                text += f"--- [ページ {page_num}] ---\n"
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"PDFの解析中にエラーが発生しました: {e}")
            return None

    def _load_pdf_page_count(self) -> int:
        try:
            reader = PdfReader(self.pdf_path)
            return len(reader.pages)
        except Exception:
            return 0

    def get_gemini_answer(self, final_prompt: str, chat_history: List[Any], base_instruction: str) -> Optional[str]:
        # システムプロンプトにPDF内容を埋め込み
        final_instruction = base_instruction.replace("{{PDF_CONTENT}}", self.pdf_content or "")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=chat_history + [final_prompt],
                config=types.GenerateContentConfig(
                    system_instruction=final_instruction,
                    temperature=0.1,
                )
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                st.warning("⚠️ API制限（リクエスト過多）が発生しました。1分ほど待ってから再度お試しください。")
            elif "503" in error_msg:
                st.error("☁️ 現在Googleのサーバーが大変混み合っています。少し時間をおいてから再度お試しください。")
            elif "400" in error_msg:
                st.error("⚠️ 送信データに不備があります（二重送信や空のデータ）。一度ページをリロードして再度お試しください。")
            else:
                st.error(f"予期せぬエラーが発生しました: {error_msg}")
            return None

@st.cache_resource
def get_rag_service(pdf_path: str, model_name: str) -> RAGChatService:
    """RAGChatServiceのシングルトンインスタンスをキャッシュ経由で取得・初期化する。"""
    return RAGChatService(pdf_path, model_name)
