# OSINT Platform - Distributed Deployment

Complete enterprise-grade deployment configuration for the OSINT Intelligence Platform on Proxmox with distributed Raspberry Pi compute nodes.

## 📁 Directory Structure

```
deployment/
├── README.md                           # This file
├── QUICKSTART.md                       # Fast deployment guide
│
├── proxmox/                            # Proxmox VE deployment
│   ├── setup-proxmox-osint.sh         # Main setup script (LXC + VMs)
│   └── docker-compose-osint-platform.yml  # OSINT platform compose file
│
├── raspberry-pi/                       # Raspberry Pi configurations
│   ├── rpi5-primary/
│   │   └── setup-rpi5-primary.sh      # RPi5 16GB + 1TB SSD setup
│   ├── rpi5-secondary/
│   │   └── setup-rpi5-secondary.sh    # RPi5 8GB setup
│   └── rpi4-monitor/
│       └── setup-rpi4-monitor.sh      # RPi4 4GB network monitoring
│
├── banana-pi/                          # Network gateway
│   └── setup-banana-pi-openwrt.sh     # OpenWRT configuration
│
├── pi-hole/                            # DNS filtering (integrated in RPi4)
│
├── monitoring/                         # Monitoring stack
│   ├── prometheus-config.yml          # Prometheus configuration
│   └── alerts/
│       └── osint-alerts.yml           # Alert rules
│
├── network-awareness/                  # Network visibility
│   └── flow_analyzer.py               # Network flow analysis system
│
├── cloudflare-tunnel/                  # Secure remote access
│   └── setup-cloudflare-tunnel.sh     # Cloudflare Tunnel setup
│
├── security/                           # Security configurations
│   ├── firewall-rules/
│   └── vpn/
│
└── honeypot/                           # Optional honeypot infrastructure
    └── (optional deployment)
```

## 🚀 Quick Start

### Option 1: Fast Track (Recommended)

Follow the **[QUICKSTART.md](QUICKSTART.md)** guide for step-by-step deployment.

**Estimated Time:** 2-3 hours

### Option 2: Detailed Deployment

Follow the comprehensive guide in **[docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md](../docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md)**

**Estimated Time:** 4-5 hours (includes customization)

## 📋 What Gets Deployed

### Proxmox Node2

**11 LXC Containers + 1 VM:**

| Component | Count | Purpose |
|-----------|-------|---------|
| Database Services | 3 | PostgreSQL, MongoDB, Redis |
| ELK Stack | 3 | Elasticsearch, Logstash, Kibana |
| Monitoring | 2 | Prometheus, Grafana |
| OSINT Platform | 1 | Docker host for main platform |
| Network Monitoring | 2 | Flow collector, Security monitor |
| Kali Linux VM | 1 | OSINT tools and analysis |

### Raspberry Pi Cluster

**3 Nodes:**

| Device | Role | Services |
|--------|------|----------|
| RPi5 16GB + 1TB SSD | Primary Compute | Heavy workers, ML processor, data storage |
| RPi5 8GB | Secondary Compute | Light workers, distributed tasks |
| RPi4 4GB | Network Monitor | Pi-hole, ntopng, flow analysis |

### Network Infrastructure

- **Banana Pi Gateway:** Firewall, VPN, IDS, QoS
- **Network Awareness:** Complete traffic visibility
- **Security Monitoring:** IDS/IPS, anomaly detection
- **Remote Access:** Cloudflare Tunnel for secure access

## 🎯 Deployment Order

```
1. Banana Pi Gateway    (15 min)  ← Network foundation
2. Proxmox Infrastructure (45 min)  ← Core services
3. Raspberry Pi Nodes    (60 min)  ← Distributed compute
4. OSINT Platform       (20 min)  ← Application deployment
5. Monitoring Stack     (15 min)  ← Observability
6. Network Awareness    (10 min)  ← Network visibility
7. Cloudflare Tunnel    (15 min)  ← Remote access (optional)
```

**Total Time:** ~3 hours

## 🔧 Scripts Usage

### Proxmox Setup

```bash
# On Proxmox Node2
cd /opt/osint-deployment/deployment/proxmox
sudo ./setup-proxmox-osint.sh
```

Creates all containers, VMs, and base configuration.

### Raspberry Pi Setup

```bash
# Copy script to target Pi
scp deployment/raspberry-pi/rpi5-primary/setup-rpi5-primary.sh pi@10.0.0.10:~

# Execute on Pi
ssh pi@10.0.0.10
sudo bash setup-rpi5-primary.sh
```

Repeat for each Pi node.

### Banana Pi Gateway

```bash
# On Banana Pi (OpenWRT)
cd /tmp
wget <script-url> || scp from workstation
chmod +x setup-banana-pi-openwrt.sh
./setup-banana-pi-openwrt.sh
```

### Cloudflare Tunnel

```bash
# On Kali VM
scp deployment/cloudflare-tunnel/setup-cloudflare-tunnel.sh root@10.0.0.30:~
ssh root@10.0.0.30
bash setup-cloudflare-tunnel.sh
```

