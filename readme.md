# Microservices Observability Platform

This project is a simple observability setup built around a microservices architecture.  
It helps in tracking logs, metrics, and request flows across multiple services so that debugging and monitoring become easier in a distributed system.

---

## Why this project?

When you work with multiple services, things break in different places at different times.  
Without proper visibility, figuring out the root cause takes a lot of time.

This setup tries to solve that by bringing everything into one place:
- metrics
- logs
- service communication tracking

---

## What it includes

- Multiple microservices (user, order, payment services)
- Centralized metrics collection
- Logging aggregation
- Dashboard visualization
- Basic tracing between services

---

## Tech Stack

- Docker
- Prometheus
- Grafana
- Loki / ELK (for logs)
- Jaeger / OpenTelemetry (for tracing)
- Node.js / Python (for microservices)
- AWS EC2 (for deployment)

---

## Architecture

Microservices generate logs and metrics  
↓  
Prometheus collects metrics  
↓  
Grafana displays dashboards  

Logs flow into Loki / ELK  
Tracing data goes through Jaeger

---

## Project Structure
