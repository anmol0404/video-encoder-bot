
print("Starting VideoEncoder __init__")
import os
from pyrogram import Client
print("Importing config")
from .config import *
print(f"Imported config. LOGGER is {locals().get('LOGGER')}")

# Client
print("Initializing Client")
app = Client(
    session,
    bot_token=bot_token,
    api_id=api_id,
    api_hash=api_hash,
    plugins={'root': os.path.join(__package__, 'plugins')},
    workers=32,
    max_concurrent_transmissions=4,
    ipv6=False,
    sleep_threshold=30)
print("Client initialized")
