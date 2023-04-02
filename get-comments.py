# This is quick and dirty script.
# So there is no appropriate error handling and convenient user IO.
from telethon import TelegramClient
from telethon.tl import functions, types
import os
from os.path import join, dirname
from dotenv import load_dotenv
import json

# Load parameters from environment
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Parameters
SESSION_NAME = "client"
API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH')
CHANNEL_USERNAME = os.environ.get('TELEGRAM_CHANNEL_USERNAME')
MESSAGE_TEXT = os.environ.get('TELEGRAM_CHANNEL_MESSAGE_TEXT')

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
client.start()

async def main():
    # Get the channel entity
    channel = await client.get_entity(CHANNEL_USERNAME)

    # Find messages with specified text, which will be target for fetching comments.
    target_message = await client.get_messages(channel, search=MESSAGE_TEXT)

    # Message not found or more than 1 messages were found.
    if target_message.total != 1:
        raise ValueError("Message not found or more than 1 messages were found. Please be more specific for TELEGRAM_CHANNEL_MESSAGE_TEXT environment variable.")

    # Get message we want to retrieve comments from
    message = await client.get_messages(channel, ids=target_message[0].id)

    # Retrieve all comments to the message
    comments = []
    offset_id = 0
    while True:
        chunk = await client.get_messages(channel, reply_to=message.id, limit=100, offset_id=offset_id)
        if not chunk:
            break
        comments += chunk
        offset_id = comments[-1].id

    # Create a new array with only the desired fields
    result_comments = [{'id': comment.id, 'message': comment.text} for comment in comments]
    
    # Serialize the output array to JSON and write it to a file
    with open('comments.json', 'w') as f:
        json.dump(result_comments, f)

with client:
    client.loop.run_until_complete(main())