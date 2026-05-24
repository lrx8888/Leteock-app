import streamlit as st
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------- 配置部分 --------------------------
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="股票分析工具",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    st.title("📈 股票分析工具（永久免费版）")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        stock_code = st.text_input(
            "输入股票代码（直接输数字，如 000001）",
            value="000001",
            help="深市（0/3开头）：000001；沪市（6开头）：601398"
        )
    with col2:
        analyze_btn = st.button("开始分析", type="primary", use_container_width=True)

    st.markdown("---")

    if analyze_btn:
        with st.spinner("🔄 正在加载数据中，请稍候..."):
            try:
                # 用最稳定的A股日线接口
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date="20250101",
                    end_date="20260524",
                    adjust="qfq"
                )

                if df.empty:
                    st.error("❌ 未获取到数据，请检查股票代码是否正确！")
                    return

                # 数据预处理（这次字段名完全对应，不会报错）
                df["日期"] = pd.to_datetime(df["日期"])
                df = df.sort_values("日期").reset_index(drop=True)
                df["20日均线"] = df["收盘"].rolling(20).mean()
                df["涨跌幅"] = df["收盘"].pct_change() * 100

                # 绘制股价走势图
                st.subheader("📊 股价走势与20日均线")
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df["日期"], df["收盘"], label="收盘价", color="#1f77b4", linewidth=2)
                ax.plot(df["日期"], df["20日均线"], label="20日均线", color="#ff7f0e", linewidth=2)
                ax.set_title(f"{stock_code} 股价走势", fontsize=16, pad=20)
                ax.set_xlabel("日期")
                ax.set_ylabel("价格（元）")
                ax.legend(fontsize=12)
                ax.grid(alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig, use_container_width=True)

                # 数据明细表格
                st.subheader("📋 数据明细")
                st.dataframe(
                    df[["日期", "开盘", "最高", "最低", "收盘", "成交量", "涨跌幅"]],
                    use_container_width=True,
                    hide_index=True
                )

                # 关键指标卡片
                st.subheader("📌 关键指标")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("最新收盘价", f"{df['收盘'].iloc[-1]:.2f} 元")
                with col2:
                    st.metric("近5日涨跌幅", f"{df['涨跌幅'].tail(5).sum():.2f}%")
                with col3:
                    st.metric("近1月最高", f"{df['最高'].max():.2f} 元")
                with col4:
                    st.metric("近1月最低", f"{df['最低'].min():.2f} 元")

                st.success("✅ 数据加载完成！")

            except Exception as e:
                st.error(f"❌ 数据加载失败：{str(e)}")
                st.info("💡 可能原因：\n1. 股票代码错误\n2. 接口波动，可稍后重试")

if __name__ == "__main__":
    main()
