# mc_bot.py
# Source: https://github.com/DrGFreeman/mc-to-discord
#
# MIT License
#
# Copyright (c) 2018 Julien de la Bruere-Terreault <drgfreeman@tuta.io>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# A simple script that monitors the logs of a Minecraft server and posts user
# activity (joining & leaving server) to Discord via webhook.

import datetime
import time
import requests

# Path to minecraft server main directory
MINECRAFT_PATH = '<insert path here>'

# Discord webhook URL ('https://discordapp.com/api/webhooks/{webhook.id}/{webhook.token}')
# See https://discordapp.com/developers/docs/resources/webhook
# and https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks
WEBHOOK_URL = '<insert webhook URL here>'

# Message templates
MSG_LAUNCH = 'Hello, I keep you informed of user activity on the Minecraft server.'
MSG_SERVER_STOPPED = 'The server is stopped. See you next time.'
MSG_PLAYER_JOINED = '[{0:%H:%M}] {player_name} joined the server.'
MSG_PLAYER_LEFT = '[{0:%H:%M}] {player_name} left the server.'

# Path to log file
LOG_FILE = MINECRAFT_PATH + 'logs/latest.log'

# Dictionaries storing players name (key) and status (value)
players_current = dict()
players_previous = dict()

# Function to post content string to discord
def post_discord(content):
    r = requests.post(WEBHOOK_URL, json={'content': content})
    print(content)

# Main program
if __name__ == '__main__':

    active = True

    try:
        post_discord(MSG_LAUNCH)

        while active:

            # Parse log file
            with open(LOG_FILE, 'r') as log_file:
                for line in log_file:
                    tokens = line.split()
                    if len(tokens) > 4:
                        if tokens[4] == 'Stopping':
                            post_discord(MSG_SERVER_STOPPED)
                            active = False
                            break
                        if tokens[4] == 'joined':
                            players_current[tokens[3]] = 'in'
                        elif tokens[4] == 'left':
                            players_current[tokens[3]] = 'out'

            # Compare current player status with previous and post changes to discord
            now = datetime.datetime.now()
            for player, status in players_current.items():
                if player in players_previous.keys():
                    if players_previous[player] != status:
                        if status == 'in':
                            post_discord(MSG_PLAYER_JOINED.format(now, player_name=player))
                        else:
                            post_discord(MSG_PLAYER_LEFT.format(now, player_name=player))
                elif status == 'in':
                    post_discord(MSG_PLAYER_JOINED.format(now, player_name=player))
            players_previous = players_current.copy()

            time.sleep(5)

    except KeyboardInterrupt:
        pass
