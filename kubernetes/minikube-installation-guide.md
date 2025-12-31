# Guide: Minikube Installation & Basic Setup

## Table of Contents

1. [What Is Minikube?](#what-is-minikube)
2. [Prerequisites](#prerequisites)
3. [Install Minikube + kubectl (Windows)](#install-minikube--kubectl-windows)
4. [Install Minikube + kubectl (Linux/Mac)](#install-minikube--kubectl-linuxmac)
5. [Start Minikube](#start-minikube)
6. [Verify Installation](#verify-installation)
7. [Working with Local Docker Images](#working-with-local-docker-images)
8. [Basic Minikube Commands](#basic-minikube-commands)
9. [kubectl Context Management](#kubectl-context-management)
10. [Resource Configuration](#resource-configuration)
11. [Troubleshooting](#troubleshooting)
12. [Quick Reference](#quick-reference)

---

## What Is Minikube?

Minikube is a lightweight Kubernetes implementation that creates a local single-node Kubernetes cluster on your machine. It's designed for:

- Learning Kubernetes concepts and commands
- Local development and testing of containerized applications
- Validating Kubernetes manifests before deploying to production
- CI/CD pipeline testing
- Experimenting with Kubernetes features without cloud costs

Minikube supports multiple container runtimes (Docker, containerd, CRI-O) and can run on various virtualization platforms.

---

## Prerequisites

Before installing Minikube, ensure you have:

**Required:**
- A hypervisor or container runtime:
  - Docker Desktop (recommended for Windows/Mac)
  - Docker Engine (Linux)
  - VirtualBox, VMware, Hyper-V, or KVM
- 2 GB of free RAM (4 GB+ recommended)
- 2 CPU cores (or more)
- 20 GB of free disk space
- Internet connection (for downloading images)

**Optional but recommended:**
- kubectl (Kubernetes command-line tool)

**Verify Docker is running:**
```bash
docker --version
docker ps
```

---

## Install Minikube + kubectl (Windows)

### Option A: Using Chocolatey (Recommended)

Open PowerShell as Administrator:
```powershell
choco install -y minikube kubernetes-cli
```

### Option B: Using Scoop

```powershell
scoop install minikube kubectl
```

### Option C: Manual Installation

1. Download Minikube installer from: https://minikube.sigs.k8s.io/docs/start/
2. Download kubectl from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
3. Add both executables to your PATH

**Verify Installation:**
```powershell
minikube version
kubectl version --client
```

---

## Install Minikube + kubectl (Linux/Mac)

### macOS (Using Homebrew - Recommended)

```bash
brew install minikube kubectl
```

### Linux (Debian/Ubuntu)

**Install Minikube:**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Install kubectl:**
```bash
curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
sudo install kubectl /usr/local/bin/kubectl
```

**Make executable (if needed):**
```bash
chmod +x /usr/local/bin/minikube
chmod +x /usr/local/bin/kubectl
```

**Verify Installation:**
```bash
minikube version
kubectl version --client
```

---

## Start Minikube

**Basic Start (Uses defaults):**
```bash
minikube start
```

**Start with Docker Driver (Recommended):**
```bash
minikube start --driver=docker
```

**Start with Custom Resources:**
```bash
minikube start --driver=docker --cpus=2 --memory=4096
```

**Start with Specific Kubernetes Version:**
```bash
minikube start --kubernetes-version=v1.28.0
```

### Common Drivers

- `docker` (Recommended for most users)
- `virtualbox`
- `hyperv` (Windows only)
- `kvm2` (Linux only)
- `vmware`

### First-Time Setup

When you start Minikube for the first time, it will:
1. Download the Minikube ISO (~200 MB)
2. Create a virtual machine or container
3. Configure kubectl to use the Minikube cluster
4. Start the Kubernetes cluster

This may take 2-5 minutes depending on your internet speed.

---

## Verify Installation

**Check Minikube Status:**
```bash
minikube status
```

**Expected output:**
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

**Check kubectl Connection:**
```bash
kubectl cluster-info
kubectl get nodes
```

**Expected output:**
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.x
```

### Test with a Sample Deployment

```bash
kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0
kubectl expose deployment hello-minikube --type=NodePort --port=8080
kubectl get services hello-minikube
```

**Access the service:**
```bash
minikube service hello-minikube
```

**Cleanup test:**
```bash
kubectl delete deployment hello-minikube
kubectl delete service hello-minikube
```

---

## Working with Local Docker Images

By default, Minikube runs in an isolated environment and cannot access images from your local Docker registry. To use locally built images:

### Method 1: Load Image into Minikube

1. **Build your image locally:**
```bash
docker build -t my-app:latest .
```

2. **Load it into Minikube's image cache:**
```bash
minikube image load my-app:latest
```

3. **Use imagePullPolicy: Never or IfNotPresent in your manifest:**
```yaml
spec:
  containers:
  - name: my-app
    image: my-app:latest
    imagePullPolicy: IfNotPresent
```

### Method 2: Use Minikube's Docker Daemon

Point your shell to Minikube's Docker daemon:

**Linux/Mac:**
```bash
eval $(minikube docker-env)
```

**Windows PowerShell:**
```powershell
minikube docker-env | Invoke-Expression
```

Now build directly in Minikube:
```bash
docker build -t my-app:latest .
```

**To revert back to your host Docker:**
```bash
eval $(minikube docker-env -u)  # Linux/Mac
```

### Method 3: Use a Registry

Push to Docker Hub, ECR, or run a local registry.

---

## Basic Minikube Commands

### Cluster Management

```bash
minikube start              # Start cluster
minikube stop               # Stop cluster (preserves state)
minikube delete             # Delete cluster completely
minikube pause              # Pause cluster
minikube unpause            # Resume cluster
minikube status             # Check cluster status
```

### Access & Networking

```bash
minikube ip                 # Get cluster IP
minikube service <name>     # Open service in browser
minikube tunnel             # Create route to services (requires sudo/admin)
```

### Image Management

```bash
minikube image ls           # List images in Minikube
minikube image load <name>  # Load image from host
minikube image pull <name>  # Pull image from registry
minikube image rm <name>    # Remove image
```

### Dashboard & Addons

```bash
minikube dashboard          # Open Kubernetes dashboard
minikube addons list        # List available addons
minikube addons enable <addon>    # Enable addon
minikube addons disable <addon>   # Disable addon
```

### SSH & Debugging

```bash
minikube ssh                # SSH into Minikube node
minikube logs               # View Minikube logs
minikube kubectl -- <cmd>   # Run kubectl commands
```

### File System

```bash
minikube mount <src>:<dest> # Mount host directory into Minikube
```

**Examples:**
```bash
minikube mount /Users/me/data:/data
minikube mount C:\Users\me\data:/data   # Windows
```

---

## kubectl Context Management

Minikube automatically creates a kubectl context named "minikube".

**Check Current Context:**
```bash
kubectl config current-context
```

**List All Contexts:**
```bash
kubectl config get-contexts
```

**Switch to Minikube Context:**
```bash
kubectl config use-context minikube
```

**Switch to Another Context:**
```bash
kubectl config use-context <context-name>
```

**View Minikube Context Details:**
```bash
kubectl config view --minify
```

This is useful when you have multiple Kubernetes clusters configured (e.g., Minikube, Docker Desktop, EKS, GKE, AKS).

---

## Resource Configuration

### Default Resources

- 2 CPUs
- 2 GB RAM
- 20 GB disk

### Recommended for Development

```bash
minikube start --cpus=4 --memory=8192 --disk-size=40g
```

### For Machine Learning / Data Processing

```bash
minikube start --cpus=6 --memory=16384 --disk-size=60g
```

### For Minimal Testing

```bash
minikube start --cpus=2 --memory=2048
```

**Check Current Resource Allocation:**
```bash
kubectl top node minikube
```

> **Note:** You must delete and recreate the cluster to change resources:
> ```bash
> minikube delete
> minikube start --cpus=4 --memory=8192
> ```

---

## Troubleshooting

### Minikube won't start

- Check Docker is running: `docker ps`
- Verify virtualization is enabled in BIOS
- Try a different driver: `minikube start --driver=virtualbox`
- Check logs: `minikube logs`

### kubectl connection refused

- Ensure Minikube is running: `minikube status`
- Verify context: `kubectl config current-context`
- Switch context if needed: `kubectl config use-context minikube`

### Port already in use

- Stop Minikube: `minikube stop`
- Check for stale processes: `docker ps`
- Delete and restart: `minikube delete && minikube start`

### ImagePullBackOff errors

- Use `minikube image load` for local images
- Verify imagePullPolicy is set correctly
- Check image name and tag are correct

### Out of memory/resources

- Increase memory: `minikube delete && minikube start --memory=8192`
- Close unnecessary applications
- Check available system resources

### Cluster takes too long to start

- Check internet connection (downloads images)
- Try a different driver
- Reduce resource allocation if system is constrained

### Can't access services

- Use `minikube service <name>` to get URL
- Use `minikube tunnel` for LoadBalancer services
- Use `kubectl port-forward` for direct access

### Reset Everything

**Linux/Mac:**
```bash
minikube delete --all --purge
rm -rf ~/.minikube
```

**Windows:**
```powershell
minikube delete --all --purge
Remove-Item -Recurse -Force $HOME/.minikube
```

---

## Quick Reference

### Essential Commands Cheat Sheet

**Start/Stop:**
```bash
minikube start
minikube stop
minikube delete
```

**Status & Info:**
```bash
minikube status
minikube ip
kubectl cluster-info
kubectl get nodes
```

**Deploy & Access:**
```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl get services
minikube service <service-name>
kubectl port-forward svc/<service-name> 8080:80
```

**Images:**
```bash
docker build -t my-app:latest .
minikube image load my-app:latest
minikube image ls
```

**Debugging:**
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
kubectl exec -it <pod-name> -- /bin/sh
minikube ssh
minikube logs
```

**Cleanup:**
```bash
kubectl delete -f deployment.yaml
minikube delete
```

---

## Additional Resources

- **Official Documentation:** https://minikube.sigs.k8s.io/docs/
- **Kubernetes Documentation:** https://kubernetes.io/docs/home/
- **kubectl Cheat Sheet:** https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Minikube GitHub:** https://github.com/kubernetes/minikube

---