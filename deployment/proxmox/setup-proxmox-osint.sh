#!/bin/bash
###############################################################################
# OSINT Platform - Proxmox Distributed Infrastructure Setup
# Node: Node2 MS-A2 Workstation (Debian Trixie 9.x)
# Description: Automated setup for LXC containers and VMs for OSINT platform
###############################################################################

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROXMOX_NODE="node2"
STORAGE_LOCAL="local"
STORAGE_LVM="local-lvm"
BRIDGE="vmbr0"
GATEWAY="10.0.0.1"
DNS_SERVER="10.0.0.12"
DOMAIN="osint.local"

# Container template (update if needed)
DEBIAN_TEMPLATE="${STORAGE_LOCAL}:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst"

###############################################################################
# Logging Functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

###############################################################################
# Pre-flight Checks
###############################################################################

check_root() {
    if [[ $EUID -ne 0 ]]; then
       log_error "This script must be run as root"
       exit 1
    fi
}

check_proxmox() {
    if ! command -v pct &> /dev/null; then
        log_error "Proxmox VE is not installed or pct command not found"
        exit 1
    fi
}

check_template() {
    if ! pveam list ${STORAGE_LOCAL} | grep -q "debian-12-standard"; then
        log_warn "Debian 12 template not found. Downloading..."
        pveam update
        pveam download ${STORAGE_LOCAL} debian-12-standard_12.0-1_amd64.tar.zst
    fi
}

###############################################################################
# Container Creation Functions
###############################################################################

create_lxc_container() {
    local id=$1
    local name=$2
    local memory=$3
    local cores=$4
    local storage=$5
    local ip=$6
    local description=$7

    log_info "Creating LXC container: ${name} (CT-${id})"

    # Check if container already exists
    if pct status ${id} &>/dev/null; then
        log_warn "Container ${id} already exists. Skipping..."
        return 0
    fi

    # Create container
    pct create ${id} ${DEBIAN_TEMPLATE} \
        --hostname ${name} \
        --memory ${memory} \
        --cores ${cores} \
        --storage ${STORAGE_LVM} \
        --rootfs ${STORAGE_LVM}:${storage} \
        --net0 name=eth0,bridge=${BRIDGE},ip=${ip}/24,gw=${GATEWAY} \
        --nameserver ${DNS_SERVER} \
        --searchdomain ${DOMAIN} \
        --features nesting=1,keyctl=1 \
        --unprivileged 1 \
        --onboot 1 \
        --description "${description}" \
        --ostype debian \
        --password "changeme123" # Change this in production!

    if [ $? -eq 0 ]; then
        log_info "Container ${name} created successfully"

        # Start container
        pct start ${id}
        sleep 5

        # Update container
        pct exec ${id} -- bash -c "apt update && apt upgrade -y"

        return 0
    else
        log_error "Failed to create container ${name}"
        return 1
    fi
}

create_vm() {
    local id=$1
    local name=$2
    local memory=$3
    local cores=$4
    local disk=$5
    local ip=$6
    local description=$7
    local iso=$8

    log_info "Creating VM: ${name} (VM-${id})"

    # Check if VM already exists
    if qm status ${id} &>/dev/null; then
        log_warn "VM ${id} already exists. Skipping..."
        return 0
    fi

    # Create VM
    qm create ${id} \
        --name ${name} \
        --memory ${memory} \
        --cores ${cores} \
        --net0 virtio,bridge=${BRIDGE} \
        --scsihw virtio-scsi-pci \
        --scsi0 ${STORAGE_LVM}:${disk},format=raw \
        --boot order=scsi0 \
        --ostype l26 \
        --agent enabled=1 \
        --description "${description}"

    if [ $? -eq 0 ]; then
        log_info "VM ${name} created successfully (manual OS installation required)"
        return 0
    else
        log_error "Failed to create VM ${name}"
        return 1
    fi
}

###############################################################################
# Database Containers
###############################################################################

