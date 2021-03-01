from irc_socket import *
import os
import random
import time
from statemachine import StateMachine, State

initial_outreach = random.choice(["Hi","Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"])

pairs_outreach = { 
    "hi" : ["What's up?" "How's it going", "What's happening?"],
    "hey" : ["What's up?" "How's it going", "What's happening?"],
    "hello" : ["What's up?" "How's it going", "What's happening?"],
    "yo" : ["What's up?" "How's it going", "What's happening?"],
    "hey there" : ["What's up?" "How's it going", "What's happening?"],
    "welcome" : ["What's up?" "How's it going", "What's happening?"],
    "yoooo" : ["What's up?" "How's it going", "What's happening?"]
}

pairs_response = { 
    "hi" : ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hey" : ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hello" : ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hiii" :  ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "yo" : ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "howdy" : ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "what's up" : ["I'm good", "I'm fine, thanks", "Nothing much", "Great"],
    "how's it going" : ["I'm good", "I'm fine, thanks", "Nothing much", "Great"],
    "what's happening" : ["I'm good", "I'm fine, thanks", "Nothing much", "Great"]
}

get_next_outreach = lambda utterance : random.choice(pairs_outreach[utterance])
get_next_response = lambda utterance : random.choice(pairs_response[utterance])

# print(get_next_response('hello'))


def main():
    bot = ChatBot()
    bot.init_bot()
    bot.run_bot()



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

    reach_out = start.to(initial_outreach)
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

    def on_enter_start(self):
        print("----------- FSM start ---------------")

    def on_enter_initial_outreach(self):
        print("------------ intial outreach  -------------")

    
class ChatBot: # init here
    def __init__(self, server="irc.freenode.net", channel="#CSC482", botnick="Default-bot"):
        self.bot_state = ChatState()
        self.bot_response = ""
        self.awaiting_response = False
        self.users = set()
        self.target = ""
        self.server = server
        self.channel = channel
        self.botnick = botnick
        self.irc = IRCSocket()
        self.irc.connect(server, channel, botnick)

    def init_bot(self):
        while True:
            text = self.irc.get_response()
            if "JOIN" in text:
                break
            # print(f"{count} output: {text}")

        time.sleep(1)
        self.get_names()

    def get_names(self):
        names = self.irc.get_names(self.channel)
        names = set([name for name in names if self.botnick not in name])
        self.users |= names

        print(f"printing names:\n\n{self.users}\n\n------------")



    def check_msg(self, _text):
        return "PRIVMSG" in _text and self.channel in _text and self.botnick + ":" in _text

    def clean_text(self,text):
        pass

    def get_timed_response(self):
        seconds_elapsed = 0
        text = None
        while seconds_elapsed != 30:
            if seconds_elapsed % 5 == 0:
                print(f"{seconds_elapsed} tries")
            if self.irc.poll_response():
                text = self.irc.get_response()
                if text and self.check_msg(text):
                    break
            seconds_elapsed += 1
        seconds_elapsed = 0
        return text


    def run_bot(self):
        while self.bot_state != ChatState.end:
            print(f"state: {self.bot_state}")
            # append name list
            if self.bot_state.is_start:
                self.bot_state.reach_out()
            elif self.bot_state.is_initial_outreach:
                self.initial_outreach_state()
            elif self.bot_state.is_secondary_outreach:
                self.secondary_outreach_state()
            elif self.bot_state.is_outreach_reply:
                self.outreach_reply_state()
            elif self.bot_state.is_giveup_frustrated:
                self.giveup_state()
            elif self.bot_state.is_end:
                self.end_state()
            else:
                print("State error")


            # if self.check_msg(text) and "hello" in text.lower():
            #     self.irc.send(channel, "Hello!")
            #
            # if self.check_msg(text) and "die" in text.lower():
            #     self.irc.send(channel, "Dying!")
            #     self.irc.kill_self(channel)
            #     exit()

    def start_state(self):
        text = self.get_timed_response() # first 30 seconds 
        if not text:
            self.awaiting_response = True
            self.target = random.choice(list(self.users))
            print(f"reaching out to {self.target}")
            self.bot_state.reach_out()

        else:
            print(text)
            self.awaiting_response = False
            self.bot_state.response()
            # TODO parse put and set target to who replied to you

    def initial_outreach_state(self):
        self.irc.send_dm(self.channel, self.target, "Hello")  # replace with more options
        text = self.get_timed_response() # first 30 seconds 
        if not text:
            self.awaiting_response = True
            self.bot_state.no_reply_one()
        else:
            print(text)
            self.awaiting_response = False
            self.bot_state.response()

    def secondary_outreach_state(self):
        self.irc.send_dm(self.channel, self.target, "Hello?????")  # replace with more options
        text = self.get_timed_response() # first 30 seconds check
        if not text:
            self.awaiting_response = True
            self.bot_state.no_reply_after_second()
        else:
            print(text)
            self.awaiting_response = False
            self.bot_state.second_response()

    def outreach_reply_state(self):
        print("In outreach reply state")
        self.irc.kill_self(self.channel)

    def giveup_state(self):
        self.irc.send_dm(self.channel, self.target, "Well bye then")
        
        self.bot_state.giveup_end()

        # maybe kill

    def end_state(self):
        self.irc.kill_self(self.channel)

if __name__ == "__main__":
    main()

