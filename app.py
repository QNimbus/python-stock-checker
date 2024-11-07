from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add at the top of the file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

app = FastAPI()

PRODUCT_URL = "https://direct.playstation.com/nl-nl/buy-accessories/disc-drive-for-ps5-digital-edition-consoles"
OUT_OF_STOCK_TEXT = "Momenteel niet beschikbaar"

def check_availability():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(PRODUCT_URL, headers=headers)
        response.raise_for_status()
        
        logging.debug(f"Status Code: {response.status_code}")
        logging.debug(f"Content Length: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the out of stock text
        availability_elements = soup.find_all(string=OUT_OF_STOCK_TEXT)
        
        is_available = len(availability_elements) == 0
        
        return {
            "is_available": is_available,
            "url": PRODUCT_URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/check-ps5-disc-drive")
async def webhook_endpoint():
    result = check_availability()
    
    if result["is_available"]:
        # Here you could add notification logic (e.g., sending an email or push notification)
        print("PS5 Disc Drive is available!")
        
    return result

@app.get("/check")
async def check_endpoint():
    return check_availability()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