setup_database_containers() {
    log_info "Setting up database containers..."

    # CT-101: PostgreSQL
    create_lxc_container 101 "postgres-osint" 2048 2 20 "10.0.0.11" \
        "PostgreSQL 15 - Primary database for OSINT platform"

    # Install PostgreSQL
    pct exec 101 -- bash -c "apt install -y postgresql-15 postgresql-contrib"
    pct exec 101 -- bash -c "systemctl enable postgresql"

    # CT-102: MongoDB
    create_lxc_container 102 "mongodb-osint" 2048 2 30 "10.0.0.12" \
        "MongoDB 7 - Document storage for raw OSINT data"

    # Install MongoDB
    pct exec 102 -- bash -c "curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor"
    pct exec 102 -- bash -c "echo 'deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main' | tee /etc/apt/sources.list.d/mongodb-org-7.0.list"
    pct exec 102 -- bash -c "apt update && apt install -y mongodb-org"
    pct exec 102 -- bash -c "systemctl enable mongod"

    # CT-103: Redis
    create_lxc_container 103 "redis-osint" 1024 1 10 "10.0.0.13" \
        "Redis 7 - Cache and message broker"

    # Install Redis
    pct exec 103 -- bash -c "apt install -y redis-server"
    pct exec 103 -- bash -c "systemctl enable redis-server"

    log_info "Database containers setup complete"
}

###############################################################################
# ELK Stack Containers
###############################################################################

setup_elk_containers() {
    log_info "Setting up ELK stack containers..."

    # CT-104: Elasticsearch
    create_lxc_container 104 "elasticsearch-osint" 4096 2 50 "10.0.0.14" \
        "Elasticsearch 8 - Search and analytics engine"

    # Install Elasticsearch
    pct exec 104 -- bash -c "apt install -y apt-transport-https"
    pct exec 104 -- bash -c "wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg"
    pct exec 104 -- bash -c "echo 'deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main' | tee /etc/apt/sources.list.d/elastic-8.x.list"
    pct exec 104 -- bash -c "apt update && apt install -y elasticsearch"
    pct exec 104 -- bash -c "systemctl enable elasticsearch"

    # CT-105: Logstash
    create_lxc_container 105 "logstash-osint" 2048 2 20 "10.0.0.15" \
        "Logstash 8 - Log processing pipeline"

    # Install Logstash
    pct exec 105 -- bash -c "apt install -y apt-transport-https"
    pct exec 105 -- bash -c "wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg"
    pct exec 105 -- bash -c "echo 'deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main' | tee /etc/apt/sources.list.d/elastic-8.x.list"
    pct exec 105 -- bash -c "apt update && apt install -y logstash"
    pct exec 105 -- bash -c "systemctl enable logstash"

    # CT-106: Kibana
    create_lxc_container 106 "kibana-osint" 2048 2 10 "10.0.0.16" \
        "Kibana 8 - Visualization and exploration"

    # Install Kibana
    pct exec 106 -- bash -c "apt install -y apt-transport-https"
    pct exec 106 -- bash -c "wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg"
    pct exec 106 -- bash -c "echo 'deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main' | tee /etc/apt/sources.list.d/elastic-8.x.list"
    pct exec 106 -- bash -c "apt update && apt install -y kibana"
    pct exec 106 -- bash -c "systemctl enable kibana"

    log_info "ELK stack containers setup complete"
}

###############################################################################
# Monitoring Containers
###############################################################################

