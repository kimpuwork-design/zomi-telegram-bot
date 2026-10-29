"""Telegram webhook endpoint for multilingual Zomi data collection."""

import hmac
import os

from flask import Flask, request
import telebot
from supabase import Client, create_client


app = Flask(__name__)

# Keep credentials in the deployment environment, not in this repository.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

MAX_UPDATE_BYTES = 64 * 1024
MAX_MESSAGE_CHARS = 2000

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if request.method == "GET":
        return "Zomi AI Bot is running securely on Vercel!", 200

    # Backward compatible when unset. To enable authentication, configure
    # TELEGRAM_WEBHOOK_SECRET and Telegram setWebhook(secret_token=...)
    # together; enabling one without the other will block legitimate updates.
    expected_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret:
        supplied_secret = request.headers.get(
            "X-Telegram-Bot-Api-Secret-Token", ""
        )
        if not hmac.compare_digest(supplied_secret, expected_secret):
            return "Forbidden", 403

    if request.content_length is not None and request.content_length > MAX_UPDATE_BYTES:
        return "Payload Too Large", 413

    body = request.get_data(cache=False)
    if len(body) > MAX_UPDATE_BYTES:
        return "Payload Too Large", 413

    try:
        update = telebot.types.Update.de_json(body.decode("utf-8"))
    except (ValueError, TypeError, UnicodeDecodeError):
        return "Bad Request", 400

    if update is None:
        return "Bad Request", 400

    try:
        bot.process_new_updates([update])
        return "OK", 200
    except Exception:
        app.logger.exception("Unable to process Telegram webhook update")
        return "Error", 500


@bot.message_handler(commands=["start"])
def send_welcome(message):
    welcome_text = (
        "မင်္ဂလာပါ! Zomi AI Data Collector မှ ကြိုဆိုပါတယ်။\n\n"
        "Data သွင်းရန် အောက်ပါပုံစံအတိုင်း ရိုက်ထည့်ပါ-\n"
        "Zomi, Burmese, English, Category\n\n"
        "ဥပမာ: Na dam hia?, နေကောင်းလား?, How are you?, Greeting"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    raw_text = getattr(message, "text", None)
    invalid_format = (
        "❌ ပုံစံမှားနေပါတယ်။ ကော်မာ (,) ခံပြီး မှန်ကန်စွာ ရိုက်ထည့်ပါ။\n"
        "ဥပမာ: Na dam hia?, နေကောင်းလား?"
    )

    if not isinstance(raw_text, str) or not raw_text or len(raw_text) > MAX_MESSAGE_CHARS:
        bot.reply_to(message, invalid_format)
        return

    parts = [part.strip() for part in raw_text.split(",")]
    if not 2 <= len(parts) <= 4 or not parts[0] or not parts[1]:
        bot.reply_to(message, invalid_format)
        return

    zomi = parts[0]
    burmese = parts[1]
    english = parts[2] if len(parts) > 2 else ""
    category = parts[3] if len(parts) > 3 and parts[3] else "General"

    try:
        # Supabase returns an APIResponse; it is not a (data, count) tuple.
        supabase.table("zomi_dictionary").insert({
            "zomi_text": zomi,
            "burmese_text": burmese,
            "english_text": english,
            "category": category,
            "added_by": str(message.from_user.id),
        }).execute()
        bot.reply_to(
            message,
            f"✅ အောင်မြင်ပါသည်။\nZomi: {zomi}\nBurmese: {burmese}\nDatabase ထဲသို့ သိမ်းဆည်းပြီးပါပြီ။",
        )
    except Exception:
        # Avoid disclosing database details or credentials to chat users.
        app.logger.exception("Failed to persist Telegram language entry")
        bot.reply_to(message, "⚠️ Data သိမ်းဆည်းရာတွင် အမှားဖြစ်နေပါသည်။ နောက်မှ ထပ်ကြိုးစားပါ။")
