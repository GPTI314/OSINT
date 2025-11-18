# OSINT Platform - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Production Deployment](#production-deployment)
4. [Container Deployment](#container-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements (Development)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 20.04+, macOS 11+, or Windows 10+ with WSL2

#### Recommended Requirements (Production)
- **CPU**: 16+ cores
- **RAM**: 32+ GB
- **Storage**: 500+ GB SSD
- **OS**: Ubuntu 22.04 LTS Server
- **Network**: 1 Gbps+

### Software Dependencies

- **Docker**: 24.0+ and Docker Compose 2.0+
- **Kubernetes**: 1.28+ (for K8s deployment)
- **Python**: 3.11+
- **Node.js**: 20 LTS
- **PostgreSQL**: 15+
- **Neo4j**: 5.0+
- **MongoDB**: 7.0+
- **Redis**: 7.0+
- **Elasticsearch**: 8.0+

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/osint-platform.git
cd osint-platform
```

### 2. Install Dependencies

#### Backend (Python)

```bash
cd services/api-gateway
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend (if applicable)

```bash
cd frontend
npm install
```

### 3. Configure Environment Variables

Create `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your local configuration (see [Configuration Reference](./CONFIGURATION.md)).

### 4. Start Database Services

Using Docker Compose for local databases:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

This starts:
- PostgreSQL on port 5432
- Neo4j on port 7687 (Bolt) and 7474 (HTTP)
- MongoDB on port 27017
- Redis on port 6379
- Elasticsearch on port 9200

### 5. Initialize Databases

Run database migrations:

```bash
# PostgreSQL migrations
alembic upgrade head

# Neo4j schema setup
python scripts/setup_neo4j.py

# MongoDB indexes
python scripts/setup_mongodb.py

# Elasticsearch indices
python scripts/setup_elasticsearch.py
```

### 6. Start Development Servers

#### Backend Services

```bash
# API Gateway
cd services/api-gateway
uvicorn main:app --reload --port 8000

# Collector Service
cd services/collector
python main.py

# Analysis Service
cd services/analysis
python main.py
```

#### Background Workers

```bash
celery -A tasks worker --loglevel=info
```

#### Frontend (if applicable)

```bash
cd frontend
npm run dev
```

### 7. Verify Installation

Access the following endpoints to verify:

- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- Elasticsearch: http://localhost:9200

## Production Deployment

### Architecture Overview

```
Internet → Load Balancer → API Gateway → Microservices → Databases
                    ↓
              SSL Termination
```

### Deployment Options

1. **Docker Compose** (Small deployments, 1-3 servers)
2. **Kubernetes** (Large scale, high availability)
3. **Cloud Managed Services** (AWS, Azure, GCP)

## Container Deployment

### Docker Compose Production Setup

#### 1. Prepare Production Environment

```bash
# Create production directory
mkdir -p /opt/osint-platform
cd /opt/osint-platform

# Clone repository
git clone https://github.com/your-org/osint-platform.git .
```

#### 2. Build Docker Images

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Or build individual services
docker build -t osint/api-gateway:latest -f services/api-gateway/Dockerfile .
docker build -t osint/collector:latest -f services/collector/Dockerfile .
docker build -t osint/enrichment:latest -f services/enrichment/Dockerfile .
docker build -t osint/analysis:latest -f services/analysis/Dockerfile .
```

#### 3. Configure Production Environment

```bash
# Create production environment file
cp .env.production.example .env.production

# Edit with production values
nano .env.production
```

Required variables:
```env
# Application
APP_ENV=production
SECRET_KEY=<generate-strong-secret>
API_HOST=0.0.0.0
API_PORT=8000

# Database URLs
DATABASE_URL=postgresql://user:pass@postgres:5432/osint
NEO4J_URI=bolt://neo4j:7687
MONGODB_URI=mongodb://mongo:27017
REDIS_URL=redis://redis:6379
ELASTICSEARCH_URL=http://elasticsearch:9200

# Security
JWT_SECRET_KEY=<generate-strong-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# External Services
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=<smtp-password>
```

#### 4. Deploy with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

#### 5. Initialize Production Database

```bash
# Run migrations inside container
docker-compose exec api-gateway alembic upgrade head

# Setup other databases
docker-compose exec api-gateway python scripts/setup_databases.py
```

#### 6. Create Admin User

```bash
docker-compose exec api-gateway python scripts/create_admin.py
```

### Docker Compose Configuration

**docker-compose.prod.yml** (example):

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: osint
      POSTGRES_USER: osint_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: osint_user
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - es_data:/usr/share/elasticsearch/data
    restart: unless-stopped

  api-gateway:
    build:
      context: .
      dockerfile: services/api-gateway/Dockerfile
    environment:
      - DATABASE_URL=postgresql://osint_user:${DB_PASSWORD}@postgres:5432/osint
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: unless-stopped

  collector:
    build:
      context: .
      dockerfile: services/collector/Dockerfile
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  enrichment:
    build:
      context: .
      dockerfile: services/enrichment/Dockerfile
    depends_on:
      - postgres
      - mongodb
    restart: unless-stopped

  celery-worker:
    build:
      context: .
      dockerfile: services/api-gateway/Dockerfile
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api-gateway
    restart: unless-stopped

volumes:
  postgres_data:
  neo4j_data:
  mongo_data:
  redis_data:
  es_data:
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.28+)
- kubectl configured
- Helm 3.0+ installed
- Ingress controller (nginx, traefik)
- Cert-manager for SSL certificates

