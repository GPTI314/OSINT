# OSINT Toolkit

Open-Source Intelligence (OSINT) toolkit: modular collectors, enrichment pipeline, link analysis, risk scoring, and investigative workflow automation.

## Features

### 🌐 Domain Intelligence Module
- **WHOIS Lookup**: Comprehensive domain registration data
- **DNS Records**: A, AAAA, MX, TXT, NS, CNAME, SOA, SPF, DMARC records
- **Subdomain Enumeration**: Multiple methods including DNS brute force and Certificate Transparency
- **SSL Certificate Analysis**: Certificate details, chain validation, expiration monitoring
- **Technology Detection**: Wappalyzer and BuiltWith integration
- **Historical Data**: Wayback Machine snapshots and historical DNS records
- **Threat Intelligence**: VirusTotal, malware/phishing detection, reputation scoring

### 🌍 IP Intelligence Module
- **Geolocation**: MaxMind GeoIP2, IPInfo, IP-API integration
- **ASN Information**: Autonomous System Number data and routing information
- **Port Scanning**: TCP/UDP port scanning with nmap
- **Service Detection**: Service fingerprinting and version detection
- **Threat Intelligence**: AbuseIPDB, VirusTotal, malware/botnet indicators
- **Historical Data**: Censys, Shodan historical scan data

### 📧 Email Intelligence Module
- **Breach Data**: Have I Been Pwned, DeHashed integration
- **Social Profile Discovery**: Find associated social media profiles
- **Domain Analysis**: MX records, SPF, DMARC validation
- **Email Verification**: SMTP verification, deliverability checks
- **Password Leak Checking**: Breach database queries
- **Disposable Email Detection**: Identify temporary email services

### 📱 Phone Intelligence Module
- **Carrier Information**: Carrier lookup and identification
- **Geolocation**: Country, region, timezone identification
- **Line Type Detection**: Mobile, landline, VoIP classification
- **Social Profile Discovery**: Find profiles associated with phone numbers
- **Number Verification**: Validation and format checking

### 📱 Social Media Intelligence (SOCMINT)
- **Profile Discovery**: Find profiles across multiple platforms
- **Post Collection**: Scrape posts, tweets, and content
- **Connection Analysis**: Follower/following relationship mapping
- **Activity Tracking**: Posting patterns and behavior analysis
- **Image Analysis**: Profile pictures and posted media analysis
- **Platforms**: Twitter, LinkedIn, Instagram, Facebook, TikTok, Reddit

### 🖼️ Image Intelligence Module
- **Reverse Image Search**: Google, Bing, Yandex, TinEye integration
- **Metadata Extraction**: EXIF, IPTC, XMP data extraction
- **GPS Coordinates**: Extract location data from images
- **OCR Text Extraction**: Tesseract OCR integration
- **Face Detection**: OpenCV and face_recognition library
- **Object Detection**: Identify objects in images
- **Image Forensics**: Tampering detection, ELA analysis, metadata consistency

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/OSINT.git
cd OSINT

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Additional Dependencies

For full functionality, install system dependencies:

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y nmap tesseract-ocr
```

#### macOS
```bash
brew install nmap tesseract
```

#### Windows
- Download and install nmap from https://nmap.org/download.html
- Download and install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki

## Configuration

### API Keys Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
# Domain Intelligence
VIRUSTOTAL_API_KEY=your_virustotal_api_key
SHODAN_API_KEY=your_shodan_api_key
SECURITYTRAILS_API_KEY=your_securitytrails_api_key

# IP Intelligence
IPINFO_API_KEY=your_ipinfo_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key

# Email Intelligence
HIBP_API_KEY=your_haveibeenpwned_api_key
HUNTER_API_KEY=your_hunter_io_api_key

# Social Media
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# And more...
```

### Getting API Keys

- **VirusTotal**: https://www.virustotal.com/gui/join-us
- **Shodan**: https://account.shodan.io/register
- **Have I Been Pwned**: https://haveibeenpwned.com/API/Key
- **Twitter**: https://developer.twitter.com/
- **Reddit**: https://www.reddit.com/prefs/apps

## Usage

### Command Line Interface

#### Domain Intelligence
```bash
# Basic domain investigation
osint domain example.com

# Exclude specific modules
osint domain example.com --no-subdomains --no-historical

# Save output to file
osint domain example.com -o results.json --pretty
```

#### IP Intelligence
```bash
# Basic IP investigation
osint ip 8.8.8.8

# Include port scanning (use responsibly)
osint ip 192.168.1.1 --include-ports --port-range "80,443,8080"

# Include service detection
osint ip 8.8.8.8 --include-services
```

