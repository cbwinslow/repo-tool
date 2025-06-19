#!/bin/bash

# Cloud deployment script for RepoTool
# This script deploys the application to various cloud platforms

set -e  # Exit on error

# Configuration
VERSION=$(grep -m1 "VERSION = " Makefile | cut -d'"' -f2)
NAME="repo-tool"
REGION="${REGION:-us-east-1}"  # Default to AWS us-east-1
ENVIRONMENT="${ENVIRONMENT:-staging}"

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

# AWS deployment
deploy_aws() {
    log "Deploying to AWS..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not installed"
        return 1
    fi
    
    # Create ECS task definition
    cat > task-definition.json <<EOL
{
    "family": "${NAME}",
    "containerDefinitions": [
        {
            "name": "${NAME}",
            "image": "ghcr.io/cbwinslow/${NAME}:${VERSION}",
            "cpu": 256,
            "memory": 512,
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "hostPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "REPO_TOOL_ENV",
                    "value": "${ENVIRONMENT}"
                }
            ],
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOL
    
    # Register task definition
    aws ecs register-task-definition \
        --cli-input-json file://task-definition.json \
        --region "${REGION}"
    
    # Update service
    aws ecs update-service \
        --cluster "${NAME}-${ENVIRONMENT}" \
        --service "${NAME}" \
        --task-definition "${NAME}" \
        --region "${REGION}"
}

# GCP deployment
deploy_gcp() {
    log "Deploying to Google Cloud..."
    
    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI not installed"
        return 1
    fi
    
    # Create Cloud Run service
    gcloud run deploy "${NAME}" \
        --image "ghcr.io/cbwinslow/${NAME}:${VERSION}" \
        --platform managed \
        --region "${REGION}" \
        --set-env-vars "REPO_TOOL_ENV=${ENVIRONMENT}" \
        --allow-unauthenticated
}

# Azure deployment
deploy_azure() {
    log "Deploying to Azure..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        error "Azure CLI not installed"
        return 1
    fi
    
    # Create container app
    az containerapp create \
        --name "${NAME}" \
        --resource-group "${NAME}-${ENVIRONMENT}" \
        --image "ghcr.io/cbwinslow/${NAME}:${VERSION}" \
        --environment "${ENVIRONMENT}" \
        --ingress external \
        --target-port 8000 \
        --env-vars "REPO_TOOL_ENV=${ENVIRONMENT}"
}

# Digital Ocean deployment
deploy_digitalocean() {
    log "Deploying to DigitalOcean..."
    
    # Check doctl CLI
    if ! command -v doctl &> /dev/null; then
        error "doctl CLI not installed"
        return 1
    fi
    
    # Create app spec
    cat > app.yaml <<EOL
name: ${NAME}
region: ${REGION}
services:
- name: web
  github:
    repo: cbwinslow/repo-tool
    branch: main
  image:
    registry_type: GITHUB
    repository: cbwinslow/repo-tool
    tag: ${VERSION}
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 8000
  env:
  - key: REPO_TOOL_ENV
    value: ${ENVIRONMENT}
EOL
    
    # Deploy app
    doctl apps create --spec app.yaml
}

# Kubernetes deployment
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl not installed"
        return 1
    fi
    
    # Create namespace if not exists
    kubectl create namespace "${NAME}-${ENVIRONMENT}" --dry-run=client -o yaml | kubectl apply -f -
    
    # Create configmap
    kubectl create configmap "${NAME}-config" \
        --from-file=config.yaml=deployment/config/${ENVIRONMENT}/config/config.yaml \
        --namespace "${NAME}-${ENVIRONMENT}" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secret
    kubectl create secret generic "${NAME}-secrets" \
        --from-file=secrets.yaml=deployment/config/${ENVIRONMENT}/secrets/secrets.yaml \
        --namespace "${NAME}-${ENVIRONMENT}" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy application
    kubectl apply -f deployment/config/kubernetes.yaml \
        --namespace "${NAME}-${ENVIRONMENT}"
}

# Helm deployment
deploy_helm() {
    log "Deploying with Helm..."
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        error "helm not installed"
        return 1
    fi
    
    # Add/update helm repo
    helm repo add repo-tool https://charts.repo-tool.dev
    helm repo update
    
    # Deploy/upgrade release
    helm upgrade --install "${NAME}" repo-tool/repo-tool \
        --namespace "${NAME}-${ENVIRONMENT}" \
        --create-namespace \
        --set image.tag="${VERSION}" \
        --set environment="${ENVIRONMENT}" \
        --values deployment/config/${ENVIRONMENT}/values.yaml
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    rm -f task-definition.json app.yaml
}

# Usage information
usage() {
    echo "Usage: $0 [options] <platform>"
    echo
    echo "Platforms:"
    echo "  aws           Deploy to AWS ECS"
    echo "  gcp           Deploy to Google Cloud Run"
    echo "  azure         Deploy to Azure Container Apps"
    echo "  do            Deploy to DigitalOcean App Platform"
    echo "  k8s           Deploy to Kubernetes cluster"
    echo "  helm          Deploy using Helm chart"
    echo
    echo "Options:"
    echo "  -e, --environment   Set deployment environment (default: staging)"
    echo "  -r, --region       Set deployment region"
    echo "  -h, --help         Show this help message"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        aws|gcp|azure|do|k8s|helm)
            PLATFORM="$1"
            shift
            ;;
        *)
            error "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate input
if [ -z "${PLATFORM}" ]; then
    error "No platform specified"
    usage
    exit 1
fi

# Main execution
main() {
    log "Starting deployment to ${PLATFORM} (${ENVIRONMENT})"
    
    # Register cleanup
    trap cleanup EXIT
    
    # Deploy to specified platform
    case "${PLATFORM}" in
        aws)
            deploy_aws
            ;;
        gcp)
            deploy_gcp
            ;;
        azure)
            deploy_azure
            ;;
        do)
            deploy_digitalocean
            ;;
        k8s)
            deploy_kubernetes
            ;;
        helm)
            deploy_helm
            ;;
        *)
            error "Unsupported platform: ${PLATFORM}"
            exit 1
            ;;
    esac
    
    log "Deployment completed successfully!"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

