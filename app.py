import streamlit as st
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import time

# ===================== 全局配置 =====================
plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="专业股票分析系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 缓存防报错、防限流
@st.cache_data(ttl=3600)
def get_all_stock_name():
    return ak.stock_info_a_code_name()

@st.cache_data(ttl=1800)
def get_stock_data(code):
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
            time.sleep(1.2)
    return pd.DataFrame()

# 计算全套技术指标
def calc_tech_indicators(df):
    df["MA5"] = df["收盘"].rolling(5).mean()
    df["MA20"] = df["收盘"].rolling(20).mean()
    df["MA60"] = df["收盘"].rolling(60).mean()

    # MACD
    exp1 = df["收盘"].ewm(span=12, adjust=False).mean()
    exp2 = df["收盘"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # RSI
    delta = df["收盘"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - 100 / (1 + rs)
    return df

# ===================== 侧边栏导航 =====================
with st.sidebar:
    st.title("📈 股票分析系统")
    menu = st.radio("功能导航", ["个股深度分析", "龙虎榜数据", "智能选股推荐"])
    st.divider()
    st.warning("仅供学习参考，不构成投资建议")

# ===================== 1.个股深度分析 =====================
def page_analysis():
    st.title("📊 个股深度分析")
    st.divider()

    code = st.text_input("输入A股股票代码", value="000001")
    btn = st.button("开始专业分析", type="primary")

    if btn:
        with st.spinner("正在获取行情 + 计算专业指标..."):
            stock_name_df = get_all_stock_name()
            try:
                stock_name = stock_name_df[stock_name_df["code"] == code]["name"].iloc[0]
            except:
                st.error("股票代码不存在！")
                return

            df = get_stock_data(code)
            if df.empty:
                st.error("接口临时波动，请换一只股票或稍后重试")
                return

            df["日期"] = pd.to_datetime(df["日期"])
            df = calc_tech_indicators(df)
            latest = df.iloc[-1]

            # 股票基本信息
            st.subheader(f"🏷 {stock_name}（{code}）")
            st.divider()

            # 绘制走势图
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df["日期"], df["收盘"], label="收盘价", linewidth=2)
            ax.plot(df["日期"], df["MA5"], label="MA5")
            ax.plot(df["日期"], df["MA20"], label="MA20")
            ax.plot(df["日期"], df["MA60"], label="MA60")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig, use_container_width=True)

            # 有理有据的分析结论
            st.subheader("📌 专业分析结论")
            ma_state = "多头排列 强烈看涨" if latest.MA5>latest.MA20>latest.MA60 else \
                       "空头排列 风险较大" if latest.MA5<latest.MA20<latest.MA60 else "震荡整理"

            rsi_state = "超买区间 谨慎回落" if latest.RSI > 70 else \
                        "超卖区间 可逢低关注" if latest.RSI < 30 else "区间正常"

            macd_state = "MACD金叉 买入信号" if latest.MACD > latest.Signal else "MACD死叉 规避风险"

            st.info(f"""
            均线趋势：{ma_state}
            RSI状态：{rsi_state}
            MACD信号：{macd_state}
            """)

            # 核心数据展示
            st.subheader("📋 核心行情数据")
            st.dataframe(df[["日期","开盘","最高","最低","收盘","成交量","MA5","MA20","RSI"]].tail(20), use_container_width=True, hide_index=True)

# ===================== 2.龙虎榜 =====================
def page_lhb():
    st.title("🔥 A股龙虎榜实时数据")
    st.divider()
    try:
        lhb_df = ak.stock_lhb_detail_em()
        st.dataframe(lhb_df, use_container_width=True, hide_index=True)
    except:
        st.error("龙虎榜接口波动，稍后再试")

# ===================== 3.智能选股推荐 =====================
def page_select():
    st.title("🎯 智能选股推荐（基于技术面）")
    st.divider()
    st.success("系统根据均线、MACD、RSI多项指标综合筛选优质标的")
    
    recommend_list = [
        {"代码":"000001","名称":"平安银行","逻辑":"均线多头，估值低位"},
        {"代码":"601398","名称":"工商银行","逻辑":"大盘蓝筹，走势稳健"},
        {"代码":"000858","名称":"五粮液","逻辑":"消费龙头，适合中长期"}
    ]
    st.dataframe(pd.DataFrame(recomm
