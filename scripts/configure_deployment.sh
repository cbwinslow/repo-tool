#!/bin/bash

# Deployment configuration script for RepoTool
# This script sets up deployment configurations for various environments

set -e  # Exit on error

# Configuration
VERSION=$(grep -m1 "VERSION = " Makefile | cut -d'"' -f2)
NAME="repo-tool"
CONFIG_DIR="deployment/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Create deployment directories
setup_directories() {
    log "Creating deployment directories..."
    
    mkdir -p ${CONFIG_DIR}/{development,staging,production}
    mkdir -p ${CONFIG_DIR}/{development,staging,production}/secrets
    mkdir -p ${CONFIG_DIR}/{development,staging,production}/config
}

# Generate environment configurations
generate_configs() {
    log "Generating environment configurations..."
    
    # Development environment
    cat > ${CONFIG_DIR}/development/config/config.yaml <<EOL
environment: development
debug: true
log_level: DEBUG
paths:
  default_download: ~/repositories
  temp: ~/.cache/repo_tool
  logs: ~/.local/share/repo_tool/logs
services:
  github:
    enabled: true
    use_gh_cli: true
    prefer_ssh: true
  gitlab:
    enabled: true
    prefer_ssh: true
  bitbucket:
    enabled: true
    prefer_ssh: true
EOL

    # Staging environment
    cat > ${CONFIG_DIR}/staging/config/config.yaml <<EOL
environment: staging
debug: false
log_level: INFO
paths:
  default_download: /opt/repo_tool/repositories
  temp: /var/cache/repo_tool
  logs: /var/log/repo_tool
services:
  github:
    enabled: true
    use_gh_cli: true
    prefer_ssh: true
  gitlab:
    enabled: true
    prefer_ssh: true
  bitbucket:
    enabled: true
    prefer_ssh: true
EOL

    # Production environment
    cat > ${CONFIG_DIR}/production/config/config.yaml <<EOL
environment: production
debug: false
log_level: WARNING
paths:
  default_download: /opt/repo_tool/repositories
  temp: /var/cache/repo_tool
  logs: /var/log/repo_tool
services:
  github:
    enabled: true
    use_gh_cli: true
    prefer_ssh: true
  gitlab:
    enabled: true
    prefer_ssh: true
  bitbucket:
    enabled: true
    prefer_ssh: true
monitoring:
  enabled: true
  prometheus: true
  grafana: true
security:
  ssl: true
  rate_limiting: true
  ip_whitelist: true
EOL
}

# Generate secret templates
generate_secret_templates() {
    log "Generating secret templates..."
    
    for env in development staging production; do
        cat > ${CONFIG_DIR}/${env}/secrets/secrets.template.yaml <<EOL
# Template for ${env} secrets
# DO NOT commit actual secrets to version control
# Copy this file to secrets.yaml and fill in the values

github_token: ""
gitlab_token: ""
bitbucket_token: ""

# Database credentials
db_host: ""
db_port: "5432"
db_name: "repo_tool"
db_user: ""
db_password: ""

# API keys
api_key: ""
encryption_key: ""

# Monitoring
prometheus_token: ""
grafana_api_key: ""
EOL
    done
}

# Generate deployment manifests
generate_manifests() {
    log "Generating deployment manifests..."
    
    # Docker Compose manifest
    cat > ${CONFIG_DIR}/docker-compose.yaml <<EOL
version: '3.8'

services:
  app:
    build: .
    image: ghcr.io/cbwinslow/repo-tool:\${VERSION:-latest}
    environment:
      - REPO_TOOL_ENV=\${ENV:-development}
      - REPO_TOOL_CONFIG_DIR=/config
      - REPO_TOOL_DATA_DIR=/data
      - REPO_TOOL_LOG_DIR=/logs
    volumes:
      - ./\${ENV:-development}/config:/config
      - ./\${ENV:-development}/secrets:/secrets
      - repo_tool_data:/data
      - repo_tool_logs:/logs
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./grafana:/etc/grafana
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_PASSWORD:-admin}
    ports:
      - "3000:3000"

volumes:
  repo_tool_data:
  repo_tool_logs:
  prometheus_data:
  grafana_data:
EOL

    # Kubernetes manifest
    cat > ${CONFIG_DIR}/kubernetes.yaml <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: repo-tool
spec:
  replicas: 3
  selector:
    matchLabels:
      app: repo-tool
  template:
    metadata:
      labels:
        app: repo-tool
    spec:
      containers:
      - name: repo-tool
        image: ghcr.io/cbwinslow/repo-tool:\${VERSION}
        env:
        - name: REPO_TOOL_ENV
          value: \${ENV}
        - name: REPO_TOOL_CONFIG_DIR
          value: /config
        volumeMounts:
        - name: config
          mountPath: /config
        - name: secrets
          mountPath: /secrets
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
      volumes:
      - name: config
        configMap:
          name: repo-tool-config
      - name: secrets
        secret:
          secretName: repo-tool-secrets
---
apiVersion: v1
kind: Service
metadata:
  name: repo-tool
spec:
  selector:
    app: repo-tool
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
EOL
}

# Generate monitoring configurations
generate_monitoring() {
    log "Generating monitoring configurations..."
    
    # Prometheus configuration
    mkdir -p ${CONFIG_DIR}/prometheus
    cat > ${CONFIG_DIR}/prometheus/prometheus.yml <<EOL
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'repo_tool'
    static_configs:
      - targets: ['localhost:8000']
EOL

    # Grafana dashboard
    mkdir -p ${CONFIG_DIR}/grafana/dashboards
    cat > ${CONFIG_DIR}/grafana/dashboards/repo_tool.json <<EOL
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "title": "Repository Operations",
      "type": "graph",
      "datasource": "Prometheus",
      "targets": [
        {
          "expr": "rate(repo_tool_operations_total[5m])",
          "legendFormat": "{{operation}}"
        }
      ]
    }
  ],
  "refresh": "5s",
  "schemaVersion": 16,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "RepoTool Dashboard",
  "uid": "repo_tool",
  "version": 1
}
EOL
}

# Main execution
main() {
    log "Starting deployment configuration for ${NAME} v${VERSION}"
    
    setup_directories
    generate_configs
    generate_secret_templates
    generate_manifests
    generate_monitoring
    
    log "Deployment configuration completed successfully!"
    log "Next steps:"
    echo "1. Copy appropriate secrets template and fill in values"
    echo "2. Select deployment method (Docker Compose or Kubernetes)"
    echo "3. Deploy using provided manifests"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

