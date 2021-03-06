
# ############################################################################
# IMPORTS BELOW
# ############################################################################
from flask import Flask, request, Response
import json
import requests
import sys


# Disable Certificate warning
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass


# ############################################################################
# Variables below
# ############################################################################

SPARK_ROOM_NAME = 'Spark Tropo Omnichannel'
SPARK_ROOM_ID = 'Y2lzY29zcGFyazovL3VzL1JPT00vMGFhNTBmODAtNDYwMS0xMWU2LWJlNjMtNmRkMjM0MjNjNzZj'

SPARK_BASE = 'https://api.ciscospark.com/v1'
SPARK_MESSAGES = '%s/messages' % SPARK_BASE
SPARK_ROOMS = '%s/rooms' % SPARK_BASE
SPARK_MEMBERSHIPS = '%s/memberships' % SPARK_BASE

# Get your access token:
# 1) Login to developer.ciscospark.com
# 2) Copy the Access Token from top-right corner portrait icon
# 3) replace YOUR-ACCESS-TOKEN-HERE in the line below, leave preceding "Bearer " intact
SPARK_TOKEN = 'Bearer ODU1MDI5MDYtYzU4My00OTc5LWIwNWMtMDg1ZTI4ZDc2NjA0MGNmZjA5NmMtOTUy'
SPARK_HEADERS = {'Content-type': 'application/json', 'Authorization': SPARK_TOKEN}


# ############################################################################
# Find Room ID
# ############################################################################
r = requests.get(SPARK_ROOMS, headers=SPARK_HEADERS, verify=False)
# print('Spark Response: ' + r.text)
j = json.loads(r.text)

for tmproom in j['items']:
    if tmproom['title'] == SPARK_ROOM_NAME:
        SPARK_ROOM_ID = tmproom['id']
        print("Found room ID for '" + SPARK_ROOM_NAME + "' : " + SPARK_ROOM_ID)
        break

if SPARK_ROOM_ID is None:
    print("Failed to find room ID for '" + SPARK_ROOM_NAME + "'")
    sys.exit(1)


# ############################################################################
# List Users in Spark Room
# ############################################################################
m = "roomId=" + SPARK_ROOM_ID
r = requests.get(SPARK_MEMBERSHIPS, params=m, headers=SPARK_HEADERS)
j = json.loads(r.text)

i = 0
a = 20
b = 6

Member = [[0 for x in range(a)] for y in range(b)]

for tmpmember in j['items']:
    print('Member Name: ' + tmpmember['personDisplayName'])
    print('Member Id: ' + tmpmember['personId'])
    print('Member Email Address: '+ tmpmember['personEmail'])
    Member[i][0] = tmpmember['personId']
    Member[i][1] = tmpmember['personDisplayName']
    Member[i][2] = 3
    Member[i][3] = ''
    Member[i][4] = tmpmember['personEmail']
    Member[i][5] = '0000000000'
    Member[i][6] = '0000000000'


app = Flask(__name__)

spark_host = "https://api.ciscospark.com/"
spark_headers = {}
spark_headers["Content-type"] = "application/json"
app_headers = {}
app_headers["Content-type"] = "application/json"


@app.route('/', methods=["POST"])
def process_webhook():


    post_data = request.get_json(force=True)

    m = json.dumps({'roomId': SPARK_ROOM_ID, 'text': 'Received Message into bot'})
    print('Spark Request: ' + SPARK_MESSAGES + m)
    r = requests.post(SPARK_MESSAGES, data=m, headers=SPARK_HEADERS, verify=False)
    print('Spark Response: ' + r.text)


    pprint(post_data)

    # Check what room this came from
    # If Demo Room process for open room
    if post_data["data"]["roomId"] == SPARK_ROOM_ID:
        print("Incoming Spark Room Message.")
        sys.stderr.write("Incoming Spark Room Message\n")
        process_room_message(post_data)
        # message_id = post_data["data"]["id"]
        # message = get_message(message_id)
        # pprint(message)
        #
        # if message["text"].lower().find("results") > -1:
        #     results = get_results()
        #     reply = "The current standings are\n"
        #     for result in results:
        #         reply += "  - %s has %s votes.\n" % (result[0], result[1])
        # elif message["text"].lower().find("options") > -1:
        #     options = get_options()
        #     reply = "The options are... \n"
        #     for option in options:
        #         reply += "  - %s \n" % (option)
        # elif message["text"].lower().find("vote") > -1:
        #     reply = "Let's vote!  Look for a new message from me so you can place a secure vote!"
        #     start_vote_session(message["personEmail"])
        # else:
        #     # Reply back to message
        #     reply =  "Hello, welcome to the MyHero Demo Room.\n" \
        #             "To find out current status of voting, ask 'What are the results?'\n" \
        #             "To find out the possible options, ask 'What are the options?\n" \
        #             '''To place a vote, say "I'd like to vote" to start a private voting session.'''
        #     send_message_to_room(demo_room_id, reply)
    # If not the demo room, assume its a user voting session
    else:
        # print("Incoming Individual Message.")
        sys.stderr.write("Incoming Individual Message\n")
        process_incoming_message(post_data)

    return ""

@app.route('/health')
def health_check():
    return "400"



app.run(debug=True, host='0.0.0.0', port=int("5000"))
