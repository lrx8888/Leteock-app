# 强制让Streamlit安装依赖
import os
os.system("pip install -r requirements.txt")

import streamlit as st
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------- 配置部分 --------------------------
# 解决matplotlib中文乱码问题
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

# 页面配置
st.set_page_config(
    page_title="股票分析工具",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    st.title("📈 股票分析工具（永久免费版）")
    st.markdown("---")

    # 用户输入区
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

    # 分析逻辑
    if analyze_btn:
        with st.spinner("🔄 正在加载数据中，请稍候..."):
            try:
                # 换成更稳定的接口
                df = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq")

                if df.empty:
                    st.error("❌ 未获取到数据，请检查股票代码是否正确！")
                    return

                # 数据预处理
                df = df.reset_index()
                df["日期"] = pd.to_datetime(df["date"])
                df = df.sort_values("日期").reset_index(drop=True)
                df["20日均线"] = df["close"].rolling(20).mean()
                df["涨跌幅"] = df["close"].pct_change() * 100

                # 绘制股价走势图
                st.subheader("📊 股价走势与20日均线")
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df["日期"], df["close"], label="收盘价", color="#1f77b4", linewidth=2)
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
                    df[["日期", "open", "high", "low", "close", "volume", "涨跌幅"]].rename(
                        columns={
                            "open": "开盘",
                            "high": "最高",
                            "low": "最低",
                            "close": "收盘",
                            "volume": "成交量"
                        }
                    ),
                    use_container_width=True,
                    hide_index=True
                )

                # 关键指标卡片
                st.subheader("📌 关键指标")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("最新收盘价", f"{df['close'].iloc[-1]:.2f} 元")
                with col2:
                    st.metric("近5日涨跌幅", f"{df['涨跌幅'].tail(5).sum():.2f}%")
                with col3:
                    st.metric("近1月最高", f"{df['high'].max():.2f} 元")
                with col4:
                    st.metric("近1月最低", f"{df['low'].min():.2f} 元")

                st.success("✅ 数据加载完成！")

            except Exception as e:
                st.error(f"❌ 数据加载失败：{str(e)}")
                st.info("💡 可能原因：\n1. 股票代码错误\n2. 网络波动，可稍后重试")

if __name__ == "__main__":
    main()
