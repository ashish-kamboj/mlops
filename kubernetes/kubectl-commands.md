| **No.** | **Command / Technique**                                               | **Description**                                                                        |
| ------: | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
|       1 | `kubectl get pods`                                                    | List pods in the default namespace                                                     |
|       2 | `kubectl logs <pod-name>`                                             | Fetch stdout/stderr logs from the pod’s primary (or only) container                    |
|         | *(with namespace)* `kubectl logs mypod -n production`                 | Fetch logs from a pod in a specific namespace                                          |
|       3 | `kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'` | List containers in a pod                                                               |
|       4 | `kubectl logs <pod-name> -c <container-name>`                         | Get container logs                                                                     |
|       5 | `kubectl logs -f <pod-name>`                                          | Stream logs in real-time                                                               |
|         | *(follow container)* `kubectl logs -f <pod-name> -c <container-name>` | Stream logs from a specific container                                                  |
|       6 | `kubectl logs --tail=50 <pod-name>`                                   | Tail recent 50 log lines                                                               |
|       7 | `kubectl logs --since=1h <pod-name>`                                  | Show logs from the last hour                                                           |
|         | `kubectl logs --since-time="2025-12-29T12:00:00Z" <pod-name>`         | Show logs since a specific timestamp                                                   |
|       8 | `kubectl logs --previous <pod-name>`                                  | Show logs from previous container instance (after restart/crash)                       |
|       9 | `kubectl logs --limit-bytes=1000 <pod-name>`                          | Limit log output by bytes                                                              |
|      10 | `kubectl logs --timestamps <pod-name>`                                | Add timestamps to log lines                                                            |
|      11 | `kubectl logs <pod-name> > pod-logs.txt`                              | Save logs to a local file                                                              |
|      12 | `kubectl describe <resource> <name>`                                  | View detailed status, events, and related objects (e.g., `kubectl describe pod mypod`) |
|      13 | `kubectl exec -it <pod-name> -- /bin/sh`                              | Open an interactive shell inside a pod’s main container                                |
|      14 | **Common exec scenarios:**                                            |                                                                                        |
|         | `kubectl exec -it <pod-name> -c <container> -- /bin/bash`             | Exec into a specific container                                                         |
|         | `kubectl exec <pod-name> -- ls /app`                                  | Run a one-off command inside a container                                               |
|         | `kubectl cp <pod-name>:/path/localfile ./localfile`                   | Copy files between pod and local machine                                               |
|         | *(Tip)* Combine `describe` with `exec`, and use `-n <namespace>`      | First identify issues, then exec in the right namespace                                |