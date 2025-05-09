# bot.py
import os
import json
import logging
import asyncio
from datetime import timedelta
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext

from scraper import fetch_new_listings_from_listedon
from binance_checker import get_binance_listed_symbols

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
NOTIFIED_TICKERS_FILE = 'notified_tickers.json'

# --- Notified Tickers persistence (remains synchronous for load at startup) ---
def load_notified_tickers():
    """Loads notified tickers from a JSON file."""
    if os.path.exists(NOTIFIED_TICKERS_FILE):
        try:
            with open(NOTIFIED_TICKERS_FILE, 'r') as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from {NOTIFIED_TICKERS_FILE}. Starting with an empty set.")
            return set()
        except Exception as e:
            logger.error(f"Error loading {NOTIFIED_TICKERS_FILE}: {e}. Starting with an empty set.")
            return set()
    return set()

# save_notified_tickers will be called from an async func, but itself can remain sync
# as it will be wrapped by asyncio.to_thread
def save_notified_tickers(tickers_set):
    """Saves notified tickers to a JSON file."""
    try:
        with open(NOTIFIED_TICKERS_FILE, 'w') as f:
            json.dump(list(tickers_set), f, indent=4)
    except Exception as e:
        logger.error(f"Error saving to {NOTIFIED_TICKERS_FILE}: {e}")

notified_tickers = load_notified_tickers()

# --- Core Logic (now async) ---
async def check_for_alerts(bot: Bot):
    """Checks for new listings and sends alerts if they are already on Binance."""
    global notified_tickers
    logger.info("Running scheduled check for new listings...")

    # Run synchronous blocking I/O in a separate thread
    newly_listed_on_listedon = await asyncio.to_thread(fetch_new_listings_from_listedon)
    if not newly_listed_on_listedon:
        logger.info("No new listings found on listedon.org or error fetching.")
        return

    logger.info(f"Fetched {len(newly_listed_on_listedon)} tickers from listedon: {newly_listed_on_listedon[:5]}...")

    binance_symbols = await asyncio.to_thread(get_binance_listed_symbols)
    if not binance_symbols:
        logger.warning("Could not fetch symbols from Binance or error fetching.")
        return
    logger.info(f"Fetched {len(binance_symbols)} symbols from Binance.")

    alerts_sent_this_run = 0
    for ticker in newly_listed_on_listedon:
        if ticker not in notified_tickers and ticker in binance_symbols:
            escaped_ticker = ticker.replace('.', '\\.')
            for char in "_[]()~`>#+-=|{}.!":
                if char != '.':
                    escaped_ticker = escaped_ticker.replace(char, f'\\{char}')

            message = f"📢 *ALREADY ON BINANCE\!* 📢\n\n`{escaped_ticker}` \(seen on listedon\.org\) is already listed on Binance\."
            try:
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='MarkdownV2')
                logger.info(f"Alert sent for {ticker}")
                notified_tickers.add(ticker)
                alerts_sent_this_run += 1
            except Exception as e:
                logger.error(f"Failed to send Telegram message for {ticker}: {e}. Message: {message}")
        elif ticker not in notified_tickers:
            pass
    
    if alerts_sent_this_run > 0:
        await asyncio.to_thread(save_notified_tickers, notified_tickers)
    
    logger.info(f"Check complete. Alerts sent this run: {alerts_sent_this_run}. Total unique tickers ever notified: {len(notified_tickers)}")

# --- Job Adapter for JobQueue ---
async def scheduled_job_adapter(context: CallbackContext):
    """Adapter function for JobQueue to call check_for_alerts."""
    bot_instance = context.job.data
    if not bot_instance or not isinstance(bot_instance, Bot):
        logger.error("Bot instance not found or incorrect type in job context for scheduled_job_adapter")
        if isinstance(context.bot, Bot):
             bot_instance = context.bot
        else:
            logger.error("No valid bot instance available for scheduled_job_adapter.")
            return
    await check_for_alerts(bot_instance)

# --- Telegram Command Handlers (now async) ---
async def start(update: Update, context: CallbackContext):
    """Sends a welcome message when the /start command is issued."""
    logger.info(f"Received /start command from user {update.effective_user.id if update.effective_user else 'Unknown'}")
    await update.message.reply_text('Merhaba! Binance listeleme takip botu aktif. Yeni listelemeler periyodik olarak kontrol edilecek.')
    context.job_queue.run_once(scheduled_job_adapter, 0, data=context.bot, name=f"manual_start_check_{update.effective_message.message_id}")

async def force_check(update: Update, context: CallbackContext):
    """Manually triggers the alert check."""
    logger.info(f"Received /checknow command from user {update.effective_user.id if update.effective_user else 'Unknown'}")
    await update.message.reply_text('Manuel kontrol başlatılıyor...')
    context.job_queue.run_once(scheduled_job_adapter, 0, data=context.bot, name=f"manual_force_check_{update.effective_message.message_id}")

def main():
    """Start the bot using ApplicationBuilder."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logger.error("HATA: Lütfen .env dosyasında TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID değerlerini ayarlayın.")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("checknow", force_check))

    application.job_queue.run_repeating(
        scheduled_job_adapter, 
        interval=timedelta(minutes=10), 
        first=timedelta(seconds=5),     
        data=application.bot, 
        name="periodic_binance_check"
    )
    
    logger.info("Bot başlatıldı ve zamanlayıcı ayarlandı. CTRL+C ile durdurabilirsiniz.")

    application.run_polling()

    logger.info("Bot durduruluyor.")

if __name__ == '__main__':
    main()