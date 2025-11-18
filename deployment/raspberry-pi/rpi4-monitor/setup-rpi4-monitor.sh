#!/bin/bash
###############################################################################
# Raspberry Pi 4 (4GB RAM) - Network Monitoring Node Setup
# Hostname: osint-monitor-rpi4
# IP: 10.0.0.12
# Purpose: Network visibility, traffic analysis, Pi-hole DNS filtering
###############################################################################

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
HOSTNAME="osint-monitor-rpi4"
IP_ADDRESS="10.0.0.12"
GATEWAY="10.0.0.1"

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
    dns-nameservers 8.8.8.8 1.1.1.1
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
        iftop \
        tcpdump \
        wireshark-common \
        tshark \
        nmap \
        dnsutils \
        net-tools \
        python3 \
        python3-pip \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
}

###############################################################################
# Pi-hole Installation
###############################################################################

install_pihole() {
    log_info "Installing Pi-hole DNS filtering..."

    # Download and install Pi-hole
    curl -sSL https://install.pi-hole.net | bash /dev/stdin --unattended

    # Configure Pi-hole
    cat > /etc/pihole/setupVars.conf << EOF
WEBPASSWORD=$(openssl rand -base64 32 | sha256sum | cut -d' ' -f1)
PIHOLE_INTERFACE=eth0
IPV4_ADDRESS=${IP_ADDRESS}/24
IPV6_ADDRESS=
PIHOLE_DNS_1=8.8.8.8
PIHOLE_DNS_2=1.1.1.1
QUERY_LOGGING=true
INSTALL_WEB_SERVER=true
INSTALL_WEB_INTERFACE=true
LIGHTTPD_ENABLED=true
CACHE_SIZE=10000
DNS_FQDN_REQUIRED=false
DNS_BOGUS_PRIV=true
DNSSEC=false
CONDITIONAL_FORWARDING=false
BLOCKING_ENABLED=true
EOF

    # Reconfigure Pi-hole with new settings
    pihole reconfigure --unattended

    log_info "Pi-hole installed. Web interface: http://${IP_ADDRESS}/admin"
}

configure_pihole_lists() {
    log_info "Configuring Pi-hole block lists..."

    # Add custom block lists for OSINT/security
    cat >> /etc/pihole/adlists.list << EOF
# Security and threat intelligence lists
https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
https://mirror1.malwaredomains.com/files/justdomains
https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt
https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt
https://hosts-file.net/ad_servers.txt
https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt
https://someonewhocares.org/hosts/zero/hosts
https://raw.githubusercontent.com/mitchellkrogza/Badd-Boyz-Hosts/master/hosts
https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt
https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt
EOF

    # Update gravity
    pihole -g

    log_info "Pi-hole block lists configured"
}

configure_pihole_logging() {
    log_info "Configuring Pi-hole logging to Elasticsearch..."

    # Install filebeat for log shipping
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-8.x.list
    apt update
    apt install -y filebeat

    # Configure filebeat
    cat > /etc/filebeat/filebeat.yml << 'EOF'
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/pihole.log
  fields:
    service: pihole
    type: dns_query
  fields_under_root: true

- type: log
  enabled: true
  paths:
    - /var/log/pihole-FTL.log
  fields:
    service: pihole
    type: ftl_log

output.elasticsearch:
  hosts: ["10.0.0.14:9200"]
  index: "pihole-logs-%{+yyyy.MM.dd}"

setup.template.name: "pihole"
setup.template.pattern: "pihole-*"
setup.ilm.enabled: false

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
EOF

    systemctl enable filebeat
    systemctl start filebeat

    log_info "Pi-hole logging configured to Elasticsearch"
}

###############################################################################
# Network Monitoring Tools
###############################################################################

install_ntopng() {
    log_info "Installing ntopng for network flow analysis..."

    # Install dependencies
    apt install -y wget gnupg software-properties-common

    # Add ntop repository
    wget https://packages.ntop.org/apt-stable/22.04/all/apt-ntop-stable.deb -O /tmp/apt-ntop.deb
    dpkg -i /tmp/apt-ntop.deb || apt-get -f install -y

    # Install ntopng
    apt update
    apt install -y ntopng pfring

    # Configure ntopng
    cat > /etc/ntopng/ntopng.conf << EOF
--local-networks=10.0.0.0/24
--interface=eth0
--http-port=3000
--community
EOF

    systemctl enable ntopng
    systemctl start ntopng

    log_info "ntopng installed. Web interface: http://${IP_ADDRESS}:3000"
}

