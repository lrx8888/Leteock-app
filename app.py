import streamlit as st
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import time

# -------------------------- 配置部分 --------------------------
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei"]
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(page_title="股票分析工具", layout="wide")

# 给AKShare加个缓存，减少接口请求次数
@st.cache_data(ttl=3600)  # 数据缓存1小时，避免重复请求
def get_stock_data(code):
    # 接口波动时自动重试2次
    for _ in range(2):
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date="20250101",
                end_date="20260524",
                adjust="qfq"
            )
            return df
        except:
            time.sleep(1)  # 失败了等1秒再试
    return None

@st.cache_data(ttl=86400)  # 股票名称缓存1天
def get_stock_name(code):
    try:
        df = ak.stock_info_a_code_name()
        return df[df["code"] == code]["name"].values[0]
    except:
        return "未知股票"

# -------------------------- 主页面 --------------------------
st.title("📈 股票分析工具（稳定版）")
st.markdown("---")

# 用户输入区
stock_code = st.text_input("输入股票代码（如 000001/601398）", value="000001")
analyze_btn = st.button("开始分析", type="primary")

if analyze_btn:
    with st.spinner("🔄 正在加载数据中..."):
        # 1. 获取股票名称
        stock_name = get_stock_name(stock_code)
        st.subheader(f"📌 {stock_name}（{stock_code}）")

        # 2. 获取历史数据（带重试+缓存）
        df = get_stock_data(stock_code)
        if df is None or df.empty:
            st.error("❌ 数据加载失败，可能是接口波动，请稍后重试或换一只股票试试")
            st.info("💡 建议先试 000001/601398 这类大盘股，接口最稳定")
            st.stop()

        # 3. 数据预处理
        df["日期"] = pd.to_datetime(df["日期"])
        df = df.sort_values("日期").reset_index(drop=True)
        df["20日均线"] = df["收盘"].rolling(20).mean()
        df["涨跌幅"] = df["收盘"].pct_change() * 100

        # 4. 绘制走势图
        st.subheader("📊 股价走势与20日均线")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["日期"], df["收盘"], label="收盘价", color="#1f77b4", linewidth=2)
        ax.plot(df["日期"], df["20日均线"], label="20日均线", color="#ff7f0e", linewidth=1.5)
        ax.set_title(f"{stock_name} 股价走势", fontsize=16, pad=20)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig, use_container_width=True)

        # 5. 关键指标
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

        st.success("✅ 数据加载完成！换个股票代码再点一次试试，现在支持多只股票了")
