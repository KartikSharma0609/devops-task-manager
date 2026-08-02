# 🚀 DevOps Task Manager API

A **production-ready REST API** built using **Flask**, **PostgreSQL**, and **SQLAlchemy**, following modern DevOps practices including **Docker**, **GitHub Actions CI**, **Alembic database migrations**, **JWT Authentication**, **Gunicorn**, **Nginx**, and **Render deployment**.

The project demonstrates the complete backend development lifecycle—from designing secure REST APIs to containerization, automated testing, CI, and production deployment.

---

# 🌐 Live Demo

**API Base URL**

```
https://devops-task-manager-7n2q.onrender.com
```

**Swagger Documentation**

```
https://devops-task-manager-7n2q.onrender.com/docs
```

---

# 📸 Project Screenshots

### Swagger UI

```
docs/images/swagger.png
```

### GitHub Actions Pipeline

```
docs/images/github-actions.png
```

### Render Deployment

```
docs/images/render-dashboard.png
```

### Docker Containers

```
docs/images/docker-containers-1.png
docs/images/docker-containers-2.png
```

---

# ✨ Features

## Backend

* RESTful API built with Flask-RESTX
* JWT Authentication
* User Registration & Login
* User-specific task management
* Complete CRUD operations
* SQLAlchemy ORM
* Alembic database migrations
* Swagger/OpenAPI documentation

## Database

* PostgreSQL
* SQLAlchemy ORM
* Database migrations with Alembic

## DevOps

* Docker
* Docker Compose (Development & Production)
* Gunicorn WSGI Server
* Nginx Reverse Proxy
* GitHub Actions CI Pipeline
* Production deployment on Render

## Monitoring

* Health Check endpoint
* Structured logging
* Database connectivity check

## Security

* JWT Authentication
* Protected endpoints
* Non-root Docker user
* Read-only container filesystem
* Dropped Linux capabilities
* No New Privileges
* Environment-based configuration

---

# 🛠 Tech Stack

| Category           | Technologies           |
| ------------------ | ---------------------- |
| Language           | Python 3.13            |
| Framework          | Flask, Flask-RESTX     |
| Database           | PostgreSQL             |
| ORM                | SQLAlchemy             |
| Authentication     | Flask-JWT-Extended     |
| Database Migration | Alembic                |
| Web Server         | Gunicorn               |
| Reverse Proxy      | Nginx                  |
| Containerization   | Docker, Docker Compose |
| CI                 | GitHub Actions         |
| Deployment         | Render                 |
| Documentation      | Swagger/OpenAPI        |

---

# 🏗 System Architecture

```
                    Client
                       │
                       ▼
                 Nginx (Production)
                       │
                       ▼
               Gunicorn WSGI Server
                       │
                       ▼
                Flask REST API
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       JWT Authentication   SQLAlchemy ORM
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

Protected endpoints require a JWT access token.

Example header:

```
Authorization: Bearer <JWT_TOKEN>
```

Authentication flow:

```
Register

↓

Login

↓

Receive JWT

↓

Access Protected Endpoints
```

---

# 📚 API Endpoints

## Authentication

| Method | Endpoint       |
| ------ | -------------- |
| POST   | /auth/register |
| POST   | /auth/login    |

## Tasks

| Method | Endpoint    |
| ------ | ----------- |
| GET    | /tasks      |
| POST   | /tasks      |
| PUT    | /tasks/{id} |
| DELETE | /tasks/{id} |

## System

| Method | Endpoint        |
| ------ | --------------- |
| GET    | /system         |
| GET    | /system/health  |
| GET    | /system/db-test |

Interactive documentation:

```
/docs
```

---

# 🚀 Local Development

## Clone Repository

```bash
git clone https://github.com/KartikSharma0609/devops-task-manager.git

cd devops-task-manager
```

## Create Virtual Environment

```bash
python -m venv venv
```

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```powershell
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file.

## Apply Database Migrations

```bash
flask db upgrade
```

## Start Application

```bash
python app.py
```

---

# 🐳 Docker

Development

```bash
docker compose up --build
```

Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

---

# ⚙ CI/CD Pipeline

GitHub Actions automatically performs:

* Checkout repository
* Install dependencies
* Start PostgreSQL service
* Apply Alembic migrations
* Execute automated tests
* Validate every push & pull request

Pipeline:

```
Git Push

↓

GitHub Actions

↓

Install Dependencies

↓

Run Database Migrations

↓

Execute Tests

↓

Build Successful ✅
```

---

# ☁ Deployment

The application is deployed on **Render**.

Deployment includes:

* Docker container
* PostgreSQL database
* Gunicorn
* Automatic database migrations
* Health monitoring
* Environment variable management

---

# ❤️ Health Monitoring

Health endpoint:

```
GET /system/health
```

Example Response

```json
{
    "status": "healthy"
    "database": "connected"
}
```

---

# 🧪 Testing

Run the test suite:

```bash
pytest
```

Current coverage includes:

* Authentication
* Task CRUD
* Protected endpoints
* Database connectivity
* Health checks

---

# 🔒 Security Highlights

* JWT Authentication
* User-specific authorization
* Protected API endpoints
* Secure password hashing
* Environment-based secrets
* Non-root Docker user
* Read-only production container
* Dropped Linux capabilities
* Structured logging
* Health monitoring

---

# 🚧 Future Enhancements

* API Versioning (`/api/v1`)
* Refresh JWT Tokens
* Redis Caching
* Role-Based Access Control (RBAC)
* Rate Limiting
* Prometheus Monitoring
* Grafana Dashboards
* Kubernetes Deployment
* Terraform Infrastructure
* Jenkins CI/CD Pipeline
* AWS EC2 Deployment
* Helm Charts

---

# 👨‍💻 Author

**Kartik Sharma**

Aspiring DevOps Engineer

* GitHub: https://github.com/KartikSharma0609/devops-task-manager
* LinkedIn: www.linkedin.com/in/kartik-sharma-54328437a

---

# ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub.
