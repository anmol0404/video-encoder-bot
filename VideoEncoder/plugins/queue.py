# VideoEncoder - a telegram bot for compressing/encoding videos in h264/h265 format.
# Copyright (c) 2021 WeebTime/VideoEncoder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from urllib.parse import unquote_plus
import signal
import json
import time
from ..config import download_dir

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..state import data
from ..utils.database.add_user import AddUserToDatabase
from ..utils.helper import check_chat

queue_callback_filter = filters.create(
    lambda _, __, query: query.data.startswith('queue+'))


async def get_title(i):
    try:
        if data[i].video:
            return data[i].video.file_name
        elif data[i].document:
            return data[i].document.file_name
        else:
            url = data[i].command[1]
            return str(unquote_plus(os.path.basename(url)))
    except:
        return "Unknown Task"


def map(pos):
    size = len(data)
    buttons = []
    
    # Navigation Row
    nav_row = []
    if pos > 0:
        nav_row.append(InlineKeyboardButton("<< Prev", callback_data=f"q_nav+{pos-1}"))
    nav_row.append(InlineKeyboardButton(f"{pos+1}/{size}", callback_data="q_ignore"))
    if pos < size - 1:
        nav_row.append(InlineKeyboardButton("Next >>", callback_data=f"q_nav+{pos+1}"))
    buttons.append(nav_row)

    # Action Row (Only for non-active tasks i.e., pos > 0)
    if pos > 0:
        action_row = []
        action_row.append(InlineKeyboardButton("🗑️ Del", callback_data=f"q_del+{pos}"))
        if pos > 1:
            action_row.append(InlineKeyboardButton("⬆️ Up", callback_data=f"q_up+{pos}"))
        if pos < size - 1:
            action_row.append(InlineKeyboardButton("⬇️ Down", callback_data=f"q_down+{pos}"))
        buttons.append(action_row)

    # Close Button
    buttons.append([InlineKeyboardButton("Close", callback_data="closeMeh")])
    return buttons


@Client.on_callback_query(filters.regex(r"^q_"))
async def queue_answer(app, cb):
    action, pos = cb.data.split('+')
    pos = int(pos) if pos else 0
    user_id = cb.from_user.id
    
    if action == "q_ignore":
        await cb.answer("Current Position", show_alert=False)
        return

    # Navigation
    if action == "q_nav":
        tasktitle = await get_title(pos)
        await cb.edit_message_text(
            f"<b>Task {pos+1}/{len(data)}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(pos))
        )
        return

    # Authorization Check for Actions
    try:
        task_user_id = data[pos].from_user.id
    except:
        task_user_id = 0 # Should not happen

    # Allow if Sudo, Owner, or Task Owner
    is_authorized = False
    if user_id in sudo_users or user_id in owner:
        is_authorized = True
    elif user_id == task_user_id:
        is_authorized = True
        
    if not is_authorized:
        await cb.answer("❌ Not your task!", show_alert=True)
        return

    # Delete
    if action == "q_del":
        start_time = time.time()
        task = data.pop(pos)
        await cb.answer(f"🗑️ Task #{pos+1} Deleted!", show_alert=True)
        # Refresh current view (stay at pos if valid, else pos-1)
        new_pos = pos if pos < len(data) else pos - 1
        if new_pos < 0: new_pos = 0 
        
        if len(data) == 0:
            await cb.edit_message_text("🥱 No Active Encodes.")
            return

        tasktitle = await get_title(new_pos)
        await cb.edit_message_text(
            f"<b>Task {new_pos+1}/{len(data)}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(new_pos))
        )

    # Move Up
    elif action == "q_up":
        if pos <= 1: return # Cannot move to 0 (Active)
        # Swap with pos-1
        data[pos], data[pos-1] = data[pos-1], data[pos]
        await cb.answer(f"Moved Up to #{pos}!", show_alert=False)
        # Follow the item to new position
        new_pos = pos - 1
        tasktitle = await get_title(new_pos)
        await cb.edit_message_text(
            f"<b>Task {new_pos+1}/{len(data)}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(new_pos))
        )

    # Move Down
    elif action == "q_down":
        if pos >= len(data) - 1: return
        # Swap with pos+1
        data[pos], data[pos+1] = data[pos+1], data[pos]
        await cb.answer(f"Moved Down to #{pos+2}!", show_alert=False)
        # Follow the item to new position
        new_pos = pos + 1
        tasktitle = await get_title(new_pos)
        await cb.edit_message_text(
            f"<b>Task {new_pos+1}/{len(data)}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(new_pos))
        )


@Client.on_message(filters.command(['queue']))
async def queue_message(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    
    if len(data) == 0:
        await message.reply("🥱 No Active Encodes.")
        return

    # Default to showing Active Task (0)
    pos = 0
    tasktitle = await get_title(pos)
    await message.reply_text(
        f"<b>Task {pos+1}/{len(data)}</b>:\n\n{tasktitle}",
        reply_markup=InlineKeyboardMarkup(map(pos))
    )


@Client.on_message(filters.command('clear'))
async def clear(app, message):
    c = await check_chat(message, chat='Sudo')
    if not c:
        await message.reply("Protected! You are not authorized.")
        return
    await AddUserToDatabase(app, message)
    if len(data) >= 1:
        current = data[0]
        data.clear()
        data.append(current)
        await message.reply('Queue cleared! Pending tasks removed.\n(Active task is still running, use /cancel to stop it)')
    else:
        await message.reply("🥱 No Active Encodes.")


@Client.on_message(filters.command('purge'))
async def purge(app, message):
    c = await check_chat(message, chat='Sudo')
    if not c:
        await message.reply("Protected! You are not authorized.")
        return
        
    # Clear Queue
    data.clear()
    
    # Kill Process
    try:
        with open(os.path.join(download_dir, "status.json"), 'r') as f:
            status = json.load(f)
            pid = status.get('pid')
            if pid:
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        pass
        
    await message.reply("♻️ Queue and Active Task PURGED!")
