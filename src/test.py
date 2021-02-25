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
 
    if "PRIVMSG" in text and channel in text and "hello" in text:
        irc.send(channel, "Hello!")
    
    if "PRIVMSG" in text and channel in text and "die" in text:
        irc.send(channel, "Dying!")
        irc.kill_self(channel)
        exit()