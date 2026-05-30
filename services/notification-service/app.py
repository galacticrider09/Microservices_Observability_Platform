from flask import Flask, jsonify, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import logging

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [notification-service] %(message)s'
)
logger = logging.getLogger(__name__)

NOTIFICATION_COUNT = Counter(
    'notification_service_sent_total',
    'Total notifications dispatched',
    ['event_type']
)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "notification-service"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json() or {}
    user_id  = data.get('user_id',  'unknown')
    event    = data.get('event',    'unknown')

    logger.info(f"Notification dispatched: user_id={user_id} event={event}")
    NOTIFICATION_COUNT.labels(event).inc()
    return jsonify({"status": "sent", "user_id": user_id, "event": event})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)