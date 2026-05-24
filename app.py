import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# 全局配置
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei"]
plt.rcParams["axes.unicode_minus"] = False
st.set_page_config(page_title="稳定A股查询系统", layout="wide")

# 内置股票名称字典
STOCK_NAME_DICT = {
    "000001": "平安银行",
    "000002": "万科A",
    "601398": "工商银行",
    "600036": "招商银行",
    "600519": "贵州茅台",
    "000858": "五粮液",
    "300750": "宁德时代",
    "002594": "比亚迪"
}

def get_local_stock_name(code):
    if code in STOCK_NAME_DICT:
        return STOCK_NAME_DICT[code]
    return f"A股({code})"

# 超稳数据获取（带重试）
@st.cache_data(ttl=86400)
def get_safe_stock_data(code):
    import akshare as ak
    for _ in range(3):
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date="20250101",
                end_date=time.strftime("%Y%m%d"),
                adjust="qfq"
            )
            return df
        except:
            time.sleep(2)
    return pd.DataFrame()

# 计算均线指标
def calc_indicator(df):
    df["MA5"] = df["收盘"].rolling(5).mean()
    df["MA20"] = df["收盘"].rolling(20).mean()
    df["MA60"] = df["收盘"].rolling(60).mean()
    return df

# 主界面
st.title("📈 全A股稳定查询分析系统")
st.divider()

stock_code = st.text_input("请输入任意A股股票代码", value="000001")
start_btn = st.button("开始查询分析", type="primary")

if start_btn:
    with st.spinner("正在稳定加载数据，请稍候..."):
        stock_name = get_local_stock_name(stock_code)
        df = get_safe_stock_data(stock_code)

        if df.empty:
            st.error("当前网络临时波动，请稍后再试，或更换股票代码")
        else:
            df["日期"] = pd.to_datetime(df["日期"])
            df = calc_indicator(df)
            latest = df.iloc[-1]

            st.subheader(f"✅ {stock_name} | 股票代码：{stock_code}")
            st.divider()

            # 绘制走势图
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df["日期"], df["收盘"], label="收盘价", linewidth=2)
            ax.plot(df["日期"], df["MA5"], label="5日均线")
            ax.plot(df["日期"], df["MA20"], label="20日均线")
            ax.plot(df["日期"], df["MA60"], label="60日均线")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig, use_container_width=True)

            # 走势分析结论
            st.subheader("📊 走势分析结论")
            if latest["MA5"] > latest["MA20"] and latest["MA20"] > latest["MA60"]:
                st.success("均线多头排列，走势强势，适合持有观察")
            elif latest["MA5"] < latest["MA20"] and latest["MA20"] < latest["MA60"]:
                st.warning("均线空头排列，整体偏弱，注意风险规避")
            else:
                st.info("目前处于区间震荡，暂无明确方向")

            # 行情数据表
            st.subheader("📋 近期行情数据")
            st.dataframe(
                df[["日期", "开盘", "最高", "最低", "收盘", "成交量", "MA5", "MA20"]].tail(30),
                use_container_width=True,
                hide_index=True
            )

st.sidebar.info("本系统已做网络加固，支持全部A股稳定查询")
st.sidebar.warning("仅供学习分析，不构成投资建议")
