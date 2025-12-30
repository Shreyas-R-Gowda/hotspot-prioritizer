---
description: Fix Docker Connectivity and Build Issues
---

# Fix Docker Issues

If you are experiencing `DeadlineExceeded` or network timeouts when building Docker images, follow these steps.

## 1. Check Network Connectivity
Ensure you have a stable internet connection.
```bash
ping -c 3 google.com
```

## 2. Restart Docker Desktop
The most common fix is to simply restart the Docker daemon.
1. Click the Docker icon in your menu bar.
2. Select **Quit Docker Desktop**.
3. Open Docker Desktop again from your Applications.
4. Wait for the status to turn green/running.

## 3. Prune Docker Cache (Optional)
Sometimes the builder cache gets corrupted.
> [!WARNING]
> This will remove all unused build cache.
```bash
docker builder prune -f
```

## 4. Increase Timeout
If your network is slow, increase the timeout for Compose.
```bash
export COMPOSE_HTTP_TIMEOUT=200
export DOCKER_CLIENT_TIMEOUT=200
```

## 5. Retry Build
Once restarted, try building again:
```bash
docker-compose up --build
```
