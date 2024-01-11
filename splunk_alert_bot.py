#You'll need to install the library first:

#maybe try flask as well ? 

#pip install slack_sdk
#pip install splunk-sdk

import os
import time
import json
import slack_sdk
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import splunk-sdk 

SLACK_BOT_TOKEN = "YOUR_SLACK_BOT_TOKEN"
SPLUNK_ALERT_MESSAGE = "ALERT: Suspicious login detected. Recognize this login?"
post_alert_message = SPLUNK_ALERT_MESSAGE

client = WebClient(token=SLACK_BOT_TOKEN)

try:
    # Post the alert message to a designated channel
    response = client.chat_postMessage(channel="#splunk-alerts", text=SPLUNK_ALERT_MESSAGE)

    # Get the message timestamp
    timestamp = response["ts"]

    # Add interactive buttons
    client.chat_update(
        channel="#splunk-alerts",
        ts=timestamp,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": SPLUNK_ALERT_MESSAGE
                },
                "accessory": {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "I recognize this login",
                            },
                            "action_id": "I recognize_login"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "I do not recognize this login",
                            },
                            "action_id": "dont_recognize_login"
                        },
                    ],
                },
            },
        ],
    )
    print("Message sent successfully!")

except SlackApiError as e:
    print(f"Error posting message to Slack: {e.response['error']}")

# Function to handle the interactive component actions
def handle_interactive_actions(payload):
    user_id = payload["user"]["id"]
    action_id = payload["actions"][0]["action_id"]

    if action_id == "recognize_login":
        response_text = f"User {user_id} recognized the login. Investigation complete."
    elif action_id == "dont_recognize_login":
        response_text = f"User {user_id} does not recognize the login. Further investigation required."
    else:
        response_text = "Unknown action"

    return response_text

# Listen for interactive component actions
def listen_for_interactive_actions():
    while True:
        payload = input("Enter interactive component payload (JSON): ")
        payload_dict = json.loads(payload)

        response_text = handle_interactive_actions(payload_dict)
        print(response_text)

if __name__ == "__main__":
    # Run the function to post the initial message
    post_alert_message()

    # Run the function to listen for interactive component actions
    listen_for_interactive_actions()

#Replace "YOUR_SLACK_BOT_TOKEN" with the actual bot token obtained from the Slack App settings.

#This script posts an initial message to a Slack channel with an "Recognize this login" button and "I don't recognize this login" button. You'll need to set up an interactive component request URL in your Slack App settings to handle user interactions.

