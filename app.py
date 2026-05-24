import streamlit as st
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
st.set_page_config(page_title="股票分析工具", layout="wide")

# 你的Tushare Token
TOKEN = "f152e2c3fa566156f1407e955d335df9e22674dffa40bec6d7000c3b"
ts.set_token(TOKEN)
pro = ts.pro_api()

st.title("📈 股票分析工具")
stock_code = st.text_input("输入股票代码（如 000001.SZ）", value="000001.SZ")

if st.button("开始分析"):
    with st.spinner("加载数据中..."):
        df = pro.daily(ts_code=stock_code, start_date="20240101", end_date="20260501")
        df = df.sort_values("trade_date").reset_index(drop=True)
        df["ma20"] = df["close"].rolling(20).mean()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["trade_date"], df["close"], label="收盘价", color="gray")
        ax.plot(df["trade_date"], df["ma20"], label="20日均线", color="blue")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
