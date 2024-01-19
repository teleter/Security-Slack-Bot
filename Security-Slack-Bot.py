import os
import json
import requests
from slack_bolt import App
from slack_sdk.web import WebClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import SectionBlock, ActionsBlock, ButtonElement
from slack_sdk.models.attachments import Attachment
from splunk_sdk import splunklib.client as client
from splunklib.client import connect, login

# Load configuration from JSON file
with open("slack.json", "r") as config_file:
    config = json.load(config_file)

# Initialize Slack app
app = App(
    token=config["slack"]["bot_token"],
    signing_secret=config["slack"]["signing_secret"]
)

# Initialize Splunk SDK Web API connection
splunk_service = client.connect(
    host=config["splunk"]["host"],
    port=config["splunk"]["port"],
    username=config["splunk"]["username"],
    password=config["splunk"]["password"],
)

def fetch_splunk_alerts():
    # Use the Splunk SDK Web API to run a search query and get alerts
    query = config["splunk"]["query"]
    search_results = splunk_service.get_search_results(query)
    alerts = search_results.list()

    return alerts

def post_interaction_message(user_email, channel_id, say):
    message = {
        "channel": channel_id,
        "text": f"Suspicious login detected for user {user_email}. Recognize this login?",
        "attachments": [
            {
                "text": "",
                "fallback": "You are unable to choose an option",
                "callback_id": "login_recognition",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "recognition",
                        "text": "I recognize this login",
                        "type": "button",
                        "value": f"recognize|{user_email}"
                    },
                    {
                        "name": "recognition",
                        "text": "I do not recognize this login",
                        "type": "button",
                        "value": f"do_not_recognize|{user_email}"
                    }
                ]
            }
        ]
    }

    say(text="", blocks=[message])

def handle_login_recognition(ack, body, respond):
    ack()
    action_value, user_email = body["actions"][0]["value"].split("|")

    if action_value == "do_not_recognize":
        create_jira_ticket(user_email)
        respond(text=f"Thanks for reporting. A Jira ticket has been created for further investigation.")

def create_jira_ticket(user_email):
    # You need to implement Rapid7 SOAR API requests to create a Jira ticket here
    # Include relevant information from the Splunk alert and Slack message
    # Use the Rapid7 SOAR API URL, and ensure you have the necessary permissions

    # Example: Making a dummy request for illustration
    jira_payload = {
        "summary": "Suspicious login - Investigation needed",
        "description": f"User {user_email} reported a suspicious login. Further investigation required.",
        "assignee": "ANALYST_JIRA_USERNAME"
        # Add more fields as needed
    }

    try:
        response = requests.post(
            f"{config['rapid7_soar']['api_url']}/create_jira_ticket",
            json=jira_payload,
            auth=(config["jira"]["username"], config["jira"]["password"]),
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            print("Jira ticket created successfully.")
        else:
            print(f"Failed to create Jira ticket. Status code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"Error creating Jira ticket: {e}")

if __name__ == "__main__":
    alerts = fetch_splunk_alerts()

    for alert in alerts:
        user_email = alert.get("user_email")
        channel_id = config["slack"]["channel_id"]

        try:
            response = app.client.conversations_open(users=[user_email])
            channel_id = response["channel"]["id"]
        except SlackApiError as e:
            print(f"Error opening conversation with {user_email}: {e.response['error']}")

        post_interaction_message(user_email, channel_id, app.client.chat_postMessage)
        
    app.start(port=int(os.environ.get("PORT", 3000)))
    
#This script posts an initial message to a Slack channel with an "Recognize this login" button and "I don't recognize this login" button. You'll need to set up an interactive component request URL in your Slack App settings to handle user interactions.

