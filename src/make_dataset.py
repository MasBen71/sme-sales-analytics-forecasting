"""
Generate a synthetic SME retail sales dataset.

This script is useful if you want to regenerate the dataset or modify
the assumptions behind the synthetic business data.
"""

from pathlib import Path
import random
import numpy as np
import pandas as pd


def generate_dataset(output_path="data/sme_sales_data.csv", seed=42):
    np.random.seed(seed)
    random.seed(seed)

    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    categories = {
        "Office Supplies": ["Notebook", "Pen Set", "Desk Organizer", "Printer Paper", "Folders"],
        "Electronics": ["Wireless Mouse", "Keyboard", "USB-C Hub", "Monitor Stand", "Webcam"],
        "Home & Living": ["Desk Lamp", "Storage Box", "Wall Clock", "Plant Pot", "Cushion"],
        "Fitness": ["Yoga Mat", "Resistance Bands", "Water Bottle", "Foam Roller", "Skipping Rope"],
    }
    regions = ["Nicosia", "Limassol", "Larnaca", "Paphos", "Famagusta"]
    channels = ["Online", "Retail Store", "Marketplace"]
    segments = ["Consumer", "Small Business", "Enterprise"]
    customer_ids = [f"CUST-{i:04d}" for i in range(1, 551)]

    rows = []
    invoice_id = 10000

    for day in dates:
        month = day.month
        weekday = day.weekday()
        seasonal_boost = 1.35 if month in [11, 12] else 1.12 if month in [3, 4, 9] else 1.0
        weekend_factor = 0.75 if weekday >= 5 else 1.0
        trend_factor = 1 + ((day - dates[0]).days / len(dates)) * 0.35
        n_orders = np.random.poisson(12 * seasonal_boost * weekend_factor * trend_factor)

        for _ in range(n_orders):
            invoice_id += 1
            category = random.choices(list(categories.keys()), weights=[0.35, 0.25, 0.25, 0.15], k=1)[0]
            product = random.choice(categories[category])
            region = random.choices(regions, weights=[0.33, 0.25, 0.20, 0.14, 0.08], k=1)[0]
            channel = random.choices(channels, weights=[0.46, 0.34, 0.20], k=1)[0]
            segment = random.choices(segments, weights=[0.68, 0.24, 0.08], k=1)[0]
            customer = random.choice(customer_ids)

            if category == "Electronics":
                unit_price = np.random.normal(45, 13)
                quantity = np.random.choice([1, 1, 1, 2, 3])
                margin = np.random.normal(0.31, 0.06)
            elif category == "Office Supplies":
                unit_price = np.random.normal(9, 3)
                quantity = np.random.choice([1, 2, 3, 4, 5, 6], p=[.20, .25, .20, .15, .12, .08])
                margin = np.random.normal(0.38, 0.05)
            elif category == "Home & Living":
                unit_price = np.random.normal(22, 7)
                quantity = np.random.choice([1, 1, 2, 2, 3, 4])
                margin = np.random.normal(0.34, 0.05)
            else:
                unit_price = np.random.normal(18, 5)
                quantity = np.random.choice([1, 1, 2, 3, 4])
                margin = np.random.normal(0.36, 0.05)

            discount = random.choices([0, 0.05, 0.10, 0.15, 0.20], weights=[0.48, 0.20, 0.18, 0.10, 0.04], k=1)[0]
            unit_price = max(2.5, round(unit_price, 2))
            revenue = round(unit_price * quantity * (1 - discount), 2)
            profit = round(revenue * max(0.08, min(0.55, margin)), 2)

            rows.append({
                "invoice_id": f"INV-{invoice_id}",
                "order_date": day.date().isoformat(),
                "customer_id": customer,
                "customer_segment": segment,
                "region": region,
                "sales_channel": channel,
                "category": category,
                "product": product,
                "quantity": int(quantity),
                "unit_price": unit_price,
                "discount": discount,
                "revenue": revenue,
                "profit": profit,
            })

    df = pd.DataFrame(rows)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    dataset = generate_dataset()
    print(f"Dataset created with {len(dataset):,} rows.")
