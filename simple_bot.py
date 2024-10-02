import slack
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

load_dotenv()

# SIGNING_SECRET = os.environ["SIGNING_SECRET"]
# app = Flask(__name__)
# slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, "/slack/events", app)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

client.chat_postMessage(channel="#testing", text="Hello")
