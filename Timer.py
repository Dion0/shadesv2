import time
import threading


class Timer(threading.Thread):
    def __init__(self, bot, sleep_time = 15000):
        self.bot = bot
        self.sleep_time = sleep_time
        self.running = True
        threading.Thread.__init__(self)

    def waitAndTrigger(self):
        time.sleep()
        with self.bot.counter_mutex:
            self.bot.msg_counter = self.bot.msg_to_gen

    def stop(self):
        self.running = False
        print('stopping timer')

    def run(self):
        while self.running:
            for i in range(self.sleep_time):
                time.sleep(1)
                if not self.running:
                    break
            if self.running:
                with self.bot.counter_mutex:
                    self.bot.msg_counter = self.bot.msg_to_gen

        print('timer stopped')

