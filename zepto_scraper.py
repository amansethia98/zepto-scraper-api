from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ✅ Base API URL
BASE_URL = "https://api.zepto.com/api/v2/store-products-by-store-subcategory-id"
STORE_ID = "fa5e892d-65d7-4da6-9bde-e1f22deb7b6f"

# ✅ Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

@app.route('/scrape', methods=['GET'])
def scrape():
    subcategory_id = request.args.get('subcategory_id')

    if not subcategory_id:
        return jsonify({"error": "Missing subcategory_id"}), 400

    all_products = []
    page_number = 1

    while True:
        api_url = f"{BASE_URL}?store_id={STORE_ID}&subcategory_id={subcategory_id}&page_number={page_number}"
        response = requests.get(api_url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            products = data.get("storeProducts", [])

            if not products:
                break  # 🚨 Stop when no more products are found

            for item in products:
                product = item.get("product", {})
                variant = item.get("productVariant", {})
                rating_summary = variant.get("ratingSummary", {})
                images = variant.get("images", [])

                # ✅ Extract additional product details
                product_details = {
                    "name": product.get("name", "N/A"),
                    "brand": product.get("brand", "N/A"),
                    "primary_category": item.get("primaryCategoryName", "N/A"),
                    "primary_subcategory": item.get("primarySubcategoryName", "N/A"),
                    "mrp": variant.get("mrp", 0) / 100,  # Convert from paisa
                    "discounted_price": item.get("discountedSellingPrice", 0) / 100,
                    "discount_percentage": item.get("discountPercent", 0),
                    "discount_amount": item.get("discountAmount", 0) / 100,
                    "super_saver_price": item.get("superSaverSellingPrice", 0) / 100,
                    "average_rating": rating_summary.get("averageRating", 0),
                    "total_ratings": rating_summary.get("totalRatings", 0),
                    "main_image_path": images[0]["path"] if images else "N/A",
                }

                all_products.append(product_details)

            page_number += 1
        else:
            break  # 🚨 Stop if API fails

    return jsonify(all_products)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
