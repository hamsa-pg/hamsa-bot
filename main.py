import telebot
from telebot import types
import sqlite3
import requests
from threading import Thread
import time

# 🌐 Render ሰርቨሩ እንዳይዘጋ የሚረዳ አጭር የዌብ ሰርቨር ኮድ (Flask)
from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "Hamsa Bot is Active and Running! 🚀"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# 1. ቦቱን ማገናኘት
TOKEN = '8976518823:AAE-GfrDj0gE7tzO37_0Zsbf1UqXwVrJoOM'
bot = telebot.TeleBot(TOKEN)

# ⚙️ የቢዝነስ ዋና መረጃዎች
ADMIN_ID = 7313131722 
CHANNEL_USERNAME = -1003969323110  
TELEBIRR_NUMBER = '0993121302'       
ACCOUNT_NAME = '50 coin market'               

user_data = {}

# 🌟 ፎቶን ወደ ሊንክ የመቀየሪያ ዘዴ
def upload_photo_to_link(file_id):
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        response = requests.get(file_url)
        if response.status_code == 200:
            files = {'file': ('photo.jpg', response.content, 'image/jpeg')}
            upload_res = requests.post('https://telegra.ph/upload', files=files).json()
            if isinstance(upload_res, list) and 'src' in upload_res[0]:
                return f"https://telegra.ph{upload_res[0]['src']}"
    except Exception as e:
        print(f"Photo upload error: {e}")
    return file_id

