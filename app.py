import streamlit as st
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt

# 配置matplotlib中文显示
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

# 页面配置
st.set_page_config(page_title="股票分析工具（永久免费版）", layout="wide")

# 页面标题
st.title("📈 股票分析工具（永久免费版）")

# 用户输入（直接用纯数字，不用后缀）
stock_code = st.text_input("输入股票代码（如 000001）", value="000001")

# 分析按钮
if st.button("开始分析"):
    with st.spinner("正在加载数据中..."):
        try:
            # 用AKShare获取数据，无需Token，完全免费
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                   start_date="20260201", end_date="20260501", 
                                   adjust="qfq")
            
            if df.empty:
                st.error("❌ 没有获取到数据，请检查股票代码是否正确！")
            else:
                # 计算20日均线
                df["ma20"] = df["收盘"].rolling(20).mean()

                # 绘制图表
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df["日期"], df["收盘"], label="收盘价", color="#1f77b4", linewidth=2)
                ax.plot(df["日期"], df["ma20"], label="20日均线", color="#ff7f0e", linewidth=2)
                ax.legend(fontsize=12)
                ax.set_title(f"{stock_code} 股价走势", fontsize=16)
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # 显示数据表格
                st.subheader("📋 数据明细")
                st.dataframe(df[["日期", "开盘", "最高", "最低", "收盘", "成交量"]])

        except Exception as e:
            st.error(f"❌ 数据加载失败，错误信息：{str(e)}")