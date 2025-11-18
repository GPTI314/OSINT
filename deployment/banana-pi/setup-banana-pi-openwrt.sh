#!/bin/bash
###############################################################################
# Banana Pi - OpenWRT Gateway Configuration
# Hostname: osint-gateway
# WAN: DHCP from ISP (eth0)
# LAN: 10.0.0.1/24 (eth1)
# DMZ: 10.0.1.1/24 (eth2) - Optional
# Purpose: Network security gateway, firewall, VPN, IDS
###############################################################################

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
# IMPORTANT: OpenWRT Installation Instructions
###############################################################################

print_installation_guide() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════╗
║           Banana Pi OpenWRT Installation Guide                          ║
╚══════════════════════════════════════════════════════════════════════════╝

STEP 1: Download OpenWRT for Banana Pi
---------------------------------------
Visit: https://downloads.openwrt.org/
Download the appropriate image for your Banana Pi model:
- Banana Pi M1/M1+: sunxi-cortexa7
- Banana Pi R1: sunxi-cortexa7-bananapi-bpi-r1
- Banana Pi R2: mediatek-mt7623
- Banana Pi R3: mediatek-filogic

STEP 2: Flash OpenWRT to SD Card/eMMC
--------------------------------------
# Using dd (Linux)
sudo dd if=openwrt-*.img of=/dev/sdX bs=4M status=progress
sudo sync

# Using Etcher (Windows/Mac/Linux)
Download from: https://www.balena.io/etcher/

STEP 3: Initial Boot and Access
--------------------------------
1. Insert SD card and power on Banana Pi
2. Connect to LAN port via Ethernet
3. Access via: http://192.168.1.1 or ssh root@192.168.1.1
4. Set root password: passwd

STEP 4: Run This Configuration Script
--------------------------------------
# Upload this script to Banana Pi
scp setup-banana-pi-openwrt.sh root@192.168.1.1:/tmp/

# SSH to Banana Pi and run
ssh root@192.168.1.1
cd /tmp
chmod +x setup-banana-pi-openwrt.sh
./setup-banana-pi-openwrt.sh

EOF
}

###############################################################################
# Check if running on OpenWRT
###############################################################################

check_openwrt() {
    if [ ! -f /etc/openwrt_release ]; then
        log_error "This script must be run on OpenWRT!"
        log_info "Printing installation guide..."
        print_installation_guide
        exit 1
    fi

    log_info "OpenWRT detected. Proceeding with configuration..."
}

###############################################################################
# Update OpenWRT
###############################################################################

update_openwrt() {
    log_info "Updating OpenWRT packages..."

    opkg update

    log_info "Installing essential packages..."
    opkg install \
        luci \
        luci-ssl \
        luci-app-firewall \
        luci-app-qos \
        luci-app-ddns \
        luci-app-upnp \
        luci-app-wireguard \
        luci-app-openvpn \
        wireguard-tools \
        openvpn-openssl \
        tcpdump \
        iperf3 \
        htop \
        nano \
        vim \
        curl \
        wget
}

###############################################################################
# Network Configuration
###############################################################################

configure_network() {
    log_info "Configuring network interfaces..."

    # Backup original config
    cp /etc/config/network /etc/config/network.bak

    cat > /etc/config/network << 'EOF'
config interface 'loopback'
    option device 'lo'
    option proto 'static'
    option ipaddr '127.0.0.1'
    option netmask '255.0.0.0'

config interface 'wan'
    option device 'eth0'
    option proto 'dhcp'
    option peerdns '0'
    option dns '1.1.1.1 8.8.8.8'

config interface 'lan'
    option device 'eth1'
    option proto 'static'
    option ipaddr '10.0.0.1'
    option netmask '255.255.255.0'
    option ip6assign '60'

config interface 'dmz'
    option device 'eth2'
    option proto 'static'
    option ipaddr '10.0.1.1'
    option netmask '255.255.255.0'
EOF

    /etc/init.d/network restart

    log_info "Network interfaces configured"
    log_info "LAN: 10.0.0.1/24"
    log_info "DMZ: 10.0.1.1/24"
}

