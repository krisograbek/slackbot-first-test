import slack
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

load_dotenv()

SIGNING_SECRET = os.environ["SIGNING_SECRET"]
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, "/slack/events", app)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
BOT_ID = client.api_call("auth.test")["user_id"]


@app.route("/compute/", methods=["GET"])
def compute():

    name = request.args.get("name", {})
    # var1 = request.args.get("var1", {})
    # var2 = request.args.get("var2", {})

    print(name)

    response = {"name": name}

    response = json.dumps(response, indent=4)

    client.chat_postMessage(channel="#testing", text=name)

    return response, 200


@slack_event_adapter.on("message")
def message(payload):
    print(payload)
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=text)


if __name__ == "__main__":
    app.run(debug=True)
