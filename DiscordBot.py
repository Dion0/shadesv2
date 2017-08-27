import discord
import asyncio
import random
from Config import DISCORD_TOKEN, IMGUR_CLIENT_SECRET, IMGUR_CLIENT_ID
import DServerState
import logging
from imgurpython import ImgurClient


YOURFACE_CHANCE = 0.2

logging.basicConfig(level=logging.INFO)

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
imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)


async def get_shibe(msg_c):
    await client.wait_until_ready()
    page_num = random.randint(0, 12)
    link = random.choice(imgur_client.gallery_search('shiba inu', page=page_num)).link
    print(link)
    await client.send_message(msg_c, link)


async def imgur_search(msg_c, msg):
    await client.wait_until_ready()
    request = msg.split(' ', )[1]
    imgur_list = []
    upper_bound = 100
    while not bool(imgur_list) and upper_bound >= 0:
        page_num = random.randint(0, upper_bound)
        upper_bound = page_num - 1
        imgur_list = imgur_client.gallery_search(request, page=page_num)
    if bool(imgur_list):
        link = random.choice(imgur_list).link
        link = 'img from page {}\n'.format(page_num) + link
    else:
        link = 'theres no such thing on imgur'
    print(link)
    await client.send_message(msg_c, link)

async def proc_msg(cur_state, msg, msg_c, message):
    await client.wait_until_ready()
    if cur_state.whitelist_mode == cur_state.chn_whitelist[msg_c.name]:
        to_send = await cur_state.process_msg(msg, msg_c.name)
        if to_send != '':
            await client.send_message(message.channel, to_send)
            print('sent: ' + to_send + '| to ' + message.channel.name)

async def force_msg(cur_state, message):
    await client.wait_until_ready()
    to_send = await cur_state.get_sample()
    await client.send_message(message.channel, to_send)


@client.event
async def on_message(message):
    await client.wait_until_ready()
    print(message.channel)

    print(message.server)
    author = message.author
    if author == client.user:
        return

    print(str(author) + ":" + message.content)
    if isinstance(message.channel, discord.Channel):
        print(message.channel.name)
        print(message.server)
        # print(msg_c.position)
    else:
        for r in message.channel.recipients:
            print(r.id)
        if message.author.id == '171777527923081219':
            if message.content.startswith('.log'):
                s_id = message.content.split(' ')[1]
                serv_to_log = client.get_server(s_id)
                client.loop.create_task(log_server(serv_to_log))
                await client.send_message(message.channel, 'logging server: ' + str(serv_to_log))
        return

    # print(author.id)

    msg_c = message.channel
    msg_serv_id = message.server.id
    cur_state = state_dict[msg_serv_id]

    msg_lower = message.content.lower()
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
        if cnt[1].isdigit():
            cnt = int(cnt[1])
        else:
            return

        if cnt > 0:
            state_dict[msg_serv_id].set_reply_rate(cnt)
            await client.send_message(message.channel, str(cnt) + ', k')
        else:
            await client.send_message(message.channel, 'ummm not ok')

    if message.content.startswith('.bolt_help') and author.permissions_in(message.channel).manage_server:
        await client.send_message(message.channel,
            """
            User with manage_server permission can use .setmode command
            to set bot to either whitelist mode or blacklist mode.
            Changing the mode also reverses w/b-listed channels so the
            effective list of channels bot can send to remains the same
            use .addchannel in a channel you want to add to w/b-list
            or  .remchannel in a channel you want to remove from w/b-list
            use .bw_debug to print current mode and channels b/w-listed
            """)

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

    if message.content.startswith('.addchannel') and (author.permissions_in(message.channel).manage_server 
        or (author.name == 'dion' and author.discriminator == '7338')):
        state_dict[msg_serv_id].chn_whitelist[message.channel.name] = True
        state_dict[msg_serv_id].save_cfg()
        await client.send_message(message.channel, 'Added this channel to the '
                                       + ['blacklist', 'whitelist'][int(state_dict[msg_serv_id].whitelist_mode)])

    if message.content.startswith('.remchannel') and (author.permissions_in(message.channel).manage_server 
        or (author.name == 'dion' and author.discriminator == '7338')):
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

    if msg_lower.startswith('.shibe'):
        print('needashibe')
        client.loop.create_task(get_shibe(msg_c))
        return

    if msg_lower.startswith('.imgur'):
        print('searching imgur')
        client.loop.create_task(imgur_search(msg_c, msg_lower))
        return

    if client.user.mentioned_in(message):
        client.loop.create_task(force_msg(cur_state, message))


    if message.author.id == '171777527923081219':
        if message.content.startswith('.make it boy'):
            client.loop.create_task(force_msg(cur_state, message))

    if message.content.startswith('.'):
        return

    msg = message.content
    print(cur_state.msg_counter)

    client.loop.create_task(proc_msg(cur_state, msg, msg_c, message))
    return


def init_server(s):
    print(s.id, ' ', s.name)
    state_dict[s.id] = DServerState.DState(s.id, [x.name for x in s.channels])
    disambig_f = open('info/servers_disambig.txt', 'a', encoding='utf-8')
    disambig_f.write(s.id + ': ' + s.name + '\n')
    disambig_f.write('\n'.join(['       ' + x.id + ': ' + x.name for x in s.channels]) + "\n")
    disambig_f.close()


async def get_invite(s):
    inv = await client.create_invite(s, unique=False)
    print(inv.url)


async def log_server(s):
    log_f = open('discord_logs/' + s.name + '.txt', 'w', encoding='utf-8')
    lim = 1000000
    for c in s.channels:
        if c.type != discord.ChannelType.text:
            continue
        print(c.name)
        perm = c.permissions_for(s.get_member(client.user.id))
        if perm.read_message_history and perm.read_messages:
            cnt = 0
            tmp_str = ''
            async for message in client.logs_from(c, limit=lim):
                tmp_str += message.content + '\n'
                cnt += 1
            log_f.write(tmp_str)
            print(str(cnt) + ' logs for ' + c.name + ' dun.')
    log_f.close()


@client.event
async def on_channel_delete(channel):
    serv_id = channel.server.id
    state_dict[serv_id].delete_chn(channel.name)
    print('delete ', channel.name)


@client.event
async def on_channel_create(channel):
    if channel.type != discord.ChannelType.text:
        return
    serv_id = channel.server.id
    state_dict[serv_id].add_chn(channel.name)
    print('added ', channel.name)


@client.event
async def on_channel_update(before, after):
    serv_id = before.server.id
    state_dict[serv_id].replace_chn(before.name, after.name)
    print(before.name, ' => ', after.name)


@client.event
async def on_server_join(server):
    print('\n', '------------------')
    print('Joined server: ', server.name, ' (', server.id, ')')
    print('------------------', '\n')
    init_server(server)


@client.event
async def on_server_remove(server):
    print('\n', '------------------')
    print('Left server: ', server.name, ' (', server.id, ')')
    print('------------------', '\n')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    global states_loaded

    if not states_loaded:
        serv_d = client.servers
        disambig_f = open('info/servers_disambig.txt', 'w', encoding='utf-8')
        disambig_f.close()
        for s in serv_d:
            init_server(s)

        states_loaded = True


if __name__ == '__main__':

    client.run(DISCORD_TOKEN)
