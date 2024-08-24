import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_community.llms import OpenAI  # Updated import

import certifi

load_dotenv()


app = Flask(__name__)

# Setup SSL certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

slack_token = os.environ["SLACK_BOT_TOKEN"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
client = WebClient(token=slack_token)
openai_api_key = os.environ["OPENAI_API_KEY"]

llm = OpenAI(api_key=openai_api_key)  # Use api_key as a keyword argument

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if request.json.get("type") == "url_verification":
        return jsonify({"challenge": request.json.get("challenge")})

    event = request.json.get("event")
    if event and event.get("type") == "message" and not event.get("bot_id"):
        user_message = event.get('text').strip().lower()
        channel = event.get("channel")
        
        # Process the user's message with OpenAI LLM
        try:
            response_text = llm.invoke(user_message)
            send_message(channel, response_text)
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")

    return jsonify({"status": "ok"})

def send_message(channel, text):
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text
        )
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")

if __name__ == "__main__":
    app.run(port=80)