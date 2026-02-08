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

from ..state import data, running_tasks
from ..utils.database.add_user import AddUserToDatabase
from ..utils.helper import check_chat, owner, sudo_users

queue_callback_filter = filters.create(
    lambda _, __, query: query.data.startswith('queue+'))


async def get_task_at_pos(i):
    num_running = len(running_tasks)
    if i < num_running:
        return running_tasks[i], "Active"
    else:
        return data[i - num_running], "Queue"

async def get_title(i):
    try:
        task, status = await get_task_at_pos(i)
        if task.video:
            title = task.video.file_name
        elif task.document:
            title = task.document.file_name
        else:
            url = task.text.split(None, 1)[1]
            title = unquote_plus(os.path.basename(url))
        return f"[{status}] {title}"
    except:
        return "Unknown Task"


def map(pos):
    num_running = len(running_tasks)
    total_size = num_running + len(data)
    buttons = []
    
    # Navigation Row
    nav_row = []
    if pos > 0:
        nav_row.append(InlineKeyboardButton("<< Prev", callback_data=f"q_nav+{pos-1}"))
    nav_row.append(InlineKeyboardButton(f"{pos+1}/{total_size}", callback_data="q_ignore"))
    if pos < total_size - 1:
        nav_row.append(InlineKeyboardButton("Next >>", callback_data=f"q_nav+{pos+1}"))
    buttons.append(nav_row)

    # Action Row (Only for non-active tasks i.e., pos >= num_running)
    if pos >= num_running:
        action_row = []
        # Calculate real pos in 'data'
        data_pos = pos - num_running
        action_row.append(InlineKeyboardButton("🗑️ Del", callback_data=f"q_del+{pos}"))
        if data_pos > 0:
            action_row.append(InlineKeyboardButton("⬆️ Up", callback_data=f"q_up+{pos}"))
        if data_pos < len(data) - 1:
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
        num_running = len(running_tasks)
        total_size = num_running + len(data)
        tasktitle = await get_title(pos)
        await cb.edit_message_text(
            f"<b>Task {pos+1}/{total_size}</b>:\n\n{tasktitle}",
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

    num_running = len(running_tasks)
    total_size = num_running + len(data)

    # Delete
    if action == "q_del":
        if pos < num_running:
            await cb.answer("❌ Cannot delete an Active task!", show_alert=True)
            return
            
        data.pop(pos - num_running)
        await cb.answer(f"🗑️ Task Deleted!", show_alert=True)
        
        new_totalSize = num_running + len(data)
        if new_totalSize == 0:
            await cb.edit_message_text("🥱 No Active Encodes.")
            return

        new_pos = pos if pos < new_totalSize else new_totalSize - 1
        if new_pos < 0: new_pos = 0 
        
        tasktitle = await get_title(new_pos)
        await cb.edit_message_text(
            f"<b>Task {new_pos+1}/{new_totalSize}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(new_pos))
        )

    # Move Up
    elif action == "q_up":
        data_pos = pos - num_running
        if data_pos <= 0: return 
        # Swap
        data[data_pos], data[data_pos-1] = data[data_pos-1], data[data_pos]
        await cb.answer(f"Moved Up!", show_alert=False)
        new_pos = pos - 1
        tasktitle = await get_title(new_pos)
        await cb.edit_message_text(
            f"<b>Task {new_pos+1}/{total_size}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(new_pos))
        )

    # Move Down
    elif action == "q_down":
        data_pos = pos - num_running
        if data_pos >= len(data) - 1: return
        # Swap
        data[data_pos], data[data_pos+1] = data[data_pos+1], data[data_pos]
        await cb.answer(f"Moved Down!", show_alert=False)
        new_pos = pos + 1
        tasktitle = await get_title(new_pos)
        await cb.edit_message_text(
            f"<b>Task {new_pos+1}/{total_size}</b>:\n\n{tasktitle}",
            reply_markup=InlineKeyboardMarkup(map(new_pos))
        )


@Client.on_message(filters.command(['queue']))
async def queue_message(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    
    num_running = len(running_tasks)
    total_size = num_running + len(data)
    
    if total_size == 0:
        await message.reply("🥱 No Active Encodes.")
        return

    # Default to showing Active Task (0)
    pos = 0
    tasktitle = await get_title(pos)
    await message.reply_text(
        f"<b>Task {pos+1}/{total_size}</b>:\n\n{tasktitle}",
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
    
    # Kill All Processes
    for file in os.listdir(download_dir):
        if file.startswith("status_"):
            try:
                with open(os.path.join(download_dir, file), 'r') as f:
                    status = json.load(f)
                    pid = status.get('pid')
                    if pid:
                        os.kill(pid, signal.SIGKILL)
            except:
                pass
        
    await message.reply("♻️ Queue and ALL Active Tasks PURGED!")