### 1. Create Namespace

```bash
kubectl create namespace osint-platform
kubectl config set-context --current --namespace=osint-platform
```

### 2. Create Secrets

```bash
# Database passwords
kubectl create secret generic db-secrets \
  --from-literal=postgres-password=$(openssl rand -base64 32) \
  --from-literal=neo4j-password=$(openssl rand -base64 32) \
  --from-literal=mongo-password=$(openssl rand -base64 32)

# Application secrets
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret=$(openssl rand -base64 64) \
  --from-literal=secret-key=$(openssl rand -base64 64)
```

### 3. Deploy Databases

#### PostgreSQL (using Helm)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install postgresql bitnami/postgresql \
  --set auth.username=osint_user \
  --set auth.database=osint \
  --set auth.existingSecret=db-secrets \
  --set auth.secretKeys.adminPasswordKey=postgres-password \
  --set primary.persistence.size=100Gi
```

#### Neo4j

```bash
helm install neo4j bitnami/neo4j \
  --set auth.existingSecret=db-secrets \
  --set auth.existingSecretPasswordKey=neo4j-password \
  --set persistence.size=50Gi
```

#### MongoDB

```bash
helm install mongodb bitnami/mongodb \
  --set auth.rootUser=osint_user \
  --set auth.existingSecret=db-secrets \
  --set persistence.size=100Gi
```

#### Redis

```bash
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.size=10Gi
```

#### Elasticsearch

```bash
helm install elasticsearch elastic/elasticsearch \
  --set persistence.size=200Gi \
  --set replicas=3
```

### 4. Deploy Application Services

Create Kubernetes manifests in `kubernetes/` directory:

#### ConfigMap

**kubernetes/configmap.yaml**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: osint-config
data:
  APP_ENV: "production"
  DATABASE_HOST: "postgresql"
  NEO4J_HOST: "neo4j"
  MONGODB_HOST: "mongodb"
  REDIS_HOST: "redis-master"
  ELASTICSEARCH_HOST: "elasticsearch-master"
```

#### Deployment - API Gateway

**kubernetes/api-gateway-deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: osint/api-gateway:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: osint-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service

**kubernetes/api-gateway-service.yaml**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  selector:
    app: api-gateway
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### Ingress

**kubernetes/ingress.yaml**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: osint-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.osint-platform.example
    secretName: osint-tls
  rules:
  - host: api.osint-platform.example
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8000
```

### 5. Apply Kubernetes Manifests

```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/api-gateway-deployment.yaml
kubectl apply -f kubernetes/api-gateway-service.yaml
kubectl apply -f kubernetes/ingress.yaml

# Apply all microservices
kubectl apply -f kubernetes/
```

### 6. Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# View logs
kubectl logs -f deployment/api-gateway

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### 7. Initialize Databases

```bash
# Run migrations
kubectl exec -it deployment/api-gateway -- alembic upgrade head

# Setup databases
kubectl exec -it deployment/api-gateway -- python scripts/setup_databases.py
```

## Post-Deployment Configuration

### 1. SSL/TLS Certificate Setup

#### Using Cert-Manager (Kubernetes)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@osint-platform.example
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

#### Using Let's Encrypt (Docker Compose)

```bash
# Install certbot
apt-get install certbot

