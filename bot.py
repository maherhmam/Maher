import os
import json
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# --- الإعدادات ---
BOT_TOKEN = "1448950819:AAG1a1IrYm7VNAI-vLR2dw_kXlhTZOKGEwc"
DEVELOPER_ID = 580885943

# المجلد المؤقت للبيانات
TMP_DIR = Path("/tmp") if os.path.exists("/tmp") else Path(".")
USERS_FILE = TMP_DIR / "bakaloria_users.txt"
CONFIG_FILE = TMP_DIR / "bakaloria_config.json"

# إعدادات القنوات والاشتراك
config = {
    "mandatory_channels": ["@SyriaEduOfficial"],
    "force_subscription": True
}

# --- وظائف النظام ---
def register_user(user_id: int):
    if not USERS_FILE.exists():
        USERS_FILE.write_text("", encoding="utf-8")
    users = set(USERS_FILE.read_text(encoding="utf-8").splitlines())
    if str(user_id) not in users:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")

async def is_subscribed(context, user_id, channels):
    from telegram.constants import ChatMemberStatus
    for channel in channels:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False
        except: return False
    return True

# --- قاعدة البيانات (المناهج) ---
CURRICULUM = {
    "📚 علمي": {
        "رياضيات": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/math.pdf"},
        "فيزياء": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/physics.pdf"},
        "كيمياء": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/chemistry.pdf"},
        "أحياء": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/biology.pdf"},
        "لغة إنكليزية": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/english.pdf"},
        "أسئلة الدورات": {
            "رياضيات": {"دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/math_d1.pdf"},
            "فيزياء": {"دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/physics_d1.pdf"},
            "كيمياء": {"دورة ثانية 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/chemistry_d2.pdf"}
        }
    },
    "📖 أدبي": {
        "لغة عربية": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/arabic.pdf"},
        "تاريخ": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/history.pdf"},
        "فلسفة": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/philosophy.pdf"},
        "أسئلة الدورات": {
            "لغة عربية": {"دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/arabic_d1.pdf"}
        }
    }
}

# --- الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    
    if user_id != DEVELOPER_ID and config["force_subscription"]:
        if not await is_subscribed(context, user_id, config["mandatory_channels"]):
            kb = [[InlineKeyboardButton(f"الاشتراك في {ch}", url=f"https://t.me/{ch.lstrip('@')}")] for ch in config["mandatory_channels"]]
            kb.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")])
            await update.message.reply_text("🔔 يجب الاشتراك بالقنوات أولاً:", reply_markup=InlineKeyboardMarkup(kb))
            return

    main_kb = [["📚 علمي"], ["📖 أدبي"]]
    await update.message.reply_text("مرحباً بك في مكتبة البكالوريا السورية 🇸🇾\nاختر فرعك:", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text in CURRICULUM:
        subs = [[s] for s in CURRICULUM[text].keys()]
        subs.append(["🔙 العودة للرئيسية"])
        await update.message.reply_text(f"قائمة مواد ال{text}:", reply_markup=ReplyKeyboardMarkup(subs, resize_keyboard=True))
        return

    if text == "🔙 العودة للرئيسية":
        await start(update, context)
        return

    for branch in CURRICULUM:
        if text in CURRICULUM[branch]:
            data = CURRICULUM[branch][text]
            if text == "أسئلة الدورات":
                d_kb = [[k] for k in data.keys()]
                d_kb.append(["🔙 العودة للرئيسية"])
                await update.message.reply_text("اختر مادة الأسئلة:", reply_markup=ReplyKeyboardMarkup(d_kb, resize_keyboard=True))
            else:
                res = f"📁 <b>ملفات {text}:</b>\n\n"
                for n, u in data.items(): res += f"• <a href='{u}'>{n}</a>\n"
                await update.message.reply_text(res, parse_mode="HTML", disable_web_page_preview=True)
            return

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_sub":
        if await is_subscribed(context, query.from_user.id, config["mandatory_channels"]):
            await query.edit_message_text("✅ تم التحقق! أرسل /start الآن.")
        else:
            await query.answer("❌ لم تشترك بعد!", show_alert=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)