###############################################################################
# DHCP Configuration
###############################################################################

configure_dhcp() {
    log_info "Configuring DHCP server..."

    cat > /etc/config/dhcp << 'EOF'
config dnsmasq
    option domainneeded '1'
    option boguspriv '1'
    option filterwin2k '0'
    option localise_queries '1'
    option rebind_protection '1'
    option rebind_localhost '1'
    option local '/osint.local/'
    option domain 'osint.local'
    option expandhosts '1'
    option nonegcache '0'
    option authoritative '1'
    option readethers '1'
    option leasefile '/tmp/dhcp.leases'
    option resolvfile '/tmp/resolv.conf.d/resolv.conf.auto'
    option localservice '1'
    option ednspacket_max '1232'
    list server '10.0.0.12'
    list server '8.8.8.8'

config dhcp 'lan'
    option interface 'lan'
    option start '100'
    option limit '150'
    option leasetime '12h'
    option dhcpv4 'server'
    option dhcpv6 'server'
    option ra 'server'
    list dhcp_option '6,10.0.0.12,8.8.8.8'

config dhcp 'dmz'
    option interface 'dmz'
    option start '100'
    option limit '50'
    option leasetime '12h'
    option dhcpv4 'server'

config dhcp 'wan'
    option interface 'wan'
    option ignore '1'

# Static DHCP reservations for infrastructure
config host
    option name 'postgres-osint'
    option mac 'XX:XX:XX:XX:XX:01'
    option ip '10.0.0.11'

config host
    option name 'pihole'
    option mac 'XX:XX:XX:XX:XX:02'
    option ip '10.0.0.12'

config host
    option name 'rpi5-primary'
    option mac 'XX:XX:XX:XX:XX:10'
    option ip '10.0.0.10'

config host
    option name 'rpi5-secondary'
    option mac 'XX:XX:XX:XX:XX:11'
    option ip '10.0.0.11'

config host
    option name 'rpi4-monitor'
    option mac 'XX:XX:XX:XX:XX:12'
    option ip '10.0.0.12'
EOF

    /etc/init.d/dnsmasq restart

    log_info "DHCP server configured"
    log_warn "Update MAC addresses in /etc/config/dhcp for static reservations"
}

###############################################################################
# Firewall Configuration
###############################################################################

configure_firewall() {
    log_info "Configuring firewall rules..."

    cat > /etc/config/firewall << 'EOF'
config defaults
    option input 'REJECT'
    option output 'ACCEPT'
    option forward 'REJECT'
    option synflood_protect '1'

config zone
    option name 'wan'
    list network 'wan'
    option input 'REJECT'
    option output 'ACCEPT'
    option forward 'REJECT'
    option masq '1'
    option mtu_fix '1'

config zone
    option name 'lan'
    list network 'lan'
    option input 'ACCEPT'
    option output 'ACCEPT'
    option forward 'ACCEPT'

config zone
    option name 'dmz'
    list network 'dmz'
    option input 'REJECT'
    option output 'ACCEPT'
    option forward 'REJECT'

# LAN to WAN forwarding
config forwarding
    option src 'lan'
    option dest 'wan'

# LAN to DMZ forwarding (controlled)
config forwarding
    option src 'lan'
    option dest 'dmz'

# DMZ to WAN forwarding
config forwarding
    option src 'dmz'
    option dest 'wan'

# Allow SSH from LAN
config rule
    option name 'Allow-SSH-LAN'
    option src 'lan'
    option proto 'tcp'
    option dest_port '22'
    option target 'ACCEPT'

# Allow Web Interface from LAN
config rule
    option name 'Allow-HTTPS-LAN'
    option src 'lan'
    option proto 'tcp'
    option dest_port '443'
    option target 'ACCEPT'

config rule
    option name 'Allow-HTTP-LAN'
    option src 'lan'
    option proto 'tcp'
    option dest_port '80'
    option target 'ACCEPT'

# Allow DNS from LAN
config rule
    option name 'Allow-DNS-LAN'
    option src 'lan'
    option proto 'tcp udp'
    option dest_port '53'
    option target 'ACCEPT'

# Allow DHCP from LAN
config rule
    option name 'Allow-DHCP-LAN'
    option src 'lan'
    option proto 'udp'
    option dest_port '67-68'
    option target 'ACCEPT'

# Allow ping from LAN
config rule
    option name 'Allow-Ping-LAN'
    option src 'lan'
    option proto 'icmp'
    option icmp_type 'echo-request'
    option target 'ACCEPT'

# Allow WireGuard VPN from WAN
config rule
    option name 'Allow-WireGuard-WAN'
    option src 'wan'
    option dest_port '51820'
    option proto 'udp'
    option target 'ACCEPT'

# Block all unsolicited traffic from WAN
config rule
    option name 'Block-WAN-Input'
    option src 'wan'
    option target 'REJECT'

# Log dropped packets
config rule
    option name 'Log-Dropped'
    option src '*'
    option target 'LOG'
    option limit '10/minute'
EOF

    /etc/init.d/firewall restart

    log_info "Firewall configured with strict rules"
}

