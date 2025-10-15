# EdgeTrade Backend - Production Deployment Guide

## 🚀 Server Deployment Options

### Option 1: Docker Compose (Recommended)
- **Best for**: VPS, dedicated servers, cloud instances
- **Requirements**: Docker & Docker Compose installed
- **Benefits**: Easy setup, isolated environment, easy scaling

### Option 2: Manual Python Deployment
- **Best for**: Shared hosting, VPS without Docker
- **Requirements**: Python 3.11+, PostgreSQL, Redis
- **Benefits**: More control, lighter resource usage

### Option 3: Cloud Platform Deployment
- **Best for**: AWS, Google Cloud, Azure, DigitalOcean
- **Requirements**: Cloud account, container registry
- **Benefits**: Managed services, auto-scaling, monitoring

---

## 📋 Pre-Deployment Checklist

### ✅ Server Requirements
- [ ] **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- [ ] **RAM**: Minimum 2GB (4GB+ recommended)
- [ ] **Storage**: Minimum 20GB SSD
- [ ] **CPU**: 2+ cores
- [ ] **Network**: Public IP with ports 80, 443, 8000 open

### ✅ Domain & SSL
- [ ] Domain name registered
- [ ] DNS A record pointing to server IP
- [ ] SSL certificate (Let's Encrypt recommended)

### ✅ Security
- [ ] Firewall configured (UFW/iptables)
- [ ] SSH key authentication enabled
- [ ] Non-root user created
- [ ] Fail2ban installed

---

## 🐳 Option 1: Docker Compose Deployment

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply docker group
```

### Step 2: Clone Repository
```bash
# Clone your repository
git clone <your-repo-url> edgetrade-backend
cd edgetrade-backend

# Or upload files via SCP/SFTP
```

### Step 3: Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit production settings
nano .env
```

### Step 4: Production Environment Variables
```bash
# Application Settings
APP_NAME=EdgeTrade Trading Platform
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Database (use strong passwords!)
DATABASE_URL=postgresql+asyncpg://edgetrade:STRONG_PASSWORD_HERE@postgres:5432/edgetrade_db

# Security (CRITICAL: Generate new secret!)
SECRET_KEY=your-super-secret-key-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (replace with your domain)
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Admin Account (CHANGE IMMEDIATELY!)
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=STRONG_ADMIN_PASSWORD_HERE

# Email Configuration
SMTP_ENABLED=True
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Trading Settings
SIMULATE_TRADING=True
DEFAULT_LEVERAGE=100
MAX_LEVERAGE=500
```

### Step 5: Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Step 6: Initialize Database
```bash
# Run database initialization
docker-compose exec api python scripts/init_db.py

# Run migrations (if any)
docker-compose exec api python scripts/migrate_name_fields.py
docker-compose exec api python scripts/migrate_figma_fields.py
```

### Step 7: Setup Reverse Proxy (Nginx)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/edgetrade
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
    }

    # Static files (if any)
    location /static/ {
        alias /path/to/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/edgetrade /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 🔧 Option 2: Manual Python Deployment

### Step 1: Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install system dependencies
sudo apt install gcc libpq-dev -y
```

### Step 2: Setup Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE edgetrade_db;
CREATE USER edgetrade WITH PASSWORD 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE edgetrade_db TO edgetrade;
\q
```

### Step 3: Setup Application
```bash
# Clone repository
git clone <your-repo-url> edgetrade-backend
cd edgetrade-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Edit with production values
```

### Step 4: Initialize Database
```bash
# Initialize database
python scripts/init_db.py

# Run migrations
python scripts/migrate_name_fields.py
python scripts/migrate_figma_fields.py
```

### Step 5: Setup Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/edgetrade.service
```

**Service Configuration:**
```ini
[Unit]
Description=EdgeTrade Trading Platform API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/edgetrade-backend
Environment=PATH=/path/to/edgetrade-backend/venv/bin
ExecStart=/path/to/edgetrade-backend/venv/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable edgetrade
sudo systemctl start edgetrade
sudo systemctl status edgetrade
```

---

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Install UFW
sudo apt install ufw -y

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow API (if direct access needed)
sudo ufw allow 8000

# Enable firewall
sudo ufw enable
```

### Fail2ban Setup
```bash
# Install Fail2ban
sudo apt install fail2ban -y

# Configure
sudo nano /etc/fail2ban/jail.local
```

**Fail2ban Configuration:**
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
```

---

## 📊 Monitoring & Maintenance

### Log Management
```bash
# Setup log rotation
sudo nano /etc/logrotate.d/edgetrade
```

**Logrotate Configuration:**
```
/path/to/edgetrade-backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload edgetrade
    endscript
}
```

### Health Monitoring
```bash
# Create health check script
sudo nano /usr/local/bin/edgetrade-health.sh
```

**Health Check Script:**
```bash
#!/bin/bash
# Health check for EdgeTrade API

