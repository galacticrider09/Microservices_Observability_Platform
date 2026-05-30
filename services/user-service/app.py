from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time, requests, logging, os

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [user-service] %(message)s'
)
logger = logging.getLogger(__name__)

# ----------- Prometheus Metrics -----------
REQUEST_COUNT = Counter(
    'user_service_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'user_service_request_duration_seconds',
    'Request latency in seconds',
    ['endpoint']
)

# ----------- Fake In-Memory Data -----------
USERS = {
    "1": {"id": "1", "name": "Alice", "email": "alice@example.com", "role": "admin"},
    "2": {"id": "2", "name": "Bob",   "email": "bob@example.com",   "role": "user"},
    "3": {"id": "3", "name": "Charlie","email": "charlie@example.com","role": "user"},
}

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:5001")

# ----------- Routes -----------
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "user-service"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/users/<user_id>')
def get_user(user_id):
    start = time.time()
    logger.info(f"Request received for user_id={user_id}")

    if user_id not in USERS:
        REQUEST_COUNT.labels('GET', '/users', '404').inc()
        REQUEST_LATENCY.labels('/users').observe(time.time() - start)
        logger.warning(f"User not found: user_id={user_id}")
        return jsonify({"error": "User not found"}), 404

    # Call order-service
    orders = []
    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}/orders/{user_id}", timeout=3)
        if resp.status_code == 200:
            orders = resp.json()
        else:
            logger.warning(f"order-service returned {resp.status_code} for user {user_id}")
    except Exception as e:
        logger.warning(f"Could not reach order-service: {e}")

    user = {**USERS[user_id], "orders": orders}
    REQUEST_COUNT.labels('GET', '/users', '200').inc()
    REQUEST_LATENCY.labels('/users').observe(time.time() - start)
    logger.info(f"Successfully returned user_id={user_id} with {len(orders)} orders")
    return jsonify(user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)