
import json
import os
import asyncio
from typing import List
from pyrogram.types import Message

class PersistentList(list):
    def __init__(self, filename, *args):
        super().__init__(*args)
        self.filename = filename

    def append(self, item):
        super().append(item)
        self.save()

    def remove(self, item):
        super().remove(item)
        self.save()

    def pop(self, index=-1):
        item = super().pop(index)
        self.save()
        return item
        
    def clear(self):
        super().clear()
        self.save()

    def save(self):
        queue_data = []
        for message in self:
            if isinstance(message, Message):
                queue_data.append({
                    'chat_id': message.chat.id,
                    'message_id': message.id
                })
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(queue_data, f, indent=4)
        except Exception as e:
            print(f"Error saving queue: {e}")

    async def load_from_valid_client(self, client):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, 'r') as f:
                queue_data = json.load(f)
            
            for item in queue_data:
                try:
                    # Fetching messages one by one to reconstruct state
                    # Note: This might hit rate limits if queue is huge, but for <10 items it's fine.
                    msg = await client.get_messages(item['chat_id'], item['message_id'])
                    if msg:
                        super().append(msg)
                except Exception as e:
                    print(f"Error fetching message {item['message_id']}: {e}")
            
            # If load succeeds, trigger processing if needed (logic to be handled by caller)
        except Exception as e:
            print(f"Error loading queue JSON: {e}")