API_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ EdgeTrade API is healthy"
    exit 0
else
    echo "❌ EdgeTrade API is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/edgetrade-health.sh

# Add to crontab for monitoring
sudo crontab -e
# Add: */5 * * * * /usr/local/bin/edgetrade-health.sh
```

---

## 🚀 Deployment Commands Summary

### Docker Compose Deployment
```bash
# 1. Setup server
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. Deploy application
git clone <your-repo-url> edgetrade-backend
cd edgetrade-backend
cp env.example .env
nano .env  # Configure production settings
docker-compose up -d --build

# 3. Initialize database
docker-compose exec api python scripts/init_db.py

# 4. Setup reverse proxy
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/edgetrade
sudo ln -s /etc/nginx/sites-available/edgetrade /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 5. SSL certificate
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

### Manual Deployment
```bash
# 1. Install dependencies
sudo apt update && sudo apt install python3.11 python3.11-venv postgresql redis-server nginx -y

# 2. Setup database
sudo -u postgres psql -c "CREATE DATABASE edgetrade_db; CREATE USER edgetrade WITH PASSWORD 'STRONG_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE edgetrade_db TO edgetrade;"

# 3. Deploy application
git clone <your-repo-url> edgetrade-backend
cd edgetrade-backend
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.example .env && nano .env
python scripts/init_db.py

# 4. Setup service
sudo nano /etc/systemd/system/edgetrade.service
sudo systemctl daemon-reload && sudo systemctl enable edgetrade && sudo systemctl start edgetrade
```

---

## ✅ Post-Deployment Checklist

- [ ] API accessible at `https://yourdomain.com/api/v1/`
- [ ] Database initialized with admin user
- [ ] SSL certificate working
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Admin password changed
- [ ] Email configuration tested
- [ ] Trading system functional

---

## 🆘 Troubleshooting

### Common Issues
1. **Port 8000 not accessible**: Check firewall and Docker port mapping
2. **Database connection failed**: Verify DATABASE_URL in .env
3. **SSL certificate issues**: Check domain DNS and Certbot logs
4. **Permission denied**: Check file ownership and SELinux/AppArmor

### Useful Commands
```bash
# Check service status
docker-compose ps
sudo systemctl status edgetrade

# View logs
docker-compose logs -f api
sudo journalctl -u edgetrade -f

# Test API
curl -X GET "https://yourdomain.com/api/v1/health"

# Database connection test
docker-compose exec postgres psql -U edgetrade -d edgetrade_db -c "SELECT version();"
```

---

## 📞 Support

If you encounter issues during deployment:
1. Check the logs: `docker-compose logs api` or `sudo journalctl -u edgetrade`
2. Verify environment variables in `.env`
3. Test database connectivity
4. Check firewall and port accessibility
5. Review Nginx configuration

Your EdgeTrade backend is now ready for production deployment! 🚀
