import os
import json
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

# مجلد مؤقت (يعمل على Pantheon)
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
async def is_subscribed(user_id: int, channels: list) -> bool:
    from telegram.constants import ChatMemberStatus
    for channel in channels:
        try:
            chat_member = await application.bot.get_chat_member(chat_id=channel, user_id=user_id)            if chat_member.status not in [
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
    "علمي": {
        "رياضيات": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/math.pdf"
        },
        "فيزياء": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/physics.pdf"
        },
        "كيمياء": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/chemistry.pdf"
        },
        "أحياء": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/biology.pdf"
        },
        "لغة إنكليزية": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/scientific/english.pdf"
        },
        "أسئلة الدورات": {
            "رياضيات": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/math_d1.pdf"
            },
            "فيزياء": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/physics_d1.pdf"
            },
            "كيمياء": {
                "دورة ثانية 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/chemistry_d2.pdf"
            },
            "أحياء": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/biology_d1.pdf"
            },
            "لغة إنكليزية": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/scientific/english_d1.pdf"
            }
        }    },
    "أدبي": {
        "لغة عربية": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/arabic.pdf"
        },
        "تاريخ": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/history.pdf"
        },
        "جغرافيا": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/geography.pdf"
        },
        "فلسفة": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/philosophy.pdf"
        },
        "علم نفس": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/psychology.pdf"
        },
        "لغة إنكليزية": {
            "الكتاب الرسمي 2026": "http://www.education.gov.sy/ar/images/books/2026/secondary/literary/english.pdf"
        },
        "أسئلة الدورات": {
            "لغة عربية": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/arabic_d1.pdf"
            },
            "تاريخ": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/history_d1.pdf"
            },
            "جغرافيا": {
                "دورة ثانية 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/geography_d2.pdf"
            },
            "فلسفة": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/philosophy_d1.pdf"
            },
            "علم نفس": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/psychology_d1.pdf"
            },
            "لغة إنكليزية": {
                "دورة أولى 2025": "http://www.education.gov.sy/ar/images/exams/2025/bac/literary/english_d1.pdf"
            }
        }
    }
}

# --- معالجات الأوامر ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    
    # التحقق من الاشتراك    if user_id != DEVELOPER_ID and config["force_subscription"]:
        if not await is_subscribed(user_id, config["mandatory_channels"]):
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك في {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
                for ch in config["mandatory_channels"]
            ]
            keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🔔 يجب الاشتراك في القنوات التالية لاستخدام البوت:",
                reply_markup=reply_markup
            )
            return

    keyboard = [
        ["📚 علمي"],
        ["📖 أدبي"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "مرحبًا بك في مكتبة البكالوريا السورية! 🇸🇾\n\nاختر فرعك الدراسي:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_sub":
        if await is_subscribed(user_id, config["mandatory_channels"]):
            await query.edit_message_text("✅ تم التحقق! يمكنك الآن استخدام البوت.\n\nاضغط /start للبدء.")
        else:
            await query.edit_message_text("❌ لم تشترك بعد! يرجى الاشتراك ثم الضغط على \"تحقق من الاشتراك\".")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    register_user(user_id)

    # التحقق من الاشتراك
    if user_id != DEVELOPER_ID and config["force_subscription"]:
        if not await is_subscribed(user_id, config["mandatory_channels"]):
            await start(update, context)
            return

    # أوامر المطور
    if user_id == DEVELOPER_ID:
        if text == "/stats":
            users = USERS_FILE.read_text(encoding="utf-8").splitlines() if USERS_FILE.exists() else []            await update.message.reply_text(f"📊 <b>إحصائيات البوت:</b>\n\n• المستخدمون المسجلون: {len(users)}", parse_mode="HTML")
            return

        if text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "", 1)
            users = USERS_FILE.read_text(encoding="utf-8").splitlines() if USERS_FILE.exists() else []
            count = 0
            for uid in users:
                try:
                    await context.bot.send_message(chat_id=uid, text=msg, parse_mode="HTML")
                    count += 1
                except Exception:
                    pass
            await update.message.reply_text(f"✅ تم إرسال الإذاعة إلى {count} مستخدم.")
            return

        if text.startswith("/addchannel @"):
            ch = text.split()[1]
            if ch not in config["mandatory_channels"]:
                config["mandatory_channels"].append(ch)
                save_config()
                await update.message.reply_text(f"✅ تمت إضافة القناة: {ch}")
            else:
                await update.message.reply_text("⚠️ القناة موجودة مسبقًا.")
            return

        if text.startswith("/removechannel @"):
            ch = text.split()[1]
            if ch in config["mandatory_channels"]:
                config["mandatory_channels"].remove(ch)
                save_config()
                await update.message.reply_text(f"🗑️ تمت إزالة القناة: {ch}")
            else:
                await update.message.reply_text("⚠️ القناة غير موجودة.")
            return

        if text == "/toggleforce":
            config["force_subscription"] = not config["force_subscription"]
            save_config()
            status = "مفعل" if config["force_subscription"] else "معطل"
            await update.message.reply_text(f"🔄 تم {status} الاشتراك الإجباري.")
            return

    # معالجة الفروع
    if text in ["علمي", "أدبي"]:
        subjects = list(CURRICULUM[text].keys())
        keyboard = [[s] for s in subjects]
        keyboard.append(["🔙 العودة إلى الفروع"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"اختر مادة أو قسم من فرع {text}:", reply_markup=reply_markup)        return

    # المواد العادية
    for branch in ["علمي", "أدبي"]:
        if text in CURRICULUM[branch] and text != "أسئلة الدورات":
            files = CURRICULUM[branch][text]
            msg = f"📁 <b>الملفات المتاحة لمادة {text}:</b>\n\n"
            for name, url in files.items():
                msg += f"• <a href='{url}'>{name}</a>\n"
            msg += "\n📥 اضغط على الرابط لتحميل الملف."
            keyboard = [["🔙 العودة إلى المواد"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
            return

    # أسئلة الدورات
    for branch in ["علمي", "أدبي"]:
        if "أسئلة الدورات" in CURRICULUM[branch] and text in CURRICULUM[branch]["أسئلة الدورات"]:
            files = CURRICULUM[branch]["أسئلة الدورات"][text]
            msg = f"📁 <b>أسئلة دورات مادة {text}:</b>\n\n"
            for name, url in files.items():
                msg += f"• <a href='{url}'>{name}</a>\n"
            msg += "\n📥 اضغط على الرابط لتحميل الأسئلة."
            keyboard = [["🔙 العودة إلى المواد"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
            return

    await update.message.reply_text("❌ لم أفهم طلبك. اضغط /start للعودة.")

# --- التشغيل ---
from telegram.ext import ReplyKeyboardMarkup

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت يعمل على Pantheon.io")
    application.run_polling()