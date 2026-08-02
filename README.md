# 🚀 DevOps Task Manager API

A production-ready RESTful Task Management API built with **Flask**, **PostgreSQL**, **SQLAlchemy**, and **JWT Authentication**, following modern DevOps practices including **Docker**, **GitHub Actions CI**, **Alembic database migrations**, and **Render deployment**.

This project demonstrates how to build, test, containerize, and deploy a secure backend application using industry-standard tools and best practices.

---

# ✨ Features

* RESTful CRUD operations for task management
* User authentication using JWT
* User-specific task access
* PostgreSQL database with SQLAlchemy ORM
* Database migrations using Alembic
* Swagger/OpenAPI documentation with Flask-RESTX
* Dockerized application
* Separate Development and Production Docker Compose configurations
* Gunicorn production server
* Nginx reverse proxy configuration
* Health check endpoints
* Structured application logging
* GitHub Actions Continuous Integration
* Production deployment on Render
* Secure Docker image

  * Non-root user
  * Read-only filesystem
  * Dropped Linux capabilities
  * No New Privileges

---

# 🛠 Tech Stack

## Backend

* Python 3.13
* Flask
* Flask-RESTX
* Flask-JWT-Extended
* SQLAlchemy
* Alembic
* Gunicorn

## Database

* PostgreSQL

## DevOps

* Docker
* Docker Compose
* GitHub Actions
* Render
* Nginx

---

# 🏗 Architecture

```
                Client
                   │
                   ▼
              Nginx (Production)
                   │
                   ▼
          Flask REST API (Gunicorn)
                   │
                   ▼
            SQLAlchemy ORM
                   │
                   ▼
              PostgreSQL
```

---

# 📁 Project Structure

```
.
├── app
│   ├── api
│   ├── models
│   ├── services
│   ├── utils
│   ├── database.py
│   ├── config.py
│   └── __init__.py
│
├── migrations
├── nginx
├── tests
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── app.py
├── requirements.txt
└── README.md
```

---

# 🔐 Authentication

Authentication is implemented using **JWT (JSON Web Tokens).**

Protected endpoints require the following header:

```
Authorization: Bearer <JWT_TOKEN>
```

---

# 📚 API Documentation

Interactive Swagger documentation is available at:

```
/docs
```

Example:

```
http://localhost:5000/docs
```

or

```
https://devops-task-manager-7n2q.onrender.com/docs
```

---

# ❤️ Health Check

The application exposes health endpoints for monitoring.

```
GET /system/health
```

Response:

```json
{
  "status": "healthy"
  "database": "connected"
}
```

---

# 🚀 Running Locally

## Clone the repository

```bash
git clone https://github.com/KartikSharma0609/devops-task-manager.git
cd devops-task-manager
```

## Create a virtual environment

```bash
python -m venv venv
```

## Activate

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```powershell
venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure environment variables

Create a `.env` file containing your database credentials and JWT secret.

## Run migrations

```bash
flask db upgrade
```

## Start the application

```bash
python app.py
```

---

# 🐳 Running with Docker

Development

```bash
docker compose up --build
```

Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

---

# ⚙ Continuous Integration

GitHub Actions automatically performs:

* Dependency installation
* PostgreSQL service startup
* Database migrations
* Automated test execution

Every push and pull request is validated before merging.

---

# ☁ Deployment

The application is deployed on **Render**.

Deployment includes:

* Docker container
* PostgreSQL database
* Gunicorn
* Automatic database migrations
* Health checks
* Production environment variables

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest
```

Current test coverage includes:

* Authentication
* Task CRUD operations
* Health endpoints
* API functionality

---

# 🔒 Security

* JWT Authentication
* Password hashing
* User-specific resource authorization
* Non-root Docker user
* Read-only container filesystem
* Dropped Linux capabilities
* Health monitoring
* Structured logging

---

# 🚧 Future Improvements

* API Versioning
* Redis Caching
* Role-Based Access Control (RBAC)
* Rate Limiting
* Refresh Tokens
* Kubernetes Deployment
* Terraform Infrastructure
* Prometheus & Grafana Monitoring
* Jenkins CI/CD Pipeline

---

# 👨‍💻 Author

**Kartik Sharma**

Aspiring DevOps Engineer

* GitHub: *Add your GitHub profile*
* LinkedIn: *Add your LinkedIn profile*

---

# ⭐ If you found this project useful, consider giving it a star!
