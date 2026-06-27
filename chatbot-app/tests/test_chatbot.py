import os
import sys
from streamlit.testing.v1 import AppTest

# chatbot-app ディレクトリを PYTHONPATH に追加して、utils 等のモジュールを解決できるようにします
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# テスト実行用のダミーAPIキーを設定
os.environ["GEMINI_API_KEY"] = "mock_gemini_api_key"

from utils.rag_service import RAGChatService

# テストで使用するモデル名（1_Chatbot.py の GEMINI_MODEL 定数と一致させる）
GEMINI_MODEL = "gemini-3.1-flash-lite"

def test_main_app_load():
    """main.py が例外を出さずに正常にロードされることをテスト"""
    at = AppTest.from_file("main.py", default_timeout=15)
    at.run()
    # アプリ実行中に発生した例外がないことを確認
    assert not at.exception

def test_chatbot_page_load():
    """pages/1_Chatbot.py が例外を出さずに正常にロードされることをテスト"""
    at = AppTest.from_file("pages/1_Chatbot.py", default_timeout=15)
    at.run()
    # アプリ実行中に発生した例外がないことを確認
    assert not at.exception
    
    # 特定の要素（タイトル文言）が正しく含まれているか確認
    title_found = False
    for md in at.markdown:
        if "勤怠管理Q&Aチャットボット" in md.value:
            title_found = True
            break
    assert title_found, "タイトルが表示されていません"

def test_rag_service_load():
    """RAGChatService クラスがPDFを正しく読み込み、初期化されることをテスト（単体テスト）"""
    # テスト対象のPDFパス（data/kintai_rule.pdf）を指定してインスタンス化
    service = RAGChatService("data/kintai_rule.pdf", GEMINI_MODEL)
    
    # 1. ページ数が正しく取得できているか（0より大きいか）
    assert service.max_pages > 0
    # 2. ページ境界線マーカーが正しくパースされ、pdf_contentに含まれているか
    assert "--- [ページ 1] ---" in service.pdf_content
    # 3. クライアントが正しく初期化されているか
    assert service.client is not None
