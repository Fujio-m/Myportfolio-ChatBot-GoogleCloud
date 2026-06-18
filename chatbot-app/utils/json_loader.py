import streamlit as st
import json
from pathlib import Path

def load_url():
    """
    設定ファイルを読み込み、st.session_state.config に格納する
    既にロード済みの場合は何もしない
    """
    if "config" not in st.session_state:
        try:
            config_path = Path("assets/config.json")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    st.session_state.config = json.load(f)
            else:
                st.session_state.config = {}
        except Exception as e:
            st.error(f"設定の読み込み中にエラーが発生しました: {e}")
            st.session_state.config = {}

def get_url(key, default=""):
    """
    指定されたキーのURLを取得する。

    Args:
        key (str): 取得したいURLのキー名 (例: 'bpmn_io_url')
        default (str): 見つからなかった場合のデフォルト値
    """
    # 1. まずロードを確実に行う
    load_url()

    # 2. ロードされたデータから値を取り出す
    # 変数 key を使うため引用符は不要
    tool_links = st.session_state.config.get("tool_links", {})
    return tool_links.get(key, default)