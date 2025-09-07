#!/bin/bash

set -e

log() {
    local timestamp
    timestamp="$(date +"%Y-%m-%d %H:%M:%S")"
    echo "[$timestamp] $*"
}

if [ -z $NAMESPACE ]; then
    export NAMESPACE="kubesnap"
fi

namespace_list=($(kubectl get ns -o json | jq -r .items[].metadata.name))

if [[ "${namespace_list[*]}" =~ " $NAMESPACE " ]] || [[ "${namespace_list[*]}" =~ "$NAMESPACE " ]] || [[ "${namespace_list[*]}" =~ " $NAMESPACE" ]]; then
    log "namespace $NAMESPACE already present"
else
    kubectl create namespace $NAMESPACE
    log "namespace $NAMESPACE created"
fi

check_deployment() {
    deployment_name=$1
    INTERVAL=5
    TIMEOUT=250
    ELAPSED=0
    deployment_status=$(kubectl -n "${NAMESPACE}" get deploy $deployment_name -o json | jq -r '.status.conditions[]' | jq -r 'select(.type == "Available").status')
    while [ $ELAPSED -lt $TIMEOUT ]; do
        deployment_status=$(kubectl -n "${NAMESPACE}" get deploy $deployment_name -o json | jq -r '.status.conditions[]' | jq -r 'select(.type == "Available").status')
        if [[ "${deployment_status^^}" == "TRUE" ]]; then
            break
        fi
        echo "Waiting for $deployment_name :: Elapsed - $ELAPSED"
        sleep $INTERVAL
        ELAPSED=$((ELAPSED + INTERVAL))
    done

    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "Microservice deployment failed. $deployment_name not in running status!"
        exit 1
    fi
}

if [[ ! -z "${OBJECT_STORE_REQ}" ]]; then
    kubectl -n "${NAMESPACE}" delete secret objectstore-auth --ignore-not-found
    kubectl -n "${NAMESPACE}" create secret generic objectstore-auth \
        --from-literal=OBJECT_STORE_REQ="${OBJECT_STORE_REQ}"
fi

# Delete the old service and deploy the signal engine service
kubectl -n "${NAMESPACE}" delete service kubesnap-service --ignore-not-found
kubectl -n "${NAMESPACE}" apply -f kubernetes/services/kubesnap-svc.yaml
log "kubesnap-service applied"

if [[ ! -z "${SF_API_KEY}" ]]; then
    kubectl -n "${NAMESPACE}" delete secret api-credentials --ignore-not-found
    kubectl -n "${NAMESPACE}" create secret generic api-credentials \
        --from-literal=api-key="${SF_API_KEY}"
    log "api-credentials secret created"
fi

# delete and recreate rbac related service configuration
kubectl delete clusterrolebinding kubesnap-rolebinding --ignore-not-found
kubectl delete clusterrole kubesnap-role --ignore-not-found
kubectl -n "${NAMESPACE}" delete serviceaccount kubesnap-svc-acc --ignore-not-found

sed -i "s|__NAMESPACE__|${NAMESPACE}|g" kubernetes/rbac/kubesnap-svc-acc.yaml
sed -i "s|__NAMESPACE__|${NAMESPACE}|g" kubernetes/rbac/role-binding.yaml

kubectl -n "${NAMESPACE}" apply -f kubernetes/rbac/kubesnap-svc-acc.yaml
kubectl -n "${NAMESPACE}" apply -f kubernetes/rbac/svc-acc-cluster-role.yaml
kubectl -n "${NAMESPACE}" apply -f kubernetes/rbac/role-binding.yaml

log "rbac related yamls applied"

# Delete and recreate stockflow-controller microservice
kubectl -n "${NAMESPACE}" delete deployment kubesnap --ignore-not-found
kubectl -n "${NAMESPACE}" apply -f kubernetes/deployments/kubesnap-deployment.yaml
log "kubesnap deployment applied"

# Verifying if the stockflow-controller is in running status
check_deployment "kubesnap"

# Apply ingress service
kubectl -n "${NAMESPACE}" delete ingress kubesnap-ingress --ignore-not-found

sed -i "s|__NAMESPACE__|${NAMESPACE}|g" kubernetes/services/kubesnap-ingress.yaml

kubectl -n "${NAMESPACE}" apply -f kubernetes/services/kubesnap-ingress.yaml
log "kubesnap-ingress applied"