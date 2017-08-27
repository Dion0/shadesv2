import sys
import re

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
link_check = re.compile(
    r'(^(?:http|ftp)s?://)?(?:\S+\.)+\S+(?:/\S*)*/*\s?',
    re.IGNORECASE
    )

curse_check = re.compile(
    r'\b(?:fuck|bitch|asshole|cunt|damn|shit|motherfuck)\w*\b',
    re.IGNORECASE
)

cmd_check = re.compile(
    r'\b(?:stop|msg|save|stop_no_save|msg_ovr|force)\s+[a-z0-9_]{3,}(?:\s\S)*',
    re.IGNORECASE
)


def translate(str):
    return str.translate(non_bmp_map)


def sanitizeMessage(msg, curses = True):
    valid = False
    msg = link_check.sub("" , msg)
    if not curses:
        msg = curse_check.sub("CatBag", msg)
    msg = msg.strip()
    if len(msg) > 0:
        valid = True

    return msg, valid


def isValidCommand(cmd):
    if cmd_check.match(cmd):
        return True
    else:
        return False


if __name__ == '__main__':
    inp = input()
    print(sanitizeMessage(inp, False))
