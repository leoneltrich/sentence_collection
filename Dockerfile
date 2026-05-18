FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app:create_app
ENV FLASK_RUN_HOST=0.0.0.0

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Run the entrypoint script
CMD ["./entrypoint.sh"]