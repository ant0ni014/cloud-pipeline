# Continuous Cloud Deployment Pipeline & ECS Test Suite

Ein durchgängiges DevOps- & Cloud-Projekt zur automatisierten Bereitstellung einer Webanwendung und Test-Suite auf der Open Telekom Cloud (OTC) / AWS ECS.

![Status Badge](https://img.shields.io/badge/Status-Healthy-emerald)
![Tech Stack Badge](https://img.shields.io/badge/Stack-Python%20%7C%20Docker%20%7C%20Tailwind-blue)
![Cloud Target Badge](https://img.shields.io/badge/Cloud-T%20Cloud%20Public%20%28ECS%29-magenta)

## Tech Stack
* **Language:** Python 3.9 (Standard Library `http.server`)
* **Containerization:** Docker (mit Container Healthcheck)
* **Frontend:** Clean Responsive UI (Tailwind CSS CDN, Live JavaScript Diagnostics)
* **CI/CD:** GitHub Actions
* **Cloud Plattform:** Open Telekom Cloud (OTC) / AWS ECS (Elastic Container Service)

---

## REST API & Diagnostic Endpoints

Diese Anwendung stellt verschiedene Endpoints speziell für Cloud- & ECS-Tests bereit:

| Methode | Endpoint | Beschreibung | Hauptsächlicher Testzweck |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Interaktives Web-Dashboard | Visualisierung & Manuelle Tests |
| `GET` | `/health` | JSON Health Check Status | ECS Target Group & ALB Health Checks |
| `GET` | `/api/metrics` | System- & Container-Metriken | Monitoring & Diagnostic-Logs |
| `GET` | `/api/load` | Simuliert CPU-Stresstest (3s) | ECS Target Tracking Auto-Scaling |
| `GET` | `/api/error` | Simuliert HTTP 500 Fehler | ALB Failover & Task Resiliency |
| `GET` | `/api/env` | Auslesen von Environment Variables | ECS Task Definition Parameter Audit |
| `GET` | `/api/headers` | Request-Header Inspector | Reverse Proxy, SSL & `X-Forwarded-For` |

---

## Lokale Ausführung mit Docker

### 1. Docker Image bauen
```bash
docker build -t otc-cloud-app .
```

### 2. Container starten
```bash
docker run -d -p 8080:8080 --name cloud-dashboard otc-cloud-app
```

### 3. Dashboard im Browser aufrufen
Öffne [http://localhost:8080](http://localhost:8080) in deinem Browser.

---

## Deployment auf ECS (Elastic Container Service)

1. Image in die Container Registry pushen (z. B. OTC SWR / AWS ECR).
2. Task Definition erstellen:
   - Port Mapping: `8080:8080`
   - Health Check Path: `/health`
3. ECS Service erstellen und an einen Application Load Balancer (ALB) koppeln.
4. Den Stresstest (`/api/load`) nutzen, um Alarmierungsregeln in CloudWatch / OTC zu überprüfen.

---

## Author

Projekt von **Antonio** | GitHub: [ant0ni014](https://github.com/ant0ni014)