# Obtain certificate
certbot certonly --standalone -d api.osint-platform.example

# Copy certificates
cp /etc/letsencrypt/live/api.osint-platform.example/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/api.osint-platform.example/privkey.pem nginx/ssl/
```

### 2. Configure Firewall

```bash
# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow SSH
ufw allow 22/tcp

# Enable firewall
ufw enable
```

### 3. Setup Monitoring

See [Monitoring and Maintenance](#monitoring-and-maintenance) section.

### 4. Configure Backup Jobs

Setup automated backups (see [Database Schema - Backup and Recovery](./DATABASE_SCHEMA.md#backup-and-recovery)).

## Monitoring and Maintenance

### Prometheus and Grafana Setup

#### 1. Deploy Prometheus (Kubernetes)

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --set grafana.enabled=true \
  --set grafana.adminPassword=<strong-password>
```

#### 2. Access Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3000:80
```

Access: http://localhost:3000

### Log Aggregation

#### ELK Stack Deployment

**docker-compose.logging.yml**:
```yaml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    volumes:
      - es_logs:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Health Checks

Monitor these endpoints:
- `/health` - Overall system health
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe

### Automated Updates

Setup CI/CD pipeline for automated deployments:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: docker-compose -f docker-compose.prod.yml build

      - name: Push to registry
        run: docker-compose -f docker-compose.prod.yml push

      - name: Deploy to Kubernetes
        run: kubectl apply -f kubernetes/
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check database is running
docker-compose ps postgres

# Check connection
docker-compose exec api-gateway python -c "from database import engine; engine.connect()"

# View database logs
docker-compose logs postgres
```

#### 2. Service Not Starting

```bash
# Check logs
kubectl logs -f deployment/api-gateway

# Describe pod for events
kubectl describe pod <pod-name>

# Check resource usage
kubectl top pods
```

#### 3. Out of Memory

```bash
# Increase container memory limits
# Edit deployment and update resources.limits.memory

# Restart deployment
kubectl rollout restart deployment/api-gateway
```

#### 4. Slow Performance

- Check database query performance
- Review application logs for slow endpoints
- Monitor resource usage
- Scale horizontally by increasing replicas

### Logs Location

#### Docker Compose
```bash
docker-compose logs -f <service-name>
```

#### Kubernetes
```bash
kubectl logs -f deployment/<deployment-name>
kubectl logs -f pod/<pod-name>
```

### Rollback Deployment

#### Kubernetes
```bash
# View deployment history
kubectl rollout history deployment/api-gateway

# Rollback to previous version
kubectl rollout undo deployment/api-gateway

# Rollback to specific revision
kubectl rollout undo deployment/api-gateway --to-revision=2
```

#### Docker Compose
```bash
# Pull previous image version
docker pull osint/api-gateway:previous-tag

# Restart with previous version
docker-compose up -d
```

## Security Hardening

### 1. Network Security

- Use private networks for inter-service communication
- Implement network policies in Kubernetes
- Enable firewall rules
- Use VPN for administrative access

### 2. Secrets Management

- Use Kubernetes secrets or HashiCorp Vault
- Rotate secrets regularly
- Never commit secrets to version control
- Use encrypted environment variables

### 3. Container Security

- Run containers as non-root user
- Use minimal base images (Alpine)
- Scan images for vulnerabilities
- Implement resource limits

### 4. Application Security

- Enable HTTPS only
- Implement rate limiting
- Use strong authentication
- Regular security updates

## Scaling Guidelines

### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment api-gateway --replicas=5

# Docker Compose
docker-compose up -d --scale api-gateway=5
```

### Vertical Scaling

Update resource limits in deployment manifests or docker-compose.yml.

### Database Scaling

- PostgreSQL: Setup read replicas
- MongoDB: Enable sharding
- Redis: Setup cluster mode
- Elasticsearch: Add data nodes

## Maintenance Windows

Schedule regular maintenance:
- **Security patches**: Monthly
- **Database backups**: Daily
- **Log rotation**: Weekly
- **Performance review**: Quarterly

---

For additional support, contact the DevOps team or consult the [Configuration Reference](./CONFIGURATION.md).
