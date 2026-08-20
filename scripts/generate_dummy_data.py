import os
import random
import csv
from datetime import datetime, timedelta

def generate_dummy_enterprise_data(num_records=500):
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed/gold", exist_ok=True)
    os.makedirs("data/processed/silver", exist_ok=True)
    os.makedirs("data/processed/bronze", exist_ok=True)

    cities = ["New York", "San Francisco", "Chicago", "Austin", "Seattle", "London", "Tokyo", "Berlin", "Toronto", "Sydney"]
    categories = ["Cloud Software", "Enterprise Hardware", "Analytics Suite", "AI Infrastructure", "Cybersecurity"]
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "PENDING", "CANCELLED"]

    # 1. Generate Customers
    customers = []
    for i in range(1, 51):
        cust_id = f"CUST-{1000 + i}"
        name = f"Enterprise Client {i}"
        email = f"contact@client{i}.com"
        city = random.choice(cities)
        customers.append({
            "customer_key": i,
            "customer_id": cust_id,
            "name": name,
            "email": email,
            "city": city
        })

    # Save dim_customers.csv
    with open("data/raw/dim_customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_key", "customer_id", "name", "email", "city"])
        writer.writeheader()
        writer.writerows(customers)

    # 2. Generate Products
    products = []
    prod_names = {
        "Cloud Software": ["DataPulse Suite v4", "Cloud Sync Pro", "API Gateway Enterprise"],
        "Enterprise Hardware": ["Quantum Blade Server X1", "Storage Array SAN-500", "Edge Compute Gateway"],
        "Analytics Suite": ["BI Analytics Studio", "Stream Processing Hub", "Predictive Engine AI"],
        "AI Infrastructure": ["GPU Acceleration Node", "Model Training Pipeline", "LLM Inference Engine"],
        "Cybersecurity": ["Zero Trust Shield", "Security Audit Agent", "Identity Vault Pro"]
    }

    prod_key = 1
    for category, names in prod_names.items():
        for name in names:
            price = round(random.uniform(500.0, 15000.0), 2)
            products.append({
                "product_key": prod_key,
                "product_id": f"PROD-{2000 + prod_key}",
                "name": name,
                "category": category,
                "unit_price": price
            })
            prod_key += 1

    # Save dim_products.csv
    with open("data/raw/dim_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_key", "product_id", "name", "category", "unit_price"])
        writer.writeheader()
        writer.writerows(products)

    # 3. Generate Fact Sales
    sales = []
    start_date = datetime(2026, 1, 1)
    
    for i in range(1, num_records + 1):
        cust = random.choice(customers)
        prod = random.choice(products)
        qty = random.randint(1, 5)
        amount = round(prod["unit_price"] * qty * random.uniform(0.9, 1.1), 2)
        status = random.choice(statuses)
        days_offset = random.randint(0, 230)
        order_dt = start_date + timedelta(days=days_offset, hours=random.randint(8, 18), minutes=random.randint(0, 59))
        
        sales.append({
            "sales_key": i,
            "order_id": f"ORD-2026-{10000 + i}",
            "customer_key": cust["customer_key"],
            "customer_id": cust["customer_id"],
            "customer_name": cust["name"],
            "city": cust["city"],
            "product_key": prod["product_key"],
            "product_name": prod["name"],
            "category": prod["category"],
            "amount": amount,
            "quantity": qty,
            "status": status,
            "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S")
        })

    # Save fact_sales.csv
    with open("data/raw/fact_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sales_key", "order_id", "customer_key", "customer_id", "customer_name",
            "city", "product_key", "product_name", "category", "amount", "quantity", "status", "order_date"
        ])
        writer.writeheader()
        writer.writerows(sales)

    # 4. Also update test_orders.csv
    with open("data/raw/test_orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "amount", "status"])
        writer.writeheader()
        for s in sales[:50]:
            writer.writerow({
                "order_id": s["order_id"],
                "customer_id": s["customer_id"],
                "amount": s["amount"],
                "status": s["status"]
            })

    print(f"Generated {len(customers)} customers, {len(products)} products, and {len(sales)} sales records.")

if __name__ == "__main__":
    generate_dummy_enterprise_data(600)
