#!/bin/bash
###############################################################################
# Cloudflare Tunnel Setup for Windows Node1 <-> Kali VM (Proxmox) Connection
# Secure remote access to Kali Linux OSINT tools from Windows workstation
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
# Configuration
###############################################################################

TUNNEL_NAME="osint-kali-tunnel"
KALI_IP="10.0.0.30"
DOMAIN="example.com"  # Replace with your domain
HOSTNAME="kali-osint.${DOMAIN}"

###############################################################################
# Check if running on Kali
###############################################################################

check_system() {
    if [ ! -f /etc/debian_version ]; then
        log_error "This script should be run on Debian-based systems (Kali Linux)"
        exit 1
    fi

    log_info "System check passed"
}

###############################################################################
# Install Cloudflared
###############################################################################

install_cloudflared() {
    log_info "Installing cloudflared..."

    # Download and install cloudflared
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

    dpkg -i cloudflared-linux-amd64.deb || apt-get -f install -y

    rm cloudflared-linux-amd64.deb

    # Verify installation
    cloudflared --version

    log_info "cloudflared installed successfully"
}

###############################################################################
# Cloudflare Tunnel Setup Guide
###############################################################################

print_setup_guide() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════╗
║           Cloudflare Tunnel Setup Instructions                          ║
╚══════════════════════════════════════════════════════════════════════════╝

PREREQUISITES:
--------------
1. Cloudflare account (free tier works)
2. Domain added to Cloudflare (can be free domain)
3. Cloudflare API token with Zone:Read and Tunnel:Edit permissions

STEP 1: Authenticate with Cloudflare
-------------------------------------
On the Kali VM, run:

  cloudflared tunnel login

This will:
- Open a browser to authenticate
- Download credentials to ~/.cloudflared/

STEP 2: Create Tunnel
---------------------
  cloudflared tunnel create osint-kali-tunnel

Save the Tunnel ID that is generated!

STEP 3: Configure DNS
---------------------
  cloudflared tunnel route dns osint-kali-tunnel kali-osint.example.com

Replace example.com with your domain.

STEP 4: Create Configuration File
----------------------------------
Create ~/.cloudflared/config.yml (this script will do it)

STEP 5: Run Tunnel
------------------
  cloudflared tunnel run osint-kali-tunnel

Or install as service:
  cloudflared service install
  systemctl enable cloudflared
  systemctl start cloudflared

SERVICES TO EXPOSE:
-------------------
- Kali Desktop (VNC/NoMachine): Port 4000
- Wireshark Web: Port 3000
- SSH: Port 22
- OSINT Web Tools: Port 8080

WINDOWS CLIENT SETUP:
---------------------
1. Download cloudflared for Windows
2. No configuration needed - just access via browser!
3. Access Kali services at: https://kali-osint.example.com

EOF
}

###############################################################################
# Setup Services on Kali
###############################################################################

setup_kali_services() {
    log_info "Setting up services on Kali Linux..."

    # Update system
    apt update

    # Install required services
    apt install -y \
        novnc \
        websockify \
        x11vnc \
        xfce4 \
        xfce4-goodies \
        nginx \
        wireshark \
        tshark

    log_info "Services installed"
}

setup_vnc_server() {
    log_info "Setting up VNC server for remote desktop access..."

    # Create VNC password
    mkdir -p ~/.vnc
    x11vnc -storepasswd changeme123 ~/.vnc/passwd

    # Create systemd service for VNC
    cat > /etc/systemd/system/x11vnc.service << 'EOF'
[Unit]
Description=x11vnc VNC Server
After=display-manager.service

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbauth /root/.vnc/passwd -rfbport 5900 -shared
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable x11vnc
    systemctl start x11vnc

    log_info "VNC server configured on port 5900"
}

setup_novnc() {
    log_info "Setting up noVNC for web-based desktop access..."

    # Clone noVNC
    git clone https://github.com/novnc/noVNC.git /opt/noVNC
    git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify

    # Create systemd service for noVNC
    cat > /etc/systemd/system/novnc.service << 'EOF'
[Unit]
Description=noVNC Web VNC Client
After=x11vnc.service

[Service]
Type=simple
ExecStart=/opt/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 4000
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable novnc
    systemctl start novnc

    log_info "noVNC configured on port 4000"
}

