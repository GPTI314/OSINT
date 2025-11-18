# OSINT Platform - Troubleshooting Guide

Comprehensive troubleshooting guide for Windows Docker deployment.

## Table of Contents

- [Docker Desktop Issues](#docker-desktop-issues)
- [Service Startup Problems](#service-startup-problems)
- [Database Connection Issues](#database-connection-issues)
- [ELK Stack Issues](#elk-stack-issues)
- [Monitoring Stack Issues](#monitoring-stack-issues)
- [Performance Issues](#performance-issues)
- [Network Issues](#network-issues)
- [Data Persistence Issues](#data-persistence-issues)
- [Windows-Specific Issues](#windows-specific-issues)

## Docker Desktop Issues

### Docker Desktop Not Starting

**Symptoms:**
- Docker Desktop icon shows error
- `docker` commands fail
- "Docker is not running" error

**Solutions:**

1. **Check Windows Features**
   ```powershell
   # Open PowerShell as Administrator
   Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
   Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
   ```

   Enable if disabled:
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -All
   ```

2. **Reset Docker Desktop**
   - Right-click Docker Desktop icon in system tray
   - Select "Troubleshoot"
   - Click "Reset to factory defaults"

3. **Check WSL2**
   ```powershell
   wsl --list --verbose
   wsl --set-default-version 2
   ```

4. **Reinstall Docker Desktop**
   - Uninstall Docker Desktop
   - Delete `C:\Users\<username>\AppData\Local\Docker`
   - Reinstall from https://www.docker.com/products/docker-desktop

### WSL2 Integration Issues

**Symptoms:**
- "WSL2 is not installed" error
- Docker can't access files

**Solutions:**

1. **Update WSL2**
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```

2. **Enable WSL2 Integration**
   - Docker Desktop → Settings → Resources → WSL Integration
   - Enable integration for your distribution

3. **Restart WSL**
   ```powershell
   wsl --shutdown
   # Wait 10 seconds
   wsl
   ```

### Insufficient Resources

**Symptoms:**
- Services crash randomly
- Out of memory errors
- Slow performance

**Solutions:**

1. **Increase Docker Memory**
   - Docker Desktop → Settings → Resources
   - Memory: 16GB (minimum 8GB)
   - CPUs: 6+ (minimum 4)
   - Swap: 2GB
   - Apply & Restart

2. **Check Windows Resource Usage**
   ```powershell
   Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
   ```

3. **Close Unnecessary Applications**

## Service Startup Problems

### Services Won't Start

**Symptoms:**
- `docker-compose up` fails
- Services exit immediately
- Health checks fail

**Diagnostic Steps:**

1. **Check Service Logs**
   ```powershell
   docker-compose logs <service-name>
   docker-compose logs -f api
   ```

2. **Check Service Status**
   ```powershell
   docker-compose ps
   ```

3. **Inspect Container**
   ```powershell
   docker inspect osint-<service-name>
   ```

### Port Conflicts

**Symptoms:**
- "port is already allocated" error
- "bind: address already in use"

**Solutions:**

1. **Find Process Using Port**
   ```powershell
   netstat -ano | findstr :<port>
   # Example: netstat -ano | findstr :8000
   ```

2. **Kill Process**
   ```powershell
   # Get PID from netstat output
   Stop-Process -Id <PID> -Force
   ```

3. **Change Port in docker-compose.yml**
   ```yaml
   ports:
     - "8001:8000"  # Use different host port
   ```

### Build Failures

**Symptoms:**
- "failed to build" error
- Missing dependencies
- Build context issues

**Solutions:**

1. **Clean Docker Cache**
   ```powershell
   docker-compose build --no-cache
   docker system prune -a
   ```

2. **Check Dockerfile**
   - Ensure Dockerfile exists
   - Check for syntax errors
   - Verify base image is accessible

3. **Check Internet Connection**
   ```powershell
   Test-Connection -ComputerName google.com
   ```

## Database Connection Issues

### PostgreSQL Connection Failed

**Symptoms:**
- "could not connect to server"
- "connection refused"
- API can't connect to database

**Solutions:**

1. **Check PostgreSQL is Running**
   ```powershell
   docker-compose ps postgres
   docker-compose logs postgres
   ```

2. **Test Connection**
   ```powershell
   docker-compose exec postgres pg_isready -U osint_user
   ```

3. **Check Environment Variables**
   ```powershell
   docker-compose exec api env | findstr DATABASE
   ```

4. **Verify Password**
   - Check `.env` file for `POSTGRES_PASSWORD`
   - Ensure no special characters causing issues
   - Try single quotes in docker-compose.yml

5. **Reset PostgreSQL**
   ```powershell
   docker-compose stop postgres
   docker volume rm osint_postgres_data
   docker-compose up -d postgres
   ```

### MongoDB Connection Failed

**Symptoms:**
- "connection to MongoDB failed"
- "authentication failed"

**Solutions:**

1. **Check MongoDB Status**
   ```powershell
   docker-compose logs mongodb
   ```

2. **Test Connection**
   ```powershell
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   ```

3. **Check Authentication**
   ```powershell
   docker-compose exec mongodb mongosh -u osint_admin -p
   ```

4. **Verify URL Format**
   ```
   mongodb://username:password@host:port/database?authSource=admin
   ```

### Redis Connection Failed

**Symptoms:**
- "Error connecting to Redis"
- Celery can't connect

**Solutions:**

1. **Check Redis Status**
   ```powershell
   docker-compose logs redis
   ```

2. **Test Connection**
   ```powershell
   docker-compose exec redis redis-cli -a <password> ping
   ```

3. **Check Password**
   - Verify `REDIS_PASSWORD` in `.env`
   - Test without password if troubleshooting

## ELK Stack Issues

### Elasticsearch Won't Start

**Symptoms:**
- Container exits with error
- "max virtual memory areas too low"
- Out of memory errors

**Solutions:**

1. **Increase vm.max_map_count (Most Common)**
   ```powershell
   wsl -d docker-desktop
   sysctl -w vm.max_map_count=262144
   exit
   ```

   Make permanent:
   ```powershell
   wsl -d docker-desktop
   echo "vm.max_map_count=262144" >> /etc/sysctl.conf
   exit
   ```

2. **Reduce Heap Size**
   Edit `docker-compose.yml`:
   ```yaml
   environment:
     - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # Reduce from 2g
   ```

3. **Check Elasticsearch Logs**
   ```powershell
   docker-compose logs elasticsearch
   ```

4. **Verify Disk Space**
   ```powershell
   docker system df
   ```

### Logstash Not Processing Logs

**Symptoms:**
- Logs not appearing in Elasticsearch
- Logstash unhealthy

**Solutions:**

1. **Check Logstash Logs**
   ```powershell
   docker-compose logs logstash
   ```

2. **Verify Pipeline Configuration**
   ```powershell
   # Check syntax
   docker-compose exec logstash bin/logstash --config.test_and_exit -f /usr/share/logstash/pipeline/osint.conf
   ```

3. **Test Input**
   ```powershell
   # Send test log
   echo '{"message":"test"}' | curl -X POST -d @- http://localhost:5000
   ```

4. **Check Elasticsearch Connection**
   ```powershell
   docker-compose exec logstash curl -X GET http://elasticsearch:9200/_cluster/health
   ```

### Kibana Can't Connect to Elasticsearch

**Symptoms:**
- Kibana shows "unable to retrieve version information"
- Login page doesn't load

**Solutions:**

1. **Wait for Elasticsearch**
   - Elasticsearch takes 1-2 minutes to start
   - Check health: `curl http://localhost:9200/_cluster/health`

2. **Check Kibana Logs**
   ```powershell
   docker-compose logs kibana
   ```

3. **Verify Elasticsearch URL**
   ```powershell
   docker-compose exec kibana env | findstr ELASTICSEARCH
   ```

4. **Restart Kibana**
   ```powershell
   docker-compose restart kibana
   ```

## Monitoring Stack Issues

### Prometheus Not Scraping Targets

**Symptoms:**
- Targets show as "DOWN" in Prometheus
- No metrics collected

**Solutions:**

1. **Check Prometheus Targets**
   - Navigate to http://localhost:9090/targets
   - Check error messages

2. **Verify Configuration**
   ```powershell
   docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
   ```

3. **Test Target Connectivity**
   ```powershell
   docker-compose exec prometheus wget -O- http://api:8000/api/v1/metrics
   ```

4. **Reload Configuration**
   ```powershell
   curl -X POST http://localhost:9090/-/reload
   ```

### Grafana Can't Connect to Prometheus

**Symptoms:**
- Datasource test fails
- "Bad Gateway" error

**Solutions:**

1. **Check Prometheus is Running**
   ```powershell
   curl http://localhost:9090/-/healthy
   ```

2. **Check Datasource Configuration**
   - Grafana → Configuration → Data Sources
   - URL should be: `http://prometheus:9090`
   - Access: Server (not Browser)

3. **Test from Grafana Container**
   ```powershell
   docker-compose exec grafana wget -O- http://prometheus:9090/-/healthy
   ```

### Grafana Dashboards Not Loading

**Symptoms:**
- "Panel plugin not found"
- Dashboard shows errors

**Solutions:**

1. **Install Plugins**
   ```powershell
   docker-compose exec grafana grafana-cli plugins install <plugin-name>
   docker-compose restart grafana
   ```

2. **Check Provisioning**
   ```powershell
   docker-compose exec grafana ls -la /etc/grafana/provisioning
   ```

3. **Verify Dashboard JSON**
   - Check for syntax errors
   - Validate datasource references

## Performance Issues

### Services Running Slow

**Symptoms:**
- High response times
- API timeouts
- Slow queries

**Solutions:**

1. **Check Resource Usage**
   ```powershell
   docker stats
   ```

2. **Increase Docker Resources**
   - Docker Desktop → Settings → Resources
   - Increase memory and CPU allocation

3. **Check Disk I/O**
   ```powershell
   # In WSL
   iostat -x 1
   ```

4. **Optimize Database**
   ```powershell
   # PostgreSQL
   docker-compose exec postgres psql -U osint_user -d osint_platform -c "VACUUM ANALYZE;"

   # MongoDB
   docker-compose exec mongodb mongosh --eval "db.runCommand({compact: 'collection_name'})"
   ```

### High Memory Usage

**Symptoms:**
- Services crashing
- "OOM killed" in logs
- System freezing

**Solutions:**

1. **Identify Memory Hogs**
   ```powershell
   docker stats --no-stream | Sort-Object
   ```

2. **Set Memory Limits**
   Edit `docker-compose.yml`:
   ```yaml
   services:
     elasticsearch:
       deploy:
         resources:
           limits:
             memory: 4G
   ```

3. **Reduce Elasticsearch Heap**
   ```yaml
   environment:
     - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
   ```

4. **Reduce Logstash Heap**
   ```yaml
   environment:
     - "LS_JAVA_OPTS=-Xmx512m -Xms512m"
   ```

### Disk Space Issues

**Symptoms:**
- "no space left on device"
- Services failing to write

**Solutions:**

1. **Check Docker Disk Usage**
   ```powershell
   docker system df
   ```

2. **Clean Up**
   ```powershell
   # Remove unused containers
   docker container prune

   # Remove unused images
   docker image prune -a

   # Remove unused volumes
   docker volume prune

   # Remove everything unused
   docker system prune -a --volumes
   ```

3. **Increase Virtual Disk Size**
   - Docker Desktop → Settings → Resources → Disk image location
   - Increase "Virtual disk limit"

## Network Issues

### Services Can't Communicate

**Symptoms:**
- "connection refused" between services
- DNS resolution failures

**Solutions:**

1. **Check Network**
   ```powershell
   docker network ls
   docker network inspect osint_osint-network
   ```

2. **Test Service Connectivity**
   ```powershell
   docker-compose exec api ping postgres
   docker-compose exec api ping elasticsearch
   ```

3. **Check Service Names**
   - Use service names from docker-compose.yml
   - Not container names or localhost

4. **Recreate Network**
   ```powershell
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

### External Access Issues

**Symptoms:**
- Can't access services from browser
- Connection timeouts

**Solutions:**

1. **Check Windows Firewall**
   ```powershell
   Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Docker*"}
   ```

2. **Allow Ports**
   ```powershell
   New-NetFirewallRule -DisplayName "OSINT API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

3. **Check Port Binding**
   ```powershell
   netstat -ano | findstr :8000
   ```

4. **Try Different Browser**
   - Clear browser cache
   - Disable extensions
   - Try incognito mode

## Data Persistence Issues

### Data Lost After Restart

**Symptoms:**
- Database empty after restart
- Lost configuration

**Solutions:**

1. **Check Volumes Exist**
   ```powershell
   docker volume ls | findstr osint
   ```

2. **Inspect Volume**
   ```powershell
   docker volume inspect osint_postgres_data
   ```

3. **Verify Mount Points**
   ```powershell
   docker-compose config
   ```

4. **Don't Use `-v` Flag**
   ```powershell
   # WRONG - Deletes volumes
   docker-compose down -v

   # CORRECT - Keeps volumes
   docker-compose down
   ```

### Volume Permission Issues

**Symptoms:**
- "permission denied" errors
- Services can't write to volumes

**Solutions:**

1. **Check Volume Ownership**
   ```powershell
   docker-compose exec <service> ls -la /data
   ```

2. **Fix Permissions**
   ```powershell
   docker-compose exec <service> chown -R <user>:<group> /data
   ```

3. **Use Named Volumes**
   - Prefer named volumes over bind mounts
   - Docker manages permissions automatically

## Windows-Specific Issues

### Path Length Limitations

**Symptoms:**
- "path too long" errors
- Build failures

**Solutions:**

1. **Enable Long Paths**
   ```powershell
   # Run as Administrator
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

2. **Use Shorter Project Path**
   - Move project to `C:\osint`
   - Avoid deep nested folders

### Line Ending Issues

**Symptoms:**
- Scripts fail in containers
- "command not found" for shell scripts

**Solutions:**

1. **Configure Git**
   ```powershell
   git config --global core.autocrlf false
   git config --global core.eol lf
   ```

2. **Convert Files**
   ```powershell
   # In WSL
   dos2unix script.sh
   ```

### Antivirus Interference

**Symptoms:**
- Slow performance
- File access errors
- Build timeouts

**Solutions:**

1. **Exclude Docker Directories**
   Add exclusions in Windows Security:
   - `C:\Program Files\Docker`
   - `C:\ProgramData\Docker`
   - `C:\Users\<username>\.docker`
   - Your project directory

2. **Exclude WSL**
   - `\\wsl$\`

## Getting More Help

If issues persist:

1. **Collect Information**
   ```powershell
   # System info
   systeminfo > systeminfo.txt

   # Docker info
   docker info > docker-info.txt
   docker version > docker-version.txt

   # Service logs
   docker-compose logs > all-logs.txt
   ```

2. **Check Documentation**
   - [Docker Desktop Docs](https://docs.docker.com/desktop/windows/)
   - [Elasticsearch Docs](https://www.elastic.co/guide/)
   - [Prometheus Docs](https://prometheus.io/docs/)

3. **Search Issues**
   - GitHub Issues
   - Stack Overflow
   - Docker Forums

4. **Create Support Ticket**
   - Include error messages
   - Attach log files
   - Describe steps to reproduce

## Useful Diagnostic Commands

```powershell
# Docker
docker version
docker info
docker system df
docker stats

# Docker Compose
docker-compose config
docker-compose ps
docker-compose logs
docker-compose top

# Network
docker network ls
docker network inspect osint_osint-network
netstat -ano | findstr :<port>

# Volumes
docker volume ls
docker volume inspect <volume>

# Containers
docker ps -a
docker inspect <container>
docker logs <container>
docker exec -it <container> sh

# System
systeminfo
Get-Process
Get-Service
Test-Connection
```

---

**Last Updated**: 2025-11-18
**Platform**: Windows 11 / Docker Desktop
