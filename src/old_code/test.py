from irc_socket import *
import os
import random
import time 


import nltk
from nltk.chat.util import Chat, reflections

from scratch_botwork import *

server = "irc.freenode.net"  # Provide a valid server IP/Hostname
channel = "#CSC482"
botnick = "BotNickPython"

irc = IRCSocket()
irc.connect(server, channel, botnick)

def get_timed_response():
    seconds_elapsed = 0
    while seconds_elapse != 30:
        text = irc.get_response()
        if text:
            break
        seconds_elapsed += 1
    return text



def check_msg(_text):
    return "PRIVMSG" in _text and channel in _text and botnick + ":" in _text

def start_logic(chatbot):
    text = get_timed_response()
    if text:
        # Go to next state after getting data
        pass
    else:
        # Hello Anyone there?

def get_state(chatbot):
    while True:
        if chatbot.bot_state == State.START:
            start_logic(chatbot)
        


chatbot = ChatBot()

while True:
    text = irc.get_response()
    check 
    if check_msg(text) and "hello" in text.lower():
        irc.send(channel, "Hello!")

    if check_msg(text) and "die" in text.lower():
        irc.send(channel, "Dying!")
        irc.kill_self(channel)
        exit()
    