## 🛡️ Security Features

### Network Security
- ✅ Stateful firewall on gateway
- ✅ Network segmentation (LAN/DMZ/VPN)
- ✅ IDS/IPS with Suricata
- ✅ VPN access only (WireGuard)
- ✅ DNS filtering with Pi-hole

### Application Security
- ✅ JWT authentication
- ✅ RBAC authorization
- ✅ API rate limiting
- ✅ Input validation
- ✅ Encrypted communications

### Monitoring & Detection
- ✅ Real-time alerting
- ✅ Log aggregation (ELK)
- ✅ Security event correlation
- ✅ Anomaly detection
- ✅ Network flow analysis

## 📊 Monitoring

### Access Points

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| Prometheus | http://10.0.0.17:9090 | None |
| Grafana | http://10.0.0.18:3000 | admin/admin |
| Kibana | http://10.0.0.16:5601 | None |
| Pi-hole | http://10.0.0.12/admin | Set during setup |
| ntopng | http://10.0.0.12:3000 | admin/admin |
| Flower | http://10.0.0.20:5555 | Configured in .env |

### Pre-configured Dashboards

1. **Infrastructure Overview** - All nodes, resource usage, service health
2. **OSINT Platform** - API metrics, worker performance, queues
3. **Network Awareness** - Traffic flows, top talkers, applications
4. **Security** - Firewall activity, IDS alerts, anomalies

## 🔍 Verification

After deployment, run health check:

```bash
# Check all containers
pct list

# Check all Raspberry Pi nodes
for ip in 10.0.0.10 10.0.0.11 10.0.0.12; do
    ping -c 1 $ip && echo "$ip OK" || echo "$ip FAILED"
done

# Check critical services
curl http://10.0.0.20:8000/health  # OSINT API
curl http://10.0.0.17:9090/-/healthy  # Prometheus
curl http://10.0.0.14:9200/_cluster/health  # Elasticsearch
```

## 📝 Configuration

### Environment Variables

Each component has an `.env` file to configure:

**Docker Host (CT-200):**
```env
POSTGRES_PASSWORD=changeme
MONGO_PASSWORD=changeme
REDIS_PASSWORD=changeme
SHODAN_API_KEY=your-key
VIRUSTOTAL_API_KEY=your-key
```

**Raspberry Pi Nodes:**
Match the database passwords from Docker Host.

### Network Settings

**IP Address Plan:**
- Gateway: 10.0.0.1
- Raspberry Pi: 10.0.0.10-12
- Proxmox Services: 10.0.0.11-49
- DHCP Pool: 10.0.0.100-250

See `docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md` for complete IP allocation.

## 🐛 Troubleshooting

### Common Issues

**Container won't start:**
```bash
pct status <CTID>
pct logs <CTID>
pct start <CTID>
```

**Network connectivity:**
```bash
# Check routing
ip route

# Test DNS
dig @10.0.0.12 google.com

# Check firewall
iptables -L -n -v
```

**Services not responding:**
```bash
# Check Docker
systemctl status docker
docker compose ps

# Check logs
docker compose logs <service>
```

### Log Locations

- **Proxmox:** `journalctl -u <service>`
- **Containers:** `pct logs <CTID>` or `docker compose logs`
- **System:** `/var/log/syslog`
- **OSINT Platform:** `/opt/osint-platform/logs/`

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Fast deployment
- **[Complete Deployment Guide](../docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md)** - Detailed documentation
- **[Network Architecture](../docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md#network-topology)** - Network diagrams
- **[Security Guide](../docs/deployment/PROXMOX_DISTRIBUTED_DEPLOYMENT.md#security)** - Security best practices
- **[Operations Runbooks](../docs/operations/runbooks/)** - Operational procedures

## 🔄 Updates & Maintenance

### Regular Maintenance

**Daily:**
- Monitor dashboards
- Review security alerts
- Check service health

**Weekly:**
- Review logs
- Update block lists (Pi-hole)
- Performance review

**Monthly:**
- Security updates
- Capacity planning
- Documentation updates

### Updating the Platform

```bash
# On Docker host
cd /opt/osint-platform
git pull
docker compose build
docker compose up -d

# Run migrations if needed
docker compose exec osint-api alembic upgrade head
```

## 🆘 Support

- **Issues:** Create GitHub issue
- **Documentation:** Check `/docs` directory
- **Logs:** Service-specific locations
- **Community:** GitHub Discussions

## 📄 License

Same as main OSINT platform - see LICENSE file.

## 🙏 Acknowledgments

- Proxmox VE for virtualization platform
- Raspberry Pi Foundation for compute nodes
- OpenWRT for network gateway
- Pi-hole for DNS filtering
- Cloudflare for secure tunneling

---

**Version:** 1.0
**Last Updated:** 2025-11-18
**Deployment Architecture:** Proxmox + Raspberry Pi Distributed
