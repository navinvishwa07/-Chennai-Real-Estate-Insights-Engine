from bs4 import BeautifulSoup
import pandas as pd

# 1. Paste your helper function here (The one we fixed earlier)
def parse_amount(text):
    if not text: return 0
    text = text.replace("₹", "").strip()
    if "Cr" in text:
        text = text.replace("Cr", "").strip()
        return int(float(text) * 10_000_000)
    elif "Lac" in text:
        text = text.replace("Lacs", "").replace("Lac", "").strip()
        return int(float(text) * 100_000)
    else:
        return 0

# 2. Load the Local HTML (The file you just saved)
print("Loading local HTML file...")
with open("chennai_housing.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# 3. Find all Property Cards
cards = soup.find_all('div', class_='mb-srp__card')
print(f"Found {len(cards)} listings in your file.")

data = []

for card in cards:
    # --- EXTRACT PRICE (We know this works) ---
    price_tag = card.find('div', class_='mb-srp__card__price--amount')
    raw_price = price_tag.text.strip() if price_tag else "0"
    clean_price = parse_amount(raw_price)

    # --- EXTRACT TITLE (Challenge A) ---
    # Look for a class that looks like 'mb-srp__card--title'
    title_tag = card.find('h2', class_='mb-srp__card--title') 
    title = title_tag.text.strip() if title_tag else "Unknown"

    # --- EXTRACT SQFT (Challenge B) ---
    # This is tricky. It's usually inside a specific summary div.
    # On MagicBricks, the area is often just a number followed by "sqft" text.
    # For now, let's try to find the specific class 'mb-srp__card__summary--value'
    sqft_tag = card.find('div', class_='mb-srp__card__summary--value')
    sqft = sqft_tag.text.strip() if sqft_tag else "0"

    # Append to list
    data.append({
        'title': title,
        'price_raw': raw_price,
        'price_numeric': clean_price,
        'sqft': sqft
    })

# 4. Preview the Data
df = pd.DataFrame(data)
print(df.head())

data = []

for card in cards:
    # 1. Price (Keep existing)
    price_tag = card.find('div', class_='mb-srp__card__price--amount')
    raw_price = price_tag.text.strip() if price_tag else "0"
    clean_price = parse_amount(raw_price)

    # 2. Title & Location Extraction
    title_tag = card.find('h2', class_='mb-srp__card--title')
    title = title_tag.text.strip() if title_tag else "Unknown"
    
    # Logic: "3 BHK Flat for Sale in Mogappair East Chennai"
    # We split by " in " and take the second part
    if " in " in title:
        location = title.split(" in ")[-1].strip()
    else:
        location = "Chennai"

    # 3. Sqft Cleaning
    sqft_tag = card.find('div', class_='mb-srp__card__summary--value')
    raw_sqft = sqft_tag.text.strip() if sqft_tag else "0"
    
    # Logic: Turn "1943 sqft" -> 1943
    try:
        clean_sqft = int(raw_sqft.split()[0]) # Take the first word, turn to int
    except:
        clean_sqft = 0

    # 4. Filter bad data (Optional but good)
    # If price is 0 or sqft is 0, skip this listing
    if clean_price > 0 and clean_sqft > 0:
        data.append({
            'title': title,
            'location': location,
            'price': clean_price,
            'sqft': clean_sqft,
            'price_per_sqft': int(clean_price / clean_sqft) # <--- Valuable Feature!
        })

# Save to CSV (This is the file our App will read)
df = pd.DataFrame(data)
df.to_csv("chennai_housing_clean.csv", index=False)
print("✅ Success! Saved 'chennai_housing_clean.csv' with", len(df), "clean listings.")
print(df.head())