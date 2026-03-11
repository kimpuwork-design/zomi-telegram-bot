from flask import Flask, request
import telebot
from supabase import create_client, Client
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Vercel လမ်းကြောင်းလွဲခြင်းကို ဖြေရှင်းမည့် Catch-all Route
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if request.method == 'POST':
        try:
            update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
            bot.process_new_updates([update])
            return "OK", 200
        except Exception as e:
            print(f"Error processing update: {e}")
            return "Error", 500
    return "Zomi AI Bot is running securely on Vercel!", 200

@bot.message_handler(commands=['start'])
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
    try:
        parts = [p.strip() for p in message.text.split(',')]
        if len(parts) >= 2:
            zomi = parts[0]
            burmese = parts[1]
            english = parts[2] if len(parts) > 2 else ""
            category = parts[3] if len(parts) > 3 else "General"
            
            data, count = supabase.table('zomi_dictionary').insert({
                "zomi_text": zomi,
                "burmese_text": burmese,
                "english_text": english,
                "category": category,
                "added_by": str(message.from_user.id)
            }).execute()
            
            bot.reply_to(message, f"✅ အောင်မြင်ပါသည်။\nZomi: {zomi}\nBurmese: {burmese}\nDatabase ထဲသို့ သိမ်းဆည်းပြီးပါပြီ။")
        else:
            bot.reply_to(message, "❌ ပုံစံမှားနေပါတယ်။ ကော်မာ (,) ခံပြီး မှန်ကန်စွာ ရိုက်ထည့်ပါ။\nဥပမာ: Na dam hia?, နေကောင်းလား?")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error ဖြစ်နေပါတယ်: {str(e)}")
