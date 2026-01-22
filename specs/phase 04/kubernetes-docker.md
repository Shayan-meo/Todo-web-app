# AI-Powered Multilingual Todo App  
## Infrastructure as Code (Docker + Kubernetes + Helm)

---

## 1. Project Context

The goal of this phase is to transition the **AI-Powered Multilingual Todo App** from a local development environment into a **scalable, production-ready, and containerized system**.

This setup follows **Infrastructure-as-Code (IaC)** principles using **Docker**, **Kubernetes (Minikube)**, and **Helm**, enabling automation, resilience, and maintainability.

---

## 2. Core Functional Requirements

### 2.1 Containerization (Dockerization)

#### Multi-Service Architecture

Each service must be containerized separately:

- **Frontend**
  - Framework: Next.js
  - Base Image: `node:alpine`
  - Production-optimized build

- **Backend**
  - Framework: FastAPI
  - Base Image: `python:slim`
  - Handles PostgreSQL (Neon DB) dependencies

#### Environment Management

- `.env` files for local development
- Build-time and runtime environment variables for:
  - Groq / OpenAI API Keys
  - Database connection URLs

#### Image Optimization

- Use **multi-stage Docker builds**
- Keep final images minimal and secure

---

### 2.2 Kubernetes Orchestration (Minikube)

#### Deployment Strategy

- **Backend Deployment**
  - Replicas: 2
  - High availability enabled
  - Liveness and readiness probes configured

- **Frontend Deployment**
  - Replicas: 1–2
  - Serves the Next.js application

#### Service Networking

- Internal service discovery using Kubernetes DNS
- Frontend communicates with Backend via K8s Service name
- Frontend exposed externally using:
  - `NodePort` or
  - `LoadBalancer` (Minikube)

#### Secret Management

- Use **Kubernetes Secrets** for:
  - Groq / OpenAI API keys
  - Neon PostgreSQL credentials

---

### 2.3 Infrastructure as Code (Helm)

#### Helm Chart Structure

- Entire system packaged into a **single Helm chart**
- Chart location:


#### Configuration Management

- Centralized configuration using `values.yaml`
- Supports:
- Development environment
- Production environment

#### Persistence

- Database remains persistent via Neon DB
- Pod restarts must not affect stored data

---

## 3. Technical Specifications & Constraints

### Spec-Driven DevOps

- Use **Claude Code** to generate:
- Dockerfiles
- Kubernetes manifests
- Helm templates
- All generated artifacts must strictly follow this specification

### AIOps Integration

- Integrate AI-driven cluster management tools:
- `kubectl-ai`
- `kagent`
- Example command:
> "Scale backend to 3 replicas"

### Resource Management

- Define CPU and Memory limits for all deployments
- Prevent resource exhaustion and leakage

---

## 4. Success Criteria

### Scenario 1: Full Deployment

```bash
helm install todo-app ./charts