# 2. የ SQLite ዳታቤዝ
def init_db():
    conn = sqlite3.connect('hamsa_coin_v5_0.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            price REAL,
            phone TEXT,
            tg_username TEXT,
            condition TEXT,
            category TEXT,
            package TEXT,
            photo_urls TEXT,
            receipt_id TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'am'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# የቋንቋ መዝገበ-ቃላት
STRINGS = {
    'am': {
        'welcome': "🪙 <b>እንኳን ወደ 𝟓𝟎 𝐂𝐨𝐢ን 𝐌𝐚ርኬት በደህና መጡ!</b> 🪙\n\nዋጋቸው ከ 1,000 ብር በላይ የሆኑ ዕቃዎችን በ 50 ብር ብቻ ለሺዎች የሚያስተዋውቁበት ብቸኛው የቴሌግራም ቦት🏽",
        'btn_sell': "➕ ዕቃ ለመመዝገብ",
        'btn_info': "ℹ️ ስለ እኛ እና ህጋችን",
        'btn_lang': "🌐 ቋንቋ ለመቀየር / Change Language",
        'warning_title': "<b>🚨 ልዩ ጥብቅ ማስጠንቀቂያ ለሻጮች 🚨</b>\n\n1️⃣ <b>የሀሰት ደረሰኝ፦</b> የተጭበረበረ የቴሌብር ደረሰኝ መላክ ሙሉ በሙሉ የተከለከለ ነው።\n2️⃣ <b>የሀሰት መረጃ፦</b> እውነተኛ ያልሆነ ዋጋ ወይም የተሰረቀ ምስል መጠቀም ክልክል ነው።\n3️⃣ <b>ህጋዊ እርምጃ፦</b> ለማጭበርበር የሚሞክር አካውንት ሙሉ በሙሉ ይታገዳል (Block ይደረጋል)!\n\n<i>\"ታማኝነት ለረጅም ጊዜ ቢዝነስ መሰረት ነው!\"</i>",
        'btn_agree': "🤝 ህጉን አክብሬ ለመቀጠል ተስማምቻለሁ",
        'no_username': "⚠️ <b>ይቅርታ!</b> ይህንን ቦት ለመጠቀም መጀመሪያ በቴሌግራም ፕሮፋይልዎ ላይ <b>Username (መለያ ስም)</b> ማስተካከል ይኖርብዎታል።",
        'req_title': "📦 እባክዎ የሚሸጡትን ዕቃ አጭር ስም (Title) ያስገቡ፦",
        'req_desc': "📝 ስለ እቃው ሁኔታ እና ማብራሪያ በአንድ መልዕክት ይጻፉ፦",
        'req_price': "💰 ዕቃውን የሚሸጡበትን ጠቅላላ ዋጋ በቁጥር ብቻ ያስገቡ፦",
        'price_error': "⚠️ ይቅርታ! በዚህ ቦት ላይ ከ 1,000 ብር ጀምሮ የሆኑ ዕቃዎችን ብቻ ማስተዋወቅ ይቻላል። እባክዎ ዋጋውን በቁጥር ድጋሚ ያስገቡ፦",
        'num_error': "⚠️ እባክዎ ዋጋውን በቁጥር ብቻ በትክክል ያስገቡ (ለምሳሌ፦ 2500)፦",
        'req_phone': "📞 ገዢዎች በቀጥታ እንዲደውሉልዎት ስልክ ቁጥርዎን ያስገቡ፦",
        'req_cond': "✨ የዕቃው ሁኔታ (Condition) ምን ይመስላል?",
        'cond_new': "✨ አዲስ (Brand New)",
        'cond_used': "🛍️ በትንሹ ያገለገለ (Used)",
        'req_cat': "🗂️ እባክዎ የዕቃውን ምድብ (Category) ይምረጡ፦",
        'req_pkg': "💎 እባክዎ የማስታወቂያ ፓኬጅ ምርጫዎን ይምረጡ፦",
        'req_photo_first': "📸 አሁን የእቃውን <b>የመጀመሪያ ፎቶ</b> ይላኩ (እስከ 4 ፎቶ መላክ ይችላሉ)፦",
        'req_photo_next': "📸 የላኩት ፎቶ ተመዝግቧል። <b>ሌላ {rem} ፎቶዎች</b> መጨመር ይችላሉ። ካበቁ '✅ ይበቃል / Done' የሚለውን ይጫኑ፦",
        'btn_done': "✅ ይበቃል / Done",
        'loading_photo': "⏳ ፎቶውን ወደ ሰርቨር በመጫን ላይ...",
        'req_receipt': "<b>🛑 የመጨረሻ ደረጃ - የክፍያ ማረጋገጫ 🛑</b>\n\nእባክዎ በቴሌብር የጠየቁትን የ<b>{fee} ብር</b> ክፍያ በዚህ ቁጥር ያጠናቁ፦\n\n📱 <b>የቴሌብር ቁጥር፦</b> <code>{num}</code>\n👤 <b>ስም፦</b> {name}\n\nክፍያውን እንደፈጸሙ የቴሌብር <b>የደረሰኝ ፎቶ (Screenshot)</b> እዚህ ላይ ይላኩ🏽",
        'success': "🎯 የክፍያ ደረሰኝዎ ደርሶናል። በአስተዳዳሪው ተገምግሞ ሲጠናቀቅ በቦቱ በኩል መልዕክት ይደርስዎታል። እናመሰግናለን!",
        'photo_error': "⚠️ እባክዎ ፎቶ ብቻ ይላኩ ወይም 'ይበቃል' የሚለውን ይጫኑ!",
        'receipt_error': "⚠️ እባክዎ የቴሌብር የደረሰኝ ፎቶ (Screenshot) ብቻ ይላኩ!",
        'disclaimer': "⚠️ <b>የገዢዎች ጥንቃቄ (Disclaimer)፦</b>\n<i>እቃውን በአካል አይተው ሳይረከቡ <b>ቅድሚያ ክፍያ (Advance) በፍጹም እንዳይፈጽሙ!</b> ግብይቱን ደህንነቱ በተጠበቀ ህዝባዊ ቦታ ያከናውኑ🏽</i>"
    },
    'en': {
        'welcome': "🪙 <b>Welcome to 𝟓𝟎 𝐂𝐨𝐢ን 𝐌𝐚ርኬት!</b> 🪙\n\nThe only Telegram bot where you can advertise items worth over 1,000 ETB for just 50 ETB to thousands of buyers.",
        'btn_sell': "➕ Register Item / Sell",
        'btn_info': "ℹ️ About Us & Rules",
        'btn_lang': "🌐 ቋንቋ ለመቀየር / Change Language",
        'warning_title': "<b>🚨 Strict Warning for Sellers 🚨</b>\n\n1️⃣ <b>Fake Receipt:</b> Sending fake Telebirr receipts is strictly prohibited.\n2️⃣ <b>Fake Information:</b> Listing false prices or stolen internet photos is banned.\n3️⃣ <b>Legal Action:</b> Fraudulent accounts will be blocked immediately!",
        'btn_agree': "🤝 I Agree to the Rules",
        'no_username': "⚠️ <b>Sorry!</b> To use this bot, you must first set up a Telegram <b>Username</b> in your profile settings.",
        'req_title': "📦 Please enter a short title for your item:",
        'req_desc': "📝 Write a clear description of your item in one message:",
        'req_price': "💰 Enter the total price in numbers only:",
        'price_error': "⚠️ Sorry! Only items worth 1,000 ETB and above can be listed. Please re-enter the price:",
        'num_error': "⚠️ Please enter a valid number (Example: 2500):",
        'req_phone': "📞 Enter your phone number for buyers to call you:",
        'req_cond': "✨ What is the condition of the item?",
        'cond_new': "✨ Brand New",
        'cond_used': "🛍️ Slightly Used",
        'req_cat': "🗂️ Please select the item category:",
        'req_pkg': "💎 Please select your advertising package:",
        'req_photo_first': "📸 Now send the <b>First Photo</b> of the item (You can send up to 4 photos):",
        'req_photo_next': "📸 Photo saved. You can add <b>{rem} more photos</b>. When finished, press '✅ ይበቃል / Done':",
        'btn_done': "✅ ይበቃል / Done",
        'loading_photo': "⏳ Uploading photo...",
        'req_receipt': "<b>🛑 Final Step - Payment Verification 🛑</b>\n\nPlease complete the payment of <b>{fee} ETB</b> via Telebirr:\n\n📱 <b>Telebirr Number:</b> <code>{num}</code>\n👤 <b>Name:</b> {name}\n\nAfter payment, send the <b>Receipt Screenshot</b> here.",
        'success': "🎯 Your receipt has been received. You will be notified once the admin reviews and approves it. Thank you!",
        'photo_error': "⚠️ Please send an image file or press Done!",
        'receipt_error': "⚠️ Please send a Telebirr receipt screenshot only!",
        'disclaimer': "⚠️ <b>Buyer's Disclaimer:</b>\n<i><b>NEVER make any advance payments</b> before seeing and verifying the item in person! Complete transactions in a safe public place.</i>"
    }
}

def get_user_lang(user_id):
    try:
        conn = sqlite3.connect('hamsa_coin_v5_0.db')
        cursor = conn.cursor()
        cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'am'
    except:
        return 'am'

# 3. የቋንቋ መምረጫ ገጽ ከ /start ጋር
@bot.message_handler(commands=['start'])
def lang_selection(message):
    markup = types.InlineKeyboardMarkup()
    btn_am = types.InlineKeyboardButton("አማርኛ 🇪🇹", callback_data="set_lang_am")
    btn_en = types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
    markup.add(btn_am, btn_en)
    bot.send_message(message.chat.id, "🌐 እባክዎ ቋንቋ ይምረጡ / Please choose your language:", reply_markup=markup)

def show_main_menu(chat_id, user_id):
    lang = get_user_lang(user_id)
    welcome_text = STRINGS[lang]['welcome']
    
    markup = types.InlineKeyboardMarkup()
    btn_sell = types.InlineKeyboardButton(STRINGS[lang]['btn_sell'], callback_data="show_warning")
    btn_info = types.InlineKeyboardButton(STRINGS[lang]['btn_info'], callback_data="about_us")
    btn_lang = types.InlineKeyboardButton(STRINGS[lang]['btn_lang'], callback_data="trigger_lang_change")
    markup.add(btn_sell)
    markup.add(btn_info, btn_lang)
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="HTML")

