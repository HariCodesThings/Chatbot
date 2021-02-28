from irc_socket import *
import os
import random
import time 


import nltk
from nltk.chat.util import Chat, reflections

from scratch_botwork import *

server = "irc.freenode.net"  # Provide a valid server IP/Hostname
channel = "#CSC482"
botnick = "Nick"

irc = IRCSocket()
irc.connect(server, channel, botnick)



def check_msg(_text):
    return "PRIVMSG" in _text and channel in _text and botnick + ":" in _text


while True:
    text = irc.get_response()
    print(text)

    if check_msg(text) and "hello" in text.lower():
        irc.send(channel, "Hello!")

    if check_msg(text) and "die" in text.lower():
        irc.send(channel, "Dying!")
        irc.kill_self(channel)
        exit()