setup_monitoring_containers() {
    log_info "Setting up monitoring containers..."

    # CT-107: Prometheus
    create_lxc_container 107 "prometheus-osint" 2048 2 30 "10.0.0.17" \
        "Prometheus - Metrics collection and monitoring"

    # Install Prometheus
    pct exec 107 -- bash -c "wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz -O /tmp/prometheus.tar.gz"
    pct exec 107 -- bash -c "cd /opt && tar xzf /tmp/prometheus.tar.gz && ln -s prometheus-2.45.0.linux-amd64 prometheus"
    pct exec 107 -- bash -c "useradd --no-create-home --shell /bin/false prometheus"

    # CT-108: Grafana
    create_lxc_container 108 "grafana-osint" 1024 1 10 "10.0.0.18" \
        "Grafana - Metrics visualization and dashboards"

    # Install Grafana
    pct exec 108 -- bash -c "apt install -y apt-transport-https software-properties-common"
    pct exec 108 -- bash -c "wget -q -O - https://packages.grafana.com/gpg.key | gpg --dearmor > /usr/share/keyrings/grafana.gpg"
    pct exec 108 -- bash -c "echo 'deb [signed-by=/usr/share/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main' | tee /etc/apt/sources.list.d/grafana.list"
    pct exec 108 -- bash -c "apt update && apt install -y grafana"
    pct exec 108 -- bash -c "systemctl enable grafana-server"

    log_info "Monitoring containers setup complete"
}

###############################################################################
# OSINT Platform Container (Docker Host)
###############################################################################

setup_docker_container() {
    log_info "Setting up Docker host container for OSINT platform..."

    # CT-200: Docker Host - OSINT Platform
    create_lxc_container 200 "docker-osint" 8192 4 100 "10.0.0.20" \
        "Docker host - OSINT platform services"

    # Install Docker
    pct exec 200 -- bash -c "apt install -y curl gnupg lsb-release"
    pct exec 200 -- bash -c "mkdir -p /etc/apt/keyrings"
    pct exec 200 -- bash -c "curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    pct exec 200 -- bash -c "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable' | tee /etc/apt/sources.list.d/docker.list"
    pct exec 200 -- bash -c "apt update && apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
    pct exec 200 -- bash -c "systemctl enable docker"

    # Create directories for OSINT platform
    pct exec 200 -- bash -c "mkdir -p /opt/osint-platform/{logs,storage,config}"

    log_info "Docker container setup complete"
}

###############################################################################
# Network Monitoring Containers
###############################################################################

setup_network_monitoring_containers() {
    log_info "Setting up network monitoring containers..."

    # CT-400: Network Flow Collector
    create_lxc_container 400 "network-flow" 2048 2 20 "10.0.0.40" \
        "Network flow collector - ntopng, NetFlow, sFlow"

    # Install ntopng
    pct exec 400 -- bash -c "apt install -y wget gnupg software-properties-common"
    pct exec 400 -- bash -c "wget https://packages.ntop.org/apt-stable/22.04/all/apt-ntop-stable.deb -O /tmp/apt-ntop.deb"
    pct exec 400 -- bash -c "dpkg -i /tmp/apt-ntop.deb || apt-get -f install -y"
    pct exec 400 -- bash -c "apt update && apt install -y ntopng pfring nprobe"
    pct exec 400 -- bash -c "systemctl enable ntopng"

    # CT-401: Security Monitor
    create_lxc_container 401 "security-monitor" 2048 2 20 "10.0.0.41" \
        "Security monitoring - Suricata IDS, Zeek"

    # Install Suricata
    pct exec 401 -- bash -c "apt install -y software-properties-common"
    pct exec 401 -- bash -c "add-apt-repository ppa:oisf/suricata-stable -y || true"
    pct exec 401 -- bash -c "apt update && apt install -y suricata"
    pct exec 401 -- bash -c "systemctl enable suricata"

    log_info "Network monitoring containers setup complete"
}

###############################################################################
# Kali Linux VM
###############################################################################

setup_kali_vm() {
    log_info "Setting up Kali Linux VM..."

    # VM-300: Kali Linux
    create_vm 300 "kali-osint" 4096 4 50 "10.0.0.30" \
        "Kali Linux - Security tools and OSINT toolkit" \
        "kali-linux-2024.iso"

    log_warn "Kali VM created. Manual installation required."
    log_info "1. Download Kali ISO from https://www.kali.org/get-kali/"
    log_info "2. Upload ISO to Proxmox storage"
    log_info "3. Attach ISO to VM and install"
    log_info "4. Configure network: IP=10.0.0.30/24, GW=10.0.0.1, DNS=10.0.0.12"
}

