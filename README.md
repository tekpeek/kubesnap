# kubesnap  

Take consistent Kubernetes snapshots of cluster resources and push them to object storage.  

[![Build](https://github.com/tekpeek/kubesnap/actions/workflows/build.yml/badge.svg)](./.github/workflows/build.yml)  
[![Deploy](https://github.com/tekpeek/kubesnap/actions/workflows/deploy.yml/badge.svg)](./.github/workflows/deploy.yml)  

---

## Overview  

**kubesnap** is a lightweight microservice designed to capture **snapshots of Kubernetes workloads** (pods, jobs, cronjobs, deployments, and services) and push them into an object storage bucket for archival, compliance, and debugging purposes.  

It integrates smoothly with Kubernetes clusters and can be deployed as a containerized service with proper RBAC and API access.  

---

## Features  

- Collects runtime information of **pods, jobs, cronjobs, deployments, services**  
- Pushes snapshot data to **Object Storage** (OCI or any S3-compatible backend)  
- Supports **scheduled snapshots** via CronJobs  
- Secured with **Kubernetes RBAC** and service accounts  
- Delivered as a **Docker container** and easily deployed on any Kubernetes cluster  
- GitHub Actions workflows for **CI/CD** (build & deploy pipelines)  

---

## Prerequisites

Before deploying, ensure you have the following tools installed:
- `kubectl`
- `jq`
- `sed`
- An Ingress Controller (e.g., Nginx, Traefik) is recommended for external access.

---

## Configuration

The deployment script and application require specific environment variables to be set.

| Variable | Description | Required |
|----------|-------------|----------|
| `OBJECT_STORE_REQ` | The target URL for uploading snapshots via HTTP PUT (e.g., `https://objectstorage.us-region.oraclecloud.com/p/...`). | **Yes** |
| `SF_API_KEY` | A secure key used to authenticate API requests. | **Yes** |
| `NAMESPACE` | The Kubernetes namespace to deploy into. Defaults to `kubesnap`. | No |

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tekpeek/kubesnap.git
   cd kubesnap
   ```

2. **Set Environment Variables**
   Export the required variables before running the deployment script.
   ```bash
   export OBJECT_STORE_REQ="<YOUR_OBJECT_STORAGE_PUT_URL>"
   export SF_API_KEY="<YOUR_SECURE_API_KEY>"
   # Optional: Custom namespace
   export NAMESPACE="kubesnap"
   ```

3. **Deploy**
   Give execute permissions and run the deployment script.
   ```bash
   chmod +x deploy_project.sh
   ./deploy_project.sh
   ```

---

## API Reference

Once deployed, you can interact with **kubesnap** using its REST API.

### Authentication
All requests to the snapshot endpoint require the `X-API-Key` header.
```bash
-H "X-API-Key: <YOUR_SF_API_KEY>"
```

### Endpoints

#### 1. Health Check
Check if the service is running.
- **URL:** `/api/kubesnap/health`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "status": "OK",
    "timestamp": "2023-10-27 10:00:00+00:00"
  }
  ```

#### 2. Create Snapshot
Trigger a snapshot for a specific namespace.
- **URL:** `/api/kubesnap/{namespace}`
- **Method:** `GET`
- **Headers:** `X-API-Key: <SF_API_KEY>`
- **Response:**
  ```json
  {
    "snapshot_status": "success",
    "file_name": "kubesnap_2023_10_27_10_00_00.zip",
    "timestamp": "1698400800.0",
    "upload_status": "success"
  }
  ```

---

## Snapshot Artifacts

The generated snapshot is a `.zip` file containing the following structure:

```
kubesnap_<timestamp>.zip
├── pod_logs/       # Logs from all pods in the namespace
├── deployments/    # YAML configurations of deployments
├── jobs/           # YAML configurations of jobs
├── cronjobs/       # YAML configurations of cronjobs
└── configmaps/     # YAML configurations of configmaps
```

---

## 📂 Project Structure  

```
kubesnap/
├── deploy_project.sh           # Deployment helper script
├── dockerfiles/
│   └── Dockerfile.kubesnap    # Container build file
├── kubernetes/
│   ├── deployments/
│   │   └── kubesnap-deployment.yaml
│   ├── rbac/
│   │   ├── kubesnap-svc-acc.yaml
│   │   ├── role-binding.yaml
│   │   └── svc-acc-cluster-role.yaml
│   └── services/
│       ├── kubesnap-svc.yaml
│       └── kubesnap-ingress.yaml
├── src/
│   ├── api/
│   │   └── kubesnap.py              # API entrypoint
│   └── core/
│       └── kubesnap_functions.py   # Core logic for snapshots
└── .github/workflows/
    ├── build.yml                   # CI build workflow
    └── deploy.yml                  # CD deployment workflow
```