import os
import json
from typing import Optional, Tuple, Dict, Any
import streamlit as st
from google import genai
from google.genai import types
from pathlib import Path
from pypdf import PdfReader
from streamlit_pdf_viewer import pdf_viewer
from utils.responsive import inject_responsive_css, responsive_title, responsive_header


# 3_Chatbot.py - - RAG & チャットUI
#
#【設計意図】
# 1. RAG実装:
#    就業規則PDFを抽出・注入し、Gemini APIによる「根拠ある回答」を実現。
# 2. 実務的なUX設計:
#    FAQボタン、解決/未解決フィードバック、外部フォーム連携を統合。
# 3. エラーハンドリング:
#    API制限(429)やサーバーダウン(503)を想定した例外処理を実装。

# --- 定数定義 ---
PDF_PATH = "data/kintai_rule.pdf"
GUIDE_PATH = "assets/usage_guide.md"
GEMINI_MODEL = "gemini-2.5-flash-lite"

FEEDBACK_RESOLVED = "解決しました"
FEEDBACK_UNRESOLVED = "解決してません"

# ---  メソッド定義 (UIパーツ) ---
def load_app_settings() -> Tuple[str, Dict[str, Any]]:
    """
    外部ファイルからシステムプロンプトとアプリケーション設定を読み込む。

    Returns:
        tuple: (load_instruction, config)
            - load_instruction (str): AIの振る舞いを定義するシステムプロンプト。
            - config (dict): 問い合わせフォームのURL等を含む設定データ。

    Raises:
        FileNotFoundError: 設定ファイルが存在しない場合。
        json.JSONDecodeError: JSONの構文エラーがある場合。
    """
    try:
        # プロンプトの読み込み
        prompt_path = Path("assets/system_prompt.md")
        load_instruction = prompt_path.read_text(encoding="utf-8")

        # 申請フォームの設定の読み込み
        config_path = Path("assets/config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return load_instruction, config
    
    except FileNotFoundError as e:
        st.error(f"設定ファイルが見つかりません: {e.filename}")
        st.stop() # アプリの実行を安全に停止
    except json.JSONDecodeError:
        st.error("config.json の形式が正しくありません。")
        st.stop()
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
        st.stop()

@st.dialog("📄 勤怠ルールpdf")
def show_pdf_dialog(pdf_path: str):
    """
    ポップアップダイアログ内にPDFを表示する。

    Args:
        pdf_path (str/Path): 読み込むPDFファイルのパス。
    """
    try:
        if not os.path.exists(pdf_path):
            st.error("表示するPDFファイルが見つかりません。")
            return

        # PDFの読み込み
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.write("AIの回答根拠となる規定の原本PDFです")

        # PDFの表示
        pdf_viewer(input=pdf_bytes)

    except Exception as e:
        st.error(f"PDFの表示中にエラーが発生しました: {e}")

def display_sidebar_pdf_trigger(pdf_path: str):
    """
    サイドバーにポップアップでPDFを表示させるボタンを設定

    Args:
        pdf_path (str/Path): 読み込むPDFファイルのパス。
    """
    with st.sidebar:
        st.divider()
        st.subheader("📚 エビデンス確認")
        st.info("AI回答の根拠となっている社内規定の原本PDFを確認できます")
        if st.button("📄 PDF原本を開く", width="stretch"):
            show_pdf_dialog(pdf_path)

@st.cache_data
def load_markdown_file(file_path: str) -> str:
    """
    指定されたパスのMarkdownファイルを読み込み、テキストとして返す。
    Streamlitのキャッシュを利用し、再読み込みの負荷を軽減する。

    Args:
        file_path (str/Path): 読み込むMarkdownファイルのパス。

    Returns:
        str: ファイルの内容。見つからない場合はエラーメッセージを返す。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "⚠️ ガイドファイルが見つかりませんでした。"

def display_faq_buttons() -> Optional[str]:
    """
    チャット開始時に表示するFAQ（よくある質問）ボタン群を生成する。

    Returns:
        str: ユーザーがクリックしたボタンに対応する質問テキスト。クリックがない場合はNone。
    """
    st.caption("💡 よくある質問例：")
    # 縦に並べる。keyを固定することで、再実行されてもボタンの状態が維持されます。
    if st.button("🕒 時差出勤の昼休憩の時間は？", key="btn_faq_1"):
        return "時差出勤の昼休憩の時間は？"
    if st.button("📝 時差出勤の申請ルール", key="btn_faq_2"):
        return "時差出勤のルールは？"
    if st.button("🆘 急に休みたくなった時は？", key="btn_faq_3"):
        return "急に休みたくなった時は？"
    if st.button("🚃 電車が遅延した場合は？", key="btn_faq_4"):
        return "電車が遅延した場合は？"
    return None

def display_feedback_buttons(idx: int) -> Optional[str]:
    """
    AIの回答後に表示する「解決・未解決」フィードバックボタンを生成する。

    Args:
        idx (int): ボタンのユニーク性を担保するためのメッセージインデックス。

    Returns:
        str: フィードバックの結果テキスト（解決/未解決）。未選択の場合はNone。
    """
    st.divider()
    st.write("💡 **解決しましたか？**")

    if st.button("👍 はい (解決した)", key=f"yes_{idx}"):
        return "解決しました"
        return FEEDBACK_RESOLVED
    if st.button("👎 いいえ (解決しない)", key=f"no_{idx}"):
        return "解決してません"
        return FEEDBACK_UNRESOLVED
    return None

# --- メソッド定義 (データ処理・API) ---
@st.cache_resource
def get_pdf_text(pdf_path: str) -> Optional[str]:
    """
    PDFファイルから全テキストを抽出し、Streamlitのリソースキャッシュに保存する。

    Args:
        pdf_path (str): 読み込み対象のPDFファイルパス。

    Returns:
        str: 抽出されたテキスト。失敗した場合はNone。
    """
    try:
        text = ""
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"PDFの解析中にエラーが発生しました:{e}")
        return None

@st.cache_resource
def get_ai_client() -> genai.Client:
    """
    Google Gen AI クライアントを初期化し、キャッシュとして保持する。

    Returns:
        genai.Client: 初期化済みのAIクライアント。
    """
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def render_chat_interface() -> Tuple[Optional[str], Optional[str]]:
    """
    現在のチャット履歴に基づき、メッセージおよびUIコンポーネントを画面に描画する。

    Returns:
        tuple: (selected_question, feedback_selection)
            - selected_question (str): FAQボタンで選択された質問。
            - feedback_selection (str): フィードバックボタンで選択された内容。
    """
    selected_question = None
    feedback_selection = None

    for i, msg in enumerate(st.session_state.display_history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # 最初のみFAQボタンを表示
            if i == 0:
                selected_question = display_faq_buttons()

            # 最新のアシスタントの回答の場合のみ表示
            if msg["role"] == "assistant" and i == len(st.session_state.display_history) - 1:
                # 解決後の挨拶メッセージにはボタンを出さない判定
                is_not_feedback_reply = "光栄です" not in msg["content"] and "申し訳ありません" not in msg["content"]
                # feedback_doneがTureならボタンを表示しない
                if i > 0 and is_not_feedback_reply and not st.session_state.get("feedback_done", False):
                    feedback_selection = display_feedback_buttons(i)

    return selected_question, feedback_selection

def handle_feedback(final_prompt: str, form_url: str) -> str:
    """
    ユーザーからのフィードバックに対し、適切な案内メッセージを生成する。

    Args:
        final_prompt (str): フィードバック内容（解決/未解決）。
        form_url (str): 未解決時に案内するGoogleフォームのURL。

    Returns:
        str: システムが返信として表示するメッセージ。
    """
    if final_prompt == FEEDBACK_RESOLVED:
        msg = "お役に立てて光栄です！また何かあればいつでもご質問ください。"
        st.success(msg)
    else:
        msg = f"お役に立てず申し訳ありません。詳細な状況を添えて、[こちらの問い合わせフォーム]({form_url})への相談をご検討ください。"
        st.info(msg)
    return msg

def get_gemini_answer(client: genai.Client, final_prompt: str, pdf_content: str, base_instruction: str) -> Optional[str]:
    """
    Gemini APIを呼び出し、PDFの内容に基づいたRAG（検索拡張生成）回答を取得する。

    Args:
        client (genai.Client): AIクライアントインスタンス。
        final_prompt (str): ユーザーの質問内容。
        pdf_content (str): 参照元となるPDFのテキスト。
        base_instruction (str): システムプロンプトのテンプレート。

    Returns:
        str: 生成されたAIの回答テキスト。エラー時はNoneを返す。
    """
    # システムプロンプトにPDF内容を埋め込み
    final_instruction = base_instruction.replace("{{PDF_CONTENT}}", pdf_content)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=st.session_state.chat_history + [final_prompt], # 履歴 + 今回の質問
            config=types.GenerateContentConfig(
                system_instruction=final_instruction,
                temperature=0.1,
            )
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            st.warning("⚠️ API制限がかかりました。1分ほど待ってから再度お試しください。")
        elif "503" in str(e):
            st.error("☁️ 現在Googleのサーバーが大変混み合っています。少し時間をおいてから再度お試しください。")
        elif "400" in str(e):
            st.error("⚠️ 送信データに不備があります（二重送信や空のデータ）。一度ページをリロードして再度お試しください。")
        error_msg = str(e)
        if "429" in error_msg:
            st.warning("⚠️ 混雑しています。少し待ってから再度お試しください。")
        elif "503" in error_msg:
            st.error("☁️ サーバーが一時的に不安定です。")
        else:
            st.error(f"エラーが発生しました: {e}")
            st.error(f"予期せぬエラー: {error_msg}")
        return None

def initialize_session_state():
    """セッション状態の初期化を集約"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "display_history" not in st.session_state:
        initial_message = (
            "こんにちは。 社内規定（勤怠管理）について、どのような情報をお探しでしょうか？\n\n"
            "お気軽にご質問ください。"
        )
        st.session_state.display_history = [{"role": "assistant", "content": initial_message}]
    if "feedback_done" not in st.session_state:
        st.session_state.feedback_done = False

def main():
    # 初期設定
    inject_responsive_css()
    st.set_page_config(page_title="勤怠管理QAボット", layout="wide")
    responsive_title("勤怠管理Q&Aチャットボット")

    # システムプロンプトと申請フォームの読み込み
    initialize_session_state()

    if "config" not in st.session_state or "system_prompt" not in st.session_state:
        load_instruction, config = load_app_settings()
        st.session_state.system_prompt = load_instruction
        st.session_state.config = config

    PROMPT = st.session_state.get("system_prompt", "あなたは優秀なアシスタントです。")
    config_data = st.session_state.get("config", {})
    FORM_URL = config_data.get("google_form_url", "")

    # セッション状態の初期化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "display_history" not in st.session_state:
        initial_message =(
            "こんにちは。 社内規定（勤怠管理）について、どのような情報をお探しでしょうか？\n\n"
            "お気軽にご質問ください。"
        )
        st.session_state.display_history = [
            {"role": "assistant", "content": initial_message}
        ]

    # 使い方ガイド表示
    guide_text = load_markdown_file(GUIDE_PATH)
    with st.popover("📖 使い方ガイド"):
        st.markdown(guide_text)
    st.divider()

    # PDFファイルの存在チェック
    if not os.path.exists(PDF_PATH):
        st.error(f"ファイルが見つかりません: {PDF_PATH}")
        return # 処理を中断

    # PDFからテキスト抽出チェック
    pdf_content = get_pdf_text(PDF_PATH)
    if pdf_content is None:
        st.error("規定PDFの読み込みに失敗しました。ファイルが破損しているか、画像のみの可能性があります。")
        return

    # --- サイドバーに原本確認ボタンを設置 ---
    display_sidebar_pdf_trigger(PDF_PATH)

    # --- インターフェース制御 ---
    client = get_ai_client()

    # --- チャット画面の表示とボタン選択の取得 ---
    selected_question, feedback_selection = render_chat_interface()

    # --- 入力プロンプトの統合と優先順位決定 ---
    chat_prompt = st.chat_input("勤怠について質問してください")
    final_prompt = selected_question or feedback_selection or chat_prompt
    ans_text = None

    # --- 回答生成プロセス ---
    if final_prompt:
        # 解決ボタン以外（新しい質問やFAQ）が入力されたら、フラグをリセットしてボタンを表示
        if final_prompt not in [FEEDBACK_RESOLVED, FEEDBACK_UNRESOLVED]:
            st.session_state.feedback_done = False

        # ユーザー入力の反映
        st.session_state.display_history.append({"role": "user", "content": final_prompt})
        with st.chat_message("user"):
            st.markdown(final_prompt)

        # 入力内容に応じて分岐(フィードバック or AI回答)
        if final_prompt in [FEEDBACK_RESOLVED, FEEDBACK_UNRESOLVED]:
            st.session_state.feedback_done = True
            with st.chat_message("assistant"):
                ans_text = handle_feedback(final_prompt, FORM_URL)
                st.session_state.display_history.append({"role": "assistant", "content": ans_text})
                st.rerun()
        else:
            with st.chat_message("assistant"):
                with st.spinner("AIが規定を確認しています..."):
                    ans_text = get_gemini_answer(client, final_prompt, pdf_content, PROMPT)

                    if ans_text:
                        st.markdown(ans_text)
                        # API利用履歴、表示用履歴、リロード
                        st.session_state.chat_history.append(
                            types.Content(role="user", parts=[types.Part.from_text(text=final_prompt)])
                        )
                        st.session_state.chat_history.append(
                            types.Content(role="model", parts=[types.Part.from_text(text=ans_text)])
                        )
                        st.session_state.display_history.append(
                            {"role": "assistant", "content": ans_text}
                        )
                        st.rerun()

if __name__ == "__main__":
    main()