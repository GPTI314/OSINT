#!/bin/bash
# OSINT Toolkit - Kubernetes Deployment Script
# This script deploys the application to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if kubectl can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Parse arguments
ACTION=${1:-apply}
NAMESPACE="osint"

print_info "Starting Kubernetes deployment for OSINT Toolkit..."

case $ACTION in
    apply)
        print_step "1. Creating namespace..."
        kubectl apply -f k8s/namespace.yaml

        print_step "2. Creating ConfigMaps..."
        kubectl apply -f k8s/configmap.yaml

        print_step "3. Creating Secrets..."
        if [ ! -f k8s/secrets.yaml ]; then
            print_error "k8s/secrets.yaml not found!"
            print_info "Please create k8s/secrets.yaml from k8s/secrets.yaml.example"
            print_info "and update it with your actual secrets."
            exit 1
        fi
        kubectl apply -f k8s/secrets.yaml

        print_step "4. Creating Persistent Volume Claims..."
        kubectl apply -f k8s/pvc.yaml

        print_step "5. Creating RBAC resources..."
        kubectl apply -f k8s/rbac.yaml

        print_step "6. Deploying StatefulSets (databases)..."
        kubectl apply -f k8s/statefulset-postgres.yaml
        kubectl apply -f k8s/statefulset-redis.yaml
        kubectl apply -f k8s/statefulset-elasticsearch.yaml

        print_step "7. Creating Services..."
        kubectl apply -f k8s/service-postgres.yaml
        kubectl apply -f k8s/service-redis.yaml
        kubectl apply -f k8s/service-elasticsearch.yaml
        kubectl apply -f k8s/service-backend.yaml
        kubectl apply -f k8s/service-frontend.yaml

        print_step "8. Waiting for databases to be ready..."
        kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s || true
        kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s || true
        kubectl wait --for=condition=ready pod -l app=elasticsearch -n $NAMESPACE --timeout=300s || true

        print_step "9. Deploying application workloads..."
        kubectl apply -f k8s/deployment-backend.yaml
        kubectl apply -f k8s/deployment-worker.yaml
        kubectl apply -f k8s/deployment-frontend.yaml

        print_step "10. Creating Network Policies..."
        kubectl apply -f k8s/network-policy.yaml

        print_step "11. Creating Horizontal Pod Autoscalers..."
        kubectl apply -f k8s/hpa.yaml

        print_step "12. Creating Ingress..."
        kubectl apply -f k8s/ingress.yaml

        print_info ""
        print_info "==================================================================="
        print_info "Waiting for deployments to be ready..."
        print_info "==================================================================="
        kubectl wait --for=condition=available deployment -l tier=backend -n $NAMESPACE --timeout=300s
        kubectl wait --for=condition=available deployment -l tier=frontend -n $NAMESPACE --timeout=300s
        kubectl wait --for=condition=available deployment -l tier=worker -n $NAMESPACE --timeout=300s

        print_info ""
        print_info "==================================================================="
        print_info "OSINT Toolkit deployed successfully to Kubernetes!"
        print_info "==================================================================="
        kubectl get all -n $NAMESPACE
        print_info "==================================================================="
        ;;

    delete)
        print_warning "This will delete all OSINT resources from Kubernetes!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            print_info "Aborted."
            exit 0
        fi

        print_step "Deleting all resources..."
        kubectl delete -f k8s/ingress.yaml --ignore-not-found=true
        kubectl delete -f k8s/hpa.yaml --ignore-not-found=true
        kubectl delete -f k8s/network-policy.yaml --ignore-not-found=true
        kubectl delete -f k8s/deployment-frontend.yaml --ignore-not-found=true
        kubectl delete -f k8s/deployment-worker.yaml --ignore-not-found=true
        kubectl delete -f k8s/deployment-backend.yaml --ignore-not-found=true
        kubectl delete -f k8s/service-frontend.yaml --ignore-not-found=true
        kubectl delete -f k8s/service-backend.yaml --ignore-not-found=true
        kubectl delete -f k8s/service-elasticsearch.yaml --ignore-not-found=true
        kubectl delete -f k8s/service-redis.yaml --ignore-not-found=true
        kubectl delete -f k8s/service-postgres.yaml --ignore-not-found=true
        kubectl delete -f k8s/statefulset-elasticsearch.yaml --ignore-not-found=true
        kubectl delete -f k8s/statefulset-redis.yaml --ignore-not-found=true
        kubectl delete -f k8s/statefulset-postgres.yaml --ignore-not-found=true
        kubectl delete -f k8s/rbac.yaml --ignore-not-found=true
        kubectl delete -f k8s/pvc.yaml --ignore-not-found=true
        kubectl delete -f k8s/secrets.yaml --ignore-not-found=true
        kubectl delete -f k8s/configmap.yaml --ignore-not-found=true

        print_warning "Namespace will NOT be deleted to preserve any data."
        print_info "To delete namespace manually: kubectl delete namespace $NAMESPACE"
        print_info "Done!"
        ;;

    status)
        print_info "Getting OSINT Toolkit status..."
        kubectl get all -n $NAMESPACE
        print_info ""
        print_info "Pod status:"
        kubectl get pods -n $NAMESPACE -o wide
        ;;

    logs)
        SERVICE=${2:-backend}
        print_info "Fetching logs for $SERVICE..."
        kubectl logs -n $NAMESPACE -l app=osint-$SERVICE --tail=100 -f
        ;;

    *)
        print_error "Unknown action: $ACTION"
        print_info "Usage: $0 {apply|delete|status|logs}"
        exit 1
        ;;
esac

print_info "Done!"
