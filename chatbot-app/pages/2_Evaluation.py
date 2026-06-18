import streamlit as st
import plotly.express as px
import pandas as pd
import os
from utils.responsive import inject_responsive_css, responsive_title, responsive_header


# 4_Evaluation.py - 精度評価とテストケース
#
# 【設計意図】
# RAGシステムの「回答品質」を客観的に評価するためのテストデータと結果を提示。
# ハルシネーションの有無、情報の網羅性、回答の正確性を検証し、
# 開発者が「品質保証（QA）」の視点を持っていることを証明することを目的とする


def load_test_data(csv_path):
    """
    指定されたCSVパスからテストケースデータを読み込む。

    Args:
        csv_path (str): テスト結果が格納されたCSVファイルのパス。

    Returns:
        pd.DataFrame: 読み込まれたデータフレーム。ファイルが存在しない場合はNoneを返す。
    """
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path, encoding="utf-8-sig")
    return None

def display_summary_metrics(df):
    """
    テスト結果の要約統計（合格率、件数など）を計算し、メトリクスとチャートを表示する。

    Args:
        df (pd.DataFrame): 全テストケースのデータフレーム。
    """
    total_cases = len(df)
    pass_cases = len(df[df["判定"].str.contains("✅", na=False)])
    fail_cases = total_cases - pass_cases
    pass_rate = (pass_cases / total_cases) * 100 if total_cases > 0 else 0

    col_metrics, col_chart = st.columns([1, 1])

    with col_metrics:
        responsive_header("📊 統計情報")
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("総テストケース数", f"{total_cases}件")
        m_col2.metric("正解率", f"{pass_rate}%")

        m_col3, m_col4 = st.columns(2)
        m_col3.metric("合格（✅）", f"{pass_cases}件")
        m_col4.metric("不合格（❌）", f"{fail_cases}件", delta=f"-{fail_cases}" if fail_cases > 0 else None, delta_color="inverse")

    with col_chart:
        chart_data = df["判定"].value_counts().reset_index()
        chart_data.columns = ["判定", "件数"]

        chart_data["判定"] = chart_data["判定"].replace({
            '✅': '✅ 合格',
            '❌': '❌ 不合格',
            '⚠️': '⚠️ 要確認'
        })

        # Plotlyで円グラフ作成
        fig = px.pie(
            chart_data,
            values="件数",
            names="判定",
            hole=0.4,
            color="判定",
            color_discrete_map={
                '✅ 合格': '#2ecc71',
                '❌ 不合格': '#e74c3c',
                '⚠️ 要確認': '#f1c40f'
            }
        )
        # グラフの余白やサイズ調整
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=250,
            showlegend=True
        )
        st.plotly_chart(fig, width='stretch')

def get_sidebar_filters(df):
    """
    サイドバーにフィルタUIを表示し、ユーザーの選択に基づいてデータを絞り込む。

    Args:
        df (pd.DataFrame): 元のデータフレーム。

    Returns:
        pd.DataFrame: フィルタ適用後のデータフレーム。
    """
    st.sidebar.header("🔍 表示フィルター")

    # 判定で絞り込み
    all_stats = df["判定"].unique().tolist()
    selected_stats = st.sidebar.multiselect(
        "判定を選択",
        all_stats,
        default=all_stats
    )

    filtered_df = df[(df["判定"].isin(selected_stats))]
    return filtered_df

def display_test_details(df):
    """
    テストケースの詳細結果を、カスタマイズされたデータフレーム形式で表示する。

    Args:
        df (pd.DataFrame): 表示対象の（フィルタ済みの）データフレーム。
    """
    # 備考欄のNoneを空文字に置き換える
    df["備考"] = df["備考"].fillna("")

    tab1, tab2 = st.tabs(["📱 テストケース", "📊 一覧テーブル", ])

    with tab1:
        st.info("💡 各テストケースの詳細内容を確認できます。")
        for _, row in df.iterrows():
            label = f"{row['判定']} | {row['カテゴリ']} : {row['質問内容'][:30]}..."

            with st.expander(label):
                st.markdown(f"**【質問内容】**\n{row['質問内容']}")
                st.divider()

                col_a, col_b = st.columns(2)
                with col_a:
                    st.success("**期待される回答**")
                    st.write(row['期待される回答（合格基準）'])
                with col_b:
                    # 判定に応じて色を変える
                    if "✅" in row['判定']:
                        st.info("**実際の回答**")
                    elif "❌" in row['判定']:
                        st.error("**実際の回答**")
                    else:
                        st.warning("**実際の回答**")
                    st.write(row['実際の回答'])

                if row['備考']:
                    st.divider()
                    st.caption(f"📝 備考: {row['備考']}")


    with tab2:
        st.info("💡テストケースを表形式で確認できます。(スクロール可能)")
        st.dataframe(df,
            width='stretch',
            height=400,
            hide_index=True,
            column_config={
                "カテゴリ": st.column_config.TextColumn("カテゴリ", width=100),
                "判定": st.column_config.TextColumn("判定", width=50),
                "質問内容": st.column_config.TextColumn("質問内容", width=400),
                "期待される回答（合格基準）": st.column_config.TextColumn("期待される回答", width=350),
                "実際の回答": st.column_config.TextColumn("実際の回答", width=1200),
                "備考": st.column_config.TextColumn("備考", width=550),
            }
        )

def main():
    inject_responsive_css()
    responsive_title("精度評価・テスト結果")
    st.markdown("""本アプリケーションの回答精度を検証した結果です。""")

    CSV_PATH = os.path.join("data", "test_cases.csv")
    df = load_test_data(CSV_PATH)

    if df is not None:
        filtered_df = get_sidebar_filters(df)
        display_summary_metrics(df)
        display_test_details(filtered_df)
    else:
        st.error(f"⚠️ テストデータが見つかりません: {CSV_PATH}")
        st.info("Excel等で作成したテスト結果をCSV形式で保存し、dataフォルダに配置してください。")

if __name__ == "__main__":
    main()
