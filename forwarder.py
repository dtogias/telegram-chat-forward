''' A script to send all messages from one chat to another. '''

import asyncio
import logging

from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.sessions import StringSession
from telethon.tl.patched import MessageService

from binance import binance_job
from settings import API_ID, API_HASH, REPLACEMENTS, forwards, get_forward, update_offset, STRING_SESSION

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def intify(string):
    try:
        return int(string)
    except:
        return string


def replace(message):
    for old,new in REPLACEMENTS.items():
        message.text = str(message.text).replace(old,new)
    return message


async def forward_job():
    ''' the function that does the job 😂 '''
    if STRING_SESSION:
        session = StringSession(STRING_SESSION)
    else:
        session = 'forwarder'

    async with TelegramClient(session, API_ID, API_HASH) as client:

        for forward in forwards:
            from_chat, to_chat, offset = get_forward(forward)

            async for message in client.iter_messages(intify(from_chat), reverse=True, offset_id=offset):
                if isinstance(message, MessageService):
                    continue
                try:
                    await client.send_message(intify(to_chat), replace(message))
                    last_id = str(message.id)
                    logging.info('forwarding message with id = %s', last_id)
                    update_offset(forward, last_id)
                except FloodWaitError as fwe:
                    print(f'{fwe}')
                    await asyncio.sleep(delay=fwe.seconds)
                except Exception as err:
                    logging.exception(err)
                    break

            logging.info('Completed working with %s', forward)


async def main():
    while True:
        await forward_job()
        await binance_job()
        await asyncio.sleep(60)


if __name__ == "__main__":
    assert forwards
    asyncio.run(main())
