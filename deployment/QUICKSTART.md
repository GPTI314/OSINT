# OSINT Platform - Distributed Deployment Quick Start Guide

**Fast-track deployment for the complete distributed OSINT platform**

## 🚀 Overview

This guide will get you from hardware to fully operational OSINT platform in approximately **2-3 hours**.

## ✅ Pre-Deployment Checklist

### Hardware Ready
- [ ] Proxmox Node2 (Debian Trixie 9.x) - powered on and accessible
- [ ] Raspberry Pi 5 (16GB) with 1TB SSD - powered and connected
- [ ] Raspberry Pi 5 (8GB) - powered and connected
- [ ] Raspberry Pi 4 (4GB) - powered and connected
- [ ] Banana Pi with OpenWRT - flashed and ready
- [ ] All devices connected to network switch
- [ ] Internet connectivity working

### Software Prepared
- [ ] Repository cloned
- [ ] SSH access to all devices configured
- [ ] Proxmox web UI accessible
- [ ] OpenWRT installed on Banana Pi

### Network Planning
- [ ] IP addresses planned (see deployment doc)
- [ ] Domain name ready (for Cloudflare Tunnel)
- [ ] Cloudflare account created
- [ ] Network diagram reviewed

## 🎯 Deployment Steps

### Phase 1: Gateway Setup (15 min)

**Set up network gateway first to provide network services**

```bash
# 1. Access Banana Pi
ssh root@192.168.1.1  # Default OpenWRT IP

# 2. Set password
passwd

# 3. Upload and run setup script
# From your workstation:
scp deployment/banana-pi/setup-banana-pi-openwrt.sh root@192.168.1.1:/tmp/

# On Banana Pi:
cd /tmp
chmod +x setup-banana-pi-openwrt.sh
./setup-banana-pi-openwrt.sh

# 4. Verify access
# Access LuCI: https://10.0.0.1
```

**Outcome:** Network gateway operational with firewall, DHCP, and routing

---

### Phase 2: Proxmox Infrastructure (45 min)

**Deploy all containers and VMs on Proxmox**

```bash
# 1. SSH to Proxmox Node2
ssh root@proxmox-node2

# 2. Clone repository
cd /opt
git clone <repository-url> osint-deployment
cd osint-deployment/deployment/proxmox

# 3. Run Proxmox setup
chmod +x setup-proxmox-osint.sh
./setup-proxmox-osint.sh

# 4. Wait for completion (30-45 min)
# Script creates:
# - 11 LXC containers
# - 1 VM (Kali - requires manual install)
# - Network configuration
# - Base services

# 5. Verify containers
pct list

# 6. Check services
pct exec 101 -- systemctl status postgresql
pct exec 103 -- systemctl status redis-server
pct exec 104 -- systemctl status elasticsearch
```

**Outcome:** All infrastructure containers running

---

### Phase 3: Raspberry Pi Deployment (60 min)

**Set up all three Raspberry Pi nodes in parallel**

#### RPi5 Primary (20 min)

```bash
# Terminal 1
scp deployment/raspberry-pi/rpi5-primary/setup-rpi5-primary.sh pi@10.0.0.10:~
ssh pi@10.0.0.10
sudo bash setup-rpi5-primary.sh
```

#### RPi5 Secondary (20 min)

```bash
# Terminal 2
scp deployment/raspberry-pi/rpi5-secondary/setup-rpi5-secondary.sh pi@10.0.0.11:~
ssh pi@10.0.0.11
sudo bash setup-rpi5-secondary.sh
```

#### RPi4 Monitor (20 min)

```bash
# Terminal 3
scp deployment/raspberry-pi/rpi4-monitor/setup-rpi4-monitor.sh pi@10.0.0.12:~
ssh pi@10.0.0.12
sudo bash setup-rpi4-monitor.sh
```

**Outcome:** All Raspberry Pi nodes configured with Docker and services

---

### Phase 4: OSINT Platform Deployment (20 min)

**Deploy the actual OSINT application**

```bash
# 1. Access Docker host container
pct enter 200

# 2. Clone OSINT platform
git clone <repository-url> /opt/osint-platform
cd /opt/osint-platform

# 3. Copy deployment compose
cp /opt/osint-deployment/deployment/proxmox/docker-compose-osint-platform.yml docker-compose.yml

# 4. Configure environment
cp .env.example .env
nano .env
# Update:
# - POSTGRES_PASSWORD
# - MONGO_PASSWORD
# - REDIS_PASSWORD
# - API keys (Shodan, VirusTotal, etc.)

# 5. Start services
docker compose up -d

# 6. Initialize database
docker compose exec osint-api alembic upgrade head

# 7. Create admin user
docker compose exec osint-api python -c "
from auth.password import hash_password
from database.models import User
print('Admin password:', hash_password('changeme'))
"

# 8. Verify services
docker compose ps
curl http://localhost:8000/health
```

