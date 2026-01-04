# PersistentVolumeClaim (PVC) Complete Guide

## Table of Contents
1. [What is a PVC?](#what-is-a-pvc)
2. [Key Concepts](#key-concepts)
3. [How PVCs Work](#how-pvcs-work)
4. [Access Modes](#access-modes)
5. [Storage Classes](#storage-classes)
6. [Example PVC](#example-pvc)
7. [Common Issues & Solutions](#common-issues--solutions)
8. [PVC Lifecycle & Reclaim Policies](#pvc-lifecycle--reclaim-policies)
9. [Best Practices](#best-practices)
10. [Debugging PVC Issues](#debugging-pvc-issues)
11. [Minikube-Specific Notes](#minikube-specific-notes)

---

## What is a PVC?

A **PersistentVolumeClaim (PVC)** is a Kubernetes resource that allows pods to request persistent storage. Think of it as a **"storage voucher"** - pods use PVCs to claim a piece of persistent storage without needing to know the underlying storage infrastructure.

Unlike ephemeral storage (`emptyDir`), PVC data survives:
- Pod restarts
- Node failures (in clustered environments)
- Container crashes
- Scheduled pod evictions

### Key Difference from emptyDir:
```yaml
# ❌ EPHEMERAL - Data lost on pod restart
volumes:
- name: temp
  emptyDir: {}

# ✅ PERSISTENT - Data survives pod restart
volumes:
- name: data
  persistentVolumeClaim:
    claimName: my-pvc
```

---

## Key Concepts

### The Storage Trio:

```
┌──────────────────────────────────────────────────────────┐
│                  KUBERNETES STORAGE STACK                │
└──────────────────────────────────────────────────────────┘

┌─────────────────────┐
│   StorageClass      │  (Defines HOW to provision storage)
│  - provisioner      │  Examples: fast-ssd, standard, slow
│  - parameters       │
└──────────┬──────────┘
           │
           │ triggers automatic provisioning
           ↓
┌─────────────────────────────────────────────────────────┐
│    Dynamic Provisioning (Optional)                      │
│    StorageClass creates PV automatically when PVC made  │
└─────────────────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────┐
│ PersistentVolume    │  (The actual storage resource)
│      (PV)           │  - Cluster-wide resource
│  - Capacity         │  - Created manually OR auto-provisioned
│  - Access Modes     │
│  - Reclaim Policy   │
└──────────┬──────────┘
           │
           │ claims
           ↓
┌─────────────────────────────────────────────────────────┐
│ PersistentVolumeClaim                                   │
│      (PVC)                                              │
│  - Size request                                         │
│  - Access mode request                                  │
│  - StorageClass reference                               │
└──────────┬──────────────────────────────────────────────┘
           │
           │ mounts as volume
           ↓
┌─────────────────────┐
│      Pod            │  (Uses the storage)
│   - Container 1     │  - Mounts PVC at specific path
│   - Container 2     │  - Can read/write data
└─────────────────────┘
```

### 1. **PersistentVolume (PV)** - The Storage

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-001
spec:
  capacity:
    storage: 10Gi                    # Total size available
  accessModes:
    - ReadWriteOnce                  # Access restrictions
  persistentVolumeReclaimPolicy: Retain  # What happens when PVC deleted
  storageClassName: fast-ssd         # Type of storage
  hostPath:                          # Storage backend (Minikube)
    path: /tmp/pv-001
```

**Properties:**
- **Cluster-wide** (not namespaced)
- Exists **independently** of pods
- Can be created **manually** or **automatically** (dynamic provisioning)
- Bound to **ONE PVC** at a time

---

### 2. **PersistentVolumeClaim (PVC)** - The Request

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-storage          # Namespaced resource
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce              # Request this access mode
  resources:
    requests:
      storage: 5Gi               # Request this much storage
  storageClassName: standard     # Request this type
```

**Properties:**
- **Namespaced** (belongs to a specific namespace)
- A **request** for storage
- Binds to a **matching PV** automatically
- Used by **pods** for persistent data

---

### 3. **StorageClass** - The Blueprint

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs    # How to provision (AWS, GCP, etc.)
parameters:
  type: gp3                            # Cloud-specific parameters
  iops: "3000"
  throughput: "125"
allowVolumeExpansion: true             # Can PVC be expanded?
volumeBindingMode: WaitForFirstConsumer # When to provision?
reclaimPolicy: Delete                  # What to do with PV when PVC deleted
```

**Common Provisioners:**
- `kubernetes.io/aws-ebs` - Amazon EBS
- `kubernetes.io/gce-pd` - Google Cloud Persistent Disk
- `csi.digitalocean.com` - DigitalOcean
- `hostpath.csi.k8s.io` - Host machine (dev only)
- `fast-ssd`, `standard` - Minikube defaults

---

## How PVCs Work

### The Full Workflow:

```
Step 1: Create StorageClass
   ↓
Step 2: Create PVC
   ├─→ Kubernetes looks for matching PV or auto-provisions one
   ├─→ PVC enters "Pending" if no PV available
   └─→ PVC binds to PV when match found
   ↓
Step 3: Pod references PVC
   ├─→ Pod uses the PVC in volumeMount
   ├─→ Kubernetes mounts the PV to the container
   └─→ Container can read/write data
   ↓
Step 4: Data Persistence
   ├─→ Pod deleted → Data remains on PV
   ├─→ Pod restarted → Same PV remounted
   └─→ Node fails → PV accessible from other nodes
   ↓
Step 5: Cleanup (Optional)
   ├─→ Delete PVC
   ├─→ Kubernetes's reclaim policy decides PV fate
   └─→ PV deleted OR retained based on policy
```

### Example: Complete Flow

```yaml
# 1. StorageClass (defines storage type)
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/hostpath

# 2. PersistentVolumeClaim (requests storage)
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 20Gi

# 3. Pod (uses the storage)
---
apiVersion: v1
kind: Pod
metadata:
  name: mysql-server
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    volumeMounts:
    - name: data
      mountPath: /var/lib/mysql      # Mount point in container
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: mysql-data          # Reference the PVC
```

---

## Access Modes

Access modes define **how** the volume can be mounted:

### 1. **ReadWriteOnce (RWO)** ⭐ Most Common
```yaml
accessModes:
  - ReadWriteOnce
```
- **Read & Write** allowed
- **Single node only** can mount at a time
- Default for most storage (EBS, PD, etc.)
- Perfect for: Databases, single-pod applications
- Example: Grafana, MySQL, PostgreSQL

### 2. **ReadOnlyMany (ROX)**
```yaml
accessModes:
  - ReadOnlyMany
```
- **Read only**
- **Multiple nodes** can mount simultaneously
- Good for: Shared configuration, static assets
- Example: Shared config files, media content

### 3. **ReadWriteMany (RWX)**
```yaml
accessModes:
  - ReadWriteMany
```
- **Read & Write** allowed
- **Multiple nodes** can mount simultaneously
- Requires special storage: NFS, Ceph, GlusterFS
- Good for: Shared data between pods, multi-pod applications
- Example: Distributed databases, shared cache

### 4. **ReadWriteOncePod (RWOP)** 🆕 v1.22+
```yaml
accessModes:
  - ReadWriteOncePod
```
- **Read & Write** allowed
- **Single Pod** only can access (prevents multiple replicas)
- More restrictive than RWO
- Good for: StatefulSets with strict isolation

### Compatibility Matrix:

| StorageClass | RWO | ROX | RWX | RWOP |
|---|---|---|---|---|
| AWS EBS | ✅ | ❌ | ❌ | ✅ |
| Google PD | ✅ | ❌ | ❌ | ✅ |
| NFS | ✅ | ✅ | ✅ | ✅ |
| Azure Disk | ✅ | ❌ | ❌ | ✅ |
| Ceph | ✅ | ✅ | ✅ | ✅ |
| HostPath | ✅ | ❌ | ❌ | ❌ |

---

## Storage Classes

StorageClasses automate PV provisioning:

### Default StorageClass (Minikube):
```bash
$ kubectl get storageclass
NAME                 PROVISIONER        RECLAIMPOLICY   VOLUMEBINDINGMODE
standard (default)   k8s.io/minikube    Delete          Immediate
```

### Creating a Custom StorageClass:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3              # EBS volume type
  iops: "3000"           # Input/Output operations per second
  throughput: "125"      # MB/s
  encrypted: "true"      # Enable encryption
allowVolumeExpansion: true                    # Allow PVC resize
reclaimPolicy: Delete                         # Delete PV when PVC deleted
volumeBindingMode: WaitForFirstConsumer       # Bind when pod scheduled
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: slow-hdd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: st1             # Throughput optimized HDD
  encrypted: "false"
reclaimPolicy: Retain                         # Keep PV when PVC deleted
```

### Volume Binding Modes:

**Immediate (default):**
- PVC binds to PV **immediately** when created
- Good for local volumes
```yaml
volumeBindingMode: Immediate
```

**WaitForFirstConsumer:**
- PVC waits until **pod** is scheduled
- Pod topology requirements considered
- Better for multi-zone clusters
```yaml
volumeBindingMode: WaitForFirstConsumer
```

---

## Example PVC

### Basic Grafana PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-storage
  namespace: monitoring
  labels:
    app: grafana
spec:
  accessModes:
    - ReadWriteOnce              # Single-pod access
  storageClassName: standard     # Use default storage
  resources:
    requests:
      storage: 5Gi              # 5 GigaBytes
```

### Advanced Database PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
  namespace: databases
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd    # Fast SSD storage
  resources:
    requests:
      storage: 100Gi            # 100 GigaBytes
  selector:                      # Target specific PV
    matchLabels:
      tier: premium
      zone: us-east-1a
```

### Using PVC in Pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: grafana-pod
  namespace: monitoring
spec:
  containers:
  - name: grafana
    image: grafana/grafana:latest
    ports:
    - containerPort: 3000
    volumeMounts:
    - name: grafana-storage
      mountPath: /var/lib/grafana    # Where to mount in container
      readOnly: false
    env:
    - name: GF_INSTALL_PLUGINS
      value: "grafana-piechart-panel"
  
  # Security context (prevents permission errors)
  securityContext:
    fsGroup: 472                      # Grafana's GID
    runAsUser: 472                    # Grafana's UID
    runAsNonRoot: true
  
  # Define the volume
  volumes:
  - name: grafana-storage
    persistentVolumeClaim:
      claimName: grafana-storage      # Reference PVC
```

---

## Common Issues & Solutions

### Issue 1: Permission Denied Errors ⚠️ (Your Grafana Issue)

**Error Messages:**
```
chown: /var/lib/grafana/csv: Permission denied
chown: /var/lib/grafana/png: Permission denied
init-chown-data: error
```

**Root Causes:**
- Volume owned by `root`, container runs as non-root (e.g., UID 472)
- SELinux or file system permissions mismatch
- Previous pod left corrupted permissions on the PVC

**Solution 1: Use fsGroup (Recommended)**
```yaml
spec:
  securityContext:
    fsGroup: 472              # Grafana UID/GID
    runAsUser: 472
    runAsNonRoot: true
  containers:
  - name: grafana
    image: grafana/grafana
    volumeMounts:
    - name: storage
      mountPath: /var/lib/grafana
```

**How fsGroup Works:**
- Kubernetes automatically changes directory ownership to `fsGroup`
- All processes in pod can read/write (if permissions allow)
- Applies to ALL volumes in the pod

**Solution 2: Init Container (What Grafana Default Does)**
```yaml
spec:
  initContainers:
  - name: init-chown-data
    image: busybox:latest
    command:
    - chown
    - -R
    - "472:472"              # chown UID:GID path
    - /var/lib/grafana
    volumeMounts:
    - name: storage
      mountPath: /var/lib/grafana
  
  containers:
  - name: grafana
    image: grafana/grafana
    volumeMounts:
    - name: storage
      mountPath: /var/lib/grafana
  
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: grafana-pvc
```

**Solution 3: Disable Persistence (Dev Only)**
```yaml
# In Helm values
persistence:
  enabled: false    # Use emptyDir instead
```

**Solution 4: Clean Up PVC**
```bash
# Force delete stuck pods
kubectl delete pod <pod-name> -n <ns> --force --grace-period=0

# Delete corrupted PVC
kubectl delete pvc <pvc-name> -n <ns>

# New pod gets fresh PVC with correct permissions
```

---

### Issue 2: PVC Stuck in Pending

**Status:**
```bash
$ kubectl get pvc
NAME              STATUS    VOLUME   CAPACITY
grafana-pvc       Pending   <none>   
```

**Root Causes:**
- No PV available with matching requirements
- StorageClass doesn't exist
- Storage quota exceeded
- Insufficient nodes with capacity

**Debug:**
```bash
kubectl describe pvc grafana-pvc
# Look for "Events" section
```

**Solutions:**

**A) Create Manual PV:**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-grafana
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: standard
  hostPath:
    path: /tmp/grafana-data
```

**B) Check StorageClass:**
```bash
kubectl get storageclass
# If none exist, create one or use default
```

**C) Check Node Capacity:**
```bash
kubectl describe nodes
# Look for "Allocatable" resources
```

---

### Issue 3: PVC Stuck in Terminating

**Status:**
```bash
$ kubectl get pvc
NAME          STATUS        VOLUME   
grafana-pvc   Terminating   pvc-xxxx
```

**Root Causes:**
- Pod still using the PVC
- Finalizers preventing deletion
- PV failed to reclaim

**Solution 1: Delete Pod First**
```bash
# Find pod using PVC
kubectl get pod -o json | jq '.items[] | select(.spec.volumes[]?.persistentVolumeClaim.claimName=="grafana-pvc")'

# Delete the pod
kubectl delete pod <pod-name> --force --grace-period=0

# PVC will automatically delete
```

**Solution 2: Remove Finalizers (Last Resort)**
```bash
kubectl patch pvc grafana-pvc -p '{"metadata":{"finalizers":null}}'
```

---

### Issue 4: Data Loss After Pod Restart

**Problem:** Data disappears when pod restarts

**Root Cause:** Using `emptyDir` instead of PVC

```yaml
# ❌ WRONG - Data lost on restart
volumes:
- name: data
  emptyDir: {}

# ✅ CORRECT - Data persists
volumes:
- name: data
  persistentVolumeClaim:
    claimName: my-pvc
```

---

### Issue 5: PVC Cannot Expand

**Error:**
```
error expanding PVC: not supported by provisioner
```

**Solution:**
Ensure `allowVolumeExpansion: true` in StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable
provisioner: kubernetes.io/hostpath
allowVolumeExpansion: true    # ← Add this
```

Then expand the PVC:
```bash
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'
```

---

## PVC Lifecycle & Reclaim Policies

### PVC States:

```
PENDING → BOUND → ACTIVE → RELEASED → (depends on reclaim policy)
```

1. **Pending**: No PV available
2. **Bound**: PVC bound to PV, ready to use
3. **Active**: Pod mounted and using it
4. **Released**: PVC deleted but PV not yet reclaimed

### Reclaim Policies (What happens when PVC deleted):

#### 1. **Delete** (Default for dynamic storage)
```yaml
reclaimPolicy: Delete
```
- PV is **deleted immediately**
- Underlying storage is **destroyed**
- Use when: Temporary data, dev environments
- ⚠️ Data is **GONE PERMANENTLY**

#### 2. **Retain** (Recommended for production)
```yaml
reclaimPolicy: Retain
```
- PV becomes "Released"
- PV **NOT deleted**, data **preserved**
- Manual cleanup required
- Use when: Production databases, critical data
- ✅ Data can be recovered if needed

#### 3. **Recycle** (Deprecated)
```yaml
reclaimPolicy: Recycle
```
- PV scrubbed and made available
- Don't use - deprecated in v1.23

### Reclaim Policy Comparison:

| Policy | Data Deleted? | PV Deleted? | Use Case |
|---|---|---|---|
| Delete | ✅ Yes | ✅ Yes | Dev/Test |
| Retain | ❌ No | ❌ No | Production |
| Recycle | ✅ Yes | ❌ No | Legacy |

### Example: Production-Safe Setup

```yaml
# Use Retain for safety
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: prod-safe
provisioner: kubernetes.io/aws-ebs
reclaimPolicy: Retain              # Keep data
volumeBindingMode: WaitForFirstConsumer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: prod-safe
  resources:
    requests:
      storage: 100Gi
```

---

## Best Practices

### 1. **Right-Size Your Storage**

```yaml
# ❌ WRONG - Over-allocate
storage: 1000Gi  # When you only need 10Gi

# ✅ CORRECT - Right size
storage: 10Gi    # Realistic requirement
```

Benefits:
- Cost savings
- Faster provisioning
- Better cluster utilization
- Easier migrations

### 2. **Use Storage Classes Properly**

```yaml
# ❌ DON'T hardcode PV names
persistentVolumeClaim:
  claimName: prod-pv-001

# ✅ DO use StorageClass for automation
storageClassName: fast-ssd
```

### 3. **Set Security Context**

Prevent permission errors:

```yaml
spec:
  securityContext:
    fsGroup: 1000          # GID for volume ownership
    runAsUser: 1000        # UID for process
    runAsNonRoot: true
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: data
      mountPath: /data
```

### 4. **Monitor PVC Usage**

```bash
# Check usage in pod
kubectl exec <pod> -- du -sh /mount/path

# Monitor multiple pods
for pod in $(kubectl get pod -o name); do
  echo "Pod: $pod"
  kubectl exec $pod -- df -h | grep /data
done
```

### 5. **Backup Critical Data**

**Using Velero (Kubernetes backup tool):**
```bash
velero backup create my-backup --include-namespaces prod
velero backup logs my-backup  # Monitor progress
velero restore create --from-backup my-backup
```

**Manual backup:**
```bash
kubectl exec <pod> -- tar czf - /data > backup.tar.gz
```

### 6. **Dev vs Prod Strategy**

**Development:**
```yaml
persistence:
  enabled: false           # Use emptyDir
# OR
storageClassName: standard
reclaimPolicy: Delete      # Auto-cleanup
```

**Production:**
```yaml
persistence:
  enabled: true
storageClassName: fast-ssd
reclaimPolicy: Retain      # Keep data
# + backup solution (Velero)
# + monitoring
# + redundancy
```

### 7. **Use StatefulSets for Stateful Apps**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  
  # Auto-create PVC per replica
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```

### 8. **Document Storage Requirements**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: storage-requirements
  namespace: prod
data:
  requirements: |
    Application: MySQL Production
    PVC Name: mysql-prod-data
    Size: 100Gi
    AccessMode: ReadWriteOnce
    StorageClass: aws-ebs-gp3
    ReclamPolicy: Retain
    BackupSchedule: daily @ 2AM UTC
    RetentionDays: 30
    RestoreRTO: 2 hours
    RestorRPO: 15 minutes
```

---

## Debugging PVC Issues

### Check PVC Status

```bash
# List all PVCs
kubectl get pvc -n <namespace>

# Detailed view
kubectl describe pvc <pvc-name> -n <namespace>

# Watch PVC status changes
kubectl get pvc -n <namespace> --watch
```

### Check PV Status

```bash
# List all PVs
kubectl get pv

# Describe specific PV
kubectl describe pv <pv-name>

# Show binding information
kubectl get pvc,pv --all-namespaces
```

### Find What's Using PVC

```bash
# Find pods using specific PVC
kubectl get pods -n <namespace> -o json | \
  jq '.items[] | select(.spec.volumes[]?.persistentVolumeClaim.claimName=="<pvc-name>") | .metadata.name'

# Or use a script
for pod in $(kubectl get pod -n <namespace> -o name); do
  kubectl describe $pod -n <namespace> | grep -q "pvc-name" && echo $pod
done
```

### Check Events

```bash
# Recent events in namespace
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Watch events in real-time
kubectl get events -n <namespace> --watch

# Filter by PVC
kubectl get events -n <namespace> | grep <pvc-name>
```

### Access Volume Data

```bash
# If pod is running, exec into it
kubectl exec -it <pod> -n <namespace> -- bash
ls -la /mount/path
du -sh /mount/path

# Check permissions
ls -l /mount/path
stat /mount/path
```

### Check Node Storage

```bash
# Describe node (includes allocatable storage)
kubectl describe node <node-name>

# Check disk usage on node
kubectl debug node/<node-name> -it --image=ubuntu
df -h
ls -la /var/lib/kubelet/pods/

# From Minikube VM
minikube ssh
df -h
ls -la /tmp/hostpath-provisioner/
```

### StorageClass Debugging

```bash
# Check available StorageClasses
kubectl get storageclass

# Show default StorageClass
kubectl get storageclass -o wide

# Describe StorageClass details
kubectl describe sc <storage-class-name>

# Test provisioning
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: <your-class>
  resources:
    requests:
      storage: 1Gi
EOF

kubectl describe pvc test-pvc
kubectl delete pvc test-pvc
```

### Common Debug Scenarios

**Scenario 1: PVC Pending**
```bash
kubectl describe pvc my-pvc
# Check Events section for reason
# Common: "no persistent volumes available", "storageclass not found"

kubectl get pv              # Check if PVs exist
kubectl get sc              # Check StorageClasses
```

**Scenario 2: PVC Bound but Pod Can't Access**
```bash
kubectl logs <pod> -c <container>
# Look for mount-related errors

kubectl exec <pod> -- mount | grep /mount/path
# Should show the PVC mounted
```

**Scenario 3: Permission Denied in Pod**
```bash
kubectl exec <pod> -- ls -la /mount/path
# Check ownership and permissions

kubectl get pod <pod> -o yaml | grep -A 20 securityContext
# Check if fsGroup is set
```

**Scenario 4: Disk Space Issue**
```bash
kubectl exec <pod> -- df -h
# Check free space

kubectl exec <pod> -- du -sh /mount/path/*
# See what's using space
```

---

## Minikube-Specific Notes

### Minikube Storage Architecture

```
Your Windows Machine
    ↓
Hyper-V/VirtualBox VM (Minikube)
    ↓
├── /tmp/hostpath-provisioner/     ← PV data stored here
├── pvc-xxxxx/
├── pvc-yyyyy/
└── pvc-zzzzz/
```

### Default StorageClass

```bash
$ kubectl get sc
NAME                 PROVISIONER        RECLAIMPOLICY
standard (default)   k8s.io/minikube    Delete
```

Uses `hostPath` provisioner:
- Data stored on Minikube VM filesystem
- Single-node only (no multi-node support)
- Suitable for development only

### Viewing PV Data on Minikube

```bash
# SSH into Minikube
minikube ssh

# Navigate to PV storage
cd /tmp/hostpath-provisioner/
ls -la
# You'll see directories like: pvc-61202842-e8fd-4ba6-8b8a-e9089ceed7fe

# Check disk usage
df -h
du -sh /tmp/hostpath-provisioner/*
```

### PV Survival

**Survives:**
- ✅ Pod restart
- ✅ Pod deletion
- ✅ Deployment scaling
- ✅ Node restart (single node)

**Does NOT survive:**
- ❌ `minikube delete` (VM is destroyed)
- ❌ `minikube stop` (data usually survives, but not guaranteed)
- ❌ Full Minikube reinstall

### Backup Strategy for Minikube

```bash
# Backup Minikube PV data
minikube ssh "tar czf - /tmp/hostpath-provisioner/" > minikube-pvc-backup.tar.gz

# Restore after minikube delete/reinstall
minikube start
minikube ssh "sudo tar xzf -" < minikube-pvc-backup.tar.gz
```

### Limitations

| Feature | Minikube | Production |
|---|---|---|
| Access Modes | RWO only | RWO, ROX, RWX |
| Reclaim Policy | Delete, Retain | Delete, Retain |
| Expansion | Supported | Depends on storage |
| Backup Tools | Manual | Velero, native tools |
| HA/Redundancy | No | Yes |
| Performance | File-based | Native storage |

---

## Real-World Example: Production MySQL Setup

```yaml
# 1. StorageClass (use fast SSD)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: mysql-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
allowVolumeExpansion: true
reclaimPolicy: Retain              # ← IMPORTANT: Keep data!
volumeBindingMode: WaitForFirstConsumer

---
# 2. Persistent Volume Claim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
  namespace: databases
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: mysql-ssd
  resources:
    requests:
      storage: 100Gi

---
# 3. StatefulSet with MySQL
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: databases
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      securityContext:
        fsGroup: 999              # MySQL's GID
        runAsUser: 999            # MySQL's UID
        runAsNonRoot: true
      
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: root-password
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
      
      # Liveness and readiness probes
      livenessProbe:
        exec:
          command:
          - mysqladmin
          - ping
        initialDelaySeconds: 30
        periodSeconds: 10
      
      readinessProbe:
        exec:
          command:
          - mysql
          - -h
          - localhost
          - -e
          - "SELECT 1"
        initialDelaySeconds: 10
        periodSeconds: 5
  
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: mysql-ssd
      resources:
        requests:
          storage: 100Gi
```

### With Backup Solution:

```bash
# Install Velero
velero install --provider aws \
  --bucket velero-backups \
  --secret-file ./credentials-velero

# Schedule automatic backups
velero schedule create mysql-daily \
  --schedule "0 2 * * *" \
  --include-namespaces databases \
  --include-resources statefulsets,persistentvolumeclaims

# Restore from backup
velero restore create --from-backup mysql-backup-20250104
```

---

## Summary

| Concept | Purpose |
|---|---|
| **PVC** | Request for persistent storage |
| **PV** | Actual storage resource |
| **StorageClass** | Blueprint for automatic provisioning |
| **Access Mode** | How many nodes can mount the volume |
| **Reclaim Policy** | What happens when PVC is deleted |
| **fsGroup** | Security context for file ownership |
| **Velero** | Backup and restore solution |

### Quick Reference Checklist:

- [ ] Choose right storage class for use case
- [ ] Set fsGroup in securityContext to avoid permission issues
- [ ] Use Retain reclaim policy for production
- [ ] Set up backups for critical data
- [ ] Monitor PVC usage
- [ ] Size PVC appropriately (not over-allocate)
- [ ] Use StatefulSets for stateful applications
- [ ] Test restore procedures regularly
- [ ] Document storage requirements
- [ ] Use ReadOnlyMany when possible for safety

---

**Need Help?** Common commands:
```bash
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc-name> -n <namespace>
kubectl get pv
kubectl get storageclass
kubectl logs <pod> -n <namespace>
kubectl exec -it <pod> -n <namespace> -- bash
```