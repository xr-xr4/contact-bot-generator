import telebot
from telebot import types
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import json
import random

FACTORY_BOT_TOKEN = "Your_Bot_Token"
factory_bot = telebot.TeleBot(FACTORY_BOT_TOKEN)

admin_ids = {7665522338}#put Your Id Here
user_states = {}
created_bots = []
running_bots = {}

def run_new_bot(bot_data):
    global ADMIN_ID, main_channel, channels, custom_buttons, button_edit_states
    global sessions, users, banned_users, bot_enabled, welcome_notification_enabled
    global admins, confirmation_message, welcome_photo_url, welcome_message

    owner_id = bot_data["owner_id"]
    id = bot_data["id"]
    token = bot_data["token"]
    
    json_filename = f"{id}.json"
    
    
    ADMIN_ID = owner_id
    main_channel = "xr_xr4_dev"
    channels = []
    custom_buttons = []
    button_edit_states = {}
    sessions = {}
    users = set()
    banned_users = set()
    bot_enabled = True
    welcome_notification_enabled = True
    admins = {ADMIN_ID}
    confirmation_message = "✅ تم إرسال رسالتك يرجى الانتظار وعدم تكرار الرسائل حتي لا يتم حظرك"
    welcome_photo_url = "https://t.me/jhgghhggggr/3"
    welcome_message = "✅ أهلاً بك {user_name}!\n\n🆔 ID: `{user_id}`\n📎 المعرف: {user_username}\n\nيمكنك الآن التواصل مع يوسف وارسال رسائلك الي بكل سهوله. ارسل رسالتك وسأرد عليك سريعًا 🤍⚡"

    
    with open(json_filename, "w", encoding="utf-8") as file:
        json.dump({}, file, indent=4)

    new_bot = telebot.TeleBot(token)
    running_bots[token] = new_bot
    
    def save_data():
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump({
                "users": list(users),
                "banned_users": list(banned_users),
                "channels": channels,
                "admins": list(admins),
                "welcome_photo_url": welcome_photo_url,
                "welcome_message": welcome_message,
                "confirmation_message": confirmation_message,
                "custom_buttons": custom_buttons
            }, f, ensure_ascii=False, indent=4)

    def load_data():
        global users, banned_users, channels, admins, welcome_photo_url, welcome_message, confirmation_message, custom_buttons
        try:
            with open(json_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                users = set(data.get("users", []))
                banned_users = set(data.get("banned_users", []))
                channels = data.get("channels", [])
                admins = set(data.get("admins", [ADMIN_ID]))
                welcome_photo_url = data.get("welcome_photo_url", welcome_photo_url)
                welcome_message = data.get("welcome_message", welcome_message)
                confirmation_message = data.get("confirmation_message", confirmation_message)
                custom_buttons = data.get("custom_buttons", [])
        except FileNotFoundError:
            save_data()

    
    
    load_data()

    

    def check_subscription(user_id):
        for channel in channels:
            try:
                status = new_bot.get_chat_member(channel, user_id).status
                if status not in ["member", "administrator", "creator"]:
                    return False
            except Exception as e:
                print(f"خطأ أثناء التحقق من القناة {channel}: {e}")
                return False
        return True
        
    def change_confirmation_message(message):
        global confirmation_message
        confirmation_message = message.text.strip()
        save_data()
        new_bot.send_message(message.chat.id, "✅ تم تغيير رسالة التأكيد بنجاح.")
    
    def broadcast_message(message):
        if message.chat.id in admins:
            broadcast_text = message.text
            success = 0
            failed = 0
            
            for user_id in users:
                try:
                    new_bot.send_message(user_id, broadcast_text)
                    success += 1
                except Exception:
                    failed += 1
            
            new_bot.send_message(ADMIN_ID, f"✅ تم إرسال الإذاعة إلى {success} مستخدم\n❌ فشل إرسالها إلى {failed} مستخدم")
            save_data()
    
    def ban_user(message):
        try:
            user_id = int(message.text.strip())
            banned_users.add(user_id)
            if user_id in users:
                users.remove(user_id)
            save_data()
            new_bot.send_message(ADMIN_ID, f"✅ تم حظر المستخدم: {user_id}")
        except ValueError:
            new_bot.send_message(ADMIN_ID, "⚠️ ID غير صالح.")
    
    def unban_user(message):
        try:
            user_id = int(message.text.strip())
            if user_id in banned_users:
                banned_users.remove(user_id)
                save_data()
                new_bot.send_message(ADMIN_ID, f"✅ تم فك حظر المستخدم: {user_id}")
            else:
                new_bot.send_message(ADMIN_ID, "⚠️ هذا المستخدم غير محظور.")
        except ValueError:
            new_bot.send_message(ADMIN_ID, "⚠️ ID غير صالح.")
    
    @new_bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if message.chat.id in admins:
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(types.InlineKeyboardButton("➕ إضافة قناة", callback_data="add_channel"))
            keyboard.add(
                types.InlineKeyboardButton("📋 عرض القنوات", callback_data="list_channels"),
                types.InlineKeyboardButton("➖ حذف قناة", callback_data="remove_channel")
            )
            keyboard.add(
                types.InlineKeyboardButton("👨‍💻 إضافة أدمن", callback_data="add_admin"),
                types.InlineKeyboardButton("❌ حذف أدمن", callback_data="remove_admin"),
                types.InlineKeyboardButton("👥 عرض الأدمنز", callback_data="list_admins")
            )
            keyboard.add(
                types.InlineKeyboardButton("📊 إحصائيات البوت", callback_data="bot_stats"),
                types.InlineKeyboardButton("📢 إرسال إذاعة", callback_data="broadcast")
            )
            keyboard.add(
                types.InlineKeyboardButton("🔒 قفل البوت", callback_data="disable_bot"),
                types.InlineKeyboardButton("🔓 تشغيل البوت", callback_data="enable_bot")
            )
            keyboard.add(
                types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="ban_user"),
                types.InlineKeyboardButton("✅ فك حظر مستخدم", callback_data="unban_user")
            )
            keyboard.add(
                types.InlineKeyboardButton("🖼 تعديل صورة الترحيب", callback_data="change_welcome_photo"),
                types.InlineKeyboardButton("💬 تعديل رسالة الترحيب", callback_data="change_welcome_message")
            )
            keyboard.add(
                types.InlineKeyboardButton("✉️ تعديل رسالة الارسال", callback_data="change_confirmation_message")
            )
            keyboard.add(
                types.InlineKeyboardButton("➕ إضافة زر", callback_data="add_button"),
                types.InlineKeyboardButton("🗑 حذف زر", callback_data="remove_button"),
            )
            keyboard.add(
                types.InlineKeyboardButton("✏️ تعديل زر", callback_data="edit_button"),
            )
            keyboard.add(
                types.InlineKeyboardButton("📋 عرض الأزرار", callback_data="list_buttons")
            )
            keyboard.add(
                types.InlineKeyboardButton("🔔 تفعيل/إيقاف إشعار الدخول", callback_data="toggle_welcome_notification")
            )
            
            new_bot.send_message(message.chat.id, "📋 لوحة التحكم\n✨ ", reply_markup=keyboard)

    def add_admin(message):
        try:
            new_admin = message.text.strip()
            if new_admin.startswith('@'):
                try:
                    user = new_bot.get_chat(new_admin)
                    new_admin_id = user.id
                except:
                    new_bot.send_message(message.chat.id, "⚠️ لا يمكن العثور على المستخدم")
                    return
            else:
                new_admin_id = int(new_admin)
                
            if new_admin_id not in admins:
                admins.add(new_admin_id)
                save_data()
                new_bot.send_message(message.chat.id, f"✅ تمت إضافة الأدمن {new_admin_id} بنجاح")
            else:
                new_bot.send_message(message.chat.id, "⚠️ هذا المستخدم أدمن بالفعل")
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")
    
    def remove_admin(message):
        try:
            admin_to_remove = message.text.strip()
            if admin_to_remove.startswith('@'):
                try:
                    user = new_bot.get_chat(admin_to_remove)
                    admin_id = user.id
                except:
                    new_bot.send_message(message.chat.id, "⚠️ لا يمكن العثور على المستخدم")
                    return
            else:
                admin_id = int(admin_to_remove)
                
            if admin_id == ADMIN_ID:
                new_bot.send_message(message.chat.id, "⚠️ لا يمكن حذف الأدمن الرئيسي")
            elif admin_id in admins:
                admins.remove(admin_id)
                save_data()
                new_bot.send_message(message.chat.id, f"✅ تم حذف الأدمن {admin_id} بنجاح")
            else:
                new_bot.send_message(message.chat.id, "⚠️ هذا المستخدم ليس أدمن")
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")

    @new_bot.callback_query_handler(func=lambda call: call.data == "list_admins")
    def list_admins(call):
        if admins:
            admin_list = "\n".join([f"👤 {admin_id} {'(المشرف الرئيسي)' if admin_id == ADMIN_ID else ''}" for admin_id in admins])
            new_bot.send_message(call.message.chat.id, f"📋 قائمة الأدمنز:\n{admin_list}")
        else:
            new_bot.send_message(call.message.chat.id, "⚠️ لا يوجد أدمنز")

    def add_button(message):
        try:
            button_text = message.text.strip()
            if len(button_text) > 20:
                new_bot.send_message(message.chat.id, "⚠️ نص الزر طويل جداً (الحد الأقصى 20 حرف)")
                return
                
            button_edit_states[message.chat.id] = {'action': 'add_button', 'text': button_text}
            new_bot.send_message(message.chat.id, "📌 أرسل الرابط الذي تريد ربطه بهذا الزر")
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")
    
    def process_button_url(message):
        try:
            user_data = button_edit_states.get(message.chat.id, {})
            if user_data.get('action') == 'add_button':
                button_url = message.text.strip()
                if not button_url.startswith(('http://', 'https://', 't.me/')):
                    new_bot.send_message(message.chat.id, "⚠️ الرابط غير صحيح (يجب أن يبدأ بـ http:// أو https:// أو t.me/)")
                    return
                    
                custom_buttons.append({
                    'text': user_data['text'],
                    'url': button_url
                })
                save_data()
                new_bot.send_message(message.chat.id, f"✅ تمت إضافة الزر '{user_data['text']}' بنجاح")
                button_edit_states.pop(message.chat.id, None)
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")
    
    def remove_button(message):
        try:
            button_text = message.text.strip()
            global custom_buttons
            custom_buttons = [btn for btn in custom_buttons if btn['text'] != button_text]
            save_data()
            new_bot.send_message(message.chat.id, f"✅ تم حذف الزر '{button_text}' بنجاح")
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")
    
    def edit_button(message):
        try:
            button_text = message.text.strip()
            found = any(btn['text'] == button_text for btn in custom_buttons)
            if found:
                button_edit_states[message.chat.id] = {'action': 'edit_button', 'old_text': button_text}
                new_bot.send_message(message.chat.id, "📌 أرسل النص الجديد للزر")
            else:
                new_bot.send_message(message.chat.id, "⚠️ لا يوجد زر بهذا النص")
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")
    
    def process_button_edit(message):
        try:
            user_data = button_edit_states.get(message.chat.id, {})
            if user_data.get('action') == 'edit_button':
                new_text = message.text.strip()
                if len(new_text) > 20:
                    new_bot.send_message(message.chat.id, "⚠️ نص الزر طويل جداً (الحد الأقصى 20 حرف)")
                    return
                    
                for btn in custom_buttons:
                    if btn['text'] == user_data['old_text']:
                        btn['text'] = new_text
                        break
                save_data()
                new_bot.send_message(message.chat.id, f"✅ تم تعديل الزر من '{user_data['old_text']}' إلى '{new_text}' بنجاح")
                button_edit_states.pop(message.chat.id, None)
        except Exception as e:
            new_bot.send_message(message.chat.id, f"⚠️ خطأ: {str(e)}")

    @new_bot.callback_query_handler(func=lambda call: call.data == "list_buttons")
    def list_buttons(call):
        if custom_buttons:
            buttons_list = "\n".join([f"🔘 {btn['text']} → {btn['url']}" for btn in custom_buttons])
            new_bot.send_message(call.message.chat.id, f"📋 قائمة الأزرار المخصصة:\n{buttons_list}")
        else:
            new_bot.send_message(call.message.chat.id, "⚠️ لا توجد أزرار مخصصة")
            
    @new_bot.message_handler(func=lambda message: button_edit_states.get(message.chat.id, {}).get('action') == 'add_button')
    def handle_button_url(message):
        process_button_url(message)
    
    @new_bot.message_handler(func=lambda message: button_edit_states.get(message.chat.id, {}).get('action') == 'edit_button' and 'old_text' in button_edit_states.get(message.chat.id, {}))
    def handle_button_edit(message):
        process_button_edit(message)
        
    @new_bot.callback_query_handler(func=lambda call: True)
    def admin_actions(call):
        global welcome_notification_enabled
        if call.data == "add_admin":
            new_bot.send_message(call.message.chat.id, "📌 أرسل معرف المستخدم أو ID لإضافته كأدمن:")
            new_bot.register_next_step_handler(call.message, add_admin)
            
        elif call.data == "remove_admin":
            new_bot.send_message(call.message.chat.id, "📌 أرسل معرف المستخدم أو ID للأدمن الذي تريد حذفه:")
            new_bot.register_next_step_handler(call.message, remove_admin)
            
        elif call.data == "add_button":
            new_bot.send_message(call.message.chat.id, "📌 أرسل نص الزر الجديد (الحد الأقصى 20 حرف):")
            new_bot.register_next_step_handler(call.message, add_button)
            
        elif call.data == "remove_button":
            new_bot.send_message(call.message.chat.id, "📌 أرسل نص الزر الذي تريد حذفه:")
            new_bot.register_next_step_handler(call.message, remove_button)
            
        elif call.data == "edit_button":
            new_bot.send_message(call.message.chat.id, "📌 أرسل نص الزر الذي تريد تعديله:")
            new_bot.register_next_step_handler(call.message, edit_button)
            
        elif call.data == "add_channel":
            new_bot.send_message(call.message.chat.id, "📌 أرسل معرف القناة لإضافتها (مثال: @QQVQQS):")
            new_bot.register_next_step_handler(call.message, add_channel)
            
        elif call.data == "list_channels":
            if channels:
                new_bot.send_message(call.message.chat.id, "📋 القنوات الحالية:\n" + "\n".join(channels))
            else:
                new_bot.send_message(call.message.chat.id, "⚠️ لا توجد قنوات مضافة.")
                
        elif call.data == "remove_channel":
            if channels:
                new_bot.send_message(call.message.chat.id, "📌 أرسل معرف القناة لحذفها (مثال: @QQVQQS):")
                new_bot.register_next_step_handler(call.message, remove_channel)
            else:
                new_bot.send_message(call.message.chat.id, "⚠️ لا توجد قنوات لحذفها.")
                
        elif call.data == "bot_stats":
            new_bot.send_message(call.message.chat.id, f"📊 عدد المستخدمين: {len(users)}\n🚫 عدد المحظورين: {len(banned_users)}")
            
        elif call.data == "broadcast":
            new_bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:")
            new_bot.register_next_step_handler(call.message, broadcast_message)
            
        elif call.data == "disable_bot":
            
            bot_enabled = False
            new_bot.send_message(call.message.chat.id, "🔒 تم قفل البوت.")
            
        elif call.data == "enable_bot":
            
            bot_enabled = True
            new_bot.send_message(call.message.chat.id, "🔓 تم تشغيل البوت.")
            
        elif call.data == "ban_user":
            new_bot.send_message(call.message.chat.id, "🚫 أرسل ID المستخدم لحظره:")
            new_bot.register_next_step_handler(call.message, ban_user)
            
        elif call.data == "unban_user":
            new_bot.send_message(call.message.chat.id, "✅ أرسل ID المستخدم لفك الحظر:")
            new_bot.register_next_step_handler(call.message, unban_user)
            
        elif call.data == "change_welcome_photo":
            new_bot.send_message(call.message.chat.id, "📌 أرسل رابط الصورة الجديدة:")
            new_bot.register_next_step_handler(call.message, change_welcome_photo)
            
        elif call.data == "change_welcome_message":
            new_bot.send_message(call.message.chat.id, "📌 أرسل الرسالة الترحيبية الجديدة (يمكنك استخدام المتغيرات التالية):\n"
                                  "{user_name} - اسم المستخدم\n{user_id} - ID المستخدم\n{user_username} - المعرف")
            new_bot.register_next_step_handler(call.message, change_welcome_message)
            
        elif call.data == "change_confirmation_message":
            new_bot.send_message(call.message.chat.id, "📌 أرسل الرسالة الجديدة لتأكيد إرسال الرسالة:")
            new_bot.register_next_step_handler(call.message, change_confirmation_message)
            
        elif call.data == "toggle_welcome_notification":
            welcome_notification_enabled = not welcome_notification_enabled
            status = "مفعل" if welcome_notification_enabled else "موقوف"
            new_bot.send_message(call.message.chat.id, f"📢 تم {'تفعيل' if welcome_notification_enabled else 'إيقاف'} إشعار الدخول.")
    
    def add_channel(message):
        channel = message.text.strip()
        if channel.startswith("@"):
            channels.append(channel)
            save_data()
            new_bot.send_message(message.chat.id, f"✅ تم إضافة القناة: {channel}")
        else:
            new_bot.send_message(message.chat.id, "⚠️ المعرف غير صالح.")
    
    def remove_channel(message):
        channel = message.text.strip()
        if channel in channels:
            channels.remove(channel)
            save_data()
            new_bot.send_message(message.chat.id, f"✅ تم حذف القناة: {channel}")
        else:
            new_bot.send_message(message.chat.id, "⚠️ القناة غير موجودة.")
    
    def change_welcome_photo(message):
        global welcome_photo_url
        welcome_photo_url = message.text.strip()
        save_data()
        new_bot.send_message(message.chat.id, "✅ تم تغيير صورة الترحيب.")
    
    def change_welcome_message(message):
        global welcome_message
        welcome_message = message.text.strip()
        save_data()
        new_bot.send_message(message.chat.id, "✅ تم تغيير رسالة الترحيب.")
    
    @new_bot.message_handler(content_types=['new_chat_members'])
    def welcome_user(message):
        if welcome_notification_enabled:
            for new_member in message.new_chat_members:
                user_info = (
                    f"📋 معلومات المستخدم الجديد:\n"
                    f"👤 الاسم: {new_member.full_name}\n"
                    f"🆔 ID: {new_member.id}\n"
                    f"💬 المعرف: @{new_member.username if new_member.username else 'لا يوجد'}\n"
                    f"🔢 رقم المستخدم في البوت: {len(users)}"
                )
                
                for admin_id in admins:
                    try:
                        new_bot.send_message(admin_id, user_info)
                    except Exception as e:
                        print(f"فشل إرسال إشعار للمشرف {admin_id}: {e}")

    @new_bot.message_handler(commands=['start'])
    def start(message):
        if message.chat.id in banned_users:
            new_bot.send_message(message.chat.id, "🚫 لقد تم حظرك من استخدام هذا البوت.")
            return
    
        if not bot_enabled:
            new_bot.send_message(message.chat.id, "🔒 البوت متوقف حاليًا. الرجاء المحاولة لاحقًا.")
            return
    
        user_name = message.from_user.first_name or "مستخدم مجهول"
        user_id = message.chat.id
        user_username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد معرف"
    
        if check_subscription(message.chat.id):
            users.add(message.chat.id)
            save_data()
    
            caption = welcome_message.format(
                user_name=user_name,
                user_id=user_id,
                user_username=user_username
            )
    
            markup = types.InlineKeyboardMarkup(row_width=2)
            for button in custom_buttons:
                markup.add(types.InlineKeyboardButton(button["text"], url=button["url"]))
    
            try:
                new_bot.send_photo(
                    message.chat.id,
                    photo=welcome_photo_url,
                    caption=caption,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Error sending welcome photo: {e}")
                new_bot.send_message(
                    message.chat.id,
                    caption,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
        else:
            markup = types.InlineKeyboardMarkup()
            for channel in channels:
                markup.add(types.InlineKeyboardButton(f"اشترك في {channel}", url=f"https://t.me/{channel[1:]}"))
            new_bot.send_message(
                message.chat.id,
                "⚠️ يجب الاشتراك في القنوات التالية أولاً للاستمرار:",
                reply_markup=markup
            )
    
    @new_bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
    def forward_to_admin(message):
        if check_subscription(message.chat.id):
            user_name = message.from_user.first_name or "مستخدم مجهول"
            user_id = message.chat.id
            user_username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد معرف"
            
            user_info = (
                f"📩 رسالة جديدة من المستخدم:\n\n"
                f"👤 الاسم: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📎 المعرف: {user_username}\n"
            )
            
            forwarded_ids = {}
            for admin_id in admins:
                try:
                    forwarded_msg = new_bot.forward_message(admin_id, message.chat.id, message.message_id)
                    new_bot.send_message(admin_id, user_info)
                    forwarded_ids[admin_id] = forwarded_msg.message_id
                except Exception as e:
                    print(f"فشل إرسال رسالة للمشرف {admin_id}: {e}")
            
            for admin_id, msg_id in forwarded_ids.items():
                sessions[(admin_id, msg_id)] = message.chat.id
            
            new_bot.send_message(
                message.chat.id,
                confirmation_message
            )
        else:
            markup = types.InlineKeyboardMarkup()
            for channel in channels:
                markup.add(types.InlineKeyboardButton(f"اشترك في {channel}", url=f"https://t.me/{channel[1:]}"))
            new_bot.send_message(
                message.chat.id,
                "⚠️ يجب الاشتراك في القنوات التالية أولاً للاستمرار:",
                reply_markup=markup
            )
    
    @new_bot.message_handler(func=lambda message: message.chat.id in admins and message.reply_to_message)
    def reply_to_user(message):
        original_message_id = message.reply_to_message.message_id
        user_id = sessions.get((message.chat.id, original_message_id))
        
        if user_id:
            try:
                new_bot.send_message(user_id, f"\n\n{message.text}")
                new_bot.send_message(message.chat.id, "✅ تم إرسال الرد للمستخدم.")
                
                for admin_id in admins:
                    if admin_id != message.chat.id:
                        try:
                            new_bot.send_message(
                                admin_id,
                                f"📬 تم إرسال رد من الأدمن {message.from_user.first_name}:\n"
                                f"المستخدم: {user_id}\n"
                                f"الرسالة: {message.text}"
                            )
                        except Exception as e:
                            print(f"فشل إرسال إشعار للمشرف {admin_id}: {e}")
            except Exception as e:
                new_bot.send_message(message.chat.id, f"⚠️ حدث خطأ أثناء إرسال الرد: {e}")
        else:
            new_bot.send_message(message.chat.id, "⚠️ تعذر العثور على المستخدم الأصلي لهذه الرسالة.")
    
    new_bot.polling()

@factory_bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛠 صناعة بوت", callback_data="create_bot"))
    
    factory_bot.send_message(chat_id, "مرحبًا بك في مصنع البوتات!\nاختر أحد الخيارات:", reply_markup=markup)

@factory_bot.callback_query_handler(func=lambda call: call.data == "create_bot")
def handle_create_bot(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = {"state": "awaiting_token"}
    factory_bot.send_message(chat_id, "🔹 أرسل توكن البوت:")


@factory_bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]["state"] == "awaiting_token")
def receive_owner_name(message):
    chat_id = message.chat.id
    token = message.text.strip()
    try:
        bot_instance = telebot.TeleBot(token)
        bot_info = bot_instance.get_me()
        bot_username = bot_info.username
    except Exception:
        factory_bot.send_message(chat_id, "❌ التوكن غير صالح! حاول مجددًا.")
        return

    
    owner_id = message.from_user.id
    owner_username = message.from_user.username or "غير معروف"
    
    random_number = random.randint(100000000, 999999999)

    bot_data = {
        "token": token,
        "username": bot_username,
        "owner_id": owner_id,
        "owner_username": owner_username,
        "id": random_number
    }
    
    created_bots.append(bot_data)
    del user_states[chat_id]
    
    threading.Thread(target=run_new_bot, args=(bot_data,), daemon=True).start()
    
    factory_bot.send_message(
        chat_id,
        f"✅ تم إنشاء البوت بنجاح!\n🤖 يوزر البوت: @{bot_data['username']}\n👤 المالك:  (@{bot_data['owner_username']})"
    )

@factory_bot.callback_query_handler(func=lambda call: call.data == "manage_bot")
def manage_bot(call):
    chat_id = call.message.chat.id
    user_bots = [bot for bot in created_bots if bot["owner_id"] == chat_id]

    if not user_bots:
        factory_bot.send_message(chat_id, "⚠️ ليس لديك أي بوتات مُسجلة.")
        return

    markup = types.InlineKeyboardMarkup()
    for bot in user_bots:
        btn = types.InlineKeyboardButton(f"🔧 @{bot['username']}", callback_data=f"edit_{bot['token']}")
        markup.add(btn)

    factory_bot.send_message(chat_id, "🔽 اختر البوت الذي تريد تعديله أو حذفه:", reply_markup=markup)

@factory_bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_bot(call):
    chat_id = call.message.chat.id
    token = call.data.split("_")[1]

    bot_data = next((bot for bot in created_bots if bot["token"] == token), None)
    if not bot_data:
        factory_bot.send_message(chat_id, "❌ لم يتم العثور على البوت.")
        return

    user_states[chat_id] = {"state": "editing_bot", "data": bot_data}

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ تغيير اسم المالك", callback_data="change_name"))
    markup.add(types.InlineKeyboardButton("🗑 حذف البوت", callback_data="delete_bot"))
    markup.add(types.InlineKeyboardButton("🔄 تحديث البوت", callback_data="restart_bot"))

    factory_bot.send_message(
        chat_id,
        f"⚙️ التحكم في البوت: @{bot_data['username']}\n"
        f"👤 المالك: {bot_data['owner_name']} (@{bot_data['owner_username']})",
        reply_markup=markup
    )

@factory_bot.callback_query_handler(func=lambda call: call.data in ["change_name", "restart_bot"])
def modify_bot(call):
    chat_id = call.message.chat.id
    if chat_id not in user_states or user_states[chat_id]["state"] != "editing_bot":
        factory_bot.send_message(chat_id, "⚠️ حدث خطأ. حاول مرة أخرى.")
        return

    bot_data = user_states[chat_id]["data"]

    if call.data == "change_name":
        user_states[chat_id]["state"] = "awaiting_new_name"
        factory_bot.send_message(chat_id, "✏️ أرسل الاسم الجديد لمالك البوت:")

    elif call.data == "restart_bot":
        token = bot_data["token"]

        if token in running_bots:
            running_bots[token].stop_polling()
            del running_bots[token]

        threading.Thread(target=run_new_bot, args=(bot_data,), daemon=True).start()
        factory_bot.send_message(chat_id, f"🔄 تم **إعادة تشغيل البوت** @{bot_data['username']} بنجاح!")

@factory_bot.callback_query_handler(func=lambda call: call.data == "delete_bot")
def delete_bot(call):
    chat_id = call.message.chat.id
    if chat_id not in user_states or user_states[chat_id]["state"] != "editing_bot":
        factory_bot.send_message(chat_id, "⚠️ حدث خطأ. حاول مرة أخرى.")
        return

    bot_data = user_states[chat_id]["data"]
    token = bot_data["token"]

    if token in running_bots:
        running_bots[token].stop_polling()
        del running_bots[token]

    created_bots.remove(bot_data)
    del user_states[chat_id]

    factory_bot.send_message(chat_id, f"🗑 تم **إيقاف وحذف البوت** @{bot_data['username']} بنجاح!")

@factory_bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_editing(message):
    chat_id = message.chat.id
    bot_data = user_states[chat_id]["data"]

    if user_states[chat_id]["state"] == "awaiting_new_name":
        bot_data["owner_name"] = message.text.strip()

        token = bot_data["token"]
        if token in running_bots:
            running_bots[token].stop_polling()
            del running_bots[token]

        new_bot = (token)
        running_bots[token] = new_bot

        factory_bot.send_message(chat_id, "✅ تم تحديث اسم المالك وإعادة تشغيل البوت.")

    del user_states[chat_id]
    
factory_bot.infinity_polling()
