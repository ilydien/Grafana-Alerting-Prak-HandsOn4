import uuid
import random
from datetime import datetime, timedelta

PRODUCTS = [
    {"name": "MacBook Pro M4", "category": "Komputer", "price_range": (18000000, 35000000)},
    {"name": "ASUS ROG Zephyrus", "category": "Komputer", "price_range": (15000000, 30000000)},
    {"name": "iPhone 16 Pro", "category": "Gadget", "price_range": (16000000, 25000000)},
    {"name": "Samsung Galaxy S25", "category": "Gadget", "price_range": (12000000, 20000000)},
    {"name": "iPad Air M3", "category": "Gadget", "price_range": (8000000, 15000000)},
    {"name": "Sony WH-1000XM6", "category": "Audio", "price_range": (3000000, 5000000)},
    {"name": "AirPods Pro 3", "category": "Audio", "price_range": (2500000, 4000000)},
    {"name": "Logitech MX Master 3S", "category": "Aksesoris", "price_range": (800000, 1500000)},
    {"name": "Samsung Galaxy Watch 7", "category": "Gadget", "price_range": (4000000, 7000000)},
    {"name": "Apple Watch Ultra 3", "category": "Gadget", "price_range": (10000000, 15000000)},
    {"name": "Dell UltraSharp 27", "category": "Elektronik", "price_range": (5000000, 9000000)},
    {"name": "Razer DeathAdder V3", "category": "Aksesoris", "price_range": (500000, 1200000)},
    {"name": "JBL Charge 6", "category": "Audio", "price_range": (1500000, 3000000)},
    {"name": "MacBook Air M4", "category": "Komputer", "price_range": (13000000, 18000000)},
    {"name": "Google Pixel 10", "category": "Gadget", "price_range": (10000000, 16000000)},
]

LOCATIONS = ["Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Medan", "Makassar", "Denpasar", "Semarang"]


def generate_transactions(count: int = 60):
    now = datetime.now()
    transactions = []

    for i in range(count):
        product = random.choice(PRODUCTS)
        qty = random.randint(1, 10)
        unit_price = random.randint(product["price_range"][0], product["price_range"][1])
        revenue_idr = unit_price * qty

        timestamp = now - timedelta(seconds=i * 37)

        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "timestamp": timestamp.isoformat(),
            "product_name": product["name"],
            "category": product["category"],
            "quantity": qty,
            "revenue_idr": revenue_idr,
            "location": random.choice(LOCATIONS),
        })

    return transactions
