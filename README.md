# Notification Service

A scalable, modular API service for sending and managing notifications across multiple channels (email, SMS, and in-app) with robust versioning, task queuing, and retry mechanisms.

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-channel notifications**: Send notifications via Email (Gmail API), SMS (Twilio), and in-app channels
- **API versioning**: Modular API design with v1 and v2 endpoints
- **Task queue processing**: Asynchronous notification delivery using Celery
- **Automatic retries**: Built-in retry mechanism for failed notifications
- **Scheduled notifications**: Schedule notifications for future delivery
- **User preference management**: Control notification preferences per user
- **Auto user creation**: Create users on demand when sending notifications
- **Daily digests**: Automated digest emails for unread notifications
- **Performance monitoring**: Celery Flower dashboard for task monitoring

## Architecture

The service follows a microservices architecture with the following components:

- **FastAPI**: Core API service with versioned endpoints
- **PostgreSQL**: Persistent storage for users and notifications
- **Celery**: Task queue for processing notifications asynchronously
- **RabbitMQ**: Message broker for Celery
- **Redis**: Result backend for Celery and for in-app notifications
- **Gmail API**: For sending email notifications
- **Twilio**: For sending SMS notifications

![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white) ![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)

## Installation

### Prerequisites

- Docker and Docker Compose
- Google API credentials for Gmail API
- Twilio account for SMS notifications

### Quick Start

1. Clone the repository:

```bash
git clone https://github.com/Surajkumarsaw1/notification-service.git
cd notification-service
```

2. Set up your environment variables:

```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Create a credentials directory and add your Google API credentials:

```bash
mkdir -p credentials
# Add your client_secret.json file to this directory
```

4. Build and start the services:

```bash
docker-compose up -d
```

## Configuration

The service can be configured through environment variables in the `.env` file:

```
# API settings
DEBUG=True
PROJECT_NAME=notification-service
VERSION=1.0.0
API_PREFIX=/api

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=notification_service
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Celery
CELERY_BROKER_URL=amqp://${RABBITMQ_USER}:${RABBITMQ_PASS}@rabbitmq:5672/
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Google Services - Gmail API
GOOGLE_CLIENT_SECRET_FILE=/app/credentials/client_secret.json
GMAIL_SENDER=your-email@gmail.com

# SMS - Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

## Usage

### Sending a Notification

```bash
curl -X POST "http://localhost:8000/api/v1/notifications/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "channels": ["email", "sms", "in-app"],
    "message": {
      "subject": "Account Security Alert",
      "body": "We detected a login to your account from a new device."
    },
    "metadata": {
      "priority": "high"
    }
  }'
```

### Getting User Notifications

```bash
curl -X GET "http://localhost:8000/api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479/notifications?status=all&type=all&page=1&limit=20"
```

### Using V2 API (with Enhanced Features) (Under Development)

```bash
curl -X POST "http://localhost:8000/api/v2/notifications/?priority=high" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "channels": ["email", "in-app"],
    "message": {
      "subject": "Payment Received",
      "body": "Your account has been credited with $100."
    }
  }'
```

## API Documentation

The API documentation is available at the following endpoints:

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Key endpoints:

- `POST /api/v1/notifications/`: Send a notification
- `GET /api/v1/notifications/{notification_id}`: Get notification status
- `GET /api/v1/users/{user_id}/notifications`: Get user notifications
- `POST /api/v2/notifications/cancel`: Cancel a pending notification (v2 only)

## Deployment

### Local Development

For local development, the Docker Compose setup is sufficient. Access the services at:

- API: [http://localhost:8000](http://localhost:8000)
- Flower Dashboard: [http://localhost:5555](http://localhost:5555)
- RabbitMQ Management: [http://localhost:15672](http://localhost:15672)

### Production Deployment Options

The service can be deployed to various platforms:

- **Cloud Platform Services**: DigitalOcean App Platform, Railway.app, Render.com
- **Container Orchestration**: AWS ECS, Google Cloud Run, DigitalOcean Kubernetes
- **Self-Hosted**: DigitalOcean or Linode VPS with Docker Compose

For production deployments, consider:

1. Setting up HTTPS with a reverse proxy
2. Configuring proper logging
3. Setting up database backups
4. Implementing monitoring with Prometheus and Grafana

## Troubleshooting

Common issues and solutions:

- **500 Internal Server Error**: Check the server logs for more details. Common causes include database connection issues, configuration errors, or code exceptions.

- **Redis "SECURITY ATTACK" Error**: Ensure you're using the correct Redis URL format (`redis://` not `http://`) in your configuration.

- **RabbitMQ Connection Issues**: Verify that you're using the AMQP protocol (`amqp://` not `http://`) for RabbitMQ connections.

- **Email/SMS Not Sending**: Check your Google API or Twilio credentials and verify the services are properly configured.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Last updated: May 19, 2025
