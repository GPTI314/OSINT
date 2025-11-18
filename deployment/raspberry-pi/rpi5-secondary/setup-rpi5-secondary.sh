#!/bin/bash
###############################################################################
# Raspberry Pi 5 (8GB RAM) - Secondary Compute Node Setup
# Hostname: osint-secondary-rpi5
# IP: 10.0.0.11
# Purpose: Secondary processing, redundancy, distributed tasks
###############################################################################

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
HOSTNAME="osint-secondary-rpi5"
IP_ADDRESS="10.0.0.11"
GATEWAY="10.0.0.1"
DNS_SERVER="10.0.0.12"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
       log_error "This script must be run as root"
       exit 1
    fi
}

###############################################################################
# System Configuration
###############################################################################

configure_hostname() {
    log_info "Configuring hostname..."
    hostnamectl set-hostname ${HOSTNAME}
    echo "127.0.1.1 ${HOSTNAME}" >> /etc/hosts
}

configure_network() {
    log_info "Configuring static IP address..."

    cat > /etc/network/interfaces.d/eth0 << EOF
auto eth0
iface eth0 inet static
    address ${IP_ADDRESS}
    netmask 255.255.255.0
    gateway ${GATEWAY}
    dns-nameservers ${DNS_SERVER} 8.8.8.8
EOF

    log_info "Network configured. Restart required for changes to take effect."
}

###############################################################################
# System Updates and Dependencies
###############################################################################

update_system() {
    log_info "Updating system packages..."
    apt update
    apt upgrade -y
    apt autoremove -y
}

install_dependencies() {
    log_info "Installing system dependencies..."
    apt install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        iotop \
        nethogs \
        tmux \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        nfs-common \
        rsync
}

###############################################################################
# Docker Installation
###############################################################################

install_docker() {
    log_info "Installing Docker..."

    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker

    usermod -aG docker pi || true

    docker --version
    docker compose version
}

configure_docker() {
    log_info "Configuring Docker daemon..."

    mkdir -p /etc/docker

    cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "metrics-addr": "0.0.0.0:9323",
  "experimental": false,
  "live-restore": true
}
EOF

    systemctl restart docker
}

###############################################################################
# OSINT Platform Deployment
###############################################################################

deploy_osint_platform() {
    log_info "Deploying OSINT platform services..."

    mkdir -p /opt/osint-platform-rpi5-secondary
    cd /opt/osint-platform-rpi5-secondary

    cat > docker-compose.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  # Light Processing Worker
  osint-worker-light:
    image: osint-platform/workers:latest
    container_name: rpi5-secondary-worker
    environment:
      - WORKER_TYPE=light_processing
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - DATABASE_URL=postgresql+asyncpg://osint_user:${POSTGRES_PASSWORD}@10.0.0.11:5432/osint_platform
      - MONGODB_URL=mongodb://osint_user:${MONGO_PASSWORD}@10.0.0.12:27017/osint_platform
      - ELASTICSEARCH_URL=http://10.0.0.14:9200
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - WORKER_QUEUE=notifications,email,reports,backup
      - WORKER_CONCURRENCY=4
    volumes:
      - ./logs:/logs
      - ./data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 6G
        reservations:
          cpus: '2'
          memory: 3G
    network_mode: host

  # Distributed Task Processor
  task-processor:
    image: osint-platform/task-processor:latest
    container_name: rpi5-secondary-tasks
    environment:
      - DATABASE_URL=postgresql+asyncpg://osint_user:${POSTGRES_PASSWORD}@10.0.0.11:5432/osint_platform
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - TASK_QUEUE=distributed_tasks
    volumes:
      - ./logs:/logs
      - ./data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    network_mode: host

  # Backup Worker (receives backups from primary)
  backup-receiver:
    image: osint-platform/backup-receiver:latest
    container_name: rpi5-secondary-backup
    environment:
      - BACKUP_PATH=/backups
      - PRIMARY_SERVER=10.0.0.10
      - SYNC_SCHEDULE=0 3 * * *
    volumes:
      - ./backups:/backups
      - ./logs:/logs
    restart: unless-stopped
    network_mode: host

  # Monitoring Agents
  node-exporter:
    image: prom/node-exporter:latest
    container_name: rpi5-secondary-node-exporter
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'
    restart: unless-stopped
    network_mode: host
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 128M

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: rpi5-secondary-cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    restart: unless-stopped
    network_mode: host
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M

  # Health Check Service
  health-monitor:
    image: osint-platform/health-monitor:latest
    container_name: rpi5-secondary-health
    environment:
      - PROMETHEUS_URL=http://10.0.0.17:9090
      - ALERT_WEBHOOK=${ALERT_WEBHOOK_URL}
      - CHECK_INTERVAL=60
    restart: unless-stopped
    network_mode: host
EOFCOMPOSE

    cat > .env << 'EOFENV'
# Raspberry Pi 5 Secondary - Environment Configuration
REDIS_PASSWORD=changeme
POSTGRES_PASSWORD=changeme
MONGO_PASSWORD=changeme

# Worker Configuration
WORKER_CONCURRENCY=4
WORKER_QUEUE=notifications,email,reports,backup

# Alert Configuration
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EOFENV

    log_warn "Environment file created at /opt/osint-platform-rpi5-secondary/.env"
    log_warn "Please update passwords and configuration before starting services!"
}

