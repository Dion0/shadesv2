import urllib.request
import json
from datetime import datetime


def getChatters(chn):
    url = ('http://tmi.twitch.tv/group/user/' +
           chn + '/chatters')
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        parsed_dict = json.loads(text)
        parsed_dict["succ"] = True
        print(str(datetime.now().time()) + ": got chatters from " + chn)
        return parsed_dict
    except:
        parsed_dict = {"succ" : False}
        print(str(datetime.now().time()) + ": failed to get chatters")
        return parsed_dict
        

def checkLive(chn, last = False):
    url = "https://api.twitch.tv/kraken/streams/" + chn
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        pd = json.loads(text)
        return pd["stream"] is not None
    except:
        print("failed to check if " + chn + " is live")
        return last


def getUser(line):
    try:
        separate = line.split(":", 2)
        user = separate[1].split("!", 1)[0]
    except:
        print('failed to parse user from ' + line)
        user = "oops"
    return user


def getMessage(line):
    try:
        separate = line.split(":", 2)
        message = separate[2]
    except:
        print('failed to parse message from ' + line)
        message = "oops message"
    return message


if __name__ == '__main__':
    getChatters('dionissium')
    print('dun')

