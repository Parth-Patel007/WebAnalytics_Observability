import logging
import os
import random
import time
from typing import Dict

import requests
from fastapi import FastAPI, HTTPException
import uvicorn

# OpenTelemetry imports 
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# OTLP exporters (gRPC)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Traces
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

# Instrumentations
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Load simulator
from load_simulator import register_load_simulation

# OTel setup

SERVICE_NAME_VALUE = os.getenv("OTEL_SERVICE_NAME", "api-service")
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

resource = Resource(
    attributes={
        SERVICE_NAME: SERVICE_NAME_VALUE,
        "service.environment": "demo",
    }
)

# Traces
tracer_provider = TracerProvider(resource=resource)
span_exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True)
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Logs
logger_provider = LoggerProvider(resource=resource)
log_exporter = OTLPLogExporter(endpoint=OTEL_ENDPOINT, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)

# Attach handler so std logging goes through OTEL logs pipeline
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

# Add trace / span info into log records
LoggingInstrumentor().instrument(set_logging_format=True)
RequestsInstrumentor().instrument()

# Metrics definitions

orders_created_counter = meter.create_counter(
    name="orders_created_total",
    description="Total number of orders created",
)

orders_failed_counter = meter.create_counter(
    name="orders_failed_total",
    description="Total number of orders that failed processing",
)

order_value_histogram = meter.create_histogram(
    name="order_value_usd",
    description="Value of created orders in USD",
)


# FastAPI app

app = FastAPI(title="Observable Orders API")

# in-memory store
orders: Dict[str, Dict] = {}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/orders")
async def create_order():
    """
    Create a fake order with a random value and random chance of failure.
    """
    order_id = str(int(time.time() * 1000))
    value = random.randint(10, 500)

    with tracer.start_as_current_span("create_order_logic") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.value", value)

        # Record metrics
        orders_created_counter.add(1, {"status": "created"})
        order_value_histogram.record(value, {"currency": "USD"})

        # Simulateing processing latency
        time.sleep(random.uniform(0.05, 0.25))

        if random.random() < 0.2:
            logging.error("Order processing failed", extra={"order_id": order_id})
            orders_failed_counter.add(1, {"reason": "random_failure"})
            orders[order_id] = {
                "id": order_id,
                "status": "failed",
                "value": value,
            }
        else:
            logging.info("Order created successfully", extra={"order_id": order_id})
            orders[order_id] = {
                "id": order_id,
                "status": "processed",
                "value": value,
            }

    return {
        "order_id": order_id,
        "status": orders[order_id]["status"],
        "value": value,
    }


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders/{order_id}/reprocess")
async def reprocess_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    with tracer.start_as_current_span("reprocess_order_call_worker") as span:
        span.set_attribute("order.id", order_id)
        try:
            resp = requests.post(
                "http://worker-service:8001/process", json={"order_id": order_id}
            )
            resp.raise_for_status()
            logging.info(
                "Reprocess request sent to worker", extra={"order_id": order_id}
            )
        except Exception as e:
            logging.exception(
                "Failed to call worker-service", extra={"order_id": order_id}
            )
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "reprocess_requested", "order_id": order_id}


# Register load simulation (UI + seed)

register_load_simulation(app)


if __name__ == "__main__":
    # Instrument FastAPI AFTER app is created
    FastAPIInstrumentor().instrument_app(app)
    uvicorn.run(app, host="0.0.0.0", port=8000)
