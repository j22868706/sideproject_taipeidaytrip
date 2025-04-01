FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && \
    apt-get install -y nginx vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up Nginx configuration
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Set working directory
WORKDIR /app

# Copy requirements.txt first to leverage Docker's cache
COPY ./app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copy application files
COPY ./app /app/

# Ensure directory structure exists
RUN mkdir -p /app/templates /app/static/css /app/static/javaScript /app/static/images

# Set up startup script
COPY start.sh /
RUN chmod +x /start.sh

# Expose ports
EXPOSE 80 3000

# Startup command
CMD ["/bin/bash", "-c", "/start.sh"]