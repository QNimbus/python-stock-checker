from fastapi import FastAPI, HTTPException, Request, Depends
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import logging
import secrets
from fastapi import Response
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True  # This ensures our config takes precedence
)

# Load environment variables
load_dotenv()

# Generate API key at startup
API_KEY = secrets.token_urlsafe(32)
logging.info(f"Generated API key: Bearer {API_KEY}")

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.warning(f"HTTP {exc.status_code} error: {exc.detail} - Request: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Replace the middleware with a more specific route handler
@app.api_route("/{path:path}", methods=["GET"])
async def block_get_requests(path: str):
    raise HTTPException(status_code=405, detail="GET requests are not allowed")

# Move the auth check to a dependency instead of middleware
async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer token")
    
    token = auth_header.split("Bearer ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")
    return token

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

@app.post("/webhook/check-ps5-disc-drive", dependencies=[Depends(verify_token)])
async def webhook_endpoint():
    result = check_availability()
    
    if result["is_available"]:
        # Here you could add notification logic (e.g., sending an email or push notification)
        print("PS5 Disc Drive is available!")
        
    return result


if __name__ == "__main__":
    import uvicorn
    
    # Add exception handler directly to the FastAPI app
    @app.exception_handler(Exception)
    async def custom_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            if 400 <= exc.status_code < 500:
                # Log 4xx errors with request details
                logging.warning(f"HTTP {exc.status_code} error: {exc.detail} - Request: {request.url.path}")
            else:
                # Log other HTTP exceptions as errors
                logging.error(f"HTTP {exc.status_code} error: {exc.detail}", exc_info=False)
        else:
            # Log unexpected exceptions as errors with full stack trace
            logging.error("Unexpected error occurred", exc_info=False)

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logging.error("Server failed to start", exc_info=False)
