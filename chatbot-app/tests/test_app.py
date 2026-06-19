import os
import sys
from streamlit.testing.v1 import AppTest

# chatbot-app ディレクトリを PYTHONPATH に追加して、utils 等のモジュールを解決できるようにします
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# テスト実行用のダミーAPIキーを設定
os.environ["GEMINI_API_KEY"] = "mock_gemini_api_key_for_testing_12345"

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

def test_evaluation_page_load():
    """pages/2_Evaluation.py が例外を出さずに正常にロードされることをテスト"""
    at = AppTest.from_file("pages/2_Evaluation.py", default_timeout=15)
    at.run()
    # アプリ実行中に発生した例外がないことを確認
    assert not at.exception
    
    # 精度評価のタイトルが含まれているか判定します
    title_found = False
    for md in at.markdown:
        if "精度評価・テスト結果" in md.value:
            title_found = True
            break
    assert title_found, "精度評価のタイトルが表示されていません"