setup_wireshark_web() {
    log_info "Setting up Wireshark web interface..."

    # Create nginx configuration for Wireshark
    cat > /etc/nginx/sites-available/wireshark << 'EOF'
server {
    listen 3000;
    server_name localhost;

    location / {
        root /var/www/wireshark;
        index index.html;
    }

    location /capture {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

    ln -sf /etc/nginx/sites-available/wireshark /etc/nginx/sites-enabled/

    # Create web directory
    mkdir -p /var/www/wireshark

    # Create simple HTML interface
    cat > /var/www/wireshark/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Wireshark Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #1e3a8a; }
        .container { max-width: 800px; margin: 0 auto; }
        .button {
            background-color: #3b82f6;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover { background-color: #2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wireshark Web Interface</h1>
        <p>Network packet analysis for OSINT platform</p>
        <button class="button" onclick="window.location.href='/capture'">
            Start Capture
        </button>
        <div id="status"></div>
    </div>
</body>
</html>
EOF

    systemctl restart nginx

    log_info "Wireshark web interface configured on port 3000"
}

###############################################################################
# Create Cloudflare Tunnel Configuration
###############################################################################

create_tunnel_config() {
    log_info "Creating Cloudflare Tunnel configuration..."

    mkdir -p ~/.cloudflared

    cat > ~/.cloudflared/config.yml << EOF
tunnel: ${TUNNEL_NAME}
credentials-file: ~/.cloudflared/${TUNNEL_NAME}.json

ingress:
  # Kali Desktop (noVNC)
  - hostname: ${HOSTNAME}
    service: http://localhost:4000
    originRequest:
      noTLSVerify: true

  # Wireshark Web Interface
  - hostname: wireshark-${HOSTNAME}
    service: http://localhost:3000

  # SSH Access
  - hostname: ssh-${HOSTNAME}
    service: ssh://localhost:22

  # OSINT Web Tools
  - hostname: tools-${HOSTNAME}
    service: http://localhost:8080

  # API Access
  - hostname: api-${HOSTNAME}
    service: http://10.0.0.20:8000

  # Catch-all rule
  - service: http_status:404

# Logging
loglevel: info
logfile: /var/log/cloudflared.log

# Metrics
metrics: localhost:9126
EOF

    log_info "Tunnel configuration created at ~/.cloudflared/config.yml"
}

###############################################################################
# Setup Systemd Service
###############################################################################

setup_systemd_service() {
    log_info "Setting up cloudflared systemd service..."

    cat > /etc/systemd/system/cloudflared.service << EOF
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run ${TUNNEL_NAME}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload

    log_info "Systemd service created"
    log_warn "Run 'systemctl enable cloudflared' to enable on boot"
    log_warn "Run 'systemctl start cloudflared' to start tunnel"
}

###############################################################################
# Security Hardening
###############################################################################

configure_security() {
    log_info "Configuring security settings..."

    # Configure firewall to only allow Cloudflare IPs
    apt install -y ufw

    # Block all incoming by default
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH from LAN only
    ufw allow from 10.0.0.0/24 to any port 22

    # Allow internal services
    ufw allow from 10.0.0.0/24

    # Enable firewall
    ufw --force enable

    log_info "Firewall configured - only LAN access allowed"
    log_info "All external access goes through Cloudflare Tunnel"
}

###############################################################################
# Windows Client Setup Guide
###############################################################################

create_windows_guide() {
    log_info "Creating Windows client setup guide..."

    cat > /tmp/windows-client-setup.md << 'EOF'
# Windows Client Setup for Cloudflare Tunnel

## Option 1: Browser Access (Recommended)

Simply access your services via browser:
- Kali Desktop: https://kali-osint.example.com
- Wireshark: https://wireshark-kali-osint.example.com
- OSINT API: https://api-kali-osint.example.com

No software installation required!

## Option 2: SSH Access via Cloudflare

### Install cloudflared on Windows

1. Download cloudflared for Windows:
   https://github.com/cloudflare/cloudflared/releases/latest

2. Add to PATH or move to C:\Windows\System32\

3. Configure SSH:

```powershell
# Add to ~/.ssh/config
Host kali-osint
    ProxyCommand cloudflared access ssh --hostname ssh-kali-osint.example.com
    User root
```

4. Connect:
```powershell
ssh kali-osint
```

## Option 3: RDP-like Access

Use noVNC in browser for full desktop access:
https://kali-osint.example.com

Credentials:
- VNC Password: (as configured)

## Security Notes

- All traffic is encrypted by Cloudflare
- No ports exposed on Kali VM
- Zero Trust security model
- Can add access policies in Cloudflare dashboard

EOF

    log_info "Windows client guide created at /tmp/windows-client-setup.md"
    cat /tmp/windows-client-setup.md
}

###############################################################################
# Post-Installation
###############################################################################

post_install_info() {
    log_info "=========================================="
    log_info "Cloudflare Tunnel Setup Complete!"
    log_info "=========================================="
    echo ""
    log_info "Services Configured:"
    echo "  - noVNC Desktop: Port 4000"
    echo "  - Wireshark Web: Port 3000"
    echo "  - SSH: Port 22"
    echo "  - OSINT Tools: Port 8080"
    echo ""
    log_info "Cloudflare Tunnel Hostnames:"
    echo "  - Kali Desktop: https://${HOSTNAME}"
    echo "  - Wireshark: https://wireshark-${HOSTNAME}"
    echo "  - SSH: ssh-${HOSTNAME}"
    echo "  - API: https://api-${HOSTNAME}"
    echo ""
    log_info "Next Steps:"
    echo "  1. Authenticate: cloudflared tunnel login"
    echo "  2. Create tunnel: cloudflared tunnel create ${TUNNEL_NAME}"
    echo "  3. Route DNS: cloudflared tunnel route dns ${TUNNEL_NAME} ${HOSTNAME}"
    echo "  4. Copy tunnel credentials to ~/.cloudflared/"
    echo "  5. Start tunnel: systemctl start cloudflared"
    echo "  6. Check status: systemctl status cloudflared"
    echo "  7. View logs: journalctl -u cloudflared -f"
    echo ""
    log_info "Monitoring:"
    echo "  - Metrics: http://localhost:9126/metrics"
    echo ""
    log_warn "Security Reminder:"
    echo "  - Change VNC password: x11vnc -storepasswd ~/.vnc/passwd"
    echo "  - Configure Cloudflare Access policies"
    echo "  - Enable 2FA on Cloudflare account"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting Cloudflare Tunnel Setup..."

    check_system
    install_cloudflared
    setup_kali_services
    setup_vnc_server
    setup_novnc
    setup_wireshark_web
    create_tunnel_config
    setup_systemd_service
    configure_security
    create_windows_guide

    post_install_info
}

# Check if user wants setup guide or actual installation
if [ "${1:-}" = "--guide" ]; then
    print_setup_guide
else
    if [ $EUID -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
    main "$@"
fi
