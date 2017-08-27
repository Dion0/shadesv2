import subprocess
import os
import shutil

CFG_PREFIX = "cfg/discord_"
CFG_POSTFIX = ".cfg"
rnn_prefix = r'rnn2/'

DEF_msg_to_reply = 69
DEF_whitelist_mode = False
DEF_chn_whitelist = []
DEF_save = 'saves/default'


class DState:
    def __init__(self, serv_id="", chn_list=()):
        self.id = serv_id
        self.can_curse = False

        self.msg_to_reply = 0
        self.msg_counter = 0
        self.chn_whitelist = {i: False for i in chn_list}
        self.whitelist_mode = False
        self.buf_str = ''
        self.save_dir = 'saves/{}'.format(self.id)

        self.load_cfg()

    """

    CFG FILE FORMAT:
    number of messages to trigger response
    bool - is it a whitelist-mode server?
    names of whitelisted channels separated by spaces

    """

    def load_cfg(self):
        filename = CFG_PREFIX + self.id + CFG_POSTFIX

        if not os.path.isdir(self.save_dir):
            print('no save dir for ' + self.save_dir)
            # os.mkdir(save_dir)
            shutil.copytree(DEF_save, self.save_dir)

        try:
            cfg_file = open(filename, 'r')
            t_s = cfg_file.readline()
            self.msg_to_reply = int(t_s)
            print(self.msg_to_reply)
            self.whitelist_mode = int(cfg_file.readline()) == 1
            print(self.whitelist_mode)
            tmp = cfg_file.readline().strip().split(' ')
            print('tmp =  |', tmp)
            for i in tmp:
                self.chn_whitelist[i] = True
            print(self.chn_whitelist)
            self.can_curse = bool(cfg_file.readline())
            cfg_file.close()
        except FileNotFoundError:
            print('loading default dstate for ' + self.id + ' and creating a cfg file')
            self.msg_to_reply = DEF_msg_to_reply
            print(self.msg_to_reply)
            self.whitelist_mode = DEF_whitelist_mode
            print(self.whitelist_mode)
            self.chn_whitelist = DEF_chn_whitelist
            print(self.chn_whitelist)
            self.save_cfg()

    def save_cfg(self):
        filename = CFG_PREFIX + self.id + CFG_POSTFIX
        cfg_file = open(filename, 'w')
        cfg_file.write(str(self.msg_to_reply) + '\n')
        cfg_file.write(str(int(self.whitelist_mode))
                       + '\n')
        tmp_list = [xkey for xkey, xval in self.chn_whitelist.items() if xval]
        print(tmp_list)
        tmp_str = " ".join(tmp_list).strip()
        print(tmp_str)
        cfg_file.write(" ".join(tmp_list).strip())
        cfg_file.write("\n" + str(self.can_curse))

        print('saved config for ' + self.id)

    def replace_chn(self, prev_c, new_c):
        tmp_bool = self.whitelist_mode
        if prev_c in self.chn_whitelist.keys():
            tmp_bool = self.chn_whitelist[prev_c]
            del self.chn_whitelist[prev_c]
        self.chn_whitelist[new_c] = tmp_bool

    def delete_chn(self, chn):
        if chn in self.chn_whitelist.keys():
            del self.chn_whitelist[chn]

    def add_chn(self, chn):
        self.chn_whitelist[chn] = self.whitelist_mode

    def reverse_mode(self):
        self.whitelist_mode = not self.whitelist_mode
        print(self.chn_whitelist)
        self.chn_whitelist = not self.chn_whitelist
        print(self.chn_whitelist)
        self.save_cfg()

    async def process_msg(self, msg, chn_name):
        assert isinstance(msg, str)
        self.buf_str += msg + '\n'
        self.msg_counter += 1
        if (self.msg_counter >= self.msg_to_reply) \
                and (self.whitelist_mode == self.chn_whitelist[chn_name]):
            self.msg_counter = 0
            ans = await self.get_sample()
            # tmp_len = len(self.buf_str)
            self.buf_str = ans + '\n'
            return ans
        else:
            return ''
    
    async def get_sample(self):
        self.buf_str = self.buf_str.encode('ascii', errors='ignore').decode('utf-8')
        if self.buf_str == '':
            self.buf_str = ' '

        cmd1 = ['python3', rnn_prefix + 'sample.py', '-n=110',
                '--prime={}'.format(self.buf_str), '--save_dir={}'.format(self.save_dir)]
        res = subprocess.run(cmd1, stdout=subprocess.PIPE)
        res_str = res.stdout.decode('utf-8')[len(self.buf_str):]
        res_str = res_str.strip('\n')
        res_ans = res_str.split('\n')[0]
        print(res_ans)
        print('asdf')
        return res_ans

    def set_reply_rate(self, cnt):
        self.msg_to_reply = cnt
        self.save_cfg()


if __name__ == '__main__':
    # state = DState('121537716566360064')
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(state.get_sample())
    # loop.close()
    pass
