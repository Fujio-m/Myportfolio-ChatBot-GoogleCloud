import os
import sys
from streamlit.testing.v1 import AppTest

# chatbot-app ディレクトリを PYTHONPATH に追加して、utils 等のモジュールを解決できるようにします
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

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
