import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

#1. Set up the geocoder
# A 'user agent' required so OpenStreetMap knows who is connecting
geolocator = Nominatim(user_agent = "chennai_real_estate_project")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

#2. Load your cleaned data
print("Loading data")
df = pd.read_csv("chennai_housing_clean.csv")

#3. Get Unique Locations
# We only want to look up each neighborhood once to be fast
unique_locs = df['location'].unique()
print(f"Found {len(unique_locs)} unique neighborhoods.")

loc_data = []

print("Starting geocoding (This will take about 30 to 60 seconds) . . .")

for loc in unique_locs:
    try:
        # We append ", Chennai" to ensure we don't find a "T Nagar" in another city
        search_query = f"{loc}, Chennai"
        location = geolocator.geocode(search_query)
        
        if location:
            print(f"✅ Found: {loc} -> {location.latitude}, {location.longitude}")
            loc_data.append({'location': loc, 'lat':location.latitude, 'lon': location.longitude})
            
        else:
            print(f"❌ Could not find: {loc}")
            
    except Exception as e:
        print(f"⚠️ Error with {loc}: {e}")
        
# 4. Merge coordinates back into the main data
coords_df = pd.DataFrame(loc_data)
df_final = df.merge(coords_df, on='location', how = 'left')
# Drop listings where we couldn't find a location (so they don't break the map)
df_final = df_final.dropna(subset=['lat', 'lon'])

df_final.to_csv("chennai_housing_final.csv", index=False)
print(f"🎉 Success! Saved 'chennai_housing_final.csv' with {len(df_final)} mappable listings.")