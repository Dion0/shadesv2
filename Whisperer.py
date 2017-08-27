import socket, json, urllib.request as urlreq, time
import Bot, MessageReceiver, StrUtil
from Config import PASS, HOST, NICK

CHAT_ROOM_URL = r'http://chatdepot.twitch.tv/room_memberships?oauth_token='

class Whisperer(Bot.Bot):
    def __init__(self,  msg_mutex, command_queue, oauth = PASS[6:]):
        self.oauth = oauth
        self.membership_dict = None
        self.irc_channel = ''
        Bot.Bot.__init__(self, msg_mutex, command_queue, '')

    def getRoomInfo(self):
        response = urlreq.urlopen(CHAT_ROOM_URL + self.oauth)
        data = response.read()
        text = data.decode('utf-8')
        self.membership_dict = json.loads(text)
        if ('errors' in self.membership_dict.keys()):
            return False
        try:
            self.membership_dict = self.membership_dict['memberships']
            self.irc_channel = self.membership_dict[0]['room']['irc_channel']
        except:
            print('u are a fucking retard')
        return True

    #Override
    def openSocket(self):
        if not self.getRoomInfo():
            return None
        s = socket.socket()
        s.connect((HOST, 80))
        s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        s.send("JOIN #{}\r\n".format(self.irc_channel).encode("utf-8"))
        return s

    #Override
    def sendMessage(self, target_user, msg):
        t_str = "PRIVMSG #jtv :/w {0} {1}\r\n".format(target_user, msg)
        with self.msg_mutex:
            self.socket.send(t_str.encode("utf-8"))
            time.sleep(1.5)
        print(t_str)

    #Override
    def run(self):
        print('starting wisp')
        self.joinRoom()
        self.running = True
        self.msg_receiver = MessageReceiver.MessageReceiver(self.socket, self.msg_mutex)

        self.msg_counter = 0
        self.msg_override = False
        self.msg_receiver.start()
        self.socket.send('CAP REQ :twitch.tv/commands\r\n'.encode('utf-8'))

        # self.sendMessage('dionissium', 'hey')

        while self.running:
            while (self.msg_receiver.hasMessage()):
                user, message = self.msg_receiver.getMessage()
                msg_sanitized, isvalid = StrUtil.sanitizeMessage(message, self.can_curse)
                print(user + ": " + msg_sanitized)
                if user == 'dionissium' and message.startswith('fuck you'):
                    self.running = False
            time.sleep(0.10)

        print('stopping different things')
        self.msg_receiver.stop()
        self.msg_receiver.join()
        self.socket.close()
        print('stopped ' + self.irc_channel)


if __name__ == '__main__':
    pass


