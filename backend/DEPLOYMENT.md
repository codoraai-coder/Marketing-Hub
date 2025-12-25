# Deployment Guide - MCP Hub Backend

## Production Deployment Checklist

### 1. Environment Configuration

```bash
# Create production .env
cp .env.example .env.production

# Update with production values:
NODE_ENV=production
DATABASE_HOST=your-prod-db-host
DATABASE_PASSWORD=strong-password-here
AWS_S3_BUCKET=prod-mcp-hub-storage
JWT_SECRET=very-strong-secret-key
```

### 2. Database Setup

#### PostgreSQL

```bash
# Option A: Managed Database (Recommended)
# Use AWS RDS, Google Cloud SQL, or Azure Database

# Option B: Self-hosted
# Ensure PostgreSQL 15+ is installed and secured
# Create database
createdb mcp_hub

# Run migrations (future)
npm run migration:run
```

#### Redis

```bash
# Option A: Managed Redis (Recommended)
# Use AWS ElastiCache, Redis Cloud, etc.

# Option B: Self-hosted
# Ensure Redis 7+ is installed and secured
redis-cli ping
```

### 3. S3 Bucket Setup

```bash
# Create S3 bucket
aws s3 mb s3://prod-mcp-hub-storage

# Set bucket policy
aws s3api put-bucket-policy \
  --bucket prod-mcp-hub-storage \
  --policy file://s3-policy.json

# Enable versioning (optional)
aws s3api put-bucket-versioning \
  --bucket prod-mcp-hub-storage \
  --versioning-configuration Status=Enabled
```

Example `s3-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:user/mcp-backend"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::prod-mcp-hub-storage/*"
    }
  ]
}
```

### 4. Build Application

```bash
# Install dependencies
npm ci --only=production

# Build TypeScript
npm run build

# Test build
node dist/main.js
```

### 5. Deployment Options

#### Option A: Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production

# Copy built application
COPY dist ./dist

# Expose port
EXPOSE 3000

# Start application
CMD ["node", "dist/main.js"]
```

Build and run:
```bash
# Build image
docker build -t mcp-hub-backend:latest .

# Run container
docker run -d \
  --name mcp-backend \
  -p 3000:3000 \
  --env-file .env.production \
  mcp-hub-backend:latest
```

#### Option B: PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'mcp-backend',
    script: 'dist/main.js',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 startup
pm2 startup
```

#### Option C: Cloud Platform (AWS, Azure, GCP)

##### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p node.js mcp-backend

# Create environment
eb create mcp-production

# Deploy
eb deploy
```

##### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT/mcp-backend

# Deploy
gcloud run deploy mcp-backend \
  --image gcr.io/PROJECT/mcp-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

##### Azure App Service

```bash
# Login
az login

# Create resource group
az group create --name mcp-rg --location eastus

# Create app service plan
az appservice plan create \
  --name mcp-plan \
  --resource-group mcp-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group mcp-rg \
  --plan mcp-plan \
  --name mcp-backend \
  --runtime "NODE|20-lts"

# Deploy
az webapp deployment source config-zip \
  --resource-group mcp-rg \
  --name mcp-backend \
  --src dist.zip
```

### 6. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.mcphub.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 7. SSL/TLS Certificate

```bash
# Using Let's Encrypt
sudo certbot --nginx -d api.mcphub.com
```

### 8. Monitoring Setup

#### Application Monitoring

```bash
# Install New Relic, Datadog, or similar
npm install newrelic

# Add to main.ts
require('newrelic');
```

#### Log Aggregation

```bash
# Using Winston for logging
npm install winston

# Configure in production
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

### 9. Health Checks

Add health check endpoint:

```typescript
// src/health/health.controller.ts
@Controller('health')
export class HealthController {
  @Get()
  check() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    };
  }

  @Get('ready')
  async ready() {
    // Check database, redis, s3
    return { ready: true };
  }
}
```

### 10. Security Hardening

```bash
# Install helmet for security headers
npm install helmet

# Add to main.ts
import helmet from 'helmet';
app.use(helmet());

# Rate limiting
npm install @nestjs/throttler

# CORS configuration
app.enableCors({
  origin: ['https://mcphub.com'],
  credentials: true
});
```

### 11. Database Migrations

```bash
# Generate migration
npm run migration:generate -- CreateInitialSchema

# Run migrations
npm run migration:run

# Revert if needed
npm run migration:revert
```

### 12. Backup Strategy

#### Database Backups

```bash
# Automated daily backups
0 2 * * * pg_dump mcp_hub > /backups/mcp_$(date +\%Y\%m\%d).sql

# Upload to S3
aws s3 cp /backups/ s3://mcp-backups/ --recursive
```

#### S3 Replication

```bash
# Enable versioning and replication
aws s3api put-bucket-versioning \
  --bucket prod-mcp-hub-storage \
  --versioning-configuration Status=Enabled

# Cross-region replication
aws s3api put-bucket-replication \
  --bucket prod-mcp-hub-storage \
  --replication-configuration file://replication.json
```

### 13. CI/CD Pipeline

#### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy to production
        run: |
          # Your deployment script here
```

### 14. Monitoring Alerts

Set up alerts for:
- High error rates
- Database connection failures
- S3 upload failures
- High response times
- Memory/CPU usage

### 15. Post-Deployment Verification

```bash
# Health check
curl https://api.mcphub.com/health

# Test API
curl https://api.mcphub.com/workspaces

# Check logs
pm2 logs mcp-backend

# Monitor metrics
pm2 monit
```

## Rollback Plan

```bash
# Docker rollback
docker stop mcp-backend
docker run -d --name mcp-backend mcp-hub-backend:previous

# PM2 rollback
pm2 stop mcp-backend
git checkout previous-tag
npm run build
pm2 restart mcp-backend

# Database rollback
npm run migration:revert
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (ALB, Nginx)
- Run multiple instances
- Session stickiness not required (stateless)

### Vertical Scaling
- Monitor CPU/Memory usage
- Upgrade instance size as needed

### Database Scaling
- Read replicas for read-heavy workloads
- Connection pooling
- Query optimization

### Job Queue Scaling
- Multiple worker instances
- Priority queues
- Dead letter queues

## Cost Optimization

1. Use spot instances for workers
2. S3 lifecycle policies for old content
3. Database connection pooling
4. Redis cache for frequently accessed data
5. CDN for S3 content delivery

## Support & Maintenance

- [ ] Set up monitoring dashboard
- [ ] Configure alerting
- [ ] Document runbooks
- [ ] Schedule regular backups
- [ ] Plan capacity reviews
- [ ] Security patch schedule

## Emergency Contacts

- DevOps Lead: [contact]
- Database Admin: [contact]
- AWS Support: [support plan]
