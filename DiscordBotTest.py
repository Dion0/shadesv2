import discord
import asyncio
import random
from Config import DISCORD_TOKEN, DISCORD_TOKEN_TEST
import StrUtil
from Markov import *
import DServerState
import logging
import time

YOURFACE_CHANCE = 0.2

logging.basicConfig(level=logging.INFO)

DISCORD_CHAIN_FILE = 'chain_dataeladdifficult'

states_loaded = False
state_dict = {}


rude_responses = ['how about i slap your shit', 'up yours QuestionMark', 'http://puu.sh/rA91W/79f04a5452.png',
                  '( ° ͜ʖ͡°)╭∩╮', "it's time to stop", 'this human is look very stupid  ༼◥▶ل͜◀◤༽ ', 'dot dot dot',
                  'shut the up', 'http://puu.sh/tthk2/e78e082e8d.jpg', 'Hehe']

PEPE = """

 ▬▬▬▬▬▬▬▬▬▬ஜ۩۞۩ஜ▬▬▬▬▬▬▬▬▬▬▬▬
  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
  ⬛🐸🐸🐸⬛🐸🐸⬛🐸🐸🐸⬛🐸🐸⬛⬛
  ⬛🐸⬛🐸⬛🐸⬛⬛🐸⬛🐸⬛🐸⬛⬛⬛
  ⬛🐸🐸🐸⬛🐸🐸⬛🐸🐸🐸⬛🐸🐸⬛⬛
  ⬛🐸⬛⬛⬛🐸⬛⬛🐸⬛⬛⬛🐸⬛⬛⬛
  ⬛🐸⬛⬛⬛🐸🐸⬛🐸⬛⬛⬛🐸🐸⬛⬛
  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
 ▬▬▬▬▬▬▬▬▬▬ஜ۩۞۩ஜ▬▬▬▬▬▬▬▬▬▬▬▬
"""

client = discord.Client()
# ch = read_chain(DISCORD_CHAIN_FILE)


def got_stdin_data(q):
    asyncio.ensure_future(q.put(sys.stdin.readline()))


@asyncio.coroutine
def bg_task():
    yield from client.wait_until_ready()
    print(111)