install_network_tools() {
    log_info "Installing additional network monitoring tools..."

    # Install nProbe for NetFlow/sFlow collection
    apt install -y nprobe

    # Configure nProbe
    cat > /etc/nprobe/nprobe.conf << EOF
--interface=eth0
--collector-port=2055
--zmq=tcp://*:5556
--ntopng=tcp://127.0.0.1:5557
EOF

    # Install iftop for bandwidth monitoring
    apt install -y iftop

    # Install vnstat for network statistics
    apt install -y vnstat
    systemctl enable vnstat
    systemctl start vnstat

    log_info "Network monitoring tools installed"
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
}

###############################################################################
# Network Awareness Dashboard
###############################################################################

deploy_network_dashboard() {
    log_info "Deploying network awareness dashboard..."

    mkdir -p /opt/network-awareness
    cd /opt/network-awareness

    cat > docker-compose.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  # Network Flow Analyzer
  flow-analyzer:
    image: osint-platform/flow-analyzer:latest
    container_name: network-flow-analyzer
    environment:
      - ELASTICSEARCH_URL=http://10.0.0.14:9200
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - PIHOLE_API=http://127.0.0.1/admin/api.php
      - NTOPNG_API=http://127.0.0.1:3000
    volumes:
      - ./data:/data
      - ./logs:/logs
    restart: unless-stopped
    network_mode: host

  # Device Discovery Service
  device-discovery:
    image: osint-platform/device-discovery:latest
    container_name: network-device-discovery
    environment:
      - NETWORK_RANGE=10.0.0.0/24
      - SCAN_INTERVAL=300
      - DATABASE_URL=postgresql+asyncpg://osint_user:${POSTGRES_PASSWORD}@10.0.0.11:5432/osint_platform
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: unless-stopped
    network_mode: host

  # Traffic Analysis Service
  traffic-analyzer:
    image: osint-platform/traffic-analyzer:latest
    container_name: network-traffic-analyzer
    environment:
      - CAPTURE_INTERFACE=eth0
      - ELASTICSEARCH_URL=http://10.0.0.14:9200
      - PCAP_PATH=/captures
    volumes:
      - ./captures:/captures
      - ./logs:/logs
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: unless-stopped
    network_mode: host

  # Anomaly Detection Service
  anomaly-detector:
    image: osint-platform/anomaly-detector:latest
    container_name: network-anomaly-detector
    environment:
      - ELASTICSEARCH_URL=http://10.0.0.14:9200
      - REDIS_URL=redis://:${REDIS_PASSWORD}@10.0.0.13:6379/0
      - ALERT_THRESHOLD=7.0
      - PROMETHEUS_URL=http://10.0.0.17:9090
    restart: unless-stopped
    network_mode: host

  # Monitoring Exporters
  node-exporter:
    image: prom/node-exporter:latest
    container_name: rpi4-node-exporter
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'
    restart: unless-stopped
    network_mode: host

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: rpi4-cadvisor
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
EOFCOMPOSE

    cat > .env << 'EOFENV'
# Raspberry Pi 4 Monitor - Environment Configuration
REDIS_PASSWORD=changeme
POSTGRES_PASSWORD=changeme
PIHOLE_API_TOKEN=changeme
EOFENV

    log_warn "Environment file created at /opt/network-awareness/.env"
}

###############################################################################
# Monitoring Scripts
###############################################################################

