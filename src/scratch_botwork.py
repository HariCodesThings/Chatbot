import os
import socket
import time 


# state keeps track of where in the discourse we are? : Greeting Protocol
class State:
    START = 1
    INITIAL_OUTREACH = 2
    SECONDARY_OUTREACH = 3
    OUTREACH_REPLY = 4
    INQUIRY = 5
    INQUIRY_REPLY = 6
    GIVEUP_FRUSTRATED = 7
    END = 8

class ChatBot: # init here
    bot_state = State.START
    bot_response = ""

    def switch_state(state):
        pass

    def wait_4_response():
        seconds_elapsed = 0
        while seconds_elapse != 30 or check_msg() == None:
            time.sleep(1)
            seconds_elapsed += 1
        