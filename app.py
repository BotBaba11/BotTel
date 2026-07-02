import os
import asyncio
import aiohttp
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHESS_API = "https://api.chess.com/pub/player"
IP_API = "https://ipinfojimpro.vercel.app/ipinfo"

# ==================== MAIN MENU BUTTONS ====================
def get_main_keyboard():
    """Main menu keyboard with buttons"""
    keyboard = [
        [InlineKeyboardButton("♟️ Chess Player Info", callback_data="chess")],
        [InlineKeyboardButton("🌍 IP Location Finder", callback_data="ip")],
        [InlineKeyboardButton("📊 About Bot", callback_data="about")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/yourusername")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command - shows main menu"""
    user = update.effective_user
    welcome_msg = f"""
👋 **Hello {user.first_name}!**

I'm a multi-purpose bot with following features:

♟️ **Chess Player Info** - Get any Chess.com player stats
🌍 **IP Location Finder** - Get location details of any IP

**Click buttons below to get started!**
"""
    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ==================== BUTTON HANDLERS ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "chess":
        await query.edit_message_text(
            "♟️ **Chess Player Info**\n\nSend me a Chess.com username.\n\nExample: `jim` or `hikaru`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]),
            parse_mode="Markdown"
        )
        context.user_data['mode'] = 'chess'
        
    elif data == "ip":
        await query.edit_message_text(
            "🌍 **IP Location Finder**\n\nSend me an IP address.\n\nExample: `161.185.160.93`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]),
            parse_mode="Markdown"
        )
        context.user_data['mode'] = 'ip'
        
    elif data == "about":
        about_text = """
🤖 **About This Bot**

✅ **Features:**
• Chess.com Player Stats
• IP Location Finder
• Fast & Reliable

📌 **Commands:**
/start - Show Main Menu
/help - Get Help

👨‍💻 **Developer:** @yourusername
"""
        await query.edit_message_text(
            about_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]),
            parse_mode="Markdown"
        )
        
    elif data == "back":
        await query.edit_message_text(
            "🏠 **Main Menu**\n\nChoose an option:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        context.user_data['mode'] = None

# ==================== CHESS API HANDLER ====================
async def get_chess_player(username: str):
    """Fetch Chess.com player data"""
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{CHESS_API}/{username}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None
        except:
            return None

def format_chess_data(data: dict, username: str):
    """Format chess player data"""
    try:
        # Convert timestamps
        last_online = datetime.datetime.fromtimestamp(data.get('last_online', 0)).strftime('%Y-%m-%d %H:%M:%S')
        joined = datetime.datetime.fromtimestamp(data.get('joined', 0)).strftime('%Y-%m-%d')
        
        msg = f"""
♟️ **Chess Player: {data.get('username', username)}**

👤 **Name:** {data.get('name', 'N/A')}
🏆 **Status:** {data.get('status', 'N/A')}
⭐ **Verified:** {data.get('verified', False)}
🎮 **Streamer:** {data.get('is_streamer', False)}
📊 **League:** {data.get('league', 'N/A')}
👥 **Followers:** {data.get('followers', 0)}

📅 **Joined:** {joined}
🕐 **Last Online:** {last_online}

🔗 **Profile:** {data.get('url', 'N/A')}
"""
        return msg
    except:
        return "❌ Error parsing player data"

# ==================== IP API HANDLER ====================
async def get_ip_info(ip: str):
    """Fetch IP location data"""
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{IP_API}?ip={ip}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('status'):
                        return result.get('data')
                return None
        except:
            return None

def format_ip_data(data: dict, ip: str):
    """Format IP location data"""
    try:
        msg = f"""
🌍 **IP Location: {ip}**

📍 **Country:** {data.get('country_name', 'N/A')} {data.get('emoji_flag', '')}
🏙️ **City:** {data.get('city', 'N/A')}
🗺️ **Region:** {data.get('region', 'N/A')}
📮 **Postal:** {data.get('postal', 'N/A')}

📍 **Coordinates:**
• Latitude: {data.get('latitude', 'N/A')}
• Longitude: {data.get('longitude', 'N/A')}

🏢 **ISP:**
• Name: {data.get('company', {}).get('name', 'N/A')}
• ASN: {data.get('asn', {}).get('asn', 'N/A')}

🌐 **Time Zone:**
• Name: {data.get('time_zone', {}).get('name', 'N/A')}
• Current: {data.get('time_zone', {}).get('current_time', 'N/A')}

🛡️ **Threat Info:**
• VPN: {data.get('threat', {}).get('is_vpn', False)}
• Proxy: {data.get('threat', {}).get('is_proxy', False)}
• Trust Score: {data.get('threat', {}).get('scores', {}).get('trust_score', 'N/A')}%
"""
        return msg
    except:
        return "❌ Error parsing IP data"

# ==================== MESSAGE HANDLER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages based on mode"""
    text = update.message.text.strip()
    mode = context.user_data.get('mode')
    
    if mode == 'chess':
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        data = await get_chess_player(text)
        if data:
            msg = format_chess_data(data, text)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        else:
            msg = f"❌ Player `{text}` not found.\n\nPlease check the username and try again."
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
        
    elif mode == 'ip':
        # Validate IP format (simple check)
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, text):
            await update.message.reply_text(
                "❌ Invalid IP format!\n\nPlease send a valid IP address.\nExample: `161.185.160.93`",
                parse_mode="Markdown"
            )
            return
            
        await update.message.chat.send_action(action="typing")
        
        data = await get_ip_info(text)
        if data:
            msg = format_ip_data(data, text)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        else:
            msg = f"❌ IP `{text}` not found or invalid."
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
    
    else:
        await update.message.reply_text(
            "Please use the buttons below to select a feature.",
            reply_markup=get_main_keyboard()
        )

# ==================== HELP COMMAND ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help command"""
    help_text = """
🤖 **Help Center**

**How to use this bot:**

1️⃣ Click **"♟️ Chess Player Info"** 
   → Send any Chess.com username

2️⃣ Click **"🌍 IP Location Finder"**
   → Send any valid IP address

**Commands:**
/start - Show main menu
/help - Show this help

**Example Usernames:**
• `jim`
• `hikaru`
• `magnuscarlsen`

**Example IPs:**
• `161.185.160.93`
• `8.8.8.8`
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    print(f"Update {update} caused error {context.error}")

# ==================== MAIN ====================
def main():
    """Start the bot"""
    print("🤖 Bot starting...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start bot
    print("✅ Bot is running!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
