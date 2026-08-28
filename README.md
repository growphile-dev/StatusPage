
# 🚀 DevOps Infrastructure Status Engine

A lightweight, containerized SaaS monitoring dashboard engineered to deliver real-time infrastructure visibility, dynamic database health metrics, system performance visualizations, and interactive service monitors.

---

## 👨‍💻 Project Details & Credits
* **Engineered by:** Zeeshan Riaz
* **GitHub Profile:** [`growphile-dev`](https://github.com/growphile-dev)
* **Repository:** `growphile-dev/statuspage`
* **Live Node:** Oracle Cloud Infrastructure (OCI)

---

## 🏗️ Architecture & Technology Stack

```text
                        [ Client / Browser ]
                                 │
                         Port 80 │ (HTTP Ingress)
                                 ▼
                      ┌─────────────────────┐
                      │    Nginx Gateway    │ (Host Reverse Proxy)
                      └──────────┬──────────┘
                                 │
                       Port 5001 │ (Local Container Port)
                                 ▼
                     ┌───────────────────────┐
                     │  StatusPage Container │ (Python 3.11 / Flask Engine)
                     └──────────┬────────────┘
                                 │
                       Port 5433 │ (Internal Container Network)
                                 ▼
                     ┌───────────────────────┐
                     │  PostgreSQL Container │ (PostgreSQL 15 Database)
                     └───────────────────────┘
