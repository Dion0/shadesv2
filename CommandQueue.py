import threading


class CommandQueue:
    def __init__(self):
        self.queue = []
        self.mutex = threading.RLock()

    def put(self, c_str):
        with self.mutex:
            self.queue.append(c_str)

    def getLen(self):
        with self.mutex:
            return len(self.queue)

    def getQueue(self):
        return self.queue