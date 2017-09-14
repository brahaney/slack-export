#!/bin/bash

echo "Enter your Mac login password below to install pip"
sudo easy_install pip
pip install requests\>=2.13 slacker
SLACKEXPORT=~/slack-export

echo
echo
echo "Generate a slack token at https://api.slack.com/custom-integrations/legacy-tokens"

read -p "Paste your Slack Token Here: " SLACK_TOKEN
read -p "Destination Directory (leave blank for default ~/Documents/slack-archive): " DEST


DEST=${DEST:-~/Documents/slack-archive}

mkdir -p ${DEST}
mkdir -p ${SLACKEXPORT}

cd ${TEMP}

curl -o slack-export.py https://gist.githubusercontent.com/brahaney/fa18124e9260410891948f82cfb6d3c5/raw/daf7bef4cf35a26d914247c76ba0f43bb0e8ede0/slack-export.py

python slack-export.py ${SLACK_TOKEN} ${DEST}
