from slacker import Slacker
import json
from pprint import pprint
import datetime
import re
import sys
from time import sleep

if len(sys.argv) != 3:
    print("invalid parameters. Command usage: \"python slack-export.py slack_token [target/directory]\"")
    exit(1)

token = sys.argv[1]
target_dir = sys.argv[2]
if target_dir[-1] != "/":
    target_dir = target_dir + "/"

slack = Slacker(token)

users = slack.users.list().body["members"]
users_dict = {user["id"]: user for user in users}
bots_dict = {user["profile"]["bot_id"]: user for user in users if user["is_bot"]}

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)

def get_im_history(imid, mpim=False):
    done = False
    latest = None
    messages = []
    sleep(.5)
    while not done:
        for attempt in range(5):
            try:
                if mpim:
                    response = slack.mpim.history(imid, latest=latest).body
                else:
                    response = slack.im.history(imid, latest=latest).body
                break
            except Exception as ex:
                if attempt == 5:
                    raise ex
                else:
                    print("failed. trying again")

        messages += response["messages"]
        if response["has_more"] is True:
            latest = response["messages"][-1]["ts"]
            continue
        return clean_messages(messages)

def clean_messages(messages):
    cleaned_messages = []
    for message in messages:
        cleaned_message = {}
        if "user" in message:
            cleaned_message["user"] = users_dict[message["user"]]["name"]
        else:
            try:
                cleaned_message["user"] = bots_dict[message["bot_id"]]["name"]
            except KeyError:
                cleaned_message["user"] = "unknown bot name"
        cleaned_message["ts"] = datetime.datetime.fromtimestamp(float(message["ts"]))
        try:
            cleaned_message["text"] = clean_text(message["text"])
        except KeyError:
            print("no text in this message?")
        cleaned_messages.append(cleaned_message)
    return cleaned_messages

def clean_text(text):
    cleaned_text = text
    matches = re.findall(r'<[^(>)]*>', text)
    for match in matches:
        try:
            if match.startswith("<@") and "|" not in match:
                username = "@" + users_dict[match[2:-1]]["name"]
                cleaned_text = cleaned_text.replace(match, username)
            elif "|" in match and (match.startswith("<#") or match.startswith("<@")):
                name = match[1] + match[match.find("|")+1:-1]
                cleaned_text = cleaned_text.replace(match, name)
        except KeyError as e:
            print("failed translating {} from message {}. SKIPPING.".format(match, text))
    return cleaned_text
    
def get_all_messages():
    ims = []
    for im in slack.im.list().body["ims"]:
        ims.append({"name": users_dict[im["user"]]["name"], "id": im["id"], "mpim": False})
    
    for mpim in slack.mpim.list().body["groups"]:
        ims.append({"name": mpim["name"], "id": mpim["id"], "mpim": True})

    for im in ims:
        print(im["id"] + ":  " + im["name"])
        im_history = get_im_history(im["id"], mpim=im["mpim"])
        if len(im_history) > 0:
            with open(target_dir + im["name"] + ".json", "w+") as f:
                f.write(json.dumps(im_history, default=date_handler, indent=4))

get_all_messages()
