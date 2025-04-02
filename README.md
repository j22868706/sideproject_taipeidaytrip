# Taipei Day Trip

## 📍 Project Overview
A comprehensive travel information platform for Taipei, providing detailed tourist attractions and itinerary recommendations.

## 🚀 Technical Architecture
- **Backend**: Flask (Python 3.8)
- **Database**: Amazon RDS (MySQL)
- **Deployment**: Docker Containerization
- **Infrastructure**: AWS EC2
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx

## 🛠 Key Technical Challenges and Solutions

### Database Connection Resilience
Our application implements a robust database connection strategy to ensure reliability:

```python
def test_database_connection(max_retries=5, delay=10):
    for attempt in range(max_retries):
        try:
            connection = pymysql.connect(
                host=os.getenv("host"),
                port=int(os.getenv("port")),
                user=os.getenv("user"),
                password=os.getenv("password"),
                database=os.getenv("database"),
                connect_timeout=30
            )
            print("Database connection successful!")
            connection.close()
            return True
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            time.sleep(delay)
    
    return False
```

### Gunicorn Configuration Optimization
Improved Gunicorn startup script for better performance and logging:

```bash
gunicorn \
    --bind 0.0.0.0:3000 \
    --workers 4 \
    --worker-class sync \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    app:app
```

### Docker Containerization
Streamlined Dockerfile for efficient deployment:

```dockerfile
FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

COPY ./app /app/

EXPOSE 80 3000

CMD ["/bin/bash", "-c", "/start.sh"]
```

## 🔒 Security and Performance

### Environment Configuration
- Secure management of sensitive configuration using environment variables
- Restricted container network access
- Comprehensive logging and monitoring

## 🔧 Deployment Workflow
Automated CI/CD pipeline using GitHub Actions:
- Automated testing
- Docker image build
- Secure deployment to AWS EC2

## 📋 Troubleshooting
1. Check container logs
```bash
sudo docker logs app
```

2. Verify network connections
```bash
telnet RDS_ENDPOINT 3306
```

## 🚧 Future Improvements
- Enhanced monitoring and alerting
- Automatic scaling
- Advanced caching strategies
- Performance optimization

## 📬 Contact
Email: j22868706@gmail.com
