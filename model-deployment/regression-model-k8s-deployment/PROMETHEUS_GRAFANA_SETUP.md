# Prometheus + Grafana Monitoring Setup for Minikube

This guide walks you through setting up production-grade monitoring and alerting on your Minikube cluster using Prometheus, Grafana, and Alertmanager. We'll track your ML model's inference metrics and Kubernetes cluster health.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Bump Minikube Resources](#step-1-bump-minikube-resources)
3. [Step 2: Install Helm and kube-prometheus-stack](#step-2-install-helm-and-kube-prometheus-stack)
4. [Step 3: Configure Prometheus Scraping](#step-3-configure-prometheus-scraping)
5. [Step 4: Access Prometheus and Grafana](#step-4-access-prometheus-and-grafana)
6. [Step 5: Create Custom Dashboards](#step-5-create-custom-dashboards)
7. [Step 6: Configure Alerting](#step-6-configure-alerting)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

## Prerequisites

- Minikube installed and running
- `kubectl` configured to work with your Minikube cluster
- Your ML model deployed to Minikube (following the MINIKUBE_SETUP_GUIDE.txt)
- 16GB RAM available on your laptop (we're bumping Minikube to 8GB)
- About 30-45 minutes for the full setup

## Step 1: Bump Minikube Resources

Your current Minikube setup likely has 4GB of RAM. Prometheus + Grafana needs more resources.

### 1.1 Stop Minikube

**Windows (PowerShell):**
```powershell
minikube stop
```

**Linux/Ubuntu:**
```bash
minikube stop
```

### 1.2 Delete Current Minikube Cluster (Start Fresh)

This ensures clean resource allocation:

**Windows (PowerShell):**
```powershell
minikube delete
```

**Linux/Ubuntu:**
```bash
minikube delete
```

If you have important data in `/tmp/ml-output`, back it up first:

**Windows (PowerShell):**
```powershell
Copy-Item -Path D:\<your-backup-path>\ml-output -Destination D:\<backup-location> -Recurse
```

**Linux/Ubuntu:**
```bash
cp -r /tmp/ml-output /your-backup-location/
```

### 1.3 Create New Minikube Cluster with 8GB RAM

**Windows (PowerShell):**
```powershell
minikube start --memory 8192 --cpus 4 --disk-size 30g
```

**Linux/Ubuntu:**
```bash
minikube start --memory 8192 --cpus 4 --disk-size 30g
```

**What this does:**
- `--memory 8192`: Allocates 8GB RAM (8192 MB) to Minikube
- `--cpus 4`: Allocates 4 CPU cores
- `--disk-size 30g`: Allocates 30GB disk space for images and volumes

### 1.4 Verify Cluster is Running

**Windows (PowerShell):**
```powershell
minikube status
```

**Linux/Ubuntu:**
```bash
minikube status
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

## Step 2: Install Helm and kube-prometheus-stack

Helm is a Kubernetes package manager. kube-prometheus-stack is a production-grade monitoring solution.

### 2.1 Install Helm (if not already installed)

**Windows (PowerShell):**
```powershell
# Using Chocolatey
choco install kubernetes-helm
```

**Linux/Ubuntu:**
```bash
# Using official script
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# OR using apt (if available)
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

Or download from: https://github.com/helm/helm/releases

Verify:
**All Platforms:**
```bash
helm version
```

### 2.2 Add Prometheus Community Helm Repository

**All Platforms (Windows/Linux/Ubuntu):**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### 2.3 Create Monitoring Namespace

It's a best practice to keep monitoring in a separate namespace:

**All Platforms (Windows/Linux/Ubuntu):**
```bash
kubectl create namespace monitoring
```

### 2.4 Install kube-prometheus-stack

First, create a values override file for custom configuration:

**File: `monitoring/prometheus-values.yaml`**

Create this file in your project root and add:

```yaml
# Prometheus values
prometheus:
  prometheusSpec:
    # Retention policy
    retention: 24h
    
    # Storage for metrics (important!)
    storageSpec:
      volumeClaimTemplate:
        spec:
          resources:
            requests:
              storage: 5Gi
    
    # Service monitor selectors
    serviceMonitorSelectorNilUsesHelmValues: false
    
    # Alert rules
    ruleNamespaceSelectorNilUsesHelmValues: false
    ruleSelector:
      matchLabels:
        prometheus: kube-prometheus

# Grafana values
grafana:
  enabled: true
  adminPassword: "admin123"  # Change this in production!
  persistence:
    enabled: true
    size: 1Gi
  
  # Pre-configured datasources
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          url: http://prometheus-operated:9090
          isDefault: true

# AlertManager values
alertmanager:
  enabled: true
  
  config:
    global:
      resolve_timeout: 5m
    
    route:
      group_by: ['alertname', 'cluster']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'default-receiver'
    
    receivers:
      - name: 'default-receiver'
        # We'll add Slack integration below

# Prometheus Operator
prometheusOperator:
  enabled: true
```

### 2.5 Install Using Helm

**Windows (PowerShell):**
```powershell
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack `
  -n monitoring `
  -f monitoring/prometheus-values.yaml
```

**Linux/Ubuntu:**
```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f monitoring/prometheus-values.yaml
```

**This will take 2-3 minutes.** You'll see several components being installed:
- Prometheus (metrics database)
- Grafana (visualization)
- AlertManager (alerting)
- Node Exporter (cluster metrics)
- Kube-State-Metrics (Kubernetes metrics)

### 2.6 Verify Installation

**All Platforms (Windows/Linux/Ubuntu):**
```bash
kubectl get pods -n monitoring
```

All pods should show `Running` status:

```
NAME                                                     READY   STATUS
alertmanager-kube-prometheus-alertmanager-0              1/1     Running
grafana-xxxxxxxxxxx-xxxxx                                1/1     Running
kube-prometheus-operator-xxxxx-xxxxx                     1/1     Running
kube-state-metrics-xxxxx-xxxxx                           1/1     Running
node-exporter-xxxxx                                      1/1     Running
prometheus-kube-prometheus-prometheus-0                  1/1     Running
```

## Step 3: Configure Prometheus Scraping

Now we need to tell Prometheus to scrape metrics from your ML model API.

### 3.1 Update Your Deployment Manifest

Prometheus uses Kubernetes ServiceMonitor custom resources to discover scrape targets. We'll add annotations to your deployment.

**File: `k8s/deployment.yaml`**

Update the deployment with Prometheus annotations:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: regression-model-deployment
  namespace: default
  labels:
    app: regression-model
    prometheus: kube-prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: regression-model
  template:
    metadata:
      labels:
        app: regression-model
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: fastapi-server
          image: regression-model-inference:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
              name: http
          env:
            - name: API_HOST
              value: "0.0.0.0"
            - name: API_PORT
              value: "5000"
            - name: MODEL_PATH
              value: "/output/modeling/regression_model.pkl"
            - name: FEATURES_PATH
              value: "/output/modeling/feature_names.json"
            - name: METADATA_PATH
              value: "/output/modeling/model_params.json"
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: output-volume
              mountPath: /output
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 5
      volumes:
        - name: output-volume
          hostPath:
            path: /tmp/ml-output
            type: DirectoryOrCreate
```

Key additions:
- **`prometheus.io/scrape: "true"`**: Tells Prometheus to scrape this pod
- **`prometheus.io/port: "5000"`**: Metrics are on port 5000
- **`prometheus.io/path: "/metrics"`**: Metrics are at `/metrics` endpoint
- **`resources`**: CPU and memory limits (important for monitoring)
- **`livenessProbe` and `readinessProbe`**: Health checks

### 3.2 Create ServiceMonitor for Pod Monitoring

Create a file that tells Prometheus exactly which metrics to collect:

**File: `monitoring/servicemonitor.yaml`**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: regression-model
  namespace: default
  labels:
    prometheus: kube-prometheus
spec:
  selector:
    matchLabels:
      app: regression-model
  endpoints:
    - port: http
      interval: 30s
      path: /metrics
```

### 3.3 Create Service for Pod Monitoring

Update your service to expose metrics properly:

**File: `k8s/service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: regression-model-service
  namespace: default
  labels:
    app: regression-model
    prometheus: kube-prometheus
spec:
  type: NodePort
  selector:
    app: regression-model
  ports:
    - port: 5000
      targetPort: 5000
      nodePort: 30080
      name: http
```

### 3.4 Deploy Updated Manifests

**All Platforms (Windows/Linux/Ubuntu):**
```bash
# Update deployment
kubectl apply -f k8s/deployment.yaml

# Apply service
kubectl apply -f k8s/service.yaml

# Create ServiceMonitor
kubectl apply -f monitoring/servicemonitor.yaml
```

Verify:

**All Platforms:**
```bash
kubectl get servicemonitor -n default
```

Expected output:
```
NAME                  AGE
regression-model      2m
```

### 3.5 Verify Prometheus is Scraping

Wait 30-60 seconds for Prometheus to pick up the new target. Then:

**All Platforms (Windows/Linux/Ubuntu):**
```bash
# Forward Prometheus port
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090
```

Visit: http://localhost:9090

Go to **Status → Targets** and look for your `regression-model` endpoint. It should show:
- **State**: UP (green)
- **Labels**: job=regression-model
- **Last Scrape**: A few seconds ago

## Step 4: Access Prometheus and Grafana

### 4.1 Port Forward to Grafana

In a new terminal:

**All Platforms (Windows/Linux/Ubuntu):**
```bash
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80
```

Visit: http://localhost:3000

**Login:**
- Username: `admin`
- Password: `admin123` (from your values.yaml)

### 4.2 Explore Prometheus Datasource

In Grafana:
1. Click the menu (≡) → **Connections → Data sources**
2. You should see **Prometheus** already configured
3. Click **Prometheus** → **Test** (should show green checkmark)

### 4.3 Query Your Model Metrics

Let's verify we're collecting model metrics:

1. Click the menu (≡) → **Explore**
2. Change datasource to **Prometheus**
3. In the query field, type: `model_inference_requests_total`
4. Click **Run**

You should see a line graph showing your inference requests over time. If nothing appears, your model pod might not be receiving traffic. Run a quick test:

**All Platforms:**
```bash
# Port forward to your model service
kubectl port-forward svc/regression-model-service 5000:5000
```

**Windows (PowerShell - in another terminal):**
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/health"
```

**Linux/Ubuntu (in another terminal):**
```bash
curl http://localhost:5000/health
```

## Step 5: Create Custom Dashboards

### 5.1 Create ML Model Metrics Dashboard

In Grafana:

1. Click the menu (≡) → **Dashboards**
2. Click **+ Create** → **New dashboard**
3. Click **+ Add visualization**

**Panel 1: Total Inference Requests**
- Query: `sum(increase(model_inference_requests_total[5m]))`
- Visualization: **Stat**
- Title: "Inference Requests (5 min)"
- **Note:** This sums both successful and failed requests. The `sum()` aggregates the `status` label.

**Panel 2: Request Latency**
- Query: `histogram_quantile(0.95, rate(model_inference_latency_seconds_bucket[5m]))`
- Visualization: **Time series**
- Title: "P95 Latency (seconds)"

**Panel 3: Error Rate**
- Query: `(increase(model_inference_errors_total[5m]) / increase(model_inference_requests_total[5m])) * 100`
- Visualization: **Gauge**
- Title: "Error Rate (%)"
- **Note:** This metric only appears after errors occur. If no errors have happened, it won't show data. Use the traffic generator with intentional errors or leave this panel empty until errors occur.

**Panel 4: Throughput (Custom)**
- Query: `sum(rate(model_inference_requests_total[1m])) * 60`
- Visualization: **Time series**
- Title: "Predictions/Second"
- **Note:** This is a custom metric derived from request rate: converts per-second rate to per-minute count by multiplying by 60. More accurate than gauge-based throughput.

### 5.2 Create Cluster Health Dashboard

In Grafana:

**Panel 1: Pod CPU Usage**
- Query: `sum(rate(container_cpu_usage_seconds_total{pod=~"regression.*"}[5m])) by (pod)`
- Visualization: **Time series**

**Panel 2: Pod Memory Usage**
- Query: `sum(container_memory_usage_bytes{pod=~"regression.*"}) by (pod) / 1024 / 1024`
- Visualization: **Time series**
- Unit: MB

**Panel 3: Node Disk Usage**
- Query: `max(node_filesystem_size_bytes{device!~"tmpfs|loop.*"} - node_filesystem_avail_bytes) / max(node_filesystem_size_bytes{device!~"tmpfs|loop.*"}) * 100`
- Visualization: **Gauge**
- Unit: %
- **Note:** Shows maximum disk usage percentage across all filesystems. Highlights the most congested filesystem for quick alerting.

### 5.3 Save Dashboards

- Click **Save** button
- Give it a meaningful name: `ML Model - Inference Metrics`
- It will auto-refresh every 30 seconds by default

## Step 6: Configure Alerting

Alerts notify you when things go wrong. Let's set up some basic alerts.

### 6.1 Create AlertManager Configuration

**File: `monitoring/alertmanager-config.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m

    route:
      group_by: ['alertname', 'job']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'default'

    receivers:
      - name: 'default'
        # For local testing, we'll use webhooks
        webhook_configs:
          - url: http://localhost:5000  # Replace with your webhook URL
```

### 6.2 Create Prometheus Alerting Rules

**File: `monitoring/prometheus-rules.yaml`**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ml-model-alerts
  namespace: default
  labels:
    prometheus: kube-prometheus
spec:
  groups:
    - name: ml-model.rules
      interval: 30s
      rules:
        # Alert if model pod is down
        - alert: MLModelPodDown
          expr: up{job="regression-model"} == 0
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "ML Model Pod is down"
            description: "regression-model pod has been unreachable for 2 minutes"

        # Alert if error rate exceeds 5%
        - alert: HighErrorRate
          expr: |
            (increase(model_inference_errors_total[5m]) / 
             (increase(model_inference_requests_total[5m]) + 1)) > 0.05
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High error rate detected"
            description: "Error rate is above 5% for the last 5 minutes"

        # Alert if P95 latency exceeds 1 second
        - alert: HighLatency
          expr: histogram_quantile(0.95, rate(model_inference_latency_seconds_bucket[5m])) > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High inference latency"
            description: "P95 latency exceeded 1 second"

        # Alert if pod restart count increases
        - alert: PodRestart
          expr: increase(kube_pod_container_status_restarts_total{pod=~"regression.*"}[15m]) > 0
          for: 1m
          labels:
            severity: warning
          annotations:
            summary: "Pod restarted"
            description: "{{ $labels.pod }} has restarted"

        # Alert if CPU usage exceeds 80%
        - alert: HighCPUUsage
          expr: |
            sum(rate(container_cpu_usage_seconds_total{pod=~"regression.*"}[5m])) > 0.8
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High CPU usage"
            description: "CPU usage exceeded 80%"

        # Alert if memory usage exceeds 80% of limit
        - alert: HighMemoryUsage
          expr: |
            sum(container_memory_usage_bytes{pod=~"regression.*"}) / 
            sum(container_spec_memory_limit_bytes{pod=~"regression.*"}) > 0.8
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High memory usage"
            description: "Memory usage exceeded 80% of limit"
```

### 6.3 Apply Alerting Rules

**All Platforms (Windows/Linux/Ubuntu):**
```bash
kubectl apply -f monitoring/prometheus-rules.yaml
```

### 6.4 Verify Alerts in Prometheus

Port forward to Prometheus:

**All Platforms (Windows/Linux/Ubuntu):**
```bash
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090
```

Visit: http://localhost:9090/alerts

You should see your custom alerts listed.

### 6.5 View Alerts in Grafana (Optional)

In Grafana:
1. Click the menu (≡) → **Alerting → Alert rules**
2. You should see all rules from Prometheus

## Troubleshooting

### Issue: Prometheus shows "DOWN" status for my pod

**Cause:** Prometheus can't reach your `/metrics` endpoint.

**Solution:**
1. Verify your pod is running: `kubectl get pods`
2. Check if port-forward works manually:
   
   **All Platforms:**
   ```bash
   kubectl port-forward svc/regression-model-service 5000:5000
   ```
   
   **Windows (PowerShell - in another terminal):**
   ```powershell
   Invoke-WebRequest http://localhost:5000/metrics
   ```
   
   **Linux/Ubuntu (in another terminal):**
   ```bash
   curl http://localhost:5000/metrics
   ```
3. Verify the `/metrics` endpoint returns valid Prometheus format

### Issue: Grafana login fails

**Cause:** Incorrect password in values.yaml.

**Solution:**
```powershell
# Reset to default admin/prom-operator
kubectl exec -it -n monitoring prometheus-kube-prometheus-grafana-xxxxx -- grafana-cli admin reset-admin-password newpassword123
```

### Issue: AlertManager pod is in CrashLoopBackOff

**Cause:** Invalid AlertManager configuration.

**Solution:**

**All Platforms (Windows/Linux/Ubuntu):**
```bash
# Check logs
kubectl logs -n monitoring alertmanager-kube-prometheus-alertmanager-0

# Fix the configuration and reapply
kubectl apply -f monitoring/prometheus-rules.yaml
```

### Issue: High memory usage from Prometheus

**Cause:** 24-hour retention with lots of metrics.

**Solution:** In `prometheus-values.yaml`, adjust:
```yaml
prometheus:
  prometheusSpec:
    retention: 6h  # Reduce from 24h to 6h
    storageSpec:
      volumeClaimTemplate:
        spec:
          resources:
            requests:
              storage: 2Gi  # Reduce from 5Gi
```

Then upgrade:

**Windows (PowerShell):**
```powershell
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack `
  -n monitoring `
  -f monitoring/prometheus-values.yaml
```

**Linux/Ubuntu:**
```bash
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f monitoring/prometheus-values.yaml
```

## Next Steps

### Short-term

1. **Set up Slack alerting** (see [Slack Integration](#slack-integration) below)
2. **Create more dashboards** for your team's needs
3. **Fine-tune alert thresholds** based on your model's behavior

### Medium-term

4. **Integrate with your CI/CD pipeline** to automatically deploy with monitoring enabled
5. **Add custom metrics** specific to your use case (model accuracy, data drift, etc.)
6. **Document alert runbooks** - what to do when alerts fire

### Long-term

7. **Plan logging stack** (EFK/Loki) - see `EFK_LOKI_FUTURE_GUIDE.md` for details
8. **Set up log aggregation** to correlate logs with metrics
9. **Deploy to EKS** with managed Prometheus (Amazon Managed Service for Prometheus)

### Slack Integration (Optional)

To send alerts to Slack:

1. **Create a Slack webhook:**
   - Go to your Slack workspace → Settings → Apps
   - Search for "Incoming Webhooks"
   - Click Add New → Select a channel → Copy webhook URL

2. **Update AlertManager config:**
   ```yaml
   receivers:
     - name: 'default'
       slack_configs:
         - api_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
           channel: '#alerts'
           title: 'ML Model Alert'
           text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
   ```

3. **Update secret in Kubernetes:**
   ```powershell
   kubectl patch secret alertmanager-kube-prometheus-alertmanager -n monitoring `
     -p '{"data": {"alertmanager.yaml": <base64-encoded-config>}}'
   ```

## Key Metrics to Monitor

For your ML model specifically, watch these:

- **`model_inference_requests_total`**: Total number of predictions made
- **`model_inference_errors_total`**: Failed predictions
- **`model_inference_latency_seconds`**: Request latency in seconds (use `histogram_quantile()` for percentiles)
- **`model_throughput_per_sec`**: Predictions per second (throughput)

Combined with Kubernetes metrics:
- **Pod CPU/Memory**: Is your model consuming too many resources?
- **Pod restarts**: Is your pod stable or crashing frequently?
- **Node disk space**: Will you run out of storage?

## Summary

You now have:

✅ **Prometheus** collecting metrics every 30 seconds
✅ **Grafana** visualizing your data with beautiful dashboards
✅ **AlertManager** ready to notify you when things go wrong
✅ **Custom metrics** from your ML model being tracked
✅ **Kubernetes cluster health** visible at all times

This is production-ready monitoring. When you move to EKS, the same patterns apply - just swap Prometheus for Amazon Managed Prometheus and configure the same Grafana datasource.

---

**Questions?** Check the troubleshooting section or review the official docs:
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- kube-prometheus-stack: https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack