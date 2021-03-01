from irc_socket import *
import os
import random
import time
from statemachine import StateMachine, State

server = "irc.freenode.net"  # Provide a valid server IP/Hostname
channel = "#CSC482"
botnick = "BotNickPython"

irc = IRCSocket()
irc.connect(server, channel, botnick)

# state keeps track of where in the discourse we are? : Greeting Protocol
class ChatState(StateMachine):
    start = State('START', initial=True)
    initial_outreach = State('INITIAL_OUTREACH')
    secondary_outreach = State('SECONDARY_OUTREACH')
    outreach_reply = State('OUTREACH_REPLY')
    inquiry = State('INQUIRY')
    inquiry_reply = State('INQUIRY_REPLY')
    inquiry_two = State('INQUIRY_TWO')
    inquiry_reply_two = State('INQUIRY_REPLY_TWO')
    giveup_frustrated = State('GIVEUP_FRUSTRATED')
    end = State('END')

    reply = start.to(initial_outreach)
    response = initial_outreach.to(outreach_reply)
    no_reply_one = initial_outreach.to(secondary_outreach)
    no_reply_after_second = secondary_outreach.to(giveup_frustrated)
    second_response = secondary_outreach.to(outreach_reply)
    no_inquiry = outreach_reply.to(giveup_frustrated)
    inquiry_given = outreach_reply.to(inquiry)
    inquiry_response = inquiry.to(inquiry_reply)
    to_next_inquiry = inquiry_reply.to(inquiry_two)
    to_next_inquiry_reply = inquiry_two.to(inquiry_reply_two)
    ignore_after_inquiry = inquiry.to(giveup_frustrated)
    ignore_after_inquiry_two = inquiry_two.to(giveup_frustrated)
    happy_end = inquiry_reply_two.to(end)
    giveup_end = giveup_frustrated.to(end)

    
class ChatBot: # init here
    def __init__(self):
        self.bot_state = ChatState.start
        self.bot_response = ""
        self.awaiting_response = False


    def check_msg(_text):
        return "PRIVMSG" in _text and channel in _text and botnick + ":" in _text


    @property
    def get_timed_response():
        seconds_elapsed = 0
        while seconds_elapsed != 30:
            text = irc.get_response()
            if text:
                break
            seconds_elapsed += 1
        return text


    def start_logic():
        text = get_timed_response()
        if text:
            # Go to next state after getting data
            pass
        else:
            # Hello Anyone there?

    def get_state(self):
        while True:
            if self.bot_state == ChatState.start:
                start_logic(chatbot)


    while True:
        text = irc.get_response()
        if check_msg(text) and "hello" in text.lower():
            irc.send(channel, "Hello!")

        if check_msg(text) and "die" in text.lower():
            irc.send(channel, "Dying!")
            irc.kill_self(channel)
            exit()

