# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY bot.py .
COPY scraper.py .
COPY binance_checker.py .

# Copy the .env file and notified_tickers.json
# Note: For .env, using docker-compose's env_file is often preferred for flexibility.
# Note: For notified_tickers.json, using a volume is essential for persistence.
COPY .env .
COPY notified_tickers.json .

# Command to run the application
CMD ["python3", "bot.py"]
