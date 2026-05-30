from flask import Flask, request, jsonify
import boto3, os, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [sns-forwarder] %(message)s')
logger = logging.getLogger(__name__)

sns = boto3.client(
    'sns',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "sns-forwarder"})

@app.route('/alert', methods=['POST'])
def receive_alert():
    data = request.get_json()
    alerts = data.get('alerts', [])

    for alert in alerts:
        status      = alert.get('status', 'unknown')
        name        = alert.get('labels', {}).get('alertname', 'Unknown')
        summary     = alert.get('annotations', {}).get('summary', name)
        description = alert.get('annotations', {}).get('description', '')
        emoji       = '🚨' if status == 'firing' else '✅ RESOLVED'

        message = f"{emoji} {summary}\n\nStatus: {status}\nDetail: {description}"

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"DevOps Alert: {name}"
        )
        logger.info(f"Alert forwarded to SNS: {name} [{status}]")

    return jsonify({"status": "forwarded"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)