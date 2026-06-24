"""
Streamlit dashboard for SME sales analytics.

Run with:
streamlit run dashboard/app.py
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/sme_sales_data.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


df = load_data()

st.set_page_config(page_title="SME Sales Analytics Dashboard", layout="wide")

st.title("SME Sales Analytics Dashboard")
st.write(
    "Business analytics dashboard for monitoring revenue, profit, "
    "customers, categories, regions, and sales channels."
)

# Sidebar filters
st.sidebar.header("Filters")

regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

channels = st.sidebar.multiselect(
    "Sales Channel",
    options=sorted(df["sales_channel"].unique()),
    default=sorted(df["sales_channel"].unique())
)

categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)

filtered = df[
    (df["region"].isin(regions))
    & (df["sales_channel"].isin(channels))
    & (df["category"].isin(categories))
]

# KPIs
total_revenue = filtered["revenue"].sum()
total_profit = filtered["profit"].sum()
orders = filtered["invoice_id"].nunique()
customers = filtered["customer_id"].nunique()
aov = total_revenue / orders if orders else 0
profit_margin = total_profit / total_revenue if total_revenue else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Revenue", f"€{total_revenue:,.0f}")
col2.metric("Profit", f"€{total_profit:,.0f}")
col3.metric("Orders", f"{orders:,}")
col4.metric("Customers", f"{customers:,}")
col5.metric("Profit Margin", f"{profit_margin:.1%}")

# Monthly trend
monthly = filtered.groupby(pd.Grouper(key="order_date", freq="ME")).agg(
    revenue=("revenue", "sum"),
    profit=("profit", "sum"),
    orders=("invoice_id", "nunique")
).reset_index()

fig_monthly = px.line(
    monthly,
    x="order_date",
    y=["revenue", "profit"],
    title="Monthly Revenue and Profit"
)
st.plotly_chart(fig_monthly, use_container_width=True)

# Category and region
left, right = st.columns(2)

category_perf = filtered.groupby("category").agg(
    revenue=("revenue", "sum"),
    profit=("profit", "sum")
).reset_index().sort_values("revenue", ascending=False)

fig_category = px.bar(
    category_perf,
    x="category",
    y="revenue",
    title="Revenue by Category"
)
left.plotly_chart(fig_category, use_container_width=True)

region_perf = filtered.groupby("region").agg(
    revenue=("revenue", "sum"),
    profit=("profit", "sum")
).reset_index().sort_values("profit", ascending=False)

fig_region = px.bar(
    region_perf,
    x="region",
    y="profit",
    title="Profit by Region"
)
right.plotly_chart(fig_region, use_container_width=True)

# Channel analysis
channel_perf = filtered.groupby("sales_channel").agg(
    revenue=("revenue", "sum"),
    profit=("profit", "sum"),
    orders=("invoice_id", "nunique")
).reset_index().sort_values("revenue", ascending=False)

fig_channel = px.pie(
    channel_perf,
    values="revenue",
    names="sales_channel",
    title="Revenue Share by Sales Channel"
)
st.plotly_chart(fig_channel, use_container_width=True)

st.subheader("Detailed Data")
st.dataframe(filtered.head(1000), use_container_width=True)
