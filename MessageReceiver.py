import threading
import select
from TwitchUtil import *


class MessageReceiver(threading.Thread):
    def __init__(self, socket, msg_mutex):
        self.socket = socket
        self.msg_mutex = msg_mutex

        self.queue_mutex = threading.RLock()
        self.msg_queue = []

        self.running = True
        threading.Thread.__init__(self)

    def hasMessage(self):
        with self.queue_mutex:
            return len(self.msg_queue) > 0

    def getMessage(self):
        with self.queue_mutex:
            if len(self.msg_queue) > 0:
                return self.msg_queue.pop()
            else:
                return ""

    def stop(self):
        self.running = False
        print('stopping receiver ')

    def run(self):
        read_buffer = ""
        self.socket.setblocking(0)
        while self.running:
            ready = select.select([self.socket], [], [], 0.5)
            if not ready[0]:
                continue

            read_buffer = read_buffer + self.socket.recv(1024).decode("utf-8")
            temp = read_buffer.split("\n")
            read_buffer = temp.pop()
            for line in temp:
                if line.startswith('PING :tmi.twitch.tv'):
                    print(line)
                    with self.msg_mutex:
                        self.socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                    break

                user = getUser(line)
                message = getMessage(line)
                with self.queue_mutex:
                    self.msg_queue.append((user, message))

        self.socket.setblocking(1)
        print('receiver stopped')
