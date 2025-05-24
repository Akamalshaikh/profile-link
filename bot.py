import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "7930172026:AAGjhibNR6PM4-ezNPBxzCmpjBmJsCdoUaI"
ADMIN_ID = 6994528708

# Initialize database
def init_db():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            join_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, join_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
🌟 <b>Welcome to Profile Link Generator Bot!</b> 🌟

👋 Hello {user.first_name}!

🔗 <b>What I can do for you:</b>
• Forward any message from any user
• Get instant profile link: <code>tg://openmessage?user_id=USER_ID</code>
• Quick access to any Telegram profile!

👨‍💻 <b>Developer:</b> @its_soloz

<i>Ready to get started? Just forward me any message! 🚀</i>
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 How to Use", callback_data="help")],
        [InlineKeyboardButton("💝 Developer", url="https://t.me/its_soloz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 <b>Detailed Guide - Profile Link Generator</b>

🔍 <b>What is this bot?</b>
This bot helps you generate direct Telegram profile links from forwarded messages!

📋 <b>Step-by-step instructions:</b>

1️⃣ <b>Find a message</b>
   • Go to any chat or channel
   • Find a message from the user you want

2️⃣ <b>Forward the message</b>
   • Tap and hold the message
   • Select "Forward"
   • Choose this bot

3️⃣ <b>Get the link</b>
   • I'll instantly generate the profile link
   • Format: <code>tg://openmessage?user_id=USER_ID</code>

4️⃣ <b>Use the link</b>
   • Click to open their profile
   • Works on any device with Telegram

🎯 <b>Pro Tips:</b>
• Works with messages from groups, channels, or private chats
• The link opens their profile directly
• No need to search for usernames!

⚡ <b>Instant Results:</b>
Forward → Get Link → Open Profile

🔒 <b>Privacy:</b>
• No messages are stored
• Only the user ID is extracted
• Your privacy is protected

Need more help? Contact: @its_soloz
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Home", callback_data="start")],
        [InlineKeyboardButton("💝 Developer", url="https://t.me/its_soloz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    if message.forward_from:
        # Message forwarded from a user
        user_id = message.forward_from.id
        user_name = message.forward_from.first_name
        username = message.forward_from.username
        
        profile_link = f"tg://openmessage?user_id={user_id}"
        
        response_text = f"""
🎉 <b>Profile Link Generated Successfully!</b>

👤 <b>User Details:</b>
• Name: {user_name}
{f"• Username: @{username}" if username else ""}
• User ID: <code>{user_id}</code>

🔗 <b>Profile Link:</b>
<code>{profile_link}</code>

✅ <b>What to do next:</b>
• Copy the link above
• Paste it in any chat
• Click to open their profile instantly!

💡 <b>Tip:</b> This link works on any device with Telegram installed.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔗 Open Profile", url=profile_link)],
            [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{user_id}")],
            [InlineKeyboardButton("🔄 Generate Another", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
    elif message.forward_from_chat:
        # Message forwarded from a channel
        chat_id = message.forward_from_chat.id
        chat_title = message.forward_from_chat.title
        chat_username = message.forward_from_chat.username
        
        if chat_username:
            profile_link = f"https://t.me/{chat_username}"
        else:
            profile_link = f"tg://openmessage?user_id={chat_id}"
        
        response_text = f"""
📢 <b>Channel/Group Link Generated!</b>

📱 <b>Chat Details:</b>
• Title: {chat_title}
{f"• Username: @{chat_username}" if chat_username else ""}
• Chat ID: <code>{chat_id}</code>

🔗 <b>Profile Link:</b>
<code>{profile_link}</code>

✅ <b>Ready to use!</b>
Click the button below to open the channel/group directly.
"""
        
        keyboard = [
            [InlineKeyboardButton("📢 Open Channel/Group", url=profile_link)],
            [InlineKeyboardButton("🔄 Generate Another", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
    else:
        # Not a forwarded message
        response_text = """
❌ <b>Oops! This is not a forwarded message.</b>

🤔 <b>What you sent:</b> Regular message (not forwarded)

📝 <b>To generate a profile link, you need to:</b>
1️⃣ Go to any chat where the user has sent a message
2️⃣ Find their message
3️⃣ Forward that message to me
4️⃣ I'll generate their profile link instantly!

💡 <b>Quick Guide:</b>
• Tap and hold any message
• Select "Forward"
• Choose this bot
• Get the profile link!

Need help? Tap the button below! 👇
"""
        
        keyboard = [
            [InlineKeyboardButton("📖 How to Forward Messages", callback_data="help")],
            [InlineKeyboardButton("💬 Contact Developer", url="https://t.me/its_soloz")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        response_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "start":
        # Recreate start message
        user = query.from_user
        welcome_text = f"""
🌟 <b>Welcome to Profile Link Generator Bot!</b> 🌟

👋 Hello {user.first_name}!

🔗 <b>What I can do for you:</b>
• Forward any message from any user
• Get instant profile link: <code>tg://openmessage?user_id=USER_ID</code>
• Quick access to any Telegram profile!

📖 <b>How to use:</b>
1️⃣ Forward any message from the user you want
2️⃣ I'll instantly generate their profile link
3️⃣ Click the link to open their profile directly!

✨ <b>Features:</b>
🚀 Lightning fast response
🔒 No data stored permanently
🎯 Works with any forwarded message
💎 Clean and beautiful interface

👨‍💻 <b>Developer:</b> @its_soloz

<i>Ready to get started? Just forward me any message! 🚀</i>
"""
        
        keyboard = [
            [InlineKeyboardButton("📖 How to Use", callback_data="help")],
            [InlineKeyboardButton("💝 Developer", url="https://t.me/its_soloz")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    elif query.data.startswith("copy_"):
        user_id = query.data.split("_")[1]
        profile_link = f"tg://openmessage?user_id={user_id}"
        
        copy_text = f"""
📋 <b>Link Ready to Copy!</b>

🔗 <b>Profile Link:</b>
<code>{profile_link}</code>

📱 <b>How to copy on:</b>
• <b>Mobile:</b> Tap and hold the link above, then select "Copy"
• <b>Desktop:</b> Select the link and press Ctrl+C (Cmd+C on Mac)

✅ <b>After copying:</b>
• Paste it in any chat
• Send the link
• Anyone can click to open the profile!

💡 <b>Pro tip:</b> You can also click "Open Profile" to test the link first!
"""
        
        keyboard = [
            [InlineKeyboardButton("🔗 Open Profile", url=profile_link)],
            [InlineKeyboardButton("🏠 Back to Home", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            copy_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

# Admin commands
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 <b>Broadcast Command Usage:</b>\n\n"
            "Send: <code>/broadcast Your message here</code>\n\n"
            "The message will be sent to all bot users.",
            parse_mode=ParseMode.HTML
        )
        return
    
    message_text = " ".join(context.args)
    users = get_all_users()
    
    success_count = 0
    failed_count = 0
    
    status_message = await update.message.reply_text(
        f"📡 <b>Broadcasting to {len(users)} users...</b>\n\n"
        "⏳ Please wait...",
        parse_mode=ParseMode.HTML
    )
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Broadcast Message</b>\n\n{message_text}\n\n"
                     f"━━━━━━━━━━━━━━━━\n"
                     f"👨‍💻 <b>From Developer:</b> @its_soloz",
                parse_mode=ParseMode.HTML
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send message to {user_id}: {e}")
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.05)
    
    await status_message.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"📊 <b>Results:</b>\n"
        f"• ✅ Successful: {success_count}\n"
        f"• ❌ Failed: {failed_count}\n"
        f"• 📈 Total Users: {len(users)}\n\n"
        f"📱 <b>Message sent:</b>\n<i>{message_text}</i>",
        parse_mode=ParseMode.HTML
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    users = get_all_users()
    
    stats_text = f"""
📊 <b>Bot Statistics</b>

👥 <b>Users:</b> {len(users)}
📅 <b>Last Updated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

🚀 <b>Bot Status:</b> ✅ Active
💻 <b>Developer:</b> @its_soloz

<b>Available Admin Commands:</b>
• <code>/broadcast [message]</code> - Send message to all users
• <code>/stats</code> - View bot statistics
"""
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

def main():
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_forwarded_message))
    
    # Start the bot
    print("🚀 Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()