from irc_socket import *
import random
import time
from statemachine import StateMachine, State
import sys


# when chatbot is speaker one
initial_outreach = random.choice(["Hi", "Hello", "Hey there", "Howdy", "Yoooo", "Yo", "Hey", "Welcome"])
pairs_outreach = {
    "hi": ["What's up?", "How's it going", "What's happening?"],
    "hey": ["What's up?", "How's it going", "What's happening?"],
    "hello": ["What's up?", "How's it going", "What's happening?"],
    "yo": ["What's up?", "How's it going", "What's happening?"],
    "hey there": ["What's up?", "How's it going", "What's happening?"],
    "welcome": ["What's up?", "How's it going", "What's happening?"],
    "yoooo": ["What's up?", "How's it going", "What's happening?"],
    "howdy": ["What's up?", "How's it going", "What's happening?"]
}


# when chatbot is speaker two
pairs_response = {
    "hi": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hey": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hello": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hiii":  ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "yo": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "howdy": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "yoooo": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "welcome": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hey there": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "what's up?": [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                  ("Nothing much", "You?"), ("Great", "What about you?")],
    "how's it going?": [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                       ("Nothing much", "You?"), ("Great", "What about you?")],
    "what's happening?": [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                         ("Nothing much", "You?"), ("Great", "What about you?")],
    "you?" : [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                  ("Nothing much", "You?"), ("Great", "What about you?")],
    "how are you?" : [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                  ("Nothing much", "You?"), ("Great", "What about you?")],
    "and you?" : [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                  ("Nothing much", "You?"), ("Great", "What about you?")],
    "What about you?" : [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                  ("Nothing much", "You?"), ("Great", "What about you?")],
}

get_next_outreach = lambda utterance: random.choice(pairs_outreach[utterance])
get_next_response = lambda utterance: random.choice(pairs_response[utterance])


def main():
    # python3 testbot.py irc.freenode.net “#CPE482” myNickname
    if len(sys.argv) == 4:
        server = sys.argv[1]
        channel = sys.argv[2].strip("\"")
        botnick = sys.argv[3]
        bot = ChatBot(server=server, channel=channel, botnick=botnick)
    else:
        bot = ChatBot()

    bot.init_bot()
    bot.run_bot()


# state keeps track of where in the discourse we are
class ChatState(StateMachine):
    start = State('START', initial=True)
    initial_outreach = State('INITIAL_OUTREACH')
    secondary_outreach = State('SECONDARY_OUTREACH')
    outreach_reply = State('OUTREACH_REPLY')
    inquiry = State('INQUIRY')
    # this is a super state that encapsulates inquiry reply and inquiry of speaker two
    inquiry_super = State('INQUIRY_SUPER')
    inquiry_reply = State('INQUIRY_REPLY')
    giveup_frustrated = State('GIVEUP_FRUSTRATED')
    end = State('END')

    reach_out = start.to(initial_outreach)
    response = initial_outreach.to(outreach_reply) | start.to(outreach_reply)
    no_reply_one = initial_outreach.to(secondary_outreach)
    no_reply_after_second = secondary_outreach.to(giveup_frustrated)
    retry_secondary = secondary_outreach.to(secondary_outreach)
    second_response = secondary_outreach.to(outreach_reply)
    retry_outreach = outreach_reply.to(outreach_reply)
    no_inquiry = outreach_reply.to(giveup_frustrated)
    inquiry_given = outreach_reply.to(inquiry)
    inquiry_response = inquiry.to(inquiry_super)
    retry_inquiry = inquiry.to(inquiry)
    to_next_inquiry = inquiry_super.to(inquiry_reply)
    ignore_after_inquiry = inquiry.to(giveup_frustrated)
    ignore_after_inquiry_two = inquiry_super.to(giveup_frustrated)
    happy_end = inquiry_reply.to(end)
    giveup_end = giveup_frustrated.to(end)
    restart = start.from_(start, initial_outreach, secondary_outreach, outreach_reply, inquiry,
                          inquiry_reply, inquiry_super, giveup_frustrated, end)