###############################################################################
# QoS Configuration
###############################################################################

configure_qos() {
    log_info "Configuring QoS (Quality of Service)..."

    opkg install luci-app-sqm

    cat > /etc/config/sqm << 'EOF'
config queue
    option enabled '1'
    option interface 'eth0'
    option download '100000'
    option upload '50000'
    option script 'piece_of_cake.qos'
    option qdisc 'cake'
    option qdisc_advanced '1'
EOF

    /etc/init.d/sqm restart

    log_info "QoS configured. Adjust download/upload speeds in /etc/config/sqm"
}

###############################################################################
# WireGuard VPN Configuration
###############################################################################

configure_wireguard() {
    log_info "Configuring WireGuard VPN server..."

    # Generate keys
    WG_PRIVATE_KEY=$(wg genkey)
    WG_PUBLIC_KEY=$(echo "$WG_PRIVATE_KEY" | wg pubkey)

    # Create WireGuard interface
    cat > /etc/config/network.wg0 << EOF
config interface 'wg0'
    option proto 'wireguard'
    option private_key '$WG_PRIVATE_KEY'
    option listen_port '51820'
    list addresses '10.0.2.1/24'

# Example peer (add more as needed)
config wireguard_wg0
    option description 'Admin Device'
    option public_key 'PEER_PUBLIC_KEY_HERE'
    list allowed_ips '10.0.2.2/32'
    option route_allowed_ips '1'
    option persistent_keepalive '25'
EOF

    cat >> /etc/config/network < /etc/config/network.wg0

    log_info "WireGuard VPN configured"
    log_info "Server Public Key: $WG_PUBLIC_KEY"
    log_warn "Save this key for client configuration!"
    log_warn "Update peer public keys in /etc/config/network"
}

###############################################################################
# Suricata IDS Installation (if resources permit)
###############################################################################

configure_suricata() {
    log_info "Installing Suricata IDS..."

    # Check if package exists
    if opkg list | grep -q suricata; then
        opkg install suricata

        # Basic configuration
        mkdir -p /etc/suricata
        cat > /etc/suricata/suricata.yaml << 'EOF'
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/24,10.0.1.0/24]"
    EXTERNAL_NET: "!$HOME_NET"

default-rule-path: /etc/suricata/rules
rule-files:
  - suricata.rules

outputs:
  - fast:
      enabled: yes
      filename: fast.log
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      types:
        - alert
        - http
        - dns
        - tls

af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
  - interface: eth1
    cluster-id: 98
    cluster-type: cluster_flow
    defrag: yes
EOF

        # Update rules
        suricata-update

        /etc/init.d/suricata enable
        /etc/init.d/suricata start

        log_info "Suricata IDS installed and configured"
    else
        log_warn "Suricata package not available for this platform"
        log_info "Consider using external IDS on Proxmox CT-401"
    fi
}

