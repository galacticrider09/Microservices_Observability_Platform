from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time, random, requests, logging, os

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [order-service] %(message)s'
)
logger = logging.getLogger(__name__)

# ----------- Prometheus Metrics -----------
REQUEST_COUNT = Counter(
    'order_service_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'order_service_request_duration_seconds',
    'Request latency in seconds',
    ['endpoint']
)
ERROR_COUNTER = Counter(
    'order_service_errors_total',
    'Total errors in order-service'
)

ORDERS = {
    "1": [{"id": "101", "item": "Laptop",  "amount": 999.99, "status": "delivered"}],
    "2": [{"id": "102", "item": "Phone",   "amount": 499.99, "status": "shipped"}],
    "3": [{"id": "103", "item": "Tablet",  "amount": 299.99, "status": "processing"}],
}

NOTIF_SERVICE_URL = os.getenv("NOTIF_SERVICE_URL", "http://notification-service:5002")

# ----------- Routes -----------
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "order-service"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/orders/<user_id>')
def get_orders(user_id):
    start = time.time()
    logger.info(f"Fetching orders for user_id={user_id}")

    # ⚡ THE VILLAIN — 20% intentional failure rate
    # This is what Prometheus will catch and alert on
    if random.random() < 0.2:
        ERROR_COUNTER.inc()
        REQUEST_COUNT.labels('GET', '/orders', '500').inc()
        REQUEST_LATENCY.labels('/orders').observe(time.time() - start)
        logger.error(f"DB_TIMEOUT: Failed to fetch orders for user_id={user_id} — simulated database timeout")
        return jsonify({"error": "Database timeout — please retry"}), 500

    # Simulate realistic DB query time
    time.sleep(random.uniform(0.05, 0.3))

    orders = ORDERS.get(user_id, [])

    # Fire-and-forget notification
    try:
        requests.post(
            f"{NOTIF_SERVICE_URL}/notify",
            json={"user_id": user_id, "event": "order_viewed"},
            timeout=1
        )
    except Exception as e:
        logger.warning(f"Notification failed (non-critical): {e}")

    REQUEST_COUNT.labels('GET', '/orders', '200').inc()
    REQUEST_LATENCY.labels('/orders').observe(time.time() - start)
    logger.info(f"Returned {len(orders)} orders for user_id={user_id}")
    return jsonify(orders)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)