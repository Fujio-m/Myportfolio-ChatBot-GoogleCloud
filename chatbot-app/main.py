import streamlit as st

# main.py
#
#【プロジェクト概要とナビゲーション設計】
#  本プロジェクトは、実務における「就業規則の参照コスト削減」と「自己解決率の向上」を目的とした
#  RAG（検索拡張生成）チャットボットのポートフォリオです。

# アプリのページ設定
st.set_page_config(
    page_title="勤怠管理AIチャットボット",
    layout="wide",
    page_icon="💼"
)

# ナビゲーションの定義
pg = st.navigation([
    st.Page("pages/1_Chatbot.py", title="AIチャットボット", icon=":material/smart_toy:", default=True),
    st.Page("pages/2_Evaluation.py", title="精度評価・テスト", icon=":material/biotech:")
])

pg.run()
