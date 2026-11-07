import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_datasets():
    np.random.seed(42)
    random.seed(42)

    regions = ["North", "South", "East", "West", "Central"]
    states_by_region = {
        "North": ["Delhi", "Punjab", "Uttar Pradesh", "Haryana"],
        "South": ["Karnataka", "Tamil Nadu", "Kerala", "Telangana"],
        "East": ["West Bengal", "Odisha", "Bihar", "Assam"],
        "West": ["Maharashtra", "Gujarat", "Goa", "Rajasthan"],
        "Central": ["Madhya Pradesh", "Chhattisgarh"]
    }
    categories = {
        "Electronics": ["Phones", "Laptops", "Accessories", "Printers"],
        "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "Clothing": ["Shirts", "Trousers", "Dresses", "Footwear"],
        "Office Supplies": ["Paper", "Binders", "Appliances", "Art"]
    }

    n_rows = 500
    start_date = datetime(2023, 1, 1)
    
    rows = []
    for i in range(1, n_rows + 1):
        order_id = f"ORD-{2023 + (i % 2)}-{1000 + i}"
        days_offset = random.randint(0, 720)
        order_date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        region = random.choice(regions)
        state = random.choice(states_by_region[region])
        
        category = random.choice(list(categories.keys()))
        sub_category = random.choice(categories[category])
        product_name = f"{sub_category} {random.choice(['Standard', 'Plus', 'Pro', 'Ultra', 'Premium'])}"
        
        sales = round(float(np.random.gamma(shape=3.0, scale=800.0)), 2)
        quantity = int(np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.3, 0.25, 0.15, 0.1, 0.08, 0.05, 0.04, 0.03]))
        discount = round(float(random.choice([0.0, 0.05, 0.1, 0.15, 0.2, 0.25])), 2)
        
        # profit depends on sales and discount with some variance
        base_margin = random.uniform(0.1, 0.35)
        profit = round(sales * (base_margin - discount * 0.8), 2)
        
        rows.append({
            "Order_ID": order_id,
            "Order_Date": order_date,
            "Region": region,
            "State": state,
            "Category": category,
            "Sub_Category": sub_category,
            "Product_Name": product_name,
            "Sales": sales,
            "Quantity": quantity,
            "Discount": discount,
            "Profit": profit
        })

    df = pd.DataFrame(rows)
    df.to_csv("sample_datasets/superstore_sales.csv", index=False)
    print("Created sample_datasets/superstore_sales.csv with", len(df), "rows")

    # Multi-sheet Excel
    df_2023 = df[df["Order_Date"].str.startswith("2023")].copy()
    df_2024 = df[df["Order_Date"].str.startswith("2024")].copy()
    
    summary = df.groupby("Category").agg({
        "Sales": "sum",
        "Profit": "sum",
        "Quantity": "sum"
    }).reset_index()

    with pd.ExcelWriter("sample_datasets/retail_sales_multisheet.xlsx", engine="openpyxl") as writer:
        df_2023.to_excel(writer, sheet_name="Sales_2023", index=False)
        df_2024.to_excel(writer, sheet_name="Sales_2024", index=False)
        summary.to_excel(writer, sheet_name="Category_Summary", index=False)
    print("Created sample_datasets/retail_sales_multisheet.xlsx with 3 sheets")

if __name__ == "__main__":
    generate_datasets()

