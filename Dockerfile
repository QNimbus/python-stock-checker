# Use a lightweight Ubuntu image
FROM ubuntu:22.04

# Set working directory
WORKDIR /app

# Install Python and other required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    unzip \
    jq \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz \
    && tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin \
    && rm ngrok-v3-stable-linux-amd64.tgz

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
trap "kill 0" SIGINT SIGTERM\n\
\n\
ngrok config add-authtoken $NGROK_AUTH_TOKEN\n\
\n\
# Start ngrok in the background\n\
ngrok http 8000 > /dev/null 2>&1 & \n\
ngrok_pid=$!\n\
\n\
# Wait for ngrok to start\n\
sleep 5\n\
\n\
# Get and display the public URL\n\
echo "Ngrok Status:"\n\
curl -s http://localhost:4040/api/tunnels | jq -r ".tunnels[0].public_url"\n\
\n\
# Start the Python app\n\
python3 app.py & \n\
app_pid=$!\n\
\n\
# Wait for any process to exit\n\
wait -n\n\
\n\
# Exit with status of process that exited first\n\
exit $?' > /app/start.sh \
    && chmod +x /app/start.sh

# Use tini as init
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the startup script
CMD ["/app/start.sh"]
