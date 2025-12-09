import logging
import os
import random
import time
import threading

import requests
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi import FastAPI  

SELF_BASE_URL = os.getenv("SELF_BASE_URL", "http://localhost:8000")


def run_load_scenario(num_orders: int, reprocess_ratio: float, duration_seconds: float):
    try:
        num_orders = max(int(num_orders), 0)
        if num_orders <= 0 or duration_seconds <= 0:
            logging.info(
                "run_load_scenario: nothing to do",
                extra={
                    "num_orders": num_orders,
                    "reprocess_ratio": reprocess_ratio,
                    "duration_seconds": duration_seconds,
                },
            )
            return

        interval = duration_seconds / num_orders
        logging.info(
            "Starting load scenario",
            extra={
                "num_orders": num_orders,
                "reprocess_ratio": reprocess_ratio,
                "duration_seconds": duration_seconds,
                "interval": interval,
            },
        )

        for i in range(num_orders):
            try:
                # Create an order
                r = requests.post(f"{SELF_BASE_URL}/orders", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    order_id = data.get("order_id")
                    logging.info(
                        "Load scenario created order",
                        extra={
                            "order_id": order_id,
                            "status": data.get("status"),
                            "index": i,
                        },
                    )

                    # reprocess
                    if order_id and random.random() < reprocess_ratio:
                        r2 = requests.post(
                            f"{SELF_BASE_URL}/orders/{order_id}/reprocess", timeout=5
                        )
                        logging.info(
                            "Load scenario reprocessed order",
                            extra={
                                "order_id": order_id,
                                "status_code": r2.status_code,
                            },
                        )
                else:
                    logging.error(
                        "Load scenario /orders returned non-200",
                        extra={"status_code": r.status_code},
                    )

            except Exception as e:
                logging.exception("Error in load scenario", extra={"error": str(e)})

            time.sleep(max(interval, 0.01))

        logging.info("Load scenario finished")

    except Exception as e:
        logging.exception("run_load_scenario crashed", extra={"error": str(e)})


def start_background_load(num_orders: int, reprocess_ratio: float, duration_seconds: float):
    thread = threading.Thread(
        target=run_load_scenario,
        args=(num_orders, reprocess_ratio, duration_seconds),
        daemon=True,
    )
    thread.start()


SIMULATE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Observable Orders - Load Simulator</title>
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }
    .card {
      background: #020617;
      border-radius: 16px;
      padding: 24px 28px;
      box-shadow: 0 18px 45px rgba(0,0,0,0.45);
      max-width: 420px;
      width: 100%;
      border: 1px solid #1f2937;
    }
    h1 {
      font-size: 1.4rem;
      margin: 0 0 12px 0;
      color: #f9fafb;
    }
    p {
      margin: 0 0 20px 0;
      font-size: 0.9rem;
      color: #9ca3af;
    }
    label {
      display: block;
      font-size: 0.8rem;
      margin-bottom: 4px;
      color: #d1d5db;
    }
    input {
      width: 100%;
      padding: 8px 10px;
      border-radius: 8px;
      border: 1px solid #374151;
      background: #020617;
      color: #e5e7eb;
      font-size: 0.9rem;
      box-sizing: border-box;
      margin-bottom: 14px;
    }
    input:focus {
      outline: none;
      border-color: #38bdf8;
      box-shadow: 0 0 0 1px rgba(56,189,248,0.4);
    }
    .hint {
      font-size: 0.75rem;
      color: #6b7280;
      margin-bottom: 10px;
    }
    button {
      width: 100%;
      padding: 10px 12px;
      font-size: 0.95rem;
      border-radius: 999px;
      border: none;
      background: linear-gradient(135deg, #38bdf8, #6366f1);
      color: #0b1120;
      font-weight: 600;
      cursor: pointer;
      margin-top: 4px;
    }
    button:hover {
      filter: brightness(1.05);
    }
    .note {
      font-size: 0.7rem;
      color: #6b7280;
      margin-top: 10px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Load Simulator</h1>
    <p>Generate demo traffic for the Observable Orders system. Watch metrics, logs, and traces update in Grafana.</p>
    <form method="post" action="/simulate/run">
      <label for="orders">Number of orders</label>
      <input id="orders" name="orders" type="number" min="1" value="50" required />

      <label for="reprocess_ratio">Reprocess %</label>
      <input id="reprocess_ratio" name="reprocess_ratio" type="number" min="0" max="100" value="60" required />
      <div class="hint">Percent of orders that will be reprocessed via worker-service.</div>

      <label for="duration_seconds">Duration (seconds)</label>
      <input id="duration_seconds" name="duration_seconds" type="number" min="1" value="60" required />
      <div class="hint">Traffic will be spread roughly evenly across this duration.</div>

      <button type="submit">Run simulation</button>
    </form>
    <div class="note">
      This runs in the background. Open Grafana to see the effect in real time.
    </div>
  </div>
</body>
</html>
"""


def register_load_simulation(app: FastAPI) -> None:

    @app.on_event("startup")
    async def startup_seed():
        def seed():
            time.sleep(5)
            logging.info("Starting initial seed load")

            run_load_scenario(num_orders=20, reprocess_ratio=0.6, duration_seconds=30)
            logging.info("Initial seed load completed")

        threading.Thread(target=seed, daemon=True).start()

    @app.get("/simulate", response_class=HTMLResponse)
    async def get_simulate_page():
        return HTMLResponse(content=SIMULATE_HTML)

    @app.post("/simulate/run", response_class=HTMLResponse)
    async def run_simulation(
        orders: int = Form(...),
        reprocess_ratio: float = Form(...),
        duration_seconds: float = Form(...),
    ):

        ratio = max(0.0, min(reprocess_ratio / 100.0, 1.0))
        start_background_load(
            num_orders=orders,
            reprocess_ratio=ratio,
            duration_seconds=duration_seconds,
        )

        duration_int = int(duration_seconds)
        message = f"""
        <html>
          <head>
            <meta charset="UTF-8" />
            <title>Simulation running...</title>
          </head>
          <body style="background:#0f172a;color:#e5e7eb;font-family:system-ui, sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;">
            <div style="background:#020617;border-radius:16px;padding:24px 28px;max-width:420px;width:100%;border:1px solid #1f2937;box-shadow:0 18px 45px rgba(0,0,0,0.45);">
              <h1 style="font-size:1.3rem;margin:0 0 12px 0;color:#f9fafb;">Simulation started</h1>
              <p style="font-size:0.9rem;color:#9ca3af;margin:0 0 8px 0;">
                Generating {orders} orders over ~{duration_int} seconds
                with ~{int(reprocess_ratio)}% reprocessed.
              </p>
              <p style="font-size:0.85rem;color:#9ca3af;margin:0 0 6px 0;">
                You will be redirected back to the simulator when this run is finished.
              </p>
              <p style="font-size:0.8rem;color:#6b7280;margin:0;">
                Remaining time: <span id="remaining">{duration_int}</span> seconds
              </p>
            </div>
            <script>
              const total = {duration_int};
              let remaining = total;
              const el = document.getElementById('remaining');
              const interval = setInterval(() => {{
                remaining -= 1;
                if (remaining <= 0) {{
                  remaining = 0;
                  clearInterval(interval);
                }}
                if (el) {{
                  el.textContent = remaining;
                }}
              }}, 1000);
              setTimeout(() => {{
                window.location.href = '/simulate';
              }}, total * 1000);
            </script>
          </body>
        </html>
        """
        return HTMLResponse(content=message)
