# 🎭 Anonymous Confessions

A modern anonymous confession platform built with **Django**, **PostgreSQL**, **Docker**, and **Nginx**. Share your thoughts, secrets, and confessions without revealing your identity.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-orange)

---

## ✨ Features

- **Anonymous Posting** — Share confessions without revealing identity
- **User Authentication** — Register, login, logout with profile management
- **Mood Tags** — Categorize confessions by mood (happy, sad, angry, etc.)
- **Reactions** — React to confessions with emojis (❤️ 👍 😢 😡 🔥)
- **Comments** — Leave anonymous or named comments on confessions
- **Tag System** — Organize confessions with tags (many-to-many)
- **Dashboard** — View stats, popular tags, and mood analytics
- **Search & Filter** — Search confessions, filter by mood or tag
- **Responsive Design** — Premium dark theme with animations
- **CRUD Operations** — Create, read, update, delete confessions
- **Admin Panel** — Full Django admin for all models

## 🛠️ Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Django 5.1** | Web framework |
| **PostgreSQL 16** | Primary database |
| **Gunicorn** | WSGI HTTP server |
| **Nginx** | Reverse proxy & static files |
| **Docker** | Containerization |
| **Docker Compose** | Multi-service orchestration |
| **GitHub Actions** | CI/CD pipeline |
| **WhiteNoise** | Static file serving |
| **pytest-django** | Testing framework |

## 📐 Database Schema

```
User (Django built-in)
 ├── Profile (1:1)     — display_name, avatar_emoji, bio
 ├── Confession (1:N)  — title, content, mood, is_anonymous
 │    ├── Comment (1:N)   — content, is_anonymous
 │    ├── Reaction (1:N)  — reaction_type (heart, thumbsup, etc.)
 │    └── Tag (M:N)       — name, slug
```

**Relationships:**
- Many-to-one: `Confession → User`, `Comment → Confession`, `Reaction → Confession`
- Many-to-many: `Confession ↔ Tag`
- One-to-one: `Profile → User`

## 🚀 Local Setup Instructions

### Prerequisites
- Docker & Docker Compose installed
- Git installed

### Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/ax1ll3ss/00016440_DSCC.git
cd 00016440_DSCC

# 2. Create environment file
cp .env.example .env
# Edit .env with your values

# 3. Build and start containers
docker compose up --build -d

# 4. Create a superuser
docker compose exec web python manage.py createsuperuser

# 5. Open in browser
# App: http://localhost
# Admin: http://localhost/admin/
```

### Development Setup (without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r app/requirements.txt

# 3. Run migrations
cd app
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

### Development Setup (Docker)

```bash
docker compose -f docker-compose.dev.yml up --build
# App available at http://localhost:8000
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | `insecure-dev-key` |
| `DJANGO_DEBUG` | Debug mode (0/1) | `0` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Database name | `confessions_db` |
| `POSTGRES_USER` | Database user | `confessions_user` |
| `POSTGRES_PASSWORD` | Database password | `confessions_pass` |
| `POSTGRES_HOST` | Database host | `db` |
| `POSTGRES_PORT` | Database port | `5432` |

## 🐳 Docker Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  Nginx   │────▶│  Django +    │────▶│ PostgreSQL   │
│  :80/443 │     │  Gunicorn    │     │  :5432       │
│          │     │  :8000       │     │              │
└──────────┘     └──────────────┘     └──────────────┘
     │
     ├── /static/ → served directly by Nginx
     └── /media/  → served directly by Nginx
```

## 🚀 Deployment Instructions

### Server Setup

```bash
# 1. SSH into your server
ssh user@your-server-ip

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo apt install docker-compose-plugin

# 4. Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# 5. Clone repository
cd ~
git clone https://github.com/ax1ll3ss/00016440_DSCC.git confessions-app
cd confessions-app

# 6. Create .env file
cp .env.example .env
nano .env  # Edit with production values

# 7. Start services
docker compose up --build -d

# 8. Set up SSL (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.uz
```

### CI/CD Pipeline

The GitHub Actions pipeline automatically:
1. **Lints** code with flake8
2. **Tests** with pytest-django (11 tests)
3. **Builds** Docker image and pushes to Docker Hub
4. **Deploys** to server via SSH

Required GitHub Secrets:
- `DOCKERHUB_USERNAME` — Docker Hub username
- `DOCKERHUB_TOKEN` — Docker Hub access token
- `SSH_PRIVATE_KEY` — Server SSH private key
- `SSH_HOST` — Server IP address
- `SSH_USERNAME` — Server SSH username

## 🧪 Running Tests

```bash
# With Docker
docker compose exec web pytest tests/ -v

# Without Docker
cd app
pytest tests/ -v
```

## 📁 Project Structure

```
00016440_DSCC/
├── app/                          # Django application
│   ├── accounts/                 # Auth app (login, register, profile)
│   ├── posts/                    # Core app (confessions, comments, reactions)
│   ├── templates/                # HTML templates
│   ├── static/                   # CSS, JS
│   ├── confessions_project/      # Django settings
│   ├── tests/                    # pytest tests
│   ├── manage.py
│   └── requirements.txt
├── nginx/                        # Nginx configuration
├── .github/workflows/            # CI/CD pipeline
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Production compose
├── docker-compose.dev.yml        # Development compose
├── entrypoint.sh                 # Container entrypoint
├── gunicorn.conf.py              # Gunicorn config
└── README.md
```

## 👤 Test User Credentials

After deployment, create a test user or use the admin panel:
- **Admin**: `http://yourdomain.uz/admin/`
- **Username**: (created via `createsuperuser`)
- **Password**: (set during creation)

## 📝 License

This project was created as part of the DSCC coursework assessment.

---

**Student ID:** 00016440
