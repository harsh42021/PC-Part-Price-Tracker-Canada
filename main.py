import json
from utils import get_price, send_email

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

price_history_file = "price_history.json"

# Load previous prices
try:
    with open(price_history_file, "r") as f:
        price_history = json.load(f)
except FileNotFoundError:
    price_history = {}

# Loop over components and retailers
for comp_type, part_numbers in config["components"].items():
    for part in part_numbers:
        for retailer in config["retailers"]["core"] + config["retailers"]["backup"]:
            price = get_price(part, retailer)
            if price is None:
                continue
            key = f"{part}_{retailer}"
            old_price = price_history.get(key)
            price_history[key] = price
            if old_price and price < old_price:
                if config["notifications"]["email"]:
                    send_email(f"Price drop for {part}", f"{retailer}: {old_price} → {price}")

# Save updated history
with open(price_history_file, "w") as f:
    json.dump(price_history, f, indent=4)
