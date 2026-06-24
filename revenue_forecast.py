"""
Simple monthly revenue forecasting.

This is intentionally simple and explainable for a business analytics portfolio.
It uses a linear trend model with month information to forecast future revenue.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


DATA_PATH = Path("data/sme_sales_data.csv")
OUTPUT_PATH = Path("reports/revenue_forecast.csv")
OUTPUT_PATH.parent.mkdir(exist_ok=True)


def forecast_revenue(df, periods=3):
    df["order_date"] = pd.to_datetime(df["order_date"])

    monthly = df.groupby(pd.Grouper(key="order_date", freq="ME")).agg(
        revenue=("revenue", "sum")
    ).reset_index()

    monthly["month_index"] = np.arange(len(monthly))
    monthly["month"] = monthly["order_date"].dt.month

    X = monthly[["month_index", "month"]]
    y = monthly["revenue"]

    model = LinearRegression()
    model.fit(X, y)

    future_dates = pd.date_range(
        monthly["order_date"].max() + pd.offsets.MonthEnd(1),
        periods=periods,
        freq="ME"
    )

    future = pd.DataFrame({
        "order_date": future_dates,
        "month_index": np.arange(len(monthly), len(monthly) + periods),
        "month": future_dates.month
    })

    future["forecast_revenue"] = model.predict(future[["month_index", "month"]])
    future["forecast_revenue"] = future["forecast_revenue"].round(2)

    return future


if __name__ == "__main__":
    data = pd.read_csv(DATA_PATH)
    forecast = forecast_revenue(data, periods=3)
    forecast.to_csv(OUTPUT_PATH, index=False)
    print(forecast)
    print(f"Forecast saved to {OUTPUT_PATH}")