setup_monitoring_scripts() {
    log_info "Setting up monitoring scripts..."

    cat > /usr/local/bin/rpi4-monitor.sh << 'EOFMON'
#!/bin/bash
# RPi4 Network Monitor

PUSHGATEWAY="http://10.0.0.17:9091/metrics/job/rpi4_monitor"

# System metrics
CPU_TEMP=$(vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')

# Pi-hole metrics
PIHOLE_QUERIES=$(pihole -c -j | jq -r '.queries_today')
PIHOLE_BLOCKED=$(pihole -c -j | jq -r '.ads_blocked_today')
PIHOLE_PERCENT=$(pihole -c -j | jq -r '.ads_percentage_today')

# Network metrics
NETWORK_RX=$(cat /sys/class/net/eth0/statistics/rx_bytes)
NETWORK_TX=$(cat /sys/class/net/eth0/statistics/tx_bytes)

cat <<EOF | curl --data-binary @- $PUSHGATEWAY
# TYPE rpi4_cpu_temperature gauge
rpi4_cpu_temperature $CPU_TEMP
# TYPE rpi4_memory_usage gauge
rpi4_memory_usage $MEM_USAGE
# TYPE pihole_queries_today gauge
pihole_queries_today $PIHOLE_QUERIES
# TYPE pihole_blocked_today gauge
pihole_blocked_today $PIHOLE_BLOCKED
# TYPE pihole_block_percentage gauge
pihole_block_percentage $PIHOLE_PERCENT
# TYPE network_rx_bytes counter
network_rx_bytes $NETWORK_RX
# TYPE network_tx_bytes counter
network_tx_bytes $NETWORK_TX
EOF
EOFMON

    chmod +x /usr/local/bin/rpi4-monitor.sh

    # Install jq for JSON parsing
    apt install -y jq

    # Create cron job
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/rpi4-monitor.sh") | crontab -
}

###############################################################################
# Security Hardening
###############################################################################

configure_security() {
    log_info "Configuring security settings..."

    apt install -y ufw

    # Allow DNS
    ufw allow 53/tcp
    ufw allow 53/udp

    # Allow Pi-hole web interface
    ufw allow 80/tcp
    ufw allow 443/tcp

    # Allow SSH
    ufw allow 22/tcp

    # Allow ntopng
    ufw allow 3000/tcp

    # Allow NetFlow/sFlow
    ufw allow 2055/udp
    ufw allow 6343/udp

    # Allow monitoring
    ufw allow 9100/tcp
    ufw allow 8080/tcp

    # Allow from LAN
    ufw allow from 10.0.0.0/24

    ufw --force enable

    log_info "Firewall configured"
}

###############################################################################
# Post-Installation
###############################################################################

post_install_info() {
    log_info "=========================================="
    log_info "Raspberry Pi 4 Monitor Setup Complete!"
    log_info "=========================================="
    echo ""
    log_info "Device Information:"
    echo "  Hostname: ${HOSTNAME}"
    echo "  IP Address: ${IP_ADDRESS}"
    echo ""
    log_info "Services Deployed:"
    echo "  - Pi-hole DNS Filtering"
    echo "  - ntopng Network Flow Analysis"
    echo "  - Network Monitoring Tools"
    echo "  - Device Discovery"
    echo "  - Traffic Analysis"
    echo "  - Anomaly Detection"
    echo ""
    log_info "Web Interfaces:"
    echo "  - Pi-hole: http://${IP_ADDRESS}/admin"
    echo "  - ntopng: http://${IP_ADDRESS}:3000"
    echo "  - Node Exporter: http://${IP_ADDRESS}:9100"
    echo ""
    log_info "DNS Configuration:"
    echo "  Set this device (${IP_ADDRESS}) as DNS server on:"
    echo "  - Router DHCP settings"
    echo "  - Individual devices"
    echo "  - Banana Pi gateway"
    echo ""
    log_info "Next Steps:"
    echo "  1. Reboot: sudo reboot"
    echo "  2. Access Pi-hole admin: http://${IP_ADDRESS}/admin"
    echo "  3. Set Pi-hole password: pihole -a -p"
    echo "  4. Update .env: nano /opt/network-awareness/.env"
    echo "  5. Start services: cd /opt/network-awareness && docker compose up -d"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting Raspberry Pi 4 Monitor Setup..."

    check_root
    configure_hostname
    configure_network
    update_system
    install_dependencies
    install_pihole
    configure_pihole_lists
    configure_pihole_logging
    install_ntopng
    install_network_tools
    install_docker
    deploy_network_dashboard
    setup_monitoring_scripts
    configure_security

    post_install_info
}

main "$@"
