
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CallbackQueryHandler, CommandHandler
from telegram.error import BadRequest

TOKEN = "7568547711:AAGZX6GgV-eOmxPDdp8ccny3bvm6dB-oAQA"
ADMINS = [6308973450]  # آیدی عددی خودت
CHANNEL_USERNAME = "@VIP_VIDS"  # نام کانال شما
CHANNEL_ID = -1002804085447  # آیدی عددی کانال VIP_VIDS

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی عضویت کاربر در کانال"""
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except BadRequest:
        return False

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی عضویت و نمایش پیام مناسب"""
    user_id = update.effective_user.id
    
    # اگر کاربر ادمین است، بررسی عضویت نکن
    if user_id in ADMINS:
        return await get_file_id(update, context)
    
    # بررسی عضویت
    if not await is_user_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("🔗 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🚨⚠️ هشدار ⚠️🚨\n\n"
            "❌ برای استفاده از ربات، ابتدا باید در کانال ما عضو شوید!\n\n"
            f"📢 کانال: {CHANNEL_USERNAME}\n\n"
            "🔥 فوری عضو شوید و روی 'بررسی عضویت' کلیک کنید!\n"
            "⛔️ بدون عضویت امکان دسترسی به فایل‌ها وجود ندارد!",
            reply_markup=reply_markup
        )
        return
    
    # اگر عضو است، ادامه بده
    await handle_message(update, context)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت دستور /start با پارامتر"""
    user_id = update.effective_user.id
    
    # اگر کاربر ادمین است، بررسی عضویت نکن
    if user_id not in ADMINS:
        # بررسی عضویت
        if not await is_user_member(user_id, context):
            # تعیین callback_data بر اساس پارامتر
            callback_data = "check_membership"
            if context.args:
                callback_data += f"_{context.args[0]}"
            
            keyboard = [
                [InlineKeyboardButton("🔗 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                [InlineKeyboardButton("✅ بررسی عضویت", callback_data=callback_data)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🚨⚠️ هشدار ⚠️🚨\n\n"
                "❌ برای استفاده از ربات، ابتدا باید در کانال ما عضو شوید!\n\n"
                f"📢 کانال: {CHANNEL_USERNAME}\n\n"
                "🔥 فوری عضو شوید و روی 'بررسی عضویت' کلیک کنید!\n"
                "⛔️ بدون عضویت امکان دسترسی به فایل‌ها وجود ندارد!",
                reply_markup=reply_markup
            )
            return
    
    # بررسی پارامتر start
    if context.args:
        film_name = context.args[0]
        
        # بارگذاری اطلاعات فیلم‌ها
        try:
            with open('films.json', 'r', encoding='utf-8') as f:
                films = json.load(f)
        except FileNotFoundError:
            await update.message.reply_text("❌ هیچ فیلمی در دیتابیس موجود نیست!")
            return
        
        # جستجو و ارسال فیلم
        if film_name in films:
            file_id = films[film_name]
            await context.bot.send_video(
                chat_id=update.message.chat_id,
                video=file_id,
                caption=f"🎬 {film_name}"
            )
        else:
            await update.message.reply_text(f"❌ فیلم '{film_name}' پیدا نشد!")
    else:
        # پیام خوش‌آمدگویی معمولی
        await update.message.reply_text("👋 سلام! برای دریافت فیلم، نام آن را ارسال کنید.")

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت callback query ها"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("check_membership"):
        user_id = query.from_user.id
        
        if await is_user_member(user_id, context):
            # حذف پیام قبلی
            await query.delete_message()
            
            # بررسی اینکه آیا پارامتر فیلم وجود دارد
            if "_" in query.data:
                film_name = query.data.split("_", 1)[1]
                
                # بارگذاری اطلاعات فیلم‌ها
                try:
                    with open('films.json', 'r', encoding='utf-8') as f:
                        films = json.load(f)
                except FileNotFoundError:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="❌ هیچ فیلمی در دیتابیس موجود نیست!"
                    )
                    return
                
                # ارسال فیلم
                if film_name in films:
                    file_id = films[film_name]
                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=file_id,
                        caption=f"🎬 {film_name}"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=f"❌ فیلم '{film_name}' پیدا نشد!"
                    )
            else:
                # پیام معمولی تایید عضویت
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="✅ عضویت شما تایید شد! حالا می‌تونید از ربات استفاده کنید."
                )
        else:
            # استخراج نام فیلم از callback_data
            film_param = ""
            if "_" in query.data:
                # فقط نام فیلم را استخراج می‌کنیم، نه کل callback_data را
                parts = query.data.split("_")
                if len(parts) > 1:
                    film_param = "_" + parts[-1]  # فقط آخرین بخش که نام فیلم است
            
            keyboard = [
                [InlineKeyboardButton("🔗 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                [InlineKeyboardButton("✅ بررسی عضویت", callback_data=f"check_membership{film_param}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    "🚨⚠️ هشدار ⚠️🚨\n\n"
                    "❌ شما هنوز عضو کانال نشده‌اید!\n\n"
                    f"📢 برای دریافت فایل باید حتماً عضو شوید: {CHANNEL_USERNAME}\n\n"
                    "🔥 فوری عضو شوید و دوباره تلاش کنید!\n"
                    "⛔️ بدون عضویت امکان دسترسی به فایل‌ها وجود ندارد!",
                    reply_markup=reply_markup
                )
            except BadRequest:
                # اگر پیام تغییری نکرده، هیچ کاری نکن
                pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های دریافتی"""
    message = update.message
    
    # بررسی اینکه آیا فایل ارسال شده یا خیر
    if message.video or message.document or message.photo:
        # بارگذاری اطلاعات فیلم‌ها
        try:
            with open('films.json', 'r', encoding='utf-8') as f:
                films = json.load(f)
        except FileNotFoundError:
            films = {}
        
        # نمایش لیست فیلم‌ها
        if films:
            film_list = "🎬 فیلم‌های موجود:\n\n"
            for i, (film_name, file_id) in enumerate(films.items(), 1):
                film_list += f"{i}. {film_name}\n"
            
            film_list += "\nنام فیلم مورد نظر خود را ارسال کنید:"
            await message.reply_text(film_list)
        else:
            await message.reply_text("❌ هیچ فیلمی در دیتابیس موجود نیست!")
    
    elif message.text:
        # جستجو در فیلم‌ها
        try:
            with open('films.json', 'r', encoding='utf-8') as f:
                films = json.load(f)
        except FileNotFoundError:
            await message.reply_text("❌ هیچ فیلمی در دیتابیس موجود نیست!")
            return
        
        search_text = message.text.strip()
        
        # جستجوی دقیق
        if search_text in films:
            file_id = films[search_text]
            await context.bot.send_video(
                chat_id=message.chat_id,
                video=file_id,
                caption=f"🎬 {search_text}"
            )
        else:
            # جستجوی تقریبی
            found_films = []
            for film_name in films.keys():
                if search_text.lower() in film_name.lower():
                    found_films.append(film_name)
            
            if found_films:
                result = "🔍 فیلم‌های پیدا شده:\n\n"
                for film in found_films:
                    result += f"• {film}\n"
                result += "\nنام دقیق فیلم را ارسال کنید:"
                await message.reply_text(result)
            else:
                await message.reply_text("❌ فیلم مورد نظر پیدا نشد!")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استخراج File ID برای ادمین‌ها"""
    user_id = update.effective_user.id

    if user_id not in ADMINS:
        return

    message = update.message

    if message.video:
        file_id = message.video.file_id
        await message.reply_text(f"🎬 File ID:\n{file_id}")
    elif message.document:
        file_id = message.document.file_id
        await message.reply_text(f"📄 File ID:\n{file_id}")
    elif message.photo:
        file_id = message.photo[-1].file_id
        await message.reply_text(f"🖼 File ID:\n{file_id}")
    else:
        await message.reply_text("⚠️ لطفاً فایل، عکس یا ویدیو ارسال کنید.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن هندلرها
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.ALL, check_membership))
    
    print("🤖 ربات با عضویت اجباری آماده است...")
    app.run_polling()

if __name__ == "__main__":
    main()