# 4. Callback Handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    
    if call.data.startswith("set_lang_"):
        lang_code = call.data.split("_")[2]
        conn = sqlite3.connect('hamsa_coin_v5_0.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang_code))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message.chat.id, user_id)
        
    elif call.data == "trigger_lang_change":
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        lang_selection(call.message)

    elif call.data == "show_warning":
        bot.answer_callback_query(call.id)
        lang = get_user_lang(user_id)
        
        if not call.from_user.username:
            bot.send_message(call.message.chat.id, STRINGS[lang]['no_username'], parse_mode="HTML")
            return
            
        markup = types.InlineKeyboardMarkup()
        btn_agree = types.InlineKeyboardButton(STRINGS[lang]['btn_agree'], callback_data="start_selling")
        markup.add(btn_agree)
        bot.send_message(call.message.chat.id, STRINGS[lang]['warning_title'], reply_markup=markup, parse_mode="HTML")

    elif call.data == "start_selling":
        bot.answer_callback_query(call.id)
        lang = get_user_lang(user_id)
        
        user_data[user_id] = {
            'tg_username': f"@{call.from_user.username}",
            'photos': []  
        }
        bot.send_message(call.message.chat.id, STRINGS[lang]['req_title'], parse_mode="HTML")
        bot.register_next_step_handler(call.message, process_title)

    elif call.data == "about_us":
        bot.answer_callback_query(call.id)
        lang = get_user_lang(user_id)
        info = STRINGS[lang]['welcome'] + "\n\nStandard: 50 ETB\nVIP Premium: 100 ETB"
        bot.send_message(call.message.chat.id, info, parse_mode="HTML")

    elif call.data.startswith("cond_"):
        bot.answer_callback_query(call.id)
        lang = get_user_lang(user_id)
        cond = "Brand New" if "new" in call.data else "Used"
        user_data[user_id]['condition'] = cond
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📱 Phone", callback_data="cat_Phone"),
                   types.InlineKeyboardButton("💻 Laptop", callback_data="cat_Laptop"))
        markup.add(types.InlineKeyboardButton("🚗 Car", callback_data="cat_Car"),
                   types.InlineKeyboardButton("🛍️ Other", callback_data="cat_Other"))
        bot.send_message(call.message.chat.id, STRINGS[lang]['req_cat'], reply_markup=markup)

    elif call.data.startswith("cat_"):
        bot.answer_callback_query(call.id)
        lang = get_user_lang(user_id)
        cat = call.data.split("_")[1]
        user_data[user_id]['category'] = cat
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if lang == 'am':
            markup.add("Standard (50 ብር)", "VIP Premium (100 ብር)")
        else:
            markup.add("Standard (50 ETB)", "VIP Premium (100 ETB)")
        bot.send_message(call.message.chat.id, STRINGS[lang]['req_pkg'], reply_markup=markup)
        bot.register_next_step_handler(call.message, process_package)

    elif call.data.startswith("adm_approve_") or call.data.startswith("adm_reject_"):
        bot.answer_callback_query(call.id)
        parts = call.data.split("_")
        action = parts[1]    
        item_id = parts[2]   
        
        conn = sqlite3.connect('hamsa_coin_v5_0.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, title, description, price, phone, tg_username, condition, category, package, photo_urls FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        
        if item:
            seller_id, title, desc, price, phone, tg_user, condition, category, package, photo_urls_str = item
            seller_lang = get_user_lang(seller_id)
            photo_list = photo_urls_str.split(",") 
            
            if action == "approve":
                cursor.execute("UPDATE items SET status = 'approved' WHERE id = ?", (item_id,))
                conn.commit()
                
                badge = "🔥 [VIP PREMIUM]" if package == "vip" else "🛍️ [STANDARD]"
                hashtag = f"#{category} #{condition.replace(' ', '')}"
                
                post_text = (
                    f"<b>{badge} አዲስ የሚሸጥ ዕቃ ቀረበ! / New Item!</b>\n\n"
                    f"📦 <b>የዕቃው ስም / Name:</b> {title}\n"
                    f"🗂️ <b>ምድብ / Category:</b> {category} ({condition})\n"
                    f"📝 <b>ዝርዝር መግለጫ / Description:</b> {desc}\n"
                    f"💰 <b>ዋጋ / Price:</b> {price:,.2f} ብር / ETB\n"
                    f"📞 <b>ስልክ / Phone:</b> {phone}\n"
                    f"👤 <b>ሻጭ / Seller:</b> {tg_user}\n\n"
                    f"{STRINGS['am']['disclaimer']}\n\n"
                    f"{hashtag}\n\n"
                    f"🪙 @{bot.get_me().username}"
                )
                
                chan_markup = types.InlineKeyboardMarkup()
                clean_tg = tg_user.replace("@", "")
                btn_chat = types.InlineKeyboardButton("💬 በቴሌግራም ለማውራት / Chat", url=f"t.me/{clean_tg}")
                chan_markup.add(btn_chat)
                
                try:
                    media_group = []
                    for i, url in enumerate(photo_list):
                        if i == 0:
                            media_group.append(types.InputMediaPhoto(url, caption=post_text, parse_mode="HTML"))
                        else:
                            media_group.append(types.InputMediaPhoto(url))
                    
                    posted_msgs = bot.send_media_group(CHANNEL_USERNAME, media_group)
                    bot.send_message(CHANNEL_USERNAME, "👇 ለባለቤቱ ቀጥታ መልዕክት ለመላክ", reply_markup=chan_markup)
                    
                    if package == "vip":
                        bot.pin_chat_message(CHANNEL_USERNAME, posted_msgs[0].message_id)
                except Exception as e:
                    print(f"Channel album post error: {e}")
                
                msg_success = "🎉 እንኳን ደስ አለዎት! ዕቃዎ በአልበም መልክ ቻናል ላይ ተለቋል።" if seller_lang == 'am' else "🎉 Congratulations! Your item album has been posted."
                bot.send_message(seller_id, msg_success)
                bot.edit_message_caption("✅ ጸድቆ ቻናል ላይ በአልበም ተለጥፏል!", chat_id=ADMIN_ID, message_id=call.message.message_id)
                
            elif action == "reject":
                cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
                conn.commit()
                msg_fail = "❌ ይቅርታ፣ ያመለከቱት ምዝገባ ውድቅ ተደርጓል።" if seller_lang == 'am' else "❌ Sorry, your listing request was rejected."
                bot.send_message(seller_id, msg_fail)
                bot.edit_message_caption("❌ ውድቅ ተደርጎ ተሰርዟል!", chat_id=ADMIN_ID, message_id=call.message.message_id)
                
        conn.close()

# 5. የምዝገባ ቅደም ተከተሎች
def process_title(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    user_data[user_id]['title'] = message.text
    bot.send_message(message.chat.id, STRINGS[lang]['req_desc'])
    bot.register_next_step_handler(message, process_description)

def process_description(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    user_data[user_id]['description'] = message.text
    bot.send_message(message.chat.id, STRINGS[lang]['req_price'])
    bot.register_next_step_handler(message, process_price)

def process_price(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    try:
        price = float(message.text.replace(",", ""))
        if price < 1000:
            bot.send_message(message.chat.id, STRINGS[lang]['price_error'])
            bot.register_next_step_handler(message, process_price)
            return
        
        user_data[user_id]['price'] = price
        bot.send_message(message.chat.id, STRINGS[lang]['req_phone'])
        bot.register_next_step_handler(message, process_phone)
    except ValueError:
        bot.send_message(message.chat.id, STRINGS[lang]['num_error'])
        bot.register_next_step_handler(message, process_price)

def process_phone(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    user_data[user_id]['phone'] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(STRINGS[lang]['cond_new'], callback_data="cond_new"),
               types.InlineKeyboardButton(STRINGS[lang]['cond_used'], callback_data="cond_used"))
    bot.send_message(message.chat.id, STRINGS[lang]['req_cond'], reply_markup=markup)

def process_package(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    choice = message.text
    
    user_data[user_id]['package'] = "vip" if "VIP" in choice else "standard"
    
    bot.send_message(message.chat.id, STRINGS[lang]['req_photo_first'], parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_package_photos)

def process_package_photos(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if message.text and ("ይበቃል" in message.text or "Done" in message.text):
        if len(user_data[user_id]['photos']) == 0:
            bot.send_message(message.chat.id, "⚠️ እባክዎ ቢያንስ 1 ፎቶ ይላኩ!")
            bot.register_next_step_handler(message, process_package_photos)
            return
        goToPaymentStep(message, user_id, lang)
        return

    if message.content_type == 'photo':
        bot.send_message(message.chat.id, STRINGS[lang]['loading_photo'])
        raw_photo_id = message.photo[-1].file_id
        uploaded_url = upload_photo_to_link(raw_photo_id)
        
        user_data[user_id]['photos'].append(uploaded_url)
        current_count = len(user_data[user_id]['photos'])
        
        if current_count >= 4:
            goToPaymentStep(message, user_id, lang)
            return
        else:
            remaining = 4 - current_count
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(STRINGS[lang]['btn_done'])
            
            next_msg = STRINGS[lang]['req_photo_next'].format(rem=remaining)
            bot.send_message(message.chat.id, next_msg, reply_markup=markup, parse_mode="HTML")
            bot.register_next_step_handler(message, process_package_photos)
    else:
        bot.send_message(message.chat.id, STRINGS[lang]['photo_error'])
        bot.register_next_step_handler(message, process_package_photos)

def goToPaymentStep(message, user_id, lang):
    fee_amount = "100" if user_data[user_id]['package'] == "vip" else "50"
    payment_text = STRINGS[lang]['req_receipt'].format(fee=fee_amount, num=TELEBIRR_NUMBER, name=ACCOUNT_NAME)
    
    bot.send_message(message.chat.id, payment_text, parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_receipt)

def process_receipt(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "⏳ ...")
        receipt_id = message.photo[-1].file_id
        receipt_url = upload_photo_to_link(receipt_id)
        data = user_data[user_id]
        
        photo_urls_str = ",".join(data['photos'])
        
        conn = sqlite3.connect('hamsa_coin_v5_0.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO items (user_id, title, description, price, phone, tg_username, condition, category, package, photo_urls, receipt_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (user_id, data['title'], data['description'], data['price'], data['phone'], data['tg_username'], data['condition'], data['category'], data['package'], photo_urls_str, receipt_url))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        bot.send_message(message.chat.id, STRINGS[lang]['success'])
        
        admin_caption = (
            f"<b>💰 New Album Request ({len(data['photos'])} Photos)!</b>\n\n"
            f"📦 <b>Item:</b> {data['title']}\n"
            f"🗂️ <b>Category:</b> {data['category']} ({data['condition']})\n"
            f"💰 <b>Price:</b> {data['price']:,.2f} ETB\n"
            f"👤 <b>Seller:</b> {data['tg_username']}\n"
            f"💎 <b>Package:</b> {data['package'].upper()}\n"
        )
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_approve_{item_id}"),
                         types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_reject_{item_id}"))
        bot.send_photo(ADMIN_ID, receipt_url, caption=admin_caption, parse_mode="HTML", reply_markup=admin_markup)
        
        if user_id in user_data:
            del user_data[user_id]
    else:
        bot.send_message(message.chat.id, STRINGS[lang]['receipt_error'])
        bot.register_next_step_handler(message, process_receipt)

# 🚀 የሰርቨር እና የቦት ማስነሻ
if __name__ == '__main__':
    print("ቦቱ ስራ ጀምሯል...")
    
    # 1. የ Flask ሰርቨሩን በጀርባ ማስነሳት
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # 2. የቴሌግራም ቦቱን ማስነሳት
    bot.remove_webhook()
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(5)
