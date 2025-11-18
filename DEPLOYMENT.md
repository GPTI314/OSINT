# OSINT Toolkit - Deployment Guide

This guide covers deploying the OSINT Toolkit using Docker Compose and Kubernetes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Common Requirements

- Git
- Docker 20.10+
- Docker Compose 2.0+ (for Docker deployment)
- kubectl 1.24+ (for Kubernetes deployment)
- A Kubernetes cluster (for K8s deployment)

### System Requirements

**Minimum (Development)**:
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB

**Recommended (Production)**:
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+

## Docker Deployment

### Quick Start

1. **Clone the repository**:
```bash
git clone <repository-url>
cd OSINT
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

3. **Deploy**:
```bash
# Production deployment
./scripts/deploy-docker.sh production up

# Development deployment
./scripts/deploy-docker.sh dev up
```

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Build images
./scripts/build-images.sh
```

### Development Environment

The development environment includes additional tools:

- **Adminer**: Database management UI at http://localhost:8080
- **Redis Commander**: Redis management UI at http://localhost:8081

Start with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Kubernetes Deployment

### Prerequisites

1. **Kubernetes cluster** (one of):
   - Minikube (local development)
   - Kind (local development)
   - GKE, EKS, AKS (cloud)
   - Self-hosted cluster

2. **Additional tools**:
   - Helm 3.0+ (optional but recommended)
   - cert-manager (for TLS certificates)
   - NGINX Ingress Controller

### Installation Steps

#### 1. Prepare Secrets

```bash
cd k8s
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml and update all values
nano secrets.yaml
```

Encode secrets to base64:
```bash
echo -n "your-secret-value" | base64
```

#### 2. Update Configuration

Edit `k8s/configmap.yaml` and update:
- Domain names
- Service URLs
- Feature flags

Edit `k8s/ingress.yaml` and update:
- Host names
- Email for Let's Encrypt
- TLS configuration

#### 3. Deploy to Kubernetes

```bash
# Deploy everything
./scripts/deploy-k8s.sh apply

# Check status
./scripts/deploy-k8s.sh status

# View logs
./scripts/deploy-k8s.sh logs backend

# Delete deployment
./scripts/deploy-k8s.sh delete
```

#### 4. Manual Deployment

If you prefer manual deployment:

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ConfigMaps and Secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# 3. Create PVCs
kubectl apply -f k8s/pvc.yaml

# 4. Deploy databases
kubectl apply -f k8s/statefulset-postgres.yaml
kubectl apply -f k8s/statefulset-redis.yaml
kubectl apply -f k8s/statefulset-elasticsearch.yaml

# 5. Create services
kubectl apply -f k8s/service-postgres.yaml
kubectl apply -f k8s/service-redis.yaml
kubectl apply -f k8s/service-elasticsearch.yaml
kubectl apply -f k8s/service-backend.yaml
kubectl apply -f k8s/service-frontend.yaml

# 6. Deploy applications
kubectl apply -f k8s/deployment-backend.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/deployment-frontend.yaml

# 7. Configure networking and scaling
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

### Install NGINX Ingress Controller

If not already installed:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### Install cert-manager

For automatic TLS certificate management:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
POSTGRES_DB=osint
POSTGRES_USER=osint
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# Application
SECRET_KEY=<random-secret-key>
JWT_SECRET_KEY=<random-jwt-key>
DEBUG=false
LOG_LEVEL=info

# External URLs
CORS_ORIGINS=https://yourdomain.com
```

### Scaling

#### Docker Compose

Edit `docker-compose.yml`:
```yaml
services:
  worker:
    deploy:
      replicas: 4  # Increase worker count
```

#### Kubernetes

```bash
# Scale manually
kubectl scale deployment osint-backend -n osint --replicas=5

# Or edit HPA
kubectl edit hpa osint-backend-hpa -n osint
```

## Monitoring

### Health Checks

- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost/health

### Kubernetes Monitoring

```bash
# Get all resources
kubectl get all -n osint

# Check pod status
kubectl get pods -n osint -o wide

# View pod logs
kubectl logs -f <pod-name> -n osint

# Check HPA status
kubectl get hpa -n osint

# View events
kubectl get events -n osint --sort-by='.lastTimestamp'
```

### Metrics

The application exposes Prometheus metrics at:
- Backend: `/metrics`

## Troubleshooting

### Docker Issues

**Problem**: Container won't start
```bash
# Check logs
docker-compose logs <service-name>

# Rebuild
docker-compose up -d --build --force-recreate
```

**Problem**: Database connection failed
```bash
# Check if database is ready
docker-compose ps
docker-compose exec postgres pg_isready
```

### Kubernetes Issues

**Problem**: Pods not starting
```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n osint

# Check logs
kubectl logs <pod-name> -n osint

# Check events
kubectl get events -n osint
```

**Problem**: Image pull errors
```bash
# Check image pull secrets
kubectl get secrets -n osint

# Create registry secret if needed
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n osint
```

**Problem**: Database not ready
```bash
# Check StatefulSet status
kubectl get statefulset -n osint

# Check PVC status
kubectl get pvc -n osint

# View database logs
kubectl logs postgres-0 -n osint
```

**Problem**: Ingress not working
```bash
# Check ingress status
kubectl get ingress -n osint
kubectl describe ingress osint-ingress -n osint

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check certificate status
kubectl get certificate -n osint
```

### Common Solutions

1. **Reset Docker environment**:
```bash
docker-compose down -v
docker-compose up -d
```

2. **Reset Kubernetes deployment**:
```bash
./scripts/deploy-k8s.sh delete
./scripts/deploy-k8s.sh apply
```

3. **Check resource limits**:
```bash
# Docker
docker stats

# Kubernetes
kubectl top nodes
kubectl top pods -n osint
```

## Security Considerations

1. **Change default passwords** in `.env` and `secrets.yaml`
2. **Use strong secret keys** for JWT and application
3. **Enable TLS/SSL** in production
4. **Implement network policies** (included in K8s deployment)
5. **Regular security updates** of base images
6. **Backup databases** regularly
7. **Use secrets management** tools (HashiCorp Vault, AWS Secrets Manager)

## Backup and Recovery

### Docker

```bash
# Backup database
docker-compose exec postgres pg_dump -U osint osint > backup.sql

# Restore database
docker-compose exec -T postgres psql -U osint osint < backup.sql
```

### Kubernetes

```bash
# Backup
kubectl exec postgres-0 -n osint -- pg_dump -U osint osint > backup.sql

# Restore
kubectl exec -i postgres-0 -n osint -- psql -U osint osint < backup.sql
```

## Production Checklist

- [ ] All secrets updated from defaults
- [ ] TLS certificates configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented
- [ ] Resource limits configured
- [ ] Autoscaling tested
- [ ] Disaster recovery plan documented
- [ ] Security scan performed
- [ ] Load testing completed
- [ ] Documentation reviewed

## Support

For issues and questions:
- Check logs first
- Review this documentation
- Check GitHub issues
- Contact support team

## License

See LICENSE file for details.
