import asyncio #asynchronous operations
import time
import signal
from telegram import Bot, Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler
from telegram.error import TelegramError

# Parameters
TELEGRAM_TOKEN = "telegram_bot_token" #Telegram Bot API token
CHAT_ID = "your_chat_id"
log_file_path = "/home/user/your/path/detection_log.txt" #path to the log file to monitor

monitor_task = None #variable to store the monitoring task
stop_future = asyncio.Future() #Future object to signal the end of the monitoring

async def monitor_log():
    print("Starting log monitoring...")
    while not stop_future.done():
        try:
            with open(log_file_path, 'r') as f: #open log_file in read ('r') mode
                f.seek(0, 2) #move file pointer to the end of the file, from start (0) to end (2)
                while not stop_future.done():
                    line = f.readline()
                    if line: #if variable line a non-empty string
                        await send_message(line.strip()) #send line as message removing leading and trailing whitespace
                    await asyncio.sleep(1) #if readline reads an empty string will wait 1 second before checking for a new line
        except FileNotFoundError:
            print(f"Error: Log file not found: {log_file_path}")
        except Exception as e:
            print(f"Error occurred while monitoring: {e}")
        finally:
            print("Stopping log monitoring...")

async def send_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_task, stop_future #global variables monitor_task and stop_future will be used and potentially modified
    if monitor_task is None: #if monitor_task is not running
        stop_future = asyncio.Future() #when /start command is used, a new monitor_log() task begins, meaning a new stop_future is needed for proper control
        monitor_task = asyncio.create_task(monitor_log()) #start new asynchronous task to run the monitor_log function
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Monitoring started") #send confirmation message to user
    else: #meaning monitor_task is already running 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Monitoring is already running") #send message to user

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_task, stop_future #global variables monitor_task and stop_future will be used and potentially modified
    if monitor_task is not None: #if monitor_task is running
        stop_future.set_result(True) #signals to monitor_log task the end of monitoring by setting a result to the stop_future Future object
        await monitor_task #waits the completion of monitor_log() task (without this it could print what was reading even after the user's /stop command or lose some data)
        monitor_task = None #monitoring is no longer active
        stop_future = asyncio.Future()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Monitoring stopped") #send confirmation message to user
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Monitoring is not running") #send message to user

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build() #create application object using Telegram bot token
    application.add_handler(CommandHandler("start", start_command)) #add handler for /start command
    application.add_handler(CommandHandler("stop", stop_command)) #add handler for /stop command
    application.run_polling() #start bot in polling mode, keeping the bot running and listening for updates

if __name__ == "__main__":
    main()