async def on_message(message):
    await client.wait_until_ready()
    print(message.channel)

    print(message.server)
    author = message.author
    if author == client.user:
        return

    print(author.id)

    msg_c = message.channel
    msg_serv_id = message.server.id

    msg_lower = message.content.lower()
    # supreme
    if random.random() < 1e-7:
        await client.send_message(message.channel, PEPE)

    if message.content.startswith('.test') and author.name == 'dion' \
            and (state_dict[msg_serv_id].whitelist_mode == state_dict[msg_serv_id].chn_whitelist[msg_c.name]):
        await client.send_message(message.channel, 'beep boop')

    if message.content.startswith('.setcount') and (author.permissions_in(message.channel).manage_server
                                                    or (author.name == 'dion' and author.discriminator == '7338')):
        cnt = message.content.split(' ')
        if len(cnt) == 1:
            return
        cnt = int(cnt[1])
        if cnt > 0:
            state_dict[msg_serv_id].msg_to_reply = cnt
            await client.send_message(message.channel, str(cnt) + ', k')
        else:
            await client.send_message(message.channel, 'ummm not ok')

    """
    User with manage_server permission can use .setmode command
    to set bot to either whitelist mode or blacklist mode.
    Changing the mode also reverses w/b-listed channels so the
    effective list of channels bot can send to remains the same
    use .addchannel in a channel you want to add to w/b-list
    or  .remchannel in a channel you want to remove from w/b-list
    use .bw_debug to print current mode and channels b/w-listed
    """

    if message.content.startswith('.setmode') and author.permissions_in(message.channel).manage_server:
        mode = message.content.split(' ')
        if len(mode) == 1:
            return
        mode = mode[1]
        if mode == 'whitelist':
            if not state_dict[msg_serv_id].whitelist_mode:
                state_dict[msg_serv_id].reverse_mode()
                await client.send_message(message.channel, 'reversed current mode to whitelist')
            else:
                await client.send_message(message.channel, "it's already in whitelist mode, you dumbohed")
        elif mode == 'blacklist':
            if state_dict[msg_serv_id].whitelist_mode:
                state_dict[msg_serv_id].reverse_mode()
                await client.send_message(message.channel, 'reversed current mode to blacklist')
            else:
                await client.send_message(message.channel, "it's already in blacklist mode, good sir")

    if message.content.startswith('.addchannel') and author.permissions_in(message.channel).manage_server:
        state_dict[msg_serv_id].chn_whitelist[message.channel.name] = True
        state_dict[msg_serv_id].save_cfg()
        await client.send_message(message.channel, 'Added this channel to the '
                                       + ['blacklist', 'whitelist'][int(state_dict[msg_serv_id].whitelist_mode)])

    if message.content.startswith('.remchannel') and author.permissions_in(message.channel).manage_server:
        state_dict[msg_serv_id].chn_whitelist[message.channel.name] = False
        state_dict[msg_serv_id].save_cfg()
        await client.send_message(message.channel, 'Removed this channel from the '
                                       + ['blacklist', 'whitelist'][int(state_dict[msg_serv_id].whitelist_mode)])

    if message.content.startswith('.bw_debug') and author.permissions_in(message.channel).manage_server:
        listed_chns = [xkey for xkey, xval in state_dict[msg_serv_id].chn_whitelist.items() if xval]
        tmp_str = (
                    "Current mode is: " +
                    ['blacklist', 'whitelist'][int(state_dict[msg_serv_id].whitelist_mode)] +
                    '\nChannels in the list:\n  ' +
                    ", ".join(listed_chns)
                   )
        await client.send_message(message.channel, tmp_str)

    if msg_lower.startswith('shadesbolt is'):
        msg_str = message.content[11:]
        if len(msg_str):
            if random.random() < YOURFACE_CHANCE:
                await client.send_message(message.channel, 'your face ' + msg_str)
    if msg_lower.startswith('shadesboit is'):
        msg_str = message.content[11:]
        if len(msg_str):
            await client.send_message(message.channel, 'your face ' + msg_str)
    if 'uh oh' == msg_lower or 'uhoh' == msg_lower or 'uh-oh' == msg_lower:
        if (author.name == 'Mortzcent (Apl.De.Ap)') and random.random() < 0.3:
            await client.send_message(message.channel, 'fuk u apl')
        else:
            await client.send_message(message.channel, 'spaghetti-os')
        return
    if 'oh uh' == msg_lower or 'ohuh' == msg_lower or 'oh-uh' == msg_lower:
        await client.send_message(message.channel, rude_responses[random.randint(0, len(rude_responses) - 1)])
        return
    if 'thea-who?' == msg_lower:
        await client.send_message(message.channel, "theano")
        return
    if 'xd' == msg_lower:
        if random.random() < 0.3:
            await client.send_message(message.channel, 'ecksss dee')
        return

    print(str(author) + ":" + message.content)
    if isinstance(msg_c, discord.Channel):
        print(msg_c.name)
        print(msg_c.server)
        print(msg_c.position)
    else:
        for r in msg_c.recipients:
            print(r)
        return

    cur_state = state_dict[msg_serv_id]

    if message.content.startswith('.'):
        return

    msg, valid = StrUtil.sanitizeMessage(message.content, cur_state.can_curse)

    if valid and len(msg.split(' ')) > 1:
        cur_state.msg_counter += 1
        print(cur_state.msg_counter)
        if cur_state.whitelist_mode == cur_state.chn_whitelist[msg_c.name]:
            cur_state.ch.process_sentence(msg)
        if ((cur_state.msg_counter >= cur_state.msg_to_reply)
                and (cur_state.whitelist_mode == cur_state.chn_whitelist[msg_c.name])):
            cur_state.msg_counter = 0
            to_send = await cur_state.ch.gen_sentence()
            await client.send_message(message.channel, to_send, tts=True)
            print('sent: ' + to_send + '| to ' + message.channel.name)
            state_dict[msg_serv_id].save_ch()


@client.event
@asyncio.coroutine
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    global states_loaded
    states_loaded = False
    if not states_loaded:
        serv_d = client.servers
        disambig_f = open('servers_disambig.txt', 'w', encoding='utf-8')
        for s in serv_d:
            """if s.id == '190237393985601536':
                yield from client.change_nickname(s.get_member(client.user.id), '『ShadesBolt』')"""
            print(s.id, ' ', s.name)
            # asdf = yield from client.create_invite(s)
            # print(str(asdf))
            state_dict[s.id] = DServerState.DState(s.id, [x.name for x in s.channels])
            disambig_f.write(s.id + ': ' + s.name + '\n')
            disambig_f.write('\n'.join(['       ' + x.id + ': ' + x.name for x in s.channels]) + "\n")

            # log_f = open('discord_logs/' + s.name + '.txt', 'w', encoding='utf-8')
            # lim = 1000000
            # for c in s.channels:
            #     if c.type != discord.ChannelType.text:
            #         continue
            #     print(c.name)
            #     perm = c.permissions_for(s.get_member(client.user.id))
            #     if perm.read_message_history and perm.read_messages:
            #         cnt = 0
            #         tmp_str = ''
            #         async for message in client.logs_from(c, limit=lim):
            #             tmp_str += message.content + '\n'
            #             cnt += 1
            #         log_f.write(tmp_str)
            #         print(str(cnt) + ' logs for ' + c.name + ' dun.')
            # log_f.close()

        disambig_f.close()
        states_loaded = True

# 『ShadesBolt』
# 189130309814452234

if __name__ == '__main__':
    # q = asyncio.Queue()
    # client.loop.add_reader(sys.stdin, got_stdin_data, q)
    # client.loop.create_task(bg_task())
    # client.run(DISCORD_TOKEN)

    client.run(DISCORD_TOKEN)