###############################################################################
# Network Configuration
###############################################################################

configure_network_bridge() {
    log_info "Configuring network bridge..."

    # Verify bridge exists
    if ! ip link show ${BRIDGE} &>/dev/null; then
        log_warn "Bridge ${BRIDGE} does not exist. Please configure manually."
        log_info "Add to /etc/network/interfaces:"
        log_info "auto ${BRIDGE}"
        log_info "iface ${BRIDGE} inet static"
        log_info "    address 10.0.2.1/24"
        log_info "    bridge-ports none"
        log_info "    bridge-stp off"
        log_info "    bridge-fd 0"
    else
        log_info "Bridge ${BRIDGE} exists"
    fi
}

###############################################################################
# Firewall Rules
###############################################################################

configure_firewall() {
    log_info "Configuring Proxmox firewall rules..."

    # Enable firewall
    pvesh set /cluster/firewall/options --enable 1

    # Allow SSH
    pvesh create /cluster/firewall/rules --type in --action ACCEPT --proto tcp --dport 22 --comment "Allow SSH"

    # Allow Proxmox Web Interface
    pvesh create /cluster/firewall/rules --type in --action ACCEPT --proto tcp --dport 8006 --comment "Allow Proxmox Web UI"

    # Allow inter-container communication
    pvesh create /cluster/firewall/rules --type in --action ACCEPT --source 10.0.0.0/24 --comment "Allow LAN"

    log_info "Firewall rules configured"
}

###############################################################################
# Post-Setup Configuration
###############################################################################

post_setup_info() {
    log_info "=========================================="
    log_info "Proxmox OSINT Platform Setup Complete!"
    log_info "=========================================="
    echo ""
    log_info "Container Summary:"
    echo ""
    echo "Database Services:"
    echo "  CT-101: PostgreSQL      - 10.0.0.11"
    echo "  CT-102: MongoDB         - 10.0.0.12"
    echo "  CT-103: Redis           - 10.0.0.13"
    echo ""
    echo "ELK Stack:"
    echo "  CT-104: Elasticsearch   - 10.0.0.14"
    echo "  CT-105: Logstash        - 10.0.0.15"
    echo "  CT-106: Kibana          - 10.0.0.16"
    echo ""
    echo "Monitoring:"
    echo "  CT-107: Prometheus      - 10.0.0.17"
    echo "  CT-108: Grafana         - 10.0.0.18"
    echo ""
    echo "OSINT Platform:"
    echo "  CT-200: Docker Host     - 10.0.0.20"
    echo ""
    echo "Network Monitoring:"
    echo "  CT-400: Flow Collector  - 10.0.0.40"
    echo "  CT-401: Security Mon.   - 10.0.0.41"
    echo ""
    echo "Virtual Machines:"
    echo "  VM-300: Kali Linux      - 10.0.0.30 (manual install required)"
    echo ""
    log_info "Next Steps:"
    echo "  1. Configure database passwords and security"
    echo "  2. Deploy OSINT platform to Docker container (CT-200)"
    echo "  3. Configure ELK stack data pipelines"
    echo "  4. Setup Prometheus scrape configs"
    echo "  5. Import Grafana dashboards"
    echo "  6. Install Kali Linux on VM-300"
    echo "  7. Configure network monitoring tools"
    echo "  8. Setup Cloudflare Tunnel on Kali VM"
    echo ""
    log_info "Configuration files are available in deployment/proxmox/"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting Proxmox OSINT Platform Setup..."

    # Pre-flight checks
    check_root
    check_proxmox
    check_template

    # Setup infrastructure
    setup_database_containers
    setup_elk_containers
    setup_monitoring_containers
    setup_docker_container
    setup_network_monitoring_containers
    setup_kali_vm

    # Network and firewall
    configure_network_bridge
    configure_firewall

    # Post-setup info
    post_setup_info
}

# Execute main function
main "$@"
