#!/bin/bash
###############################################################################
# Raspberry Pi 5 (16GB RAM + 1TB SSD) - Primary Compute Node Setup
# Hostname: osint-primary-rpi5
# IP: 10.0.0.10
# Purpose: Primary OSINT processing, heavy computation, data storage
###############################################################################

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
HOSTNAME="osint-primary-rpi5"
IP_ADDRESS="10.0.0.10"
GATEWAY="10.0.0.1"
DNS_SERVER="10.0.0.12"
SSD_DEVICE="/dev/sda"  # Adjust if needed
SSD_MOUNT="/mnt/ssd"

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
# SSD Configuration
###############################################################################

setup_ssd() {
    log_info "Setting up 1TB SSD..."

    # Check if SSD exists
    if [ ! -b "${SSD_DEVICE}" ]; then
        log_error "SSD device ${SSD_DEVICE} not found!"
        log_info "Available devices:"
        lsblk
        return 1
    fi

    log_warn "This will FORMAT ${SSD_DEVICE}. All data will be lost!"
    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "SSD setup cancelled"
        return 0
    fi

    # Partition SSD
    log_info "Partitioning SSD..."
    parted -s ${SSD_DEVICE} mklabel gpt
    parted -s ${SSD_DEVICE} mkpart primary ext4 0% 100%

    # Format partition
    log_info "Formatting SSD..."
    mkfs.ext4 -F ${SSD_DEVICE}1

    # Create mount point
    mkdir -p ${SSD_MOUNT}

    # Get UUID
    UUID=$(blkid -s UUID -o value ${SSD_DEVICE}1)

    # Add to fstab
    echo "UUID=${UUID} ${SSD_MOUNT} ext4 defaults,noatime 0 2" >> /etc/fstab

    # Mount SSD
    mount -a

    # Verify mount
    if mountpoint -q ${SSD_MOUNT}; then
        log_info "SSD mounted successfully at ${SSD_MOUNT}"
    else
        log_error "Failed to mount SSD"
        return 1
    fi

    # Create directory structure
    log_info "Creating directory structure..."
    mkdir -p ${SSD_MOUNT}/{data,captures,models,processing,backups,logs}
    chmod -R 755 ${SSD_MOUNT}
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
        iftop \
        tmux \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        nfs-common \
        rsync \
        unzip
}

###############################################################################
# Docker Installation
###############################################################################

install_docker() {
    log_info "Installing Docker..."

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up repository (for Debian/Raspberry Pi OS)
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Enable Docker service
    systemctl enable docker
    systemctl start docker

    # Add pi user to docker group
    usermod -aG docker pi || true

    # Verify installation
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
  "data-root": "${SSD_MOUNT}/docker",
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

    # Create project directory
    mkdir -p /opt/osint-platform-rpi5
    cd /opt/osint-platform-rpi5

    # Create Docker Compose configuration
    cat > docker-compose.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  # Heavy Processing Worker
  osint-worker-heavy:
    image: osint-platform/workers:latest
    container_name: rpi5-worker-heavy
    environment:
      - WORKER_TYPE=heavy_processing
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - DATABASE_URL=postgresql+asyncpg://osint_user:${POSTGRES_PASSWORD}@10.0.0.11:5432/osint_platform
      - MONGODB_URL=mongodb://osint_user:${MONGO_PASSWORD}@10.0.0.12:27017/osint_platform
      - ELASTICSEARCH_URL=http://10.0.0.14:9200
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - WORKER_QUEUE=scraping,crawling,processing
      - WORKER_CONCURRENCY=6
    volumes:
      - /mnt/ssd/data:/data
      - /mnt/ssd/captures:/captures
      - /mnt/ssd/logs:/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '6'
          memory: 12G
        reservations:
          cpus: '4'
          memory: 8G
    network_mode: host

  # ML Processor
  ml-processor:
    image: osint-platform/ml-processor:arm64
    container_name: rpi5-ml-processor
    environment:
      - MODEL_PATH=/models
      - DATA_PATH=/data
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - RESULTS_PATH=/processing/ml-results
    volumes:
      - /mnt/ssd/models:/models
      - /mnt/ssd/data:/data
      - /mnt/ssd/processing:/processing
      - /mnt/ssd/logs:/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    network_mode: host

  # Data Processing Pipeline
  data-processor:
    image: osint-platform/data-processor:latest
    container_name: rpi5-data-processor
    environment:
      - DATABASE_URL=postgresql+asyncpg://osint_user:${POSTGRES_PASSWORD}@10.0.0.11:5432/osint_platform
      - MONGODB_URL=mongodb://osint_user:${MONGO_PASSWORD}@10.0.0.12:27017/osint_platform
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - PROCESSING_PATH=/processing
    volumes:
      - /mnt/ssd/processing:/processing
      - /mnt/ssd/data:/data
      - /mnt/ssd/logs:/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    network_mode: host

  # Backup Service
  backup-service:
    image: osint-platform/backup:latest
    container_name: rpi5-backup
    environment:
      - BACKUP_SOURCE=/data
      - BACKUP_DEST=/backups
      - BACKUP_SCHEDULE=0 2 * * *
      - PROXMOX_BACKUP_SERVER=10.0.0.11
    volumes:
      - /mnt/ssd/data:/data:ro
      - /mnt/ssd/backups:/backups
      - /mnt/ssd/logs:/logs
    restart: unless-stopped
    network_mode: host

  # Node Exporter for Prometheus
  node-exporter:
    image: prom/node-exporter:latest
    container_name: rpi5-node-exporter
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

  # cAdvisor for container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: rpi5-cadvisor
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
EOFCOMPOSE

    # Create environment file
    cat > .env << 'EOFENV'
# Raspberry Pi 5 Primary - Environment Configuration
REDIS_PASSWORD=changeme
POSTGRES_PASSWORD=changeme
MONGO_PASSWORD=changeme

# Worker Configuration
WORKER_CONCURRENCY=6
WORKER_QUEUE=scraping,crawling,processing

# Paths
DATA_PATH=/mnt/ssd/data
MODELS_PATH=/mnt/ssd/models
PROCESSING_PATH=/mnt/ssd/processing
BACKUPS_PATH=/mnt/ssd/backups
EOFENV

    log_warn "Environment file created at /opt/osint-platform-rpi5/.env"
    log_warn "Please update passwords and configuration before starting services!"
}