###############################################################################
# Monitoring Setup
###############################################################################

setup_monitoring() {
    log_info "Setting up monitoring agents..."

    cat > /usr/local/bin/rpi5-secondary-monitor.sh << 'EOFMON'
#!/bin/bash
# RPi5 Secondary System Monitor

PUSHGATEWAY="http://10.0.0.17:9091/metrics/job/rpi5_secondary"

CPU_TEMP=$(vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')

cat <<EOF | curl --data-binary @- $PUSHGATEWAY
# TYPE rpi5_secondary_cpu_temperature gauge
rpi5_secondary_cpu_temperature $CPU_TEMP
# TYPE rpi5_secondary_memory_usage gauge
rpi5_secondary_memory_usage $MEM_USAGE
EOF
EOFMON

    chmod +x /usr/local/bin/rpi5-secondary-monitor.sh
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/rpi5-secondary-monitor.sh") | crontab -
}

###############################################################################
# Security Hardening
###############################################################################

configure_security() {
    log_info "Configuring security settings..."

    apt install -y ufw

    ufw allow 22/tcp
    ufw allow 9323/tcp
    ufw allow 9100/tcp
    ufw allow 8080/tcp
    ufw allow from 10.0.0.0/24

    ufw --force enable
}

###############################################################################
# Post-Installation
###############################################################################

post_install_info() {
    log_info "=========================================="
    log_info "Raspberry Pi 5 Secondary Setup Complete!"
    log_info "=========================================="
    echo ""
    log_info "Device Information:"
    echo "  Hostname: ${HOSTNAME}"
    echo "  IP Address: ${IP_ADDRESS}"
    echo ""
    log_info "Services Deployed:"
    echo "  - Light Processing Worker"
    echo "  - Distributed Task Processor"
    echo "  - Backup Receiver"
    echo "  - Health Monitor"
    echo "  - Monitoring Agents"
    echo ""
    log_info "Next Steps:"
    echo "  1. Reboot: sudo reboot"
    echo "  2. Update .env: nano /opt/osint-platform-rpi5-secondary/.env"
    echo "  3. Start services: cd /opt/osint-platform-rpi5-secondary && docker compose up -d"
    echo ""
    log_info "Monitoring Endpoints:"
    echo "  - Node Exporter: http://10.0.0.11:9100"
    echo "  - cAdvisor: http://10.0.0.11:8080"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting Raspberry Pi 5 Secondary Setup..."

    check_root
    configure_hostname
    configure_network
    update_system
    install_dependencies
    install_docker
    configure_docker
    deploy_osint_platform
    setup_monitoring
    configure_security

    post_install_info
}

main "$@"
