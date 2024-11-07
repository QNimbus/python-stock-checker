# PS5 Disc Drive Stock Checker

A FastAPI application that monitors the availability of the PS5 disc drive on the PlayStation website.

## Features

- Webhook endpoint for IFTTT integration
- Web scraping to check product availability
- Debug logging
- Browser-accessible endpoint for manual checks

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/QNimbus/python-stock-checker
   cd python-stock-checker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. The server will start at `http://localhost:8000`

### Available Endpoints

- GET `/check` - Check availability via browser
- POST `/webhook/check-ps5-disc-drive` - Webhook endpoint for webservices like IFTTT
- Interactive API docs available at `/docs`

## Testing with external services

To test with external services, you'll need to make your local server accessible to the internet using ngrok.
You have two options:

### Option 1: Using Docker (recommended)

1. Build and run the container:
   ```bash
   docker build -t stock-checker .
   docker run --name stock-checker --rm -p 8000:8000 -e NGROK_AUTH_TOKEN=your_token_here stock-checker
   ```

The container will automatically:
- Start the FastAPI application
- Configure ngrok with your auth token
- Display the public ngrok URL
- Create a tunnel to your application

### Option 2: Manual Setup

1. Sign up for a free account at https://ngrok.com/

2. Install ngrok from https://ngrok.com/download

3. Set up your authtoken (only needed once):
   ```bash
   ngrok config add-authtoken your_auth_token_here
   ```

4. Start ngrok (in a separate terminal):
   ```bash
   ngrok http 8000
   ```

## Access Points

- FastAPI app: http://localhost:8000
- FastAPI docs: http://localhost:8000/docs
- Ngrok interface: http://localhost:4040

## Debugging

- Logs are written to `app.log`
- HTML content is saved to `debug_output.html` for inspection
- Visit `http://localhost:4040` to see ngrok traffic inspection

## Environment Variables

Create a `.env` file in the root directory:
```env
# Add your environment variables here
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
