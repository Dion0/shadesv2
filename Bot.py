import threading
import socket
import time
import StrUtil
import Timer
import CommandQueue
import MessageReceiver
import re
from Config import HOST, PORT, PASS, NICK
from Markov import *
from TwitchUtil import *

IGNORELIST = ['nightbot', 'fubzdj', 'mikuia', 'moobot', 'twitchnotify', 'hairclubbot']
RESPONSE_CHANCE = 0.3
RESPONSE_TIMEOUT = 120
RESPONSE_LAST = -RESPONSE_TIMEOUT

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


class Gender:
    def __init__(self, name):
        self.g = name


class Bot(threading.Thread):
    def __init__(self, _msg_mutex, command_queue, channel="dionissium",
                 msg_to_gen=500, can_chat=True, can_curse=False, is_logging=False):
        self.channel = channel
        self.is_logging = is_logging
        self.can_curse = can_curse
        self.can_chat = can_chat

        self.socket = None

        self.com_q = command_queue
        self.msg_mutex = _msg_mutex
        self.chain = Chain()

        self.msg_override = False
        self.msg_to_gen = msg_to_gen
        self.msg_counter = 0
        self.counter_mutex = threading.RLock()
        self.timer = Timer.Timer(self)
        self.gender = Gender('Male')

        self.msg_receiver = None

        self.running = False

        self.msg_str = ""

        threading.Thread.__init__(self)

    def openSocket(self):
        s = socket.socket()
        s.connect((HOST, PORT))
        s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        s.send("JOIN #{}\r\n".format(self.channel).encode("utf-8"))
        return s

    def sendMessage(self, msg):
        if self.can_chat:
            t_str = "PRIVMSG #{0} :{1}\r\n".format(self.channel, msg)
            with self.msg_mutex:
                self.socket.send(t_str.encode("utf-8"))
                time.sleep(1.5)
            print(t_str)

    def processCmd(self, cmd):
        pass

    # Override
    def run(self):
        self.joinRoom()
        self.running = True
        self.msg_receiver = MessageReceiver.MessageReceiver(self.socket, self.msg_mutex)

        chain = self.chain = read_chain(SAVE_PREFIX + self.channel)
        self.msg_counter = 0
        self.msg_override = False
        self.timer.start()
        self.msg_receiver.start()

        while self.running:
            to_send = ''
            with self.com_q.mutex:
                for i in range(len(self.com_q.queue)):
                    cmd = self.com_q.queue[i]
                    cmd_ar = cmd.split(' ', 2)
                    if cmd_ar[1] == self.channel:
                        self.com_q.queue.pop(i)
                        if 'msg' == cmd_ar[0]:
                            self.msg_override = True
                            with self.counter_mutex:
                                self.msg_counter = self.msg_to_gen
                            to_send = cmd_ar[min(2, len(cmd_ar) - 1)]
                        elif 'stop' == cmd_ar[0]:
                            print('manually stopping ' + self.channel)
                            self.running = False
                            break
                        elif 'msg_ovr' == cmd_ar[0]:
                            self.sendMessage(cmd_ar[min(2, len(cmd_ar) - 1)])
                        elif 'save' == cmd_ar[0]:
                            write_chain(chain, SAVE_PREFIX + self.channel)
                        elif 'force' == cmd_ar[0]:
                            with self.counter_mutex:
                                self.msg_counter = self.msg_to_gen
                            to_send = StrUtil.sanitizeMessage(chain.gen_sentence(), self.can_curse)

            while self.msg_receiver.hasMessage():
                user, message = self.msg_receiver.getMessage()

                if user.lower() in IGNORELIST:
                    continue
                message, isvalid = StrUtil.sanitizeMessage(message, self.can_curse)
                self.msg_str += user + ': ' + message + "\n"
                if re.search(r'!shades off', message, re.IGNORECASE) and user.lower() == self.channel:
                    self.sendMessage('( -ᴗ-)')
                    self.can_chat = False
                if re.search(r'!shades on', message, re.IGNORECASE) and user.lower() == self.channel:
                    self.can_chat = True
                    self.sendMessage('( •ᴗ•)')

                if re.search(r'!bet', message, re.IGNORECASE):
                    if random.random() < 0.1:
                        self.sendMessage('incnone wins, stop')
                if re.search(r'@shadesbolt', message, re.IGNORECASE):
                    message = re.sub('@shadesbolt', '', message, flags=re.IGNORECASE).strip()
                    tmp = time.clock()
                    global RESPONSE_LAST
                    if tmp - RESPONSE_LAST >= RESPONSE_TIMEOUT:
                        self.sendMessage('@' + user + ' ' + self.chain.gen_response(message))
                        RESPONSE_LAST = tmp

                pls_response = re.search(r'^(shadesbolt|shades|bolt|bot)\spls', message, re.IGNORECASE)
                if pls_response:
                    self.sendMessage(user + ' pls')

                if isvalid:
                    chain.process_sentence(message)
                    with self.counter_mutex:
                        self.msg_counter += 1

            with self.counter_mutex:
                if self.msg_counter >= self.msg_to_gen:
                    with open("logs/" + self.channel + '.txt', 'a', encoding="utf-8") as flog:
                        flog.write(self.msg_str)
                        self.msg_str = ""
                    # print(self.msg_str)
                    if self.msg_override:
                        self.msg_override = False
                    else:
                        to_send = chain.gen_sentence()
                    to_send, valid = StrUtil.sanitizeMessage(to_send, self.can_curse)
                    if valid:
                        print(checkLive(self.channel))
                        self.sendMessage(to_send)
                    else:
                        print(checkLive(self.channel))
                        print(valid)
                    write_chain(chain, SAVE_PREFIX + self.channel)
                    self.msg_counter = 0
            time.sleep(0.10)

        write_chain(chain, SAVE_PREFIX + self.channel)
        print('stopping different things')
        self.msg_receiver.stop()
        self.timer.stop()
        self.msg_receiver.join()
        self.timer.join()
        self.socket.close()
        print('stopped ' + self.channel)

    def stop(self):
        self.running = False

    def joinRoom(self):
        self.socket = self.openSocket()
        read_buffer = ""
        Loading = True
        while Loading:
            read_buffer = read_buffer + self.socket.recv(1024).decode("utf-8")
            temp = read_buffer.split("\n")
            read_buffer = temp.pop()
            for line in temp:
                # print(line)
                Loading = self.loadingComplete(line)
        # self.sendMessage("CatBag")

    def loadingComplete(self, line):
        if "End of /NAMES list" in line:
            return False
        else:
            return True


if __name__ == '__main__':
    msg_mutex = threading.RLock()
    cm_q = CommandQueue.CommandQueue()

    chn = input()
    bot = Bot(msg_mutex, cm_q, chn)
    bot.start()
    bot.join()
