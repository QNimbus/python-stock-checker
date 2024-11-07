# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install tini for proper init process and other required packages
RUN apt-get update && apt-get install -y \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create a startup script
RUN echo '#!/bin/bash\n\
trap "kill 0" SIGINT SIGTERM\n\
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
