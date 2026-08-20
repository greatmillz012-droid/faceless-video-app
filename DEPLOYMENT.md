# Production Deployment Guide

## Overview

This guide covers deploying the Faceless Video App to a production environment. The stack includes FastAPI backend, Next.js frontend, Celery workers, and PostgreSQL database.

---

## Pre-Deployment Checklist

- [ ] All OAuth credentials are set up (YouTube, TikTok, Meta)
- [ ] `.env` file is updated with production values
- [ ] Database backups are configured
- [ ] Email/notifications service is ready
- [ ] Storage for videos (S3 or local path) is configured
- [ ] SSL/TLS certificates are obtained
- [ ] DNS records are configured
- [ ] Environment variables are stored in a secret manager

---

## Option 1: Deploy to Docker (Recommended)

### Prerequisites

- Linux server with Docker and Docker Compose installed
- Domain name (e.g., `faceless.example.com`)
- SSL certificate (from Let's Encrypt, AWS Certificate Manager, etc.)
- PostgreSQL database (managed service or self-hosted)
- Redis instance (managed service or self-hosted)
- S3 or equivalent object storage for videos

### Step 1: Prepare the Server

```bash
# SSH into your server
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone Repository and Configure

```bash
# Clone your repository
git clone <your-repo-url> /opt/faceless-video-app
cd /opt/faceless-video-app

# Create production .env
cp backend/.env.example backend/.env

# Edit with production values
nano backend/.env
```

Update `backend/.env` with:
```bash
# Use strong secret key
SECRET_KEY=<generate-with-python-secrets>

# Use production database URL
DATABASE_URL=postgresql://user:password@your-db-host:5432/dbname

# Use production Redis URL
REDIS_URL=redis://your-redis-host:6379/0

# Update base URL to production domain
BASE_URL=https://faceless.example.com

# Add production OAuth credentials
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
# ... etc for TikTok and Meta

# Use production storage path or S3
STORAGE_PATH=/data/videos  # or S3 URL
```

### Step 3: Configure Docker Compose for Production

Use the production overlay already included in this repository:

```bash
cat > .env.production <<'EOF'
NEXT_PUBLIC_API_URL=https://faceless.example.com
EOF

docker compose --env-file .env.production \
  -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --build
```

The overlay builds and serves Next.js in production mode, binds the app ports to localhost for Nginx, adds health checks, and restarts services after failures or reboots. Keep provider credentials in `backend/.env` on the server only; never commit that file.

For reference, the equivalent service settings are:

```yaml
version: "3.8"

services:
  backend:
    image: faceless-backend:latest
    environment:
      - env_file: backend/.env
    ports:
      - "8000:8000"
    volumes:
      - /data/videos:/app/storage/videos
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: faceless-frontend:latest
    environment:
      - NEXT_PUBLIC_API_URL=https://faceless.example.com
    ports:
      - "3000:3000"
    restart: always

  # ... worker, beat, db services (configured similarly)
```

### Step 4: Build and Deploy

```bash
# Check service status
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Verify
docker compose ps
curl https://faceless.example.com/health
```

### Step 5: Set Up Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt-get install nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/faceless
```

Add:
```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name faceless.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name faceless.example.com;

    ssl_certificate /etc/letsencrypt/live/faceless.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/faceless.example.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend;
    }
}
```

Enable and start Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/faceless /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Step 6: SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d faceless.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Option 2: Deploy to Heroku

### Prerequisites

- Heroku account
- Heroku CLI installed
- PostgreSQL database (use Heroku Postgres)
- Redis (use Heroku Redis)

### Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create faceless-video-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0 -a faceless-video-app

# Add Redis
heroku addons:create heroku-redis:premium-0 -a faceless-video-app

# Set environment variables
heroku config:set SECRET_KEY=<your-secret-key> -a faceless-video-app
heroku config:set YOUTUBE_CLIENT_ID=<your-id> -a faceless-video-app
# ... set all other env vars

# Deploy
git push heroku main

# Run migrations
heroku run python -c "from app.database import Base, engine; Base.metadata.create_all(engine)" -a faceless-video-app
```

---

## Option 3: Deploy to AWS ECS (Elastic Container Service)

### Prerequisites

- AWS account
- AWS CLI configured
- ECR repository created for images
- RDS PostgreSQL database
- ElastiCache Redis
- ALB (Application Load Balancer)

### High-Level Steps

1. Build and push Docker images to ECR
2. Create ECS cluster
3. Create task definitions for backend, worker, beat
4. Create services to run tasks
5. Configure ALB to route traffic
6. Set up CloudWatch monitoring

---

## Monitoring & Maintenance

### Logs

```bash
# View backend logs
docker compose logs -f backend

# View worker logs
docker compose logs -f worker

# View in production with ELK Stack or CloudWatch
```

### Database Backups

```bash
# Manual backup
docker compose exec db pg_dump -U appuser facelessapp > backup.sql

# Restore from backup
docker compose exec -T db psql -U appuser facelessapp < backup.sql

# For production, use automated backups:
# - AWS RDS automated backups
# - PostgreSQL pg_basebackup
# - Third-party tools (Navicat, Datadog, etc.)
```

### Performance Monitoring

Monitor these metrics:
- API response times (target: <200ms)
- Worker queue depth (target: 0 or low)
- Database connections
- Redis memory usage
- Celery task success/failure rates

### Security Best Practices

- ✅ Use HTTPS everywhere
- ✅ Rotate API keys regularly
- ✅ Enable database encryption at rest
- ✅ Use VPC/security groups to restrict access
- ✅ Enable audit logging
- ✅ Keep dependencies updated (`pip list --outdated`)
- ✅ Run security scans (`pip install safety && safety check`)
- ✅ Use a Web Application Firewall (WAF)
- ✅ Monitor for suspicious activity

---

## Updating Production

### Zero-Downtime Deployment

```bash
# 1. Build new image
docker build -t faceless-backend:v2 ./backend

# 2. Push to registry
docker push faceless-backend:v2

# 3. Update service (Docker Swarm or Kubernetes)
docker service update --image faceless-backend:v2 backend

# 4. Verify health checks pass
docker compose ps
```

### Database Migrations

For schema changes:
```bash
# 1. Create backup
docker compose exec db pg_dump -U appuser facelessapp > backup.sql

# 2. Run migration
docker compose exec backend alembic upgrade head

# 3. Verify
curl http://localhost:8000/health
```

---

## Troubleshooting Production Issues

### High CPU Usage

```bash
# Check processes
docker top <container>

# Check slow database queries
docker compose exec db psql -U appuser -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Database Connections Maxed Out

```bash
# Check connections
docker compose exec db psql -U appuser -c "SELECT count(*) FROM pg_stat_activity;"

# Reduce connection pool in app config
# Implement connection pooling (PgBouncer)
```

### Redis Memory Issues

```bash
# Check Redis memory
docker compose exec redis redis-cli INFO memory

# Clear old cache
docker compose exec redis redis-cli FLUSHDB

# Implement key expiration policies
```

---

## Disaster Recovery

### Recovery Time Objectives (RTO) & Recovery Point Objectives (RPO)

- **RTO**: Max downtime acceptable (target: <1 hour)
- **RPO**: Max data loss acceptable (target: <15 minutes)

### Backup Strategy

1. **Database**: Daily backups, 30-day retention
2. **Code**: Version control (Git)
3. **Videos**: S3 with versioning and cross-region replication
4. **Configuration**: Store in Secrets Manager with version history

### Restore Procedure

1. Spin up new infrastructure
2. Restore database from latest backup
3. Deploy latest code from Git
4. Restore video files from S3
5. Update DNS to point to new infrastructure
6. Verify all systems operational

---

## Cost Optimization

- Use auto-scaling for worker processes based on queue depth
- Store old videos in cheaper S3 storage tier
- Use CDN for static assets and video delivery
- Monitor database query performance to reduce resource usage
- Schedule non-essential tasks during off-peak hours

---

## Next Steps

1. Choose a deployment platform (Docker, Heroku, AWS, etc.)
2. Set up OAuth credentials in production environment
3. Configure monitoring and alerting
4. Perform load testing before go-live
5. Set up incident response procedures

For specific platform details, refer to official documentation:
- [Docker Documentation](https://docs.docker.com/)
- [Heroku Documentation](https://devcenter.heroku.com/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