###############################################################################
# Monitoring Setup
###############################################################################

setup_monitoring() {
    log_info "Setting up monitoring agents..."

    # Install Prometheus node exporter (already in Docker Compose)
    # Install custom monitoring script
    cat > /usr/local/bin/rpi5-monitor.sh << 'EOFMON'
#!/bin/bash
# RPi5 System Monitor - Sends metrics to Prometheus Pushgateway

PUSHGATEWAY="http://10.0.0.17:9091/metrics/job/rpi5_primary"

# CPU Temperature
CPU_TEMP=$(vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')

# Disk Usage
DISK_USAGE=$(df -h /mnt/ssd | tail -1 | awk '{print $5}' | sed 's/%//')

# Memory Usage
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')

# Push metrics
cat <<EOF | curl --data-binary @- $PUSHGATEWAY
# TYPE rpi5_cpu_temperature gauge
rpi5_cpu_temperature $CPU_TEMP
# TYPE rpi5_disk_usage gauge
rpi5_disk_usage $DISK_USAGE
# TYPE rpi5_memory_usage gauge
rpi5_memory_usage $MEM_USAGE
EOF
EOFMON

    chmod +x /usr/local/bin/rpi5-monitor.sh

    # Create cron job
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/rpi5-monitor.sh") | crontab -
}

###############################################################################
# Security Hardening
###############################################################################

configure_security() {
    log_info "Configuring security settings..."

    # Configure firewall (ufw)
    apt install -y ufw

    # Allow SSH
    ufw allow 22/tcp

    # Allow Docker metrics
    ufw allow 9323/tcp

    # Allow Prometheus exporters
    ufw allow 9100/tcp
    ufw allow 8080/tcp

    # Allow from LAN
    ufw allow from 10.0.0.0/24

    # Enable firewall
    ufw --force enable

    log_info "Firewall configured"
}

###############################################################################
# Post-Installation
###############################################################################

post_install_info() {
    log_info "=========================================="
    log_info "Raspberry Pi 5 Primary Setup Complete!"
    log_info "=========================================="
    echo ""
    log_info "Device Information:"
    echo "  Hostname: ${HOSTNAME}"
    echo "  IP Address: ${IP_ADDRESS}"
    echo "  SSD Mount: ${SSD_MOUNT}"
    echo ""
    log_info "Services Deployed:"
    echo "  - Heavy Processing Worker"
    echo "  - ML Processor"
    echo "  - Data Processing Pipeline"
    echo "  - Backup Service"
    echo "  - Monitoring Agents"
    echo ""
    log_info "Next Steps:"
    echo "  1. Reboot the system: sudo reboot"
    echo "  2. Update .env file: nano /opt/osint-platform-rpi5/.env"
    echo "  3. Pull Docker images or build locally"
    echo "  4. Start services: cd /opt/osint-platform-rpi5 && docker compose up -d"
    echo "  5. Monitor logs: docker compose logs -f"
    echo ""
    log_info "Monitoring Endpoints:"
    echo "  - Node Exporter: http://10.0.0.10:9100"
    echo "  - cAdvisor: http://10.0.0.10:8080"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting Raspberry Pi 5 Primary Setup..."

    check_root

    configure_hostname
    configure_network
    update_system
    install_dependencies
    setup_ssd
    install_docker
    configure_docker
    deploy_osint_platform
    setup_monitoring
    configure_security

    post_install_info
}

main "$@"
