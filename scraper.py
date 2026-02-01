from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. Setup the Chrome Driver
# (This downloads the correct driver for your Chrome version automatically)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 2. Go to Real Website (MagicBricks Chennai - 2BHK & 3BHK)
url = "https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=2,3&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Chennai"
print(f"Navigativing{url}")
driver.get(url)

# Give it time to load the initial page
time.sleep(5) 

# 3. The Scroll Loop (The "Spy" Logic)
print("Starting scroll loop...")
for i in range(5): # Let's scroll 5 times for now
    # A. Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # B. Wait for the "pop" (loading new data)
    print(f"Scrolled {i+1} times. Waiting for data to load...")
    time.sleep(4) # Wait 4 seconds for valid data load
    
# 4. Save the Data
# Instead of scraping right now, we SAVE the HTML.
# This prevents us from getting banned for hitting the site too often.
with open("chennai_housing.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("✅ Success! HTML saved to 'chennai_housing.html'")
driver.quit()