###############################################################################
# NetFlow Export Configuration
###############################################################################

configure_netflow() {
    log_info "Configuring NetFlow/sFlow export..."

    opkg install softflowd

    cat > /etc/config/softflowd << 'EOF'
config softflowd
    option enabled '1'
    option interface 'eth1'
    option collector '10.0.0.40:2055'
    option timeout_general '60'
    option timeout_tcp '1800'
    option timeout_udp '120'
    option timeout_icmp '60'
EOF

    /etc/init.d/softflowd enable
    /etc/init.d/softflowd start

    log_info "NetFlow export configured to 10.0.0.40:2055"
}

###############################################################################
# Logging Configuration
###############################################################################

configure_logging() {
    log_info "Configuring remote syslog..."

    cat > /etc/config/system.logging << 'EOF'
config system
    option hostname 'osint-gateway'
    option timezone 'UTC'
    option log_ip '10.0.0.15'
    option log_proto 'udp'
    option log_port '514'
    option log_prefix 'banana-pi'
    option conloglevel '8'
    option cronloglevel '8'
EOF

    cat /etc/config/system.logging >> /etc/config/system

    /etc/init.d/system restart

    log_info "Remote logging configured to Logstash (10.0.0.15:514)"
}

###############################################################################
# Monitoring
###############################################################################

configure_monitoring() {
    log_info "Setting up monitoring exporters..."

    # Install Prometheus node exporter
    opkg install prometheus-node-exporter-lua

    /etc/init.d/prometheus-node-exporter-lua enable
    /etc/init.d/prometheus-node-exporter-lua start

    log_info "Node exporter available on port 9100"
}

###############################################################################
# Post-Configuration
###############################################################################

post_config_info() {
    log_info "=========================================="
    log_info "Banana Pi Gateway Configuration Complete!"
    log_info "=========================================="
    echo ""
    log_info "Network Configuration:"
    echo "  WAN: DHCP (eth0)"
    echo "  LAN: 10.0.0.1/24 (eth1)"
    echo "  DMZ: 10.0.1.1/24 (eth2)"
    echo ""
    log_info "Services Running:"
    echo "  - Firewall (strict rules)"
    echo "  - DHCP Server"
    echo "  - DNS Forwarder (to Pi-hole)"
    echo "  - WireGuard VPN (port 51820)"
    echo "  - QoS/Traffic Shaping"
    echo "  - NetFlow Export"
    echo "  - Remote Logging"
    echo ""
    log_info "Web Interface:"
    echo "  - LuCI: https://10.0.0.1"
    echo ""
    log_info "VPN Access:"
    echo "  - WireGuard: Port 51820/UDP"
    echo "  - Generate client configs in LuCI"
    echo ""
    log_info "Monitoring:"
    echo "  - Prometheus Exporter: http://10.0.0.1:9100"
    echo ""
    log_info "Next Steps:"
    echo "  1. Access LuCI: https://10.0.0.1"
    echo "  2. Configure WireGuard clients"
    echo "  3. Update MAC addresses for static DHCP"
    echo "  4. Adjust QoS bandwidth limits"
    echo "  5. Configure port forwarding if needed"
    echo "  6. Test connectivity from LAN devices"
    echo ""
    log_warn "Important Security Notes:"
    echo "  - Change default password: passwd"
    echo "  - Update firewall rules as needed"
    echo "  - Keep OpenWRT updated: opkg update && opkg upgrade"
    echo "  - Monitor logs: logread -f"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting Banana Pi OpenWRT Configuration..."

    # Check if running on OpenWRT
    check_openwrt

    # Configuration steps
    update_openwrt
    configure_network
    configure_dhcp
    configure_firewall
    configure_qos
    configure_wireguard
    configure_netflow
    configure_logging
    configure_monitoring

    # Optional: Suricata (comment out if not needed)
    # configure_suricata

    # Post-configuration info
    post_config_info
}

# Show installation guide if not on OpenWRT
if [ -f /etc/openwrt_release ]; then
    main "$@"
else
    print_installation_guide
fi