#### Email Intelligence
```bash
# Basic email investigation
osint email user@example.com

# Include password leak checking
osint email user@example.com --include-passwords

# Exclude social profiles
osint email user@example.com --no-social
```

#### Phone Intelligence
```bash
# Phone number investigation
osint phone "+1234567890"
```

#### Social Media Intelligence
```bash
# Twitter investigation
osint social twitter username --max-posts 50

# Reddit investigation
osint social reddit username

# All platforms
osint social all username
```

#### Image Intelligence
```bash
# Local image analysis
osint image /path/to/image.jpg

# Image from URL
osint image https://example.com/image.jpg

# Include forensics analysis
osint image /path/to/image.jpg --include-forensics --include-objects
```

### Python API

```python
from osint import DomainIntelligence, IPIntelligence
from osint.core import Config

# Initialize with configuration
config = Config()

# Domain Intelligence
domain_intel = DomainIntelligence(config.get_all())
result = domain_intel.collect('example.com')
print(result)

# IP Intelligence
ip_intel = IPIntelligence(config.get_all())
result = ip_intel.collect('8.8.8.8', include_geolocation=True)
print(result)
```

### Advanced Examples

See the `examples/` directory for more comprehensive usage examples:

```python
# Combined investigation
from osint import DomainIntelligence, IPIntelligence, EmailIntelligence

# Investigate domain
domain_result = domain_intel.collect('example.com')

# Get IPs from DNS records
ips = domain_result['data']['dns']['A']

# Investigate each IP
for ip in ips:
    ip_result = ip_intel.collect(ip)
    print(ip_result)

# Check associated emails
emails = domain_result['data']['whois']['emails']
for email in emails:
    email_result = email_intel.collect(email)
    print(email_result)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_domain.py

# Run with coverage
pytest --cov=osint --cov-report=html

# Skip slow tests
pytest -m "not slow"
```

## Project Structure

```
OSINT/
├── src/
│   └── osint/
│       ├── __init__.py
│       ├── cli.py                 # Command-line interface
│       ├── core/                  # Core functionality
│       │   ├── base.py           # Base classes
│       │   ├── config.py         # Configuration management
│       │   └── utils.py          # Utility functions
│       └── modules/               # Intelligence modules
│           ├── domain.py         # Domain intelligence
│           ├── ip.py             # IP intelligence
│           ├── email.py          # Email intelligence
│           ├── phone.py          # Phone intelligence
│           ├── social.py         # Social media intelligence
│           └── image.py          # Image intelligence
├── tests/                         # Test suite
├── examples/                      # Usage examples
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── .env.example                   # Example environment variables
└── README.md                      # This file
```

## Legal and Ethical Considerations

⚠️ **IMPORTANT**: This toolkit is for authorized security testing, research, and educational purposes only.

### Legal Guidelines
- Only scan domains, IPs, and systems you own or have explicit permission to test
- Respect robots.txt and terms of service
- Be aware of and comply with local laws (e.g., CFAA in the US, Computer Misuse Act in the UK)
- Port scanning without permission may be illegal in your jurisdiction

### Ethical Use
- Use responsibly and ethically
- Respect privacy and data protection laws (GDPR, CCPA, etc.)
- Do not use for stalking, harassment, or malicious purposes
- Rate limit your requests to avoid overwhelming target services
- Consider the impact on target systems

### Best Practices
- Always get written authorization before testing third-party systems
- Document your testing activities
- Use API keys responsibly and keep them secure
- Respect rate limits and terms of service
- Consider using this tool in isolated/sandboxed environments

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This toolkit integrates with numerous open-source tools and APIs:

- **WHOIS/DNS**: python-whois, dnspython
- **Port Scanning**: python-nmap
- **Threat Intelligence**: VirusTotal, Shodan, AbuseIPDB
- **Social Media**: Tweepy, PRAW, Instaloader
- **Image Analysis**: Pillow, OpenCV, Tesseract, face_recognition
- **And many more...**

## Support

- **Issues**: https://github.com/yourusername/OSINT/issues
- **Documentation**: https://github.com/yourusername/OSINT/wiki
- **Discussions**: https://github.com/yourusername/OSINT/discussions

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. Users are responsible for ensuring their use of this tool complies with all applicable laws and regulations. The authors and contributors are not responsible for any misuse or damage caused by this software.

---

**Made with 🔍 for the OSINT community**
