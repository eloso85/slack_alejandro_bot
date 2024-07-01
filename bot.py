import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import certifi

load_dotenv()


app = Flask(__name__)

# Setup SSL certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

slack_token = os.environ["SLACK_BOT_TOKEN"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
client = WebClient(token=slack_token)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if request.json.get("type") == "url_verification":
        return jsonify({"challenge": request.json.get("challenge")})

    event = request.json.get("event")
    if event and event.get("type") == "message" and not event.get("bot_id"):
        try:
            response = client.chat_postMessage(
                channel=event.get("channel"),
                text=f"Hello, <@{event.get('user')}>!"
            )
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=3000)
