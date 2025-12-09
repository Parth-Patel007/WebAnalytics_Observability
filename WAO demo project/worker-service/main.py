import logging
import os
import random
import time

from fastapi import FastAPI
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

# OTel setup

SERVICE_NAME_VALUE = os.getenv("OTEL_SERVICE_NAME", "worker-service")
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

# Metrics definitions

orders_processed_counter = meter.create_counter(
    name="orders_processed_total",
    description="Orders processed by worker",
)


# FastAPI app

app = FastAPI(title="Observable Orders Worker")


@app.post("/process")
async def process_order(payload: dict):
    order_id = payload.get("order_id", "unknown")

    with tracer.start_as_current_span("worker_process_order") as span:
        span.set_attribute("order.id", order_id)

        # Simulate variable latency
        delay = random.uniform(0.1, 1.0)
        time.sleep(delay)
        span.set_attribute("processing.delay", delay)

        if random.random() < 0.3:
            logging.error(
                "Worker failed processing order", extra={"order_id": order_id}
            )
            orders_processed_counter.add(1, {"status": "failed"})
            return {"status": "failed", "order_id": order_id}

        logging.info("Worker processed order", extra={"order_id": order_id})
        orders_processed_counter.add(1, {"status": "success"})
        return {"status": "success", "order_id": order_id}


if __name__ == "__main__":
    FastAPIInstrumentor().instrument_app(app)
    uvicorn.run(app, host="0.0.0.0", port=8001)
