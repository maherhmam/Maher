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

# مجلد مؤقت (يعمل على الاستضافات السحابية)
TMP_DIR = Path("/tmp") if os.path.exists("/tmp") else Path(".")
USERS_FILE = TMP_DIR / "bakaloria_users.txt"
CONFIG_FILE = TMP_DIR / "bakaloria_config.json"

# تحميل أو إنشاء config
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {
        "mandatory_channels": ["@SyriaEduOfficial"],
        "force_subscription": True
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# تسجيل مستخدم
def register_user(user_id: int):
    if not USERS_FILE.exists():
        USERS_FILE.write_text("", encoding="utf-8")
    users = set(USERS_FILE.read_text(encoding="utf-8").splitlines())
    if str(user_id) not in users:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")

# التحقق من الاشتراك
async def is_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int, channels: list) -> bool:
    from telegram.constants import ChatMemberStatus
    for channel in channels:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]:
                return False
        except Exception:
            return False
    return True

# حفظ الإعدادات
def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# --- المناهج وأسئلة الدورات ---
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
        "لغة إنكليزية": {"الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/english.pdf"},
        "أسئلة الدورات": {
            "لغة عربية": {"دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/arabic_d1.pdf"}
        }
    }
}

# --- معالجات الأوامر ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    
    if user_id != DEVELOPER_ID and config["force_subscription"]:
        if not await is_subscribed(context, user_id, config["mandatory_channels"]):
            keyboard = [[InlineKeyboardButton(f"الاشتراك في {ch}", url=f"https://t.me/{ch.lstrip('@')}")] for ch in config["mandatory_channels"]]
            keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")])
            await update.message.reply_text("🔔 يجب الاشتراك في القنوات لاستخدام البوت:", reply_markup=InlineKeyboardMarkup(keyboard))
            return

    keyboard = [["📚 علمي"], ["📖 أدبي"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("مرحبًا بك! اختر فرعك الدراسي:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_sub":
        if await is_subscribed(context, query.from_user.id, config["mandatory_channels"]):
            await query.edit_message_text("✅ تم التحقق! اضغط /start للبدء.")
        else:
            await query.answer("❌ لم تشترك بعد!", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if text in CURRICULUM:
        subjects = [[s] for s in CURRICULUM[text].keys()]
        subjects.append(["🔙 العودة"])
        await update.message.reply_text(f"اختر المادة:", reply_markup=ReplyKeyboardMarkup(subjects, resize_keyboard=True))
        return

    if text == "🔙 العودة":
        await start(update, context)
        return

    # بحث في المواد
    for branch in CURRICULUM:
        if text in CURRICULUM[branch]:
            files = CURRICULUM[branch][text]
            msg = f"📁 ملفات <b>{text}</b>:\n\n"
            for name, url in files.items():
                msg += f"• <a href='{url}'>{name}</a>\n"
            await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)
            return

    await update.message.reply_text("الرجاء اختيار خيار من القائمة.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
    
