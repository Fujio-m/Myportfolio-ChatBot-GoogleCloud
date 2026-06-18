import streamlit as st

def inject_responsive_css():
    """
    全ページ共通のレスポンシブデザイン（タイトル・ヘッダー用）CSSを注入する。
    これを各ページの冒頭で呼び出すことで、デバイスサイズに応じた文字サイズ調整が可能になる。
    """
    st.markdown("""
        <style>
        /* --- デフォルト（PC）のスタイル --- */
        .res-title {
            font-size: 3rem !important;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 1rem;
            color: #1E3A8A; /* 濃いブルー */
        }
        .res-header {
            font-size: 1.8rem !important;
            font-weight: 600;
            margin-top: 1.5rem;
            color: #374151;
        }

        /* --- モバイル表示（画面幅768px以下） --- */
        @media (max-width: 768px) {
            .res-title {
                font-size: 1.6rem !important; /* スマホではサイズを大幅に抑える */
                text-align: center;
                margin-bottom: 0.5rem;
            }
            .res-header {
                font-size: 1.2rem !important;
                text-align: center;
            }
            /* ダイアログやコンテナのパディング調整（任意） */
            div[data-testid="stVerticalBlock"] {
                gap: 0.5rem !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

def responsive_title(text):
    """
    レスポンシブ対応のタイトルを表示する。
    """
    st.markdown(f'<h1 class="res-title">{text}</h1>', unsafe_allow_html=True)

def responsive_header(text):
    """
    レスポンシブ対応のヘッダーを表示する。
    """
    st.markdown(f'<h2 class="res-header">{text}</h2>', unsafe_allow_html=True)