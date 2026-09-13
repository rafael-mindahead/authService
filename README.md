AuthService

Authentication and authorization service built with Python + FastAPI, designed as a standalone backend service that can later be consumed by applications written in Node.js, Java, React or mobile clients.

The project is being developed as a portfolio backend project focused on authentication, security, API design, database integration and infrastructure.

🚀 Current Status

At the current stage, the project already has:

FastAPI application running locally

Swagger/OpenAPI documentation

PostgreSQL running with Docker

Redis running with Docker

SQLAlchemy integration

Psycopg PostgreSQL driver

Environment configuration with .env

Alembic configured for database migrations

Initial User model structure

Database health-check endpoint

The next step is generating and applying the first Alembic migration for the users table.

🧰 Tech Stack

Backend

Python 3.14

FastAPI

SQLAlchemy 2.x

Pydantic Settings

Psycopg

Database & Cache

PostgreSQL

Redis

Infrastructure

Docker

Docker Compose

Database Migrations

Alembic

Planned Security

JWT Access Tokens

Refresh Tokens

Argon2 password hashing

Role-Based Access Control (RBAC)

Login attempt protection

Token/session revocation

Testing

Pytest

HTTPX

🏗️ Architecture

Client / Frontend
       |
       v
   FastAPI
       |
       +------------------+
       |                  |
       v                  v
 PostgreSQL             Redis
       |                  |
 users / roles       sessions / cache
 audit data          rate limiting

In a later stage, the project will also include a small Node.js service consuming the FastAPI AuthService, demonstrating communication between Node.js and Python services.

📁 Project Structure

auth-service/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   └── models/
│       ├── __init__.py
│       └── user.py
│
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── README.md

⚙️ Environment Setup

1. Clone the repository

git clone <YOUR_REPOSITORY_URL>
cd auth-service

2. Create a virtual environment

python3 -m venv .venv

Activate it:

source .venv/bin/activate

3. Install dependencies

pip install "fastapi[standard]"
pip install sqlalchemy "psycopg[binary]" alembic pydantic-settings pyjwt "pwdlib[argon2]" redis email-validator pytest httpx

🔐 Environment Variables

Create a .env file in the project root.

Example:

POSTGRES_DB=auth_service
POSTGRES_USER=auth_user
POSTGRES_PASSWORD=auth_dev_password

DATABASE_URL=postgresql+psycopg://auth_user:auth_dev_password@localhost:5432/auth_service
REDIS_URL=redis://localhost:6379/0

Never commit the real .env file.

Use .env.example as the public configuration template.

🐳 Running PostgreSQL and Redis

Start the containers:

docker compose up -d

Check their status:

docker compose ps

Expected services:

auth_postgres
auth_redis

▶️ Running FastAPI

With the virtual environment active:

fastapi dev app/main.py

Application:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs

❤️ Health Checks

API Health

GET /health

Example response:

{
  "status": "healthy"
}

Database Health

GET /database/health

Example response:

{
  "database": "PostgreSQL",
  "status": "connected",
  "result": 1
}

🗃️ Initial User Model

The initial User entity is planned with:

id
name
email
password_hash
is_active
is_verified
created_at
updated_at

The table will be managed through Alembic migrations.

🔄 Database Migrations

Generate a migration:

alembic revision --autogenerate -m "create users table"

Apply migrations:

alembic upgrade head

Check the current revision:

alembic current

🔑 Planned Authentication Endpoints

POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
POST /auth/forgot-password
POST /auth/reset-password

GET  /auth/me
GET  /auth/sessions

DELETE /auth/sessions/{id}

🛡️ Planned Security Features

The project roadmap includes:

Password hashing with Argon2

Short-lived JWT access tokens

Refresh token rotation

Session management

Token revocation

Role-Based Access Control

Login attempt protection with Redis

Rate limiting

Password reset flow

Email verification

Audit logging

🗺️ Roadmap

Phase 1 — Infrastructure

FastAPI setup

Swagger/OpenAPI

PostgreSQL container

Redis container

SQLAlchemy integration

Database health check

Alembic setup

First users migration

Phase 2 — Authentication

User registration

Password hashing

Login

JWT access token

Refresh token

Logout

Current user endpoint

Phase 3 — Security

Redis session management

Login attempt protection

Rate limiting

RBAC

Password recovery

Email verification

Phase 4 — Integration

Node.js client/service integration

Automated tests

Production-ready Docker setup

Deployment

🎯 Project Goal

The goal of AuthService is not only to implement login and registration, but to explore how a real authentication service is structured in a modern backend environment.

The project focuses on:

API architecture

authentication and authorization

database persistence

caching

security

migrations

containerization

service-to-service communication

👨‍💻 Author

Rafael Alves

Software Engineering student focused on backend development, currently expanding experience with Python, FastAPI and distributed backend architectures.

GitHub: https://github.com/rafael-mindahead

LinkedIn: www.linkedin.com/in/rafael-alves-0a6990379

📄 License

This project is intended for learning, portfolio and academic development purposes.
