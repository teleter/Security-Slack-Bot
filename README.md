# Security-Slack-Bot
A SIRT Slack Bot that will take "suspicious login" alerts from splunk and prompt the affected user via Slack to either click "i recognise this login" or click "i do not recognise this login" If the user clicks i do not recognise this login the bot will ping rapid 7 soar to create a jira ticket in the SIRT dashboard

This Tool is meant to be a another data point during a incident / alert and is not intended to be a point of truth. Further investigation should always be done. 