**Outcome:** OSINT platform running and accessible

---

### Phase 5: Network Monitoring (10 min)

**Configure and verify network awareness**

```bash
# 1. Access Pi-hole admin
# Browser: http://10.0.0.12/admin

# 2. Set Pi-hole password
ssh pi@10.0.0.12
pihole -a -p

# 3. Configure DNS on gateway
# LuCI: https://10.0.0.1
# Navigate to: Network > DHCP and DNS
# Set DNS forwarder: 10.0.0.12

# 4. Access ntopng
# Browser: http://10.0.0.12:3000

# 5. Verify flow collection
# Check Elasticsearch for network-flows index
curl http://10.0.0.14:9200/_cat/indices?v
```

**Outcome:** Complete network visibility operational

---

### Phase 6: Monitoring Setup (15 min)

**Configure monitoring and dashboards**

```bash
# 1. Copy Prometheus config
pct push 107 deployment/monitoring/prometheus-config.yml /etc/prometheus/prometheus.yml

# 2. Copy alert rules
pct push 107 deployment/monitoring/alerts/osint-alerts.yml /etc/prometheus/alerts/osint-alerts.yml

# 3. Restart Prometheus
pct exec 107 -- systemctl restart prometheus

# 4. Access Prometheus
# Browser: http://10.0.0.17:9090

# 5. Access Grafana
# Browser: http://10.0.0.18:3000
# Login: admin/admin (change on first login)

# 6. Import dashboards
# Grafana > Dashboards > Import
# Use dashboard IDs:
# - 1860 (Node Exporter)
# - 893 (Docker)
# - 7362 (PostgreSQL)
```

**Outcome:** Full monitoring stack operational

---

### Phase 7: Cloudflare Tunnel (Optional, 15 min)

**Enable secure remote access to Kali VM**

```bash
# 1. Setup tunnel on Kali
scp deployment/cloudflare-tunnel/setup-cloudflare-tunnel.sh root@10.0.0.30:~
ssh root@10.0.0.30
bash setup-cloudflare-tunnel.sh

# 2. Authenticate
cloudflared tunnel login

# 3. Create tunnel
cloudflared tunnel create osint-kali-tunnel

# 4. Route DNS
cloudflared tunnel route dns osint-kali-tunnel kali-osint.yourdomain.com

# 5. Start tunnel
systemctl start cloudflared
systemctl enable cloudflared

# 6. Verify
curl https://kali-osint.yourdomain.com
```

**Outcome:** Secure remote access to Kali tools

---

## 🔍 Verification & Testing

### Infrastructure Health Check

```bash
# Run this script to check all services
cat > check-health.sh << 'EOF'
#!/bin/bash

echo "=== Infrastructure Health Check ==="
echo ""

# Proxmox Containers
echo "Proxmox Containers:"
pct list | grep running | wc -l
echo " containers running"

# Raspberry Pi Nodes
echo ""
echo "Raspberry Pi Nodes:"
for ip in 10.0.0.10 10.0.0.11 10.0.0.12; do
    if ping -c 1 -W 1 $ip &> /dev/null; then
        echo "  ✓ $ip online"
    else
        echo "  ✗ $ip OFFLINE"
    fi
done

# Critical Services
echo ""
echo "Critical Services:"
services=(
    "10.0.0.11:5432:PostgreSQL"
    "10.0.0.13:6379:Redis"
    "10.0.0.14:9200:Elasticsearch"
    "10.0.0.20:8000:OSINT API"
    "10.0.0.17:9090:Prometheus"
    "10.0.0.18:3000:Grafana"
)

for service in "${services[@]}"; do
    IFS=':' read -r ip port name <<< "$service"
    if nc -z -w1 $ip $port 2>/dev/null; then
        echo "  ✓ $name ($ip:$port)"
    else
        echo "  ✗ $name UNREACHABLE ($ip:$port)"
    fi
done

echo ""
echo "=== Health Check Complete ==="
EOF

chmod +x check-health.sh
./check-health.sh
```

### Access All Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Gateway (LuCI) | https://10.0.0.1 | root / your-password |
| OSINT API | http://10.0.0.20:8000/docs | - |
| Flower (Celery) | http://10.0.0.20:5555 | admin / flower-password |
| Pi-hole | http://10.0.0.12/admin | pihole / your-password |
| ntopng | http://10.0.0.12:3000 | admin / admin |
| Kibana | http://10.0.0.16:5601 | - |
| Grafana | http://10.0.0.18:3000 | admin / admin |
| Prometheus | http://10.0.0.17:9090 | - |
| Kali (Cloudflare) | https://kali-osint.yourdomain.com | - |

