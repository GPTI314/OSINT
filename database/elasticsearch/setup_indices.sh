#!/bin/bash
# ============================================================================
# Elasticsearch Indices Setup Script
# ============================================================================
# This script creates all required indices for the OSINT platform
# ============================================================================

set -e

# Configuration
ES_HOST="${ES_HOST:-localhost:9200}"
ES_USER="${ES_USER:-elastic}"
ES_PASS="${ES_PASS:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Function to make Elasticsearch API calls
es_api() {
    local method=$1
    local path=$2
    local data=$3

    if [ -n "$ES_PASS" ]; then
        curl -s -X "$method" \
            -H "Content-Type: application/json" \
            -u "$ES_USER:$ES_PASS" \
            "$ES_HOST/$path" \
            ${data:+-d "$data"}
    else
        curl -s -X "$method" \
            -H "Content-Type: application/json" \
            "$ES_HOST/$path" \
            ${data:+-d "$data"}
    fi
}

# Check Elasticsearch connection
print_info "Checking Elasticsearch connection..."
if ! es_api GET "" | grep -q "cluster_name"; then
    print_error "Cannot connect to Elasticsearch at $ES_HOST"
    exit 1
fi
print_success "Connected to Elasticsearch"

# Create ILM policy for logs
print_info "Creating ILM policy for logs..."
es_api PUT "_ilm/policy/logs_policy" '{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "30d"
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          }
        }
      },
      "cold": {
        "min_age": "60d",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}' > /dev/null
print_success "ILM policy created"

# Create scraped_content index
print_info "Creating scraped_content index..."
es_api PUT "scraped_content" '{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "html_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "char_filter": ["html_strip"],
          "filter": ["lowercase", "stop", "snowball"]
        },
        "url_analyzer": {
          "type": "custom",
          "tokenizer": "uax_url_email",
          "filter": ["lowercase"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "job_id": {"type": "keyword"},
      "investigation_id": {"type": "keyword"},
      "target_id": {"type": "keyword"},
      "url": {
        "type": "text",
        "analyzer": "url_analyzer",
        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
      },
      "title": {
        "type": "text",
        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
      },
      "content": {"type": "text", "analyzer": "html_analyzer"},
      "content_hash": {"type": "keyword"},
      "data_type": {"type": "keyword"},
      "mime_type": {"type": "keyword"},
      "status_code": {"type": "integer"},
      "created_at": {"type": "date"}
    }
  }
}' > /dev/null
print_success "scraped_content index created"

# Create intelligence_data index
print_info "Creating intelligence_data index..."
es_api PUT "intelligence_data" '{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "investigation_id": {"type": "keyword"},
      "target_id": {"type": "keyword"},
      "data_type": {"type": "keyword"},
      "source": {"type": "keyword"},
      "target_value": {
        "type": "text",
        "fields": {"keyword": {"type": "keyword"}}
      },
      "target_type": {"type": "keyword"},
      "domain": {"type": "keyword"},
      "ip_address": {"type": "ip"},
      "email": {"type": "keyword"},
      "confidence_score": {"type": "float"},
      "verified": {"type": "boolean"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}' > /dev/null
print_success "intelligence_data index created"

# Create findings index
print_info "Creating findings index..."
es_api PUT "findings" '{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "investigation_id": {"type": "keyword"},
      "title": {
        "type": "text",
        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
      },
      "description": {"type": "text"},
      "finding_type": {"type": "keyword"},
      "severity": {"type": "keyword"},
      "confidence": {"type": "float"},
      "status": {"type": "keyword"},
      "tags": {"type": "keyword"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}' > /dev/null
print_success "findings index created"

# Create logs index template
print_info "Creating logs index template..."
es_api PUT "_index_template/logs_template" '{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "logs_policy",
      "index.lifecycle.rollover_alias": "logs"
    },
    "mappings": {
      "properties": {
        "timestamp": {"type": "date"},
        "log_type": {"type": "keyword"},
        "level": {"type": "keyword"},
        "message": {"type": "text"},
        "source": {"type": "keyword"},
        "component": {"type": "keyword"},
        "investigation_id": {"type": "keyword"},
        "job_id": {"type": "keyword"},
        "session_id": {"type": "keyword"},
        "user_id": {"type": "keyword"},
        "url": {"type": "keyword"},
        "status_code": {"type": "integer"},
        "tags": {"type": "keyword"}
      }
    }
  }
}' > /dev/null
print_success "logs index template created"

# Create initial logs index
print_info "Creating initial logs index..."
es_api PUT "logs-000001" '{
  "aliases": {
    "logs": {
      "is_write_index": true
    }
  }
}' > /dev/null
print_success "logs-000001 index created"

# Create social_intelligence index
print_info "Creating social_intelligence index..."
es_api PUT "social_intelligence" '{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "investigation_id": {"type": "keyword"},
      "platform": {"type": "keyword"},
      "username": {"type": "keyword"},
      "profile_url": {"type": "keyword"},
      "follower_count": {"type": "integer"},
      "following_count": {"type": "integer"},
      "collected_at": {"type": "date"}
    }
  }
}' > /dev/null
print_success "social_intelligence index created"

# Create domain_intelligence index
print_info "Creating domain_intelligence index..."
es_api PUT "domain_intelligence" '{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "investigation_id": {"type": "keyword"},
      "domain": {"type": "keyword"},
      "subdomains": {"type": "keyword"},
      "registrar": {"type": "keyword"},
      "creation_date": {"type": "date"},
      "expiration_date": {"type": "date"},
      "collected_at": {"type": "date"}
    }
  }
}' > /dev/null
print_success "domain_intelligence index created"

print_success "All Elasticsearch indices created successfully!"
print_info "You can verify the indices with: curl $ES_HOST/_cat/indices?v"
