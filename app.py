import streamlit as st
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

# 配置matplotlib中文显示
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

# 页面配置
st.set_page_config(page_title="股票分析工具", layout="wide")

# --- 你的Tushare Token ---
TOKEN = "f152e2c3fa566156f1407e955d335df9e22674dffa40bec6d7000c3b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 页面标题
st.title("📈 股票分析工具（免费版）")

# 用户输入
stock_code = st.text_input("输入股票代码（如 000001.SZ）", value="000001.SZ")

# 分析按钮
if st.button("开始分析"):
    with st.spinner("正在加载数据中..."):
        try:
            # 适配免费Token：只获取最近3个月数据
            df = pro.daily(
                ts_code=stock_code,
                start_date="20260201",  # 起始日期改为近3个月
                end_date="20260501"
            )

            # 数据为空的情况
            if df.empty:
                st.error("❌ 没有获取到数据，请检查股票代码是否正确，或更换其他股票尝试！")
            else:
                # 数据预处理
                df = df.sort_values("trade_date").reset_index(drop=True)
                df["ma20"] = df["close"].rolling(20).mean()

                # 绘制图表
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df["trade_date"], df["close"], label="收盘价", color="#1f77b4", linewidth=2)
                ax.plot(df["trade_date"], df["ma20"], label="20日均线", color="#ff7f0e", linewidth=2)
                ax.legend(fontsize=12)
                ax.set_title(f"{stock_code} 股价走势", fontsize=16)
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # 显示数据表格
                st.subheader("📋 数据明细")
                st.dataframe(df[["trade_date", "open", "high", "low", "close", "vol"]])

        except Exception as e:
            st.error(f"❌ 数据加载失败，错误信息：{str(e)}")
            st.info("💡 免费Tushare Token权限有限，可尝试：\n1. 更换其他股票代码\n2. 稍后再试（免费用户有请求次数限制）")