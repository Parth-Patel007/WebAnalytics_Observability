# Observable Orders - Web Observability

This project is a hands-on, beginner-friendly environment for learning **modern observability** using:

- **FastAPI (Python)**
- **OpenTelemetry**
- **Prometheus** (metrics)
- **Loki** (logs)
- **Tempo** (traces)
- **Grafana** (visualization)

It simulates a tiny “orders system” with real metrics, logs, traces, and a built-in **load generator UI** so you can experiment and instantly see everything update live in Grafana.(after running the container, initially it will take around 2-3 mins for all the services to start and collect data)

---

## Prerequisites

- **Docker & Docker Compose** installed and running
- Navigate to this directory from the repository root:
  ```bash
  cd "WAO demo project"
  ```

## How to Run the Project

1. Make sure **Docker Desktop** is running.
2. Start everything:

```bash
docker compose up --build
```

3. Access the system:

| Component                           | URL                                                              |
| ----------------------------------- | ---------------------------------------------------------------- |
| **Load Simulator UI**               | [http://localhost:8000/simulate](http://localhost:8000/simulate) |
| **API Documentation (Swagger UI)**  | [http://localhost:8000/docs](http://localhost:8000/docs)         |
| **Prometheus**                      | [http://localhost:9090](http://localhost:9090)                   |
| **Grafana**                         | [http://localhost:3000](http://localhost:3000)                   |
| **Logs & Traces (Grafana Explore)** | [http://localhost:3000/explore](http://localhost:3000/explore)   |

Grafana Login:

```
Username: admin
Password: admin
```

Dashboards and data sources load automatically.
On startup, a small sample load runs.

---

## What’s Inside the System

### **API Service (FastAPI)**

* Creates orders (sometimes fail)
* Reprocesses orders via worker service
* Emits **metrics, logs, and traces** via OpenTelemetry
* Hosts the **Load Simulator UI** at `/simulate`

### **Worker Service**

* Processes orders with random delays + failures
* Also fully instrumented with OpenTelemetry

### **OpenTelemetry Collector**

Acts as the observability “hub”:

* Receives telemetry from services
* Exports:

  * Metrics → **Prometheus**
  * Logs → **Loki**
  * Traces → **Tempo**

Prometheus scrapes:

```
http://otel-collector:9464/metrics
```

### **Prometheus**

Scrapes metrics from the OTel Collector
Provides time-series data for Grafana.

### **Loki**

Stores structured logs from both services
Searchable through Grafana using **LogQL**.

### **Tempo**

Stores distributed traces showing the full request path.

### **Grafana**

* Preconfigured data sources
* Auto-loaded dashboard
* Unified UI for metrics, logs, and traces

---

## Load Simulation UI

Visit:

```
http://localhost:8000/simulate
```

You can configure:

* Number of orders
* Percent to reprocess
* Duration in seconds

Click **Run Simulation** and the system will:

* Generate traffic in the background
* Show a countdown
* Redirect back once the simulation finishes

Metrics, logs, and traces appear instantly in Grafana.

---

## Sample PromQL Queries (Metrics)

**Orders per second**

```promql
sum(rate(orders_created_total[1m]))
```

**Failed orders per second**

```promql
sum(rate(orders_failed_total[5m]))
```

**Error rate**

```promql
100 * (
  sum(rate(orders_failed_total[15m])) /
  sum(rate(orders_created_total[15m]))
)
```

**Order value (P90)**

```promql
histogram_quantile(
  0.9,
  sum(rate(order_value_usd_bucket[5m])) by (le)
)
```

**Worker processed per second**

```promql
sum(rate(orders_processed_total[1m]))
```

---

## Sample LogQL Queries (Logs)

**All API logs**

```logql
{service_name="api-service"}
```

**API failures**

```logql
{service_name="api-service"} |= "failed"
```

**Worker failures**

```logql
{service_name="worker-service"} |= "failed"
```

**Count worker errors**

```logql
count_over_time(({service_name="worker-service"} |= "failed")[5m])
```

---

## Sample Tempo Searches (Traces)

In Grafana → **Explore → Tempo**

**API traces**

```
service.name = "api-service"
```

**Worker traces**

```
service.name = "worker-service"
```

**Search using a trace_id**

* Copy a `trace_id` from a Loki log line
* Paste directly into Tempo search

