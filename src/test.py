from irc_socket import *
import os
import random

## IRC Config
server = "irc.freenode.net" # Provide a valid server IP/Hostname
channel = "#CSC482"
botnick = "Nick"
irc = IRCSocket()
irc.connect(server, channel, botnick)





while True:
    text = irc.get_response()
    print(text)
 
    if self.checkMsg(text) and "hello" in text:
            self.irc.send(self.channel, "Hello!")

    if self.checkMsg(text) and "die" in text:
        self.irc.send(self.channel, "Dying!")
        self.irc.kill_self()
        exit()


def checkMsg(self, text):
    return "PRIVMSG" in text and self.channel in text and self.name in text and ":" in text