### Run Test OSINT Query

```bash
# Test domain intelligence gathering
curl -X POST http://10.0.0.20:8000/api/v1/intelligence/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "include_subdomains": true}'

# Check Celery tasks
curl http://10.0.0.20:5555/api/tasks

# View logs
ssh root@proxmox-node2
pct exec 200 -- docker compose logs -f --tail=50
```

---

## 🛡️ Post-Deployment Security

### Immediate Actions

```bash
# 1. Change all default passwords
# - Proxmox root password
# - Container passwords
# - Pi-hole admin password
# - Grafana admin password
# - Database passwords

# 2. Setup SSH keys (disable password auth)
ssh-keygen -t ed25519
ssh-copy-id root@10.0.0.1
ssh-copy-id pi@10.0.0.10
# ... for all nodes

# 3. Enable firewalls
# Already done by setup scripts, verify:
ssh pi@10.0.0.10 "sudo ufw status"

# 4. Configure WireGuard VPN
# Access: https://10.0.0.1
# Navigate to: Services > WireGuard
```

### Backup Configuration

```bash
# 1. Verify backup services running
ssh pi@10.0.0.10
docker compose ps | grep backup

# 2. Test manual backup
docker compose exec backup-service /backup-now.sh

# 3. Verify backup location
ls -lh /mnt/ssd/backups/

# 4. Configure offsite backup (optional)
# Edit: /opt/osint-platform-rpi5/.env
# Add: BACKUP_REMOTE_SERVER=user@backup-server.com
```

---

## 📊 Monitoring Dashboard Setup

### Import Recommended Dashboards

1. **Access Grafana:** http://10.0.0.18:3000

2. **Add Prometheus Data Source:**
   - Configuration > Data Sources > Add data source
   - Select Prometheus
   - URL: http://10.0.0.17:9090
   - Save & Test

3. **Import Dashboards:**
   - Dashboards > Import
   - Enter Dashboard ID:
     - **1860** - Node Exporter Full
     - **893** - Docker & System Monitoring
     - **7362** - PostgreSQL Database
     - **11074** - Nginx
     - **7249** - Redis Dashboard

4. **Configure Alerts:**
   - Alerting > Notification channels
   - Add: Slack/Email/Webhook
   - Test notification

---

## 🚨 Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check logs
docker compose logs <service-name>

# Restart service
docker compose restart <service-name>

# Check resources
htop
df -h
```

**Network connectivity issues:**
```bash
# Check routing
ip route

# Test DNS
dig @10.0.0.12 google.com

# Check firewall
iptables -L -n -v
```

**Container issues:**
```bash
# Check container status
pct list

# View container logs
pct enter <CTID>
journalctl -xe
```

**Raspberry Pi issues:**
```bash
# Check temperature
vcgencmd measure_temp

# Check disk
df -h /mnt/ssd

# Check Docker
systemctl status docker
docker info
```

---

## 📝 Next Steps

After successful deployment:

1. **Review Documentation:**
   - Read: `docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md`
   - Review: `docs/operations/runbooks/`

2. **Configure Integrations:**
   - Add API keys for OSINT sources
   - Configure webhooks for alerts
   - Setup notification channels

3. **Customize:**
   - Adjust worker concurrency
   - Tune QoS settings
   - Configure block lists

4. **Test:**
   - Run sample OSINT queries
   - Test failover scenarios
   - Verify backups

5. **Monitor:**
   - Watch dashboards for 24 hours
   - Review alerts
   - Optimize as needed

---

## 🆘 Support

- **Documentation:** `/docs`
- **Logs:** Check service-specific logs
- **Health Checks:** `./check-health.sh`
- **Issues:** Create GitHub issue

---

## 📋 Deployment Checklist

Track your progress:

- [ ] Phase 1: Gateway Setup
- [ ] Phase 2: Proxmox Infrastructure
- [ ] Phase 3: Raspberry Pi Deployment
- [ ] Phase 4: OSINT Platform Deployment
- [ ] Phase 5: Network Monitoring
- [ ] Phase 6: Monitoring Setup
- [ ] Phase 7: Cloudflare Tunnel (optional)
- [ ] Verification & Testing
- [ ] Post-Deployment Security
- [ ] Monitoring Dashboard Setup
- [ ] Documentation Review

---

**Total Deployment Time:** 2-3 hours
**Difficulty:** Intermediate to Advanced
**Result:** Production-ready distributed OSINT platform

🎉 **Congratulations!** Your distributed OSINT Intelligence Platform is now operational!
