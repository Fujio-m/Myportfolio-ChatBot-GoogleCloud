import os
import time
from typing import Optional, List, Any
from pypdf import PdfReader
from google import genai
from google.genai import types
import streamlit as st


# rag_service.py - RAGサービス & Gemini API連携
#
#【設計意図】
# 1. 責務の分離:
#    PDFの読み込み・テキスト抽出・API呼び出しをUIレイヤー(1_Chatbot.py)から切り離し、
#    単一責任の原則に従ったサービスクラスとして実装。
# 2. 耐障害性:
#    503(サーバー過負荷)・429(レート制限)エラーに対して指数バックオフ付きの
#    自動リトライを実装し、一時的な障害時のUXを向上。
# 3. キャッシュ戦略:
#    @st.cache_resource によりインスタンスをシングルトン管理し、
#    PDF読み込みとAPIクライアント初期化の重複処理を防止。


class RAGChatService:
    """
    RAG (Retrieval-Augmented Generation) チャットボットの
    データ処理とAPI連携を管理するサービスクラス。

    PDFからテキストを抽出し、Gemini APIへのリクエスト送信・
    エラーハンドリング・自動リトライを一元管理する。
    """

    def __init__(self, pdf_path: str, model_name: str):
        """
        Args:
            pdf_path (str): RAGの参照元となるPDFファイルのパス。
            model_name (str): 使用するGeminiモデルの名称。
        """
        self.pdf_path = pdf_path
        self.model_name = model_name
        self.client = self._init_ai_client()
        self.pdf_content = self._load_pdf_text()
        self.max_pages = self._load_pdf_page_count()

    def _init_ai_client(self) -> genai.Client:
        """
        Gemini APIクライアントを初期化する。

        APIキーの取得を以下の優先順位で試みる。
        1. 環境変数 GEMINI_API_KEY (Docker / Cloud Run 本番環境用)
        2. Streamlit Secrets (ローカル開発環境用)

        Returns:
            genai.Client: 初期化済みのGemini APIクライアント。

        Raises:
            st.stop(): APIキーが見つからない場合、アプリを停止する。
        """
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
        """
        PDFファイルからテキストを抽出し、ページ番号付きの文字列として返す。

        抽出されたテキストはシステムプロンプトへ注入され、
        AIが参照するナレッジベースとして機能する。

        Returns:
            str: 各ページの内容を「--- [ページ N] ---」で区切った文字列。
                 読み込みに失敗した場合は None。
        """
        try:
            text = ""
            reader = PdfReader(self.pdf_path)
            for i, page in enumerate(reader.pages):
                page_num = i + 1
                # ページ番号を付与してAIが参照箇所を特定しやすくする
                text += f"--- [ページ {page_num}] ---\n"
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"PDFの解析中にエラーが発生しました: {e}")
            return None

    def _load_pdf_page_count(self) -> int:
        """
        PDFファイルの総ページ数を返す。

        チャットUI側でページ番号の有効範囲を検証するために使用する。

        Returns:
            int: PDFの総ページ数。読み込みに失敗した場合は 0。
        """
        try:
            reader = PdfReader(self.pdf_path)
            return len(reader.pages)
        except Exception:
            return 0

    def get_gemini_answer(self, final_prompt: str, chat_history: List[Any], base_instruction: str) -> Optional[str]:
        """
        Gemini APIにリクエストを送信し、AIの回答テキストを返す。

        503(サーバー過負荷)・429(レート制限)エラーが発生した場合は
        指数バックオフ(1秒→2秒)で最大3回まで自動リトライする。
        全試行が失敗した場合のみエラーメッセージを1件表示する。

        Args:
            final_prompt (str): ユーザーの入力テキスト。
            chat_history (List[Any]): これまでの会話履歴 (google.genai.types.Content のリスト)。
            base_instruction (str): {{PDF_CONTENT}} プレースホルダーを含むシステムプロンプト。

        Returns:
            str: Gemini APIが生成した回答テキスト。
                 全試行失敗またはリトライ不要エラーの場合は None。
        """
        # システムプロンプトのプレースホルダーにPDF全文を注入
        final_instruction = base_instruction.replace("{{PDF_CONTENT}}", self.pdf_content or "")

        MAX_RETRIES = 3                    # 最大リトライ回数
        RETRYABLE_ERRORS = ["503", "429"]  # 自動リトライ対象のエラーコード

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=chat_history + [final_prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=final_instruction,
                        temperature=0.1,
                    )
                )
                return response.text  # 成功したら即返す

            except Exception as e:
                error_msg = str(e)
                is_last_attempt = (attempt == MAX_RETRIES - 1)

                # ── リトライ可能なエラー（503・429）────────────────────
                if any(code in error_msg for code in RETRYABLE_ERRORS):
                    if not is_last_attempt:
                        wait_seconds = 2 ** attempt  # 1秒 → 2秒（指数バックオフ）
                        time.sleep(wait_seconds)
                        continue  # リトライ（メッセージはスピナー側で一元管理）
                    else:
                        # 全試行失敗時のみ1件だけエラーを表示
                        if "503" in error_msg:
                            st.error("☁️ Googleのサーバーが大変混み合っています。しばらく待ってから再度お試しください。")
                        else:
                            st.warning("⚠️ API制限（リクエスト過多）が発生しました。1分ほど待ってから再度お試しください。")

                # ── リトライ不要なエラー（400等）────────────────────────
                elif "400" in error_msg:
                    st.error("⚠️ 送信データに不備があります（二重送信や空のデータ）。一度ページをリロードして再度お試しください。")
                else:
                    st.error(f"予期せぬエラーが発生しました: {error_msg}")

                return None  # リトライ不要エラー or 全試行失敗

        return None  # 念のため（到達しないが安全のため）


@st.cache_resource
def get_rag_service(pdf_path: str, model_name: str) -> RAGChatService:
    """
    RAGChatServiceのシングルトンインスタンスをキャッシュ経由で取得・初期化する。

    @st.cache_resource によりアプリ起動中はインスタンスを使い回し、
    PDF読み込みとAPIクライアント初期化の重複処理を防ぐ。

    Args:
        pdf_path (str): RAGの参照元となるPDFファイルのパス。
        model_name (str): 使用するGeminiモデルの名称。

    Returns:
        RAGChatService: 初期化済みのRAGChatServiceインスタンス。
    """
    return RAGChatService(pdf_path, model_name)
