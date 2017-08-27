import random
import pickle
import sys
import re

DEF_STR = "#@!"
SAVE_PREFIX = "chain_data"

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


class Word:

    def __init__(self, st = DEF_STR):
        self.cnt = 1
        self.chance = 0.0
        self.st = st

    def isNil(self):
        return self.st == DEF_STR


def insert_sorted(ls, st):
    if len(ls) == 0:
        ls.append(Word(st))
        return
    for i in range(len(ls)):
        if st == ls[i].st:
            ls[i].cnt += 1.0
            j = i - 1
            while j > 0 and ls[j].cnt < ls[j + 1].cnt:
                ls[j], ls[j + 1] = ls[j + 1], ls[j]
                j -= 1
            return
    ls.append(Word(st))


def upd_chances(ls, total_cnt):
    for wd in ls:
        wd.chance = wd.cnt / total_cnt

class Chain:

    def __init__(self):
        #tmp_w = Word()
        self.words = {DEF_STR : [0,[]]}

    def add_word(self, wd, key = DEF_STR):
        if key in self.words.keys():
            self.words[key][0] += 1.0
        else:
            self.words[key] = [1.0, []]
        insert_sorted(self.words[key][1], wd)
        upd_chances(self.words[key][1], self.words[key][0])

    def process_sentence(self, inp):
        if inp.startswith("!"):
            return
        l1 = re.split(r'[\.!?]\s', inp)
        for sentence in l1:
            tmp_l = sentence.split(' ')
            if len(tmp_l) <= 1:
                continue
            prev_st = tmp_l[0]
            self.add_word(tmp_l[0])
            tmp_l.pop(0)
            for st in tmp_l:
                self.add_word(st, prev_st)
                prev_st = st
            self.add_word(DEF_STR, prev_st)

    def gen_response(self, inp):
        assert isinstance(inp, str)
        words = inp.split(' ')
        print(words)
        seed = random.choice(words)
        print(seed)
        ans = self.gen_sentence(seed)
        print(ans)
        return ans



    def gen_random_wd(self, key = DEF_STR):
        if not(key in self.words.keys()):
            return DEF_STR
        rnd = random.random()
        ttl_chance = 0.0
        for wd in self.words[key][1]:
            ttl_chance += wd.chance
            if rnd < ttl_chance:
                return wd.st
        return "~"

    def gen_sentence(self, key = DEF_STR):
        if key != DEF_STR:
            res = key + " "
        else:
            res = ""
        next_w = self.gen_random_wd(key)
        if next_w != DEF_STR:
            res += next_w
        while next_w != DEF_STR:
            next_w = self.gen_random_wd(next_w)
            if (next_w != DEF_STR):
                res += " " + next_w
        #print(res.translate(non_bmp_map))
        while len(res.split(' ')) > 12 or re.search(r'child porn', res, re.IGNORECASE):
            res = self.gen_sentence()

        return res.lstrip()

    def deb(self):
        for key in self.words.keys():
            print(key)
            for wd in self.words[key][1]:
                print(("     " + wd.st + "    "
                       +  str(wd.chance)).translate(non_bmp_map))

    def write_txt(self, filename = 'chain.txt'):
        f_out = open(filename, 'w', encoding = 'utf-8')
        tmp_ls = sorted(self.words)
        for key in tmp_ls:
            f_out.write(key.translate(non_bmp_map))
            for wd in self.words[key][1]:
                f_out.write((" " + wd.st + " ").translate(non_bmp_map))
                f_out.write(str(wd.cnt))
            f_out.write('\n')

    def read_txt(filename = 'chain.txt'):
        f_out = open(filename, 'r', encoding = 'utf-8')
        ch = Chain()
        inp = f_out.read()
        ls = inp.split('\n')
        for line in ls:
            words = line.split(' ')
            key = words[0]
            words.pop(0)
            ch.words[key] = [0.0, []]
            i = 0
            key_cnt = 0
            while i < len(words):
                t_wd = Word(words[i])
                t_wd.cnt = float(words[i + 1])
                key_cnt += t_wd.cnt
                ch.words[key][1].append(t_wd)
                i += 2
            ch.words[key][0] = key_cnt
            upd_chances(ch.words[key][1], key_cnt)
        return ch
            

def write_chain(chn, filename = SAVE_PREFIX):
    chFile = open(filename, 'wb')
    pickle.dump(chn, chFile)
    chFile.close()


def read_chain(filename = SAVE_PREFIX):
    try:
        chFile = open(filename, 'rb')
        chn = pickle.load(chFile)
        chFile.close()
    except:
        chn = Chain()
    return chn

if __name__ == "__main__":
    ch = read_chain('chain_dataeladdifficult')
    #write_chain(ch, 'chain_datadionissium')
    sen = ch.gen_sentence('not')
    print(sen)

    print("done")

