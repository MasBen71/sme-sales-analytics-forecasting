"""
Customer segmentation using RFM analysis.

RFM stands for:
- Recency: how recently the customer purchased
- Frequency: how often the customer purchased
- Monetary: how much revenue the customer generated
"""

from pathlib import Path
import pandas as pd


DATA_PATH = Path("data/sme_sales_data.csv")
OUTPUT_PATH = Path("reports/customer_segments.csv")
OUTPUT_PATH.parent.mkdir(exist_ok=True)


def build_rfm_segments(df):
    df["order_date"] = pd.to_datetime(df["order_date"])
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency=("invoice_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()

    rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1])
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4])

    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )

    def label_customer(row):
        score_sum = int(row["r_score"]) + int(row["f_score"]) + int(row["m_score"])
        if score_sum >= 10:
            return "High Value"
        if score_sum >= 7:
            return "Growth Potential"
        if int(row["r_score"]) <= 2:
            return "At Risk"
        return "Low Value"

    rfm["customer_segment"] = rfm.apply(label_customer, axis=1)
    return rfm


if __name__ == "__main__":
    data = pd.read_csv(DATA_PATH)
    segments = build_rfm_segments(data)
    segments.to_csv(OUTPUT_PATH, index=False)
    print(f"Customer segmentation saved to {OUTPUT_PATH}")
    print(segments["customer_segment"].value_counts())
