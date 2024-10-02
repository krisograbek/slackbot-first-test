import os
import openai
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Slack and OpenAI credentials
slack_token = os.environ["SLACK_BOT_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]
client = WebClient(token=slack_token)
openai.api_key = openai_api_key


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "event" in data:
        event_data = data["event"]

        if event_data.get("type") == "app_mention":
            user_message = event_data.get("text")
            channel_id = event_data.get("channel")

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
            )

            bot_reply = response["choices"][0]["message"]["content"]

            try:
                # Send the response back to Slack
                client.chat_postMessage(channel=channel_id, text=bot_reply)
            except SlackApiError as e:
                return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=3000)
