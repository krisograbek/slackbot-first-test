import slack
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from openai import OpenAI

load_dotenv()

openai_client = OpenAI()

SIGNING_SECRET = os.environ["SIGNING_SECRET"]
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, "/slack/events", app)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
BOT_ID = client.api_call("auth.test")["user_id"]


message_counts = {}
welcome_messages = {}


class WelcomeMessage:
    START_TEXT = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Welcome to this awesome channel! \n\n"
                "*Get started by completing the tasks!*"
            ),
        },
    }

    DIVIDER = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.completed = False

    def get_message(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "Welcome Robot!",
            "icon_emoji": self.icon_emoji,
            "blocks": [self.START_TEXT, self.DIVIDER, self._get_reaction_task()],
        }

    def _get_reaction_task(self):
        checkmark = ":white_check_mark:"
        if not self.completed:
            checkmark = ":white_large_square:"

        text = f"{checkmark} *React to this message!*"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response["ts"]

    welcome_messages[channel][user] = welcome


@slack_event_adapter.on("message")
def message(payload):

    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    print(f"User ID: {user_id}")
    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if text.lower() == "start":
            send_welcome_message(f"@{user_id}", user_id)


@app.route("/message-count", methods=["POST"])
def message_count():
    data = request.form
    # print(data)
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    message_count = message_counts.get(user_id, 0)
    print(f"User ID: {user_id}")
    response = "You've already sent " + str(message_count) + " messages."

    client.chat_postMessage(
        channel=channel_id, text=f"You've sent {message_count} messages"
    )
    return Response(), 200


@app.route("/motivate-me", methods=["POST"])
def motivate_me():
    data = request.form
    user_text = data.get("text")
    channel_id = data.get("channel_id")
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You're an expert in motivating people. It the user shares what's wrong, address it. Otherwise give general motivation",
            },
            {"role": "user", "content": user_text},
        ],
    )
    motivation = response.choices[0].message.content
    client.chat_postMessage(channel=channel_id, text=motivation)

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
