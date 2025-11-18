# Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OSINT
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Generate secure keys**
   ```bash
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
   python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
   ```

4. **Start services**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Manual Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

```bash
# Create database
createdb osint_db

# Create user
psql -c "CREATE USER osint_user WITH PASSWORD 'osint_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE osint_db TO osint_user;"
```

### 3. Set Up Redis

```bash
# Start Redis
redis-server
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Required
SECRET_KEY=<generate-secure-key>
ENCRYPTION_KEY=<generate-secure-key>
DATABASE_URL=postgresql+asyncpg://osint_user:osint_password@localhost:5432/osint_db
REDIS_URL=redis://localhost:6379/0

# Optional
DEBUG=False
ENVIRONMENT=production
```

### 5. Initialize Database

```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or start the app (auto-creates tables)
python -m app.main
```

### 6. Create Admin User

```bash
# Register via API
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "YourSecurePassword123!",
    "full_name": "Admin User"
  }'
```

### 7. Assign Admin Role

```python
# Run in Python shell
from app.database import async_session, User, Role
from app.auth.rbac import RBACManager
import asyncio

async def make_admin():
    async with async_session() as db:
        # Get user
        user = await db.get(User, 1)  # Adjust ID

        # Get admin role
        from sqlalchemy import select
        result = await db.execute(select(Role).where(Role.name == "admin"))
        admin_role = result.scalar_one()

        # Assign role
        await RBACManager.assign_role_to_user(db, user, admin_role)
        print("Admin role assigned!")

asyncio.run(make_admin())
```

## OAuth2 Setup

### Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project
3. Enable Google+ API
4. Create OAuth2 credentials
5. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/oauth2/google/callback`
6. Copy Client ID and Secret to `.env`

### GitHub OAuth2

1. Go to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Create New OAuth App
3. Authorization callback URL: `http://localhost:8000/api/v1/auth/oauth2/github/callback`
4. Copy Client ID and Secret to `.env`

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

## Production Deployment

### Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Use HTTPS/TLS
- [ ] Configure firewall
- [ ] Set up log rotation
- [ ] Enable monitoring
- [ ] Configure backups
- [ ] Review CORS settings
- [ ] Enable security headers

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### Using Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Application Logs

```bash
# View logs
tail -f logs/osint.log

# View audit logs
tail -f logs/audit.log
```

### Database

```bash
# Check connections
psql osint_db -c "SELECT * FROM pg_stat_activity;"

# Check table sizes
psql osint_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Redis

```bash
# Check memory usage
redis-cli info memory

# Check keys
redis-cli keys "rate_limit:*"
```

## Maintenance

### Database Backups

```bash
# Backup
pg_dump osint_db > backup_$(date +%Y%m%d).sql

# Restore
psql osint_db < backup_20231118.sql
```

### Log Rotation

```bash
# Install logrotate config
sudo cp deployment/logrotate.conf /etc/logrotate.d/osint

# Test rotation
sudo logrotate -f /etc/logrotate.d/osint
```

### Data Cleanup

```python
# Run cleanup script
from app.utils.compliance import compliance_manager
from app.database import async_session
import asyncio

async def cleanup():
    async with async_session() as db:
        await compliance_manager.cleanup_expired_data(db)
        print("Cleanup completed!")

asyncio.run(cleanup())
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
systemctl status postgresql

# Check connection
psql -U osint_user -d osint_db -h localhost
```

### Redis Connection Issues

```bash
# Check Redis is running
systemctl status redis

# Test connection
redis-cli ping
```

### Import Errors

```bash
# Ensure you're in the right directory
cd /path/to/OSINT

# Install dependencies
pip install -r requirements.txt
```

### Permission Issues

```bash
# Create logs directory
mkdir -p logs
chmod 755 logs
```

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: `docs/`
- Security: See `docs/SECURITY.md`
