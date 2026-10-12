import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

products = [
    {"id": 1, "name": "Wireless Headphones", "price": 79.99,
     "category": "Electronics", "image": "headphones.png"},
    {"id": 2, "name": "Running Shoes", "price": 59.99,
     "category": "Fashion", "image": "shoes.png"},
    {"id": 3, "name": "Coffee Mug", "price": 14.99,
     "category": "Home", "image": "mug.png"}
]

def generate_listing(product):
    image_path = BASE_DIR / "product_images" / product["image"]

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Analyze this product image. "
                        f"Product: {product['name']}, "
                        f"Price: ${product['price']}, "
                        f"Category: {product['category']}. "
                        "Create an e-commerce listing as JSON with "
                        "title, description, features, and keywords. "
                        "Describe visible details accurately. "
                        "Do not invent specifications."
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded}"
                    }
                }
            ]
        }],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

results = []

for product in products:
    try:
        print(f"Analyzing: {product['name']}")
        listing = generate_listing(product)
        results.append({"product_id": product["id"], **listing})
        print("SUCCESS!")
    except Exception as e:
        print(f"ERROR: {e}")

output = BASE_DIR / "product_listings.json"
with open(output, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved {len(results)} listings to {output}")
