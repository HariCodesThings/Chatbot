import socket
import sys
import time


class IRCSocket:

    irc = socket.socket()

    def __init__(self):
        # Define the socket
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, channel, msg):
        # Transfer data
        self.irc.send(bytes(f"PRIVMSG {channel} : {msg}\n", "UTF-8"))
        time.sleep(3)

    def connect(self, server, channel, botnick):
        # Connect to the server
        print("Connecting to: " + server)
        self.irc.connect((server, 6667)) #hard code port to 6667

        # Perform user authentication
        self.irc.send(bytes(f"USER {botnick} {botnick} {botnick} :python\n", "UTF-8"))
        self.irc.send(bytes(f"NICK {botnick}\n", "UTF-8"))
        time.sleep(3)

        # join the channel
        self.irc.send(bytes(f"JOIN {channel}\n", "UTF-8"))

    def get_response(self):
        time.sleep(1)
        # Get the response
        resp = self.irc.recv(2040).decode("UTF-8")
        print(resp)

        if resp.find('PING') != -1:
            self.irc.send(bytes('PONG ' + resp.split()[1] + '\r\n', "UTF-8"))
        return resp

    # add kill self functionality as per spec
    def kill_self(self, channel):
        self.irc.send(bytes(f'KILLED ON {channel} /n', "UTF-8"))
        print(f'KILLED ON {channel} /n')
        time.sleep(3)
        self.irc.close()
        return

