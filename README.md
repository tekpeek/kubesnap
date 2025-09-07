# kubesnap  

> Take consistent Kubernetes snapshots of cluster resources and push them to object storage.  

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

## 📂 Project Structure  

kubesnap/

├── deploy_project.sh # Deployment helper script

├── dockerfiles/

│ └── Dockerfile.kubesnap # Container build file

├── kubernetes/
│ ├── deployments/
│ │ └── kubesnap-deployment.yaml
│ ├── rbac/
│ │ ├── kubesnap-svc-acc.yaml
│ │ ├── role-binding.yaml
│ │ └── svc-acc-cluster-role.yaml
│ └── services/
│ ├── kubesnap-svc.yaml
│ └── kubesnap-ingress.yaml
├── src/
│ ├── api/
│ │ └── kubesnap.py # API entrypoint
│ └── core/
│ └── kubesnap_functions.py# Core logic for snapshots
└── .github/workflows/
├── build.yml # CI build workflow
└── deploy.yml # CD deployment workflow

# Installation

- Clone the repository
- Enter the kubesnap repository
- In case you want to deploy kubesnap to a custom namespace, run the command
    - `export NAMESPACE="<CUSTOM-NAMESPACE>"`
- Give execute permissions to the file
    - `chmod +x deploy_project.sh`
- Run the file
    - `./deploy_project.sh`