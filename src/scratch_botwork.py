import os
import socket


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

