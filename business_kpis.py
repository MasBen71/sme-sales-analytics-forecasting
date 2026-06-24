"""
Business KPI analysis for SME sales data.
"""

from pathlib import Path
import pandas as pd


DATA_PATH = Path("data/sme_sales_data.csv")
REPORT_PATH = Path("reports")
REPORT_PATH.mkdir(exist_ok=True)


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def calculate_kpis(df):
    kpis = {
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_profit": round(df["profit"].sum(), 2),
        "total_orders": df["invoice_id"].nunique(),
        "unique_customers": df["customer_id"].nunique(),
        "average_order_value": round(df["revenue"].sum() / df["invoice_id"].nunique(), 2),
        "profit_margin": round(df["profit"].sum() / df["revenue"].sum(), 4),
    }
    return kpis


def create_reports(df):
    monthly = df.groupby(pd.Grouper(key="order_date", freq="ME")).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("invoice_id", "nunique"),
        customers=("customer_id", "nunique")
    ).reset_index()
    monthly["avg_order_value"] = monthly["revenue"] / monthly["orders"]

    category = df.groupby("category").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        units_sold=("quantity", "sum"),
        orders=("invoice_id", "nunique")
    ).sort_values("revenue", ascending=False)

    region = df.groupby("region").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("invoice_id", "nunique")
    ).sort_values("revenue", ascending=False)

    channel = df.groupby("sales_channel").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("invoice_id", "nunique")
    ).sort_values("revenue", ascending=False)

    monthly.to_csv(REPORT_PATH / "monthly_kpis.csv", index=False)
    category.to_csv(REPORT_PATH / "category_performance.csv")
    region.to_csv(REPORT_PATH / "region_performance.csv")
    channel.to_csv(REPORT_PATH / "channel_performance.csv")

    return monthly, category, region, channel


if __name__ == "__main__":
    data = load_data()
    kpis = calculate_kpis(data)
    print("Business KPIs")
    for key, value in kpis.items():
        print(f"{key}: {value}")

    create_reports(data)
    print("Reports saved in /reports")