class ChatBot: # init here
    def __init__(self, server="irc.freenode.net", channel="#CSC482", botnick="Default-bot"):
        self.bot_state = ChatState()
        self.bot_response = ""
        self.awaiting_response = False
        self.users = set()
        self.target = ""
        self.server = server
        self.channel = channel
        if "-bot" not in botnick[-4:]:
            botnick += "-bot"
        self.botnick = botnick
        self.irc = IRCSocket()
        self.irc.connect(server, channel, botnick)
        self.user_text = ""
        self.retries = 0
        self.spoke_first = None

    def init_bot(self):
        while True:
            text = self.irc.get_response()
            if "JOIN" in text:
                break

            # print(f"{count} output: {text}")

        time.sleep(1)
        self.get_names(debug=True)

    def get_names(self, debug=False):
        names = self.irc.get_names(self.channel)
        names = set([name for name in names if self.botnick not in name])
        self.users |= names

        if debug:
            print(f"printing names: {self.users}")

    def check_msg(self, _text):
        return "PRIVMSG" in _text and self.channel in _text and self.botnick + ":" in _text

    def get_user_text(self, text):
        exp_index = text.find("!")
        who_sent = text[1:exp_index] if exp_index > 0 else ""
        if not self.target:
            self.target = who_sent
        if who_sent != self.target:
            return False

        name_index = text.find(self.botnick)
        self.user_text = text[name_index+len(self.botnick)+1:].strip().lower()  # +1 to get rid of colon

        print(f"{who_sent} said `{self.user_text}`")
        self.check_for_commands()
        return True

    def check_for_commands(self):
        if "die" == self.user_text:
            self.irc.kill_self(self.channel)
            exit()
        elif "forget" == self.user_text:
            self.bot_state.restart()
        else:
            pass

    def get_timed_response(self):
        seconds_elapsed = 0
        text = None
        while seconds_elapsed != 30:
            if seconds_elapsed % 5 == 0:
                print(f"{seconds_elapsed} tries")
            if self.irc.poll_read_response():
                text = self.irc.get_response()
                if text:
                    for line in text.split("\n"):
                        if self.check_msg(line) and self.get_user_text(line):
                            return line
                    text = None
            seconds_elapsed += 1
        return text

    def run_bot(self):
        while True:
            print(f"state: {self.bot_state}")
            # append name list
            self.get_names()
            if self.bot_state.is_start:
                self.start_state()
            elif self.bot_state.is_initial_outreach:
                self.initial_outreach_state()
            elif self.bot_state.is_secondary_outreach:
                self.secondary_outreach_state()
            elif self.bot_state.is_outreach_reply:
                self.outreach_reply_state()
            elif self.bot_state.is_inquiry:
                self.inquiry_state()
            elif self.bot_state.is_inquiry_super:
                self.inquiry_state()
            elif self.bot_state.is_inquiry_reply:
                self.inquiry_reply_state()
            elif self.bot_state.is_giveup_frustrated:
                self.giveup_state()
            elif self.bot_state.is_end:
                self.end_state()
            else:
                print("State error")

    def wait_for_text(self, no_message_func, has_message_func):
        text = self.get_timed_response()  # first 30 seconds
        if text:
            self.awaiting_response = False
            has_message_func()
        else:
            self.awaiting_response = True
            no_message_func()
        return self.awaiting_response

    def start_state(self):
        self.bot_state.reach_out()

    def initial_outreach_state(self):
        # we are always speaker one
        if not self.target:  # TODO remove later
            self.target = ""
        #                                     we are speaker one,          we are speaker two
        self.spoke_first = self.wait_for_text(self.bot_state.no_reply_one, self.bot_state.response)
        if self.spoke_first:
            if not self.target:  # TODO remove too
                self.target = random.choice(list(self.users))
            print(f"reaching out to {self.target}")
            self.irc.send_dm(self.channel, self.target, initial_outreach)

    def secondary_outreach_state(self):
        if self.wait_for_text(self.bot_state.retry_secondary, self.bot_state.second_response):
            self.irc.send_dm(self.channel, self.target, "Hello?????")  # TODO replace with more options
            self.wait_for_text(self.bot_state.no_reply_after_second, self.bot_state.second_response)

    def outreach_reply_state(self):
        if self.spoke_first:  # we are speaker one
            max_retries = 3
            if self.user_text in pairs_outreach.keys():
                resp = get_next_outreach(self.user_text)  # should look like a question
                self.bot_state.inquiry_given()
                self.retries = 0
                self.irc.send_dm(self.channel, self.target, resp)
            elif self.retries <= max_retries:
                resp = "Try again"  # TODO change to enum that has confused phrases
                self.irc.send_dm(self.channel, self.target, resp)
                self.wait_for_text(self.bot_state.retry_outreach, self.bot_state.retry_outreach)
                if self.awaiting_response:
                    return
                self.retries += 1
            else:
                self.bot_state.no_inquiry()
        else:  # we are speaker two
            if self.user_text in pairs_response.keys():
                # hi or hi and question if they asked a question
                resp = get_next_response(self.user_text)
                self.bot_state.inquiry_given()
                if isinstance(resp, tuple):
                    self.bot_response = resp
                    return  # they asked a question; skipping
                else:
                    self.irc.send_dm(self.channel, self.target, resp)
            else:
                # TODO check for unique questions (phase 3)
                resp = "What are you trying to say?"  # TODO change to confused
                self.irc.send_dm(self.channel, self.target, resp)
                self.wait_for_text(self.bot_state.retry_outreach, self.bot_state.retry_outreach)

        # self.irc.send_dm(self.channel, self.target, resp)

    def inquiry_state(self):
        if self.spoke_first:
            # bot just asked a question
            self.wait_for_text(self.bot_state.ignore_after_inquiry, self.bot_state.inquiry_response)
            if self.awaiting_response:
                return
            self.wait_for_text(self.bot_state.ignore_after_inquiry_two, self.bot_state.to_next_inquiry)
            if self.user_text in pairs_response.keys():
                resp = get_next_response(self.user_text)
                # self.bot_state.inquiry_response()
                if isinstance(resp, tuple):
                    answer = resp[0]
                    self.irc.send_dm(self.channel, self.target, answer)  # send reply
            else:
                resp = "What"  # TODO more confused
                self.irc.send_dm(self.channel, self.target, resp)
        elif self.bot_response:
            if isinstance(self.bot_response, tuple):
                answer = self.bot_response[0]
                question = self.bot_response[1]  # question
                self.irc.send_dm(self.channel, self.target, answer)
                time.sleep(3)
                self.irc.send_dm(self.channel, self.target, question)
        else:
            self.wait_for_text(self.bot_state.ignore_after_inquiry, self.bot_state.inquiry_response)
            if self.awaiting_response:
                return
            if self.user_text in pairs_response.keys():
                # question if they asked a question
                resp = get_next_response(self.user_text)
                self.bot_state.to_next_inquiry()
                if isinstance(resp, tuple):
                    answer = resp[0]
                    question = resp[1]  # question
                    self.irc.send_dm(self.channel, self.target, answer)
                    time.sleep(3)
                    self.irc.send_dm(self.channel, self.target, question)
            else:
                self.bot_state.ignore_after_inquiry_two()

    def inquiry_reply_state(self):
        """ get a response from other speaker and head to terminal state """
        # if we speak first
        if self.spoke_first:
            self.bot_state.happy_end()

        # we speak second
        else:
            # TODO: Check for malformed user input / if input is a question
            self.wait_for_text(self.bot_state.happy_end, self.bot_state.happy_end)

    def normalize_response(self):
        # TODO make response same, ie `I'm good` to `i am good`
        pass

    def giveup_state(self):
        self.irc.send_dm(self.channel, self.target, "Well bye then")  # TODO change to enum of frustration
        self.bot_state.giveup_end()

    def end_state(self):
        print("Restarting State machine")  # debug
        self.bot_state.restart()


if __name__ == "__main__":
    main()

