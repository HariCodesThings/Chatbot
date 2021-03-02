from irc_socket import *
import random
import time
from statemachine import StateMachine, State
# import os


# when chatbot is speaker one
initial_outreach = random.choice(["Hi", "Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"])
pairs_outreach = {
    "hi" : ["What's up?", "How's it going", "What's happening?"],
    "hey" : ["What's up?", "How's it going", "What's happening?"],
    "hello" : ["What's up?", "How's it going", "What's happening?"],
    "yo" : ["What's up?", "How's it going", "What's happening?"],
    "hey there" : ["What's up?", "How's it going", "What's happening?"],
    "welcome" : ["What's up?", "How's it going", "What's happening?"],
    "yoooo" : ["What's up?", "How's it going", "What's happening?"]
}


# when chatbot is speaker two
pairs_response = {
    "hi": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hey": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hello": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "hiii":  ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "yo": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "howdy": ["Hello", "Hey there", "Howdy", "Yoooo", "Hey", "Welcome"],
    "what's up": [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                  ("Nothing much", "You?"), ("Great", "What about you?")],
    "how's it going": [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                       ("Nothing much", "You?"), ("Great", "What about you?")],
    "what's happening": [("I'm good", "How are you?"), ("I'm fine, thanks", "And you?"),
                         ("Nothing much", "You?"), ("Great", "What about you?")],
}

get_next_outreach = lambda utterance: random.choice(pairs_outreach[utterance])
get_next_response = lambda utterance: random.choice(pairs_response[utterance])

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
    response = initial_outreach.to(outreach_reply) | start.to(outreach_reply)
    no_reply_one = initial_outreach.to(secondary_outreach)
    no_reply_after_second = secondary_outreach.to(giveup_frustrated)
    second_response = secondary_outreach.to(outreach_reply)
    retry_outreach = outreach_reply.to(outreach_reply)
    no_inquiry = outreach_reply.to(giveup_frustrated)
    inquiry_given = outreach_reply.to(inquiry)
    inquiry_response = inquiry.to(inquiry_reply)
    to_next_inquiry = inquiry_reply.to(inquiry_two)
    to_next_inquiry_reply = inquiry_two.to(inquiry_reply_two)
    ignore_after_inquiry = inquiry.to(giveup_frustrated)
    ignore_after_inquiry_two = inquiry_two.to(giveup_frustrated)
    happy_end = inquiry_reply_two.to(end) | inquiry_reply.to(end)
    giveup_end = giveup_frustrated.to(end)
    restart = start.from_(start, initial_outreach, secondary_outreach, outreach_reply, inquiry, inquiry_reply,
                          inquiry_two, inquiry_reply_two, giveup_frustrated, end)



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
        while self.bot_state != ChatState.end:
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
            elif self.bot_state.is_inquiry_reply:
                self.inquiry_two_state()
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
        # TODO parse put and set target to who replied to you
        return self.awaiting_response

    def start_state(self):
        self.target = ""
                                                 # we are speaker one,    we are speaker two
        self.spoke_first = self.wait_for_text(self.bot_state.reach_out, self.bot_state.response)
        if self.spoke_first:
            self.target = random.choice(list(self.users))
            print(f"reaching out to {self.target}")

    def initial_outreach_state(self):
        # we are always speaker one
        self.irc.send_dm(self.channel, self.target, initial_outreach)  # replace with more options
        self.wait_for_text(self.bot_state.no_reply_one, self.bot_state.response)

    def secondary_outreach_state(self):
        self.irc.send_dm(self.channel, self.target, "Hello?????")  # replace with more options
        self.wait_for_text(self.bot_state.no_reply_after_second, self.bot_state.second_response)

    def outreach_reply_state(self):
        print("In outreach reply state")
        if self.spoke_first:  # we are speaker one
            max_retries = 3
            if self.user_text in pairs_outreach.keys():
                resp = get_next_outreach(self.user_text)  # should look like a question
                self.bot_state.inquiry_given()
            else:
                resp = "Try again"  # TODO change to enum that has confused phrases
                if self.retries <= max_retries:
                    self.wait_for_text(self.bot_state.retry_outreach, self.bot_state.inquiry_given)
                    self.retries += 1
        else:  # we are speaker two
            time.sleep(1)
            if self.user_text in pairs_response.keys():
                resp = get_next_response(self.user_text)  # hi or hi and question if they asked a question
                self.bot_state.inquiry_given()
                if isinstance(resp, tuple):
                    resp = resp[1] # question
                    answer = resp[0]
                    self.irc.send_dm(self.channel, self.target, answer) # send answer
            else:
                # TODO check for unique questions (phase 3)
                resp = "What are you trying to say?"  # TODO change to confused

        self.irc.send_dm(self.channel, self.target, resp)

    def inquiry_state(self):
        print("In inquiry state")
        # bot just asked a question
        self.wait_for_text(self.bot_state.ignore_after_inquiry, self.bot_state.inquiry_response)
        if self.spoke_first and not self.awaiting_response:
            self.wait_for_text(self.bot_state.ignore_after_inquiry,
                               self.bot_state.happy_end)  # return text should be a question
            if self.user_text in pairs_response.keys():
                resp = get_next_response(self.user_text)
                # self.bot_state.inquiry_response()
                if isinstance(resp, tuple):
                    resp = resp[0]

                self.irc.send_dm(self.channel, self.target, resp)  # send im good-like
            else:
                resp = "What" # TODO more confused
                self.irc.send_dm(self.channel, self.target, resp)
        else:
            # done
            # TODO check if text is another question (phase 3)
            self.bot_state.happy_end()
        # self.normalize_response()


    def normalize_response(self):
        # TODO make response same, ie `I'm good` to `i am good`
        pass


    def giveup_state(self):
        self.irc.send_dm(self.channel, self.target, "Well bye then")  # TODO change to enum of frustration
        self.bot_state.giveup_end()

    def end_state(self):
        print("Restarting State machine")  # debug
        self.bot_state.restart()

    def inquiry_two_state(self):
        print("in inquiry two state")
        # respond first

        self.bot_state.restart()  # remove later




if __name__ == "__main__":
    main()

