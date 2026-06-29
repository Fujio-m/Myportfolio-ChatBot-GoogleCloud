import json
import streamlit as st
from pathlib import Path


# json_loader.py - config.json の読み込みユーティリティ
#
#【設計意図】
# 単一責任原則に従い、config.json の読み込み責務をUIレイヤー（1_Chatbot.py）から分離。
# @st.cache_data によりアプリ起動中はファイルI/Oを1回のみ行い、パフォーマンスを最適化。

CONFIG_PATH = Path("assets/config.json")


@st.cache_data
def load_config() -> dict:
    """
    assets/config.json を読み込み、設定データを辞書として返す。
    @st.cache_data により初回のみファイルを読み込み、以降はキャッシュを返す。

    Returns:
        dict: config.json の内容。読み込み失敗時は空の辞書を返す。

    Raises:
        FileNotFoundError: ファイルが存在しない場合（エラーとして通知し空辞書を返す）。
        json.JSONDecodeError: JSONの構文エラーがある場合（エラーとして通知し空辞書を返す）。
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"設定ファイルが見つかりません: {CONFIG_PATH}")
        return {}
    except json.JSONDecodeError:
        st.error("config.json の形式が正しくありません。")
        return {}


def get_form_url(default: str = "") -> str:
    """
    config.json から問い合わせフォームの URL を取得する。

    Args:
        default (str): 設定が存在しない場合のデフォルト値。

    Returns:
        str: google_form_url の値。存在しない場合は default を返す。
    """
    config = load_config()
    return config.get("google_form_url", default)
