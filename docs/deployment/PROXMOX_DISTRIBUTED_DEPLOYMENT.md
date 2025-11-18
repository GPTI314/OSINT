# OSINT INTELLIGENCE PLATFORM - PROXMOX ENTERPRISE DEPLOYMENT

**Complete Distributed Network Architecture with Raspberry Pi Compute Nodes**

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Infrastructure Components](#infrastructure-components)
3. [Network Topology](#network-topology)
4. [Deployment Guide](#deployment-guide)
5. [Configuration](#configuration)
6. [Monitoring & Operations](#monitoring--operations)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

This deployment implements a complete, enterprise-grade OSINT Intelligence Platform using:

- **Proxmox VE** - Virtualization platform hosting core services
- **Raspberry Pi Cluster** - Distributed compute nodes for processing
- **Banana Pi Gateway** - Network security and routing (OpenWRT/pfSense)
- **Pi-hole** - DNS filtering and network awareness
- **Comprehensive Monitoring** - Full visibility across the infrastructure

### Design Principles

1. **Distributed Processing** - Workload distribution across multiple nodes
2. **Network Visibility** - Complete awareness of all network traffic
3. **Security First** - Defense in depth with multiple security layers
4. **High Availability** - Redundancy in critical components
5. **Scalability** - Easy to add more nodes and services

---

## Infrastructure Components

### Proxmox Node2 (MS-A2 Workstation)

**Specifications:** Debian Trixie 9.x, Multiple cores, 32GB+ RAM

**Containers (LXC):**

| ID | Name | IP | RAM | CPU | Storage | Purpose |
|----|------|-----|-----|-----|---------|---------|
| CT-101 | postgres-osint | 10.0.0.11 | 2GB | 2 | 20GB | PostgreSQL Database |
| CT-102 | mongodb-osint | 10.0.0.12 | 2GB | 2 | 30GB | MongoDB Document Store |
| CT-103 | redis-osint | 10.0.0.13 | 1GB | 1 | 10GB | Redis Cache/Broker |
| CT-104 | elasticsearch-osint | 10.0.0.14 | 4GB | 2 | 50GB | Elasticsearch |
| CT-105 | logstash-osint | 10.0.0.15 | 2GB | 2 | 20GB | Logstash |
| CT-106 | kibana-osint | 10.0.0.16 | 2GB | 2 | 10GB | Kibana |
| CT-107 | prometheus-osint | 10.0.0.17 | 2GB | 2 | 30GB | Prometheus |
| CT-108 | grafana-osint | 10.0.0.18 | 1GB | 1 | 10GB | Grafana |
| CT-200 | docker-osint | 10.0.0.20 | 8GB | 4 | 100GB | Docker Host for OSINT Platform |
| CT-400 | network-flow | 10.0.0.40 | 2GB | 2 | 20GB | Network Flow Collector (ntopng) |
| CT-401 | security-monitor | 10.0.0.41 | 2GB | 2 | 20GB | Security Monitor (Suricata/Zeek) |

**Virtual Machines:**

| ID | Name | IP | RAM | CPU | Storage | Purpose |
|----|------|-----|-----|-----|---------|---------|
| VM-300 | kali-osint | 10.0.0.30 | 4GB | 4 | 50GB | Kali Linux - OSINT Tools & Analysis |

### Raspberry Pi Cluster

**RPi5 Primary (16GB + 1TB SSD):**
- Hostname: osint-primary-rpi5
- IP: 10.0.0.10
- Role: Heavy processing, ML models, data storage
- Services: Heavy workers, ML processor, data pipeline, backup

**RPi5 Secondary (8GB):**
- Hostname: osint-secondary-rpi5
- IP: 10.0.0.11
- Role: Light processing, distributed tasks, backup receiver
- Services: Light workers, task processor, health monitor

**RPi4 Monitor (4GB):**
- Hostname: osint-monitor-rpi4
- IP: 10.0.0.12
- Role: Network monitoring and DNS filtering
- Services: Pi-hole, ntopng, network flow analysis, device discovery

### Network Gateway

**Banana Pi:**
- Hostname: osint-gateway
- WAN: DHCP (eth0)
- LAN: 10.0.0.1/24 (eth1)
- DMZ: 10.0.1.1/24 (eth2) - Optional
- Services: Firewall, NAT, VPN (WireGuard), IDS, QoS, NetFlow export

---

## Network Topology

```
┌────────────────────────────────────────────────────────────┐
│                    INTERNET / WAN                          │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│         Banana Pi - OpenWRT/pfSense Gateway                │
│  • Firewall Rules                                          │
│  • VPN Server (WireGuard)                                  │
│  • Traffic Shaping (QoS)                                   │
│  • Intrusion Detection                                     │
│  • NetFlow Export                                          │
└──────────────────────┬─────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│   LAN Net    │ │  DMZ Net  │ │  Mgmt Net   │
│ 10.0.0.0/24  │ │10.0.1.0/24│ │10.0.2.0/24  │
└───────┬──────┘ └────┬─────┘ └─────┬──────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│  Proxmox     │ │  RPi5     │ │  RPi4       │
│  Node2       │ │  16GB     │ │  4GB        │
│  (11 CT +    │ │  Primary  │ │  Monitor    │
│   1 VM)      │ │  + RPi5   │ │  (Pi-hole)  │
│              │ │  8GB Sec  │ │             │
└──────────────┘ └───────────┘ └─────────────┘
```

### Network Segmentation

**LAN (10.0.0.0/24) - Trusted Network:**
- Proxmox containers and VMs
- Raspberry Pi compute nodes
- Workstations
- Trusted devices

**DMZ (10.0.1.0/24) - Public Services (Optional):**
- Public-facing services
- Isolated from LAN
- Controlled access

**Management (10.0.2.0/24) - VPN Access:**
- WireGuard VPN clients
- Remote management
- Secure administrative access

---

## Deployment Guide

### Prerequisites

1. **Hardware:**
   - Proxmox Node2 (running Debian Trixie 9.x)
   - Raspberry Pi 5 (16GB) with 1TB SSD
   - Raspberry Pi 5 (8GB)
   - Raspberry Pi 4 (4GB)
   - Banana Pi (with OpenWRT)
   - Network switch (managed L2/L3 recommended)
   - Sufficient power supplies and cooling

2. **Software:**
   - Proxmox VE installed on Node2
   - Raspberry Pi OS (64-bit) or Ubuntu Server 24.04 for RPis
   - OpenWRT for Banana Pi
   - Cloudflare account (for tunnel)

3. **Network:**
   - Internet connection
   - Ethernet cables
   - Static IP planning completed

### Step 1: Proxmox Infrastructure Setup

```bash
# On Proxmox Node2
cd /opt
git clone <repository-url> osint-deployment
cd osint-deployment/deployment/proxmox

# Make scripts executable
chmod +x setup-proxmox-osint.sh

# Run setup (creates all containers and VMs)
./setup-proxmox-osint.sh
```

This creates:
- All LXC containers with appropriate resources
- Kali Linux VM (requires manual OS installation)
- Network bridges and firewall rules
- Base service installations

**Expected Duration:** 30-45 minutes

### Step 2: Raspberry Pi Setup

#### RPi5 Primary (16GB + 1TB SSD)

```bash
# Copy script to RPi
scp deployment/raspberry-pi/rpi5-primary/setup-rpi5-primary.sh pi@10.0.0.10:~

# SSH to RPi
ssh pi@10.0.0.10

# Run setup
sudo bash setup-rpi5-primary.sh
```

**Important:** The script will format the 1TB SSD. Confirm before proceeding.

#### RPi5 Secondary (8GB)

```bash
# Copy and run
scp deployment/raspberry-pi/rpi5-secondary/setup-rpi5-secondary.sh pi@10.0.0.11:~
ssh pi@10.0.0.11
sudo bash setup-rpi5-secondary.sh
```

#### RPi4 Monitor (4GB)

```bash
# Copy and run
scp deployment/raspberry-pi/rpi4-monitor/setup-rpi4-monitor.sh pi@10.0.0.12:~
ssh pi@10.0.0.12
sudo bash setup-rpi4-monitor.sh
```

**Expected Duration per Pi:** 20-30 minutes

### Step 3: Banana Pi Gateway Setup

1. **Flash OpenWRT:**
   ```bash
   # Download OpenWRT for your Banana Pi model
   # Flash to SD card
   sudo dd if=openwrt-*.img of=/dev/sdX bs=4M status=progress
   ```

2. **Initial Configuration:**
   ```bash
   # Connect to Banana Pi via Ethernet
   # Default IP: 192.168.1.1
   ssh root@192.168.1.1

   # Set password
   passwd
   ```

3. **Run Configuration Script:**
   ```bash
   # Copy script
   scp deployment/banana-pi/setup-banana-pi-openwrt.sh root@192.168.1.1:/tmp/

   # Run setup
   ssh root@192.168.1.1
   cd /tmp
   chmod +x setup-banana-pi-openwrt.sh
   ./setup-banana-pi-openwrt.sh
   ```

**Expected Duration:** 15-20 minutes

### Step 4: Deploy OSINT Platform

1. **On Docker Host (CT-200):**
   ```bash
   # Enter container
   pct enter 200

   # Clone repository
   git clone <repository-url> /opt/osint-platform
   cd /opt/osint-platform

   # Copy deployment compose file
   cp /path/to/deployment/proxmox/docker-compose-osint-platform.yml docker-compose.yml

   # Configure environment
   cp .env.example .env
   nano .env  # Update passwords and settings

   # Start services
   docker compose up -d
   ```

2. **Initialize Database:**
   ```bash
   # Run migrations
   docker compose exec osint-api alembic upgrade head

   # Create admin user
   docker compose exec osint-api python scripts/create_admin.py
   ```

**Expected Duration:** 10-15 minutes

### Step 5: Cloudflare Tunnel (Windows <-> Kali)

1. **On Kali VM (VM-300):**
   ```bash
   # Copy script
   scp deployment/cloudflare-tunnel/setup-cloudflare-tunnel.sh root@10.0.0.30:~

   # Run setup
   ssh root@10.0.0.30
   bash setup-cloudflare-tunnel.sh
   ```

2. **Authenticate and Create Tunnel:**
   ```bash
   # Login to Cloudflare
   cloudflared tunnel login

   # Create tunnel
   cloudflared tunnel create osint-kali-tunnel

   # Route DNS
   cloudflared tunnel route dns osint-kali-tunnel kali-osint.yourdomain.com

   # Start tunnel
   systemctl start cloudflared
   systemctl enable cloudflared
   ```

3. **Windows Client:**
   - No software needed for browser access
   - Access: https://kali-osint.yourdomain.com

**Expected Duration:** 10-15 minutes

---

## Configuration

### Environment Variables

Update `.env` files on each component:

**Docker Host (CT-200):**
```env
# Database Passwords
POSTGRES_PASSWORD=<strong-password>
MONGO_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# API Keys
SHODAN_API_KEY=your-key
VIRUSTOTAL_API_KEY=your-key

# Flower Monitoring
FLOWER_USER=admin
FLOWER_PASSWORD=<strong-password>
```

**Raspberry Pi Nodes:**
```env
# Match Docker Host passwords
REDIS_PASSWORD=<strong-password>
POSTGRES_PASSWORD=<strong-password>
MONGO_PASSWORD=<strong-password>
```

### Pi-hole Configuration

1. **Access Pi-hole Admin:**
   ```
   http://10.0.0.12/admin
   ```

2. **Set Password:**
   ```bash
   ssh pi@10.0.0.12
   pihole -a -p
   ```

3. **Configure Network:**
   - Set as primary DNS in Banana Pi DHCP
   - Add custom block lists
   - Enable query logging

### Network Flow Analysis

The network awareness system collects:
- NetFlow/sFlow from Banana Pi
- DNS queries from Pi-hole
- Traffic metrics from ntopng
- Security events from Suricata

**Access Points:**
- ntopng: http://10.0.0.12:3000
- Pi-hole: http://10.0.0.12/admin
- Flow Analyzer: Integrated with Elasticsearch

---

## Monitoring & Operations

### Monitoring Stack

**Prometheus (10.0.0.17:9090):**
- Metrics collection from all nodes
- Scrapes exporters every 30s
- Retention: 15 days

**Grafana (10.0.0.18:3000):**
- Visualization dashboards
- Alerting rules
- Default login: admin/admin

**Elasticsearch (10.0.0.14:9200):**
- Log aggregation
- Network flow data
- DNS queries
- Security events

**Kibana (10.0.0.16:5601):**
- Log visualization
- Network analytics
- Security dashboards

### Key Metrics

**System Metrics:**
- CPU usage per node
- Memory utilization
- Disk I/O and usage
- Network bandwidth

**Application Metrics:**
- API request rates
- Worker queue depth
- Task completion times
- Error rates

**Network Metrics:**
- Flow counts
- Top talkers
- Application distribution
- Anomaly scores

**Security Metrics:**
- Firewall blocks
- IDS alerts
- Failed logins
- DNS blocks (Pi-hole)

### Dashboards

Import pre-configured dashboards:

1. **Infrastructure Overview:**
   - All nodes status
   - Resource utilization
   - Service health

2. **OSINT Platform:**
   - API metrics
   - Worker performance
   - Task queues

3. **Network Awareness:**
   - Traffic flows
   - Top devices
   - Application usage
   - Security events

4. **Security Dashboard:**
   - Firewall activity
   - IDS alerts
   - Anomalies
   - Threat intelligence

---

## Security

### Defense in Depth

**Layer 1: Network Perimeter (Banana Pi)**
- Stateful firewall
- IDS/IPS (Suricata)
- VPN only for remote access
- NetFlow monitoring

**Layer 2: Network Segmentation**
- VLAN isolation
- LAN/DMZ separation
- Access control lists

**Layer 3: Host-based Security**
- UFW firewalls on all nodes
- SSH key authentication
- Fail2ban
- Automatic updates

**Layer 4: Application Security**
- JWT authentication
- RBAC authorization
- API rate limiting
- Input validation

**Layer 5: Monitoring & Detection**
- Real-time alerting
- Log aggregation
- Anomaly detection
- Security event correlation

### Firewall Rules

**Banana Pi (Gateway):**
```
WAN → LAN: DENY (except VPN)
LAN → WAN: ALLOW (NAT)
LAN → DMZ: ALLOW (specific services)
DMZ → LAN: DENY
```

**All Nodes:**
- Allow from 10.0.0.0/24
- Deny from WAN
- Service-specific ports only

### VPN Access

**WireGuard on Banana Pi:**
- Port: 51820/UDP
- Network: 10.0.2.0/24
- Encrypted tunnels
- Client configs in LuCI

### Security Checklist

- [ ] All default passwords changed
- [ ] SSH key authentication enabled
- [ ] Firewalls configured and enabled
- [ ] VPN tested and working
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented
- [ ] Incident response plan documented
- [ ] Regular security updates scheduled

---

## Troubleshooting

### Container Issues

**Container won't start:**
```bash
# Check status
pct status <CTID>

# View logs
pct logs <CTID>

# Try manual start
pct start <CTID>

# Enter console
pct enter <CTID>
```

**Network issues:**
```bash
# Check network config
pct config <CTID>

# Verify bridge
ip link show vmbr0

# Test connectivity
pct exec <CTID> -- ping 8.8.8.8
```

### Raspberry Pi Issues

**Services not starting:**
```bash
# Check Docker
systemctl status docker

# Check containers
docker compose ps

# View logs
docker compose logs <service>

# Restart services
docker compose restart
```

**SSD not mounting:**
```bash
# Check mount point
mountpoint /mnt/ssd

# Check fstab
cat /etc/fstab

# Manual mount
mount -a
```

### Network Issues

**No internet access:**
```bash
# Check gateway
ip route

# Test DNS
nslookup google.com

# Check Pi-hole
dig @10.0.0.12 google.com
```

**Slow performance:**
```bash
# Check bandwidth
iftop

# Check connections
netstat -an | grep ESTABLISHED | wc -l

# Check QoS
tc -s qdisc show dev eth0
```

### Common Solutions

1. **High CPU Usage:**
   - Check worker concurrency
   - Review Celery tasks
   - Scale resources

2. **Memory Issues:**
   - Check container limits
   - Review application logs
   - Increase swap if needed

3. **Disk Full:**
   - Clean Docker images: `docker system prune`
   - Rotate logs
   - Check Elasticsearch indices

4. **Network Congestion:**
   - Review QoS settings
   - Check for bandwidth hogs in ntopng
   - Adjust traffic shaping

---

## Backup & Recovery

### Backup Strategy

**Daily:**
- PostgreSQL database
- MongoDB collections
- Configuration files

**Weekly:**
- Full system backups
- Elasticsearch snapshots
- Log archives

**Monthly:**
- Complete infrastructure backup
- Documentation updates
- Security audit

### Backup Locations

- Primary: RPi5 1TB SSD (`/mnt/ssd/backups`)
- Secondary: RPi5 Secondary
- Offsite: Configured cloud storage

### Recovery Procedures

See `docs/deployment/BACKUP_RECOVERY.md` for detailed recovery procedures.

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor dashboards
- Review security alerts
- Check service health

**Weekly:**
- Review logs
- Update block lists
- Performance review

**Monthly:**
- Security updates
- Capacity planning
- Documentation updates

**Quarterly:**
- Full security audit
- Disaster recovery test
- Architecture review

---

## Support & Documentation

- **Main Documentation:** `/docs`
- **API Documentation:** `http://10.0.0.20:8000/docs`
- **Network Diagrams:** `/docs/deployment/diagrams`
- **Runbooks:** `/docs/operations/runbooks`

---

## Appendix

### A. IP Address Allocation

| IP Range | Purpose |
|----------|---------|
| 10.0.0.1 | Gateway (Banana Pi) |
| 10.0.0.10-19 | Raspberry Pi Nodes |
| 10.0.0.20-29 | Proxmox Application Containers |
| 10.0.0.30-39 | Proxmox VMs |
| 10.0.0.40-49 | Proxmox Monitoring |
| 10.0.0.100-250 | DHCP Pool |

### B. Port Reference

| Port | Service | Host |
|------|---------|------|
| 80/443 | Web UI | Gateway |
| 8000 | OSINT API | CT-200 |
| 5555 | Flower | CT-200 |
| 5432 | PostgreSQL | CT-101 |
| 27017 | MongoDB | CT-102 |
| 6379 | Redis | CT-103 |
| 9200 | Elasticsearch | CT-104 |
| 5601 | Kibana | CT-106 |
| 9090 | Prometheus | CT-107 |
| 3000 | Grafana/ntopng | CT-108/RPi4 |

### C. Credentials

**IMPORTANT:** Change all default credentials!

See `docs/deployment/CREDENTIALS.md` (not in git) for production credentials.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-18
**Maintained By:** OSINT Platform Team
