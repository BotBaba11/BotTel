# app.py
from flask import Flask, request, jsonify
import requests
import os
import re
import datetime
import json

app = Flask(__name__)

# ==================== CONFIG ====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"
CHESS_API = "https://api.chess.com/pub/player"
IP_API = "https://ipinfojimpro.vercel.app/ipinfo"

# ==================== HELPER FUNCTIONS ====================
def send_message(chat_id, text, reply_markup=None):
    """Send message to Telegram"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    response = requests.post(url, json=payload)
    return response.json()

def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edit existing message"""
    url = f"{TELEGRAM_API_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    response = requests.post(url, json=payload)
    return response.json()

def answer_callback(callback_id, text=None):
    """Answer callback query"""
    url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
    requests.post(url, json=payload)

def get_main_keyboard():
    """Main menu keyboard"""
    return {
        "inline_keyboard": [
            [{"text": "♟️ Chess Player Info", "callback_data": "chess"}],
            [{"text": "🌍 IP Location Finder", "callback_data": "ip"}],
            [{"text": "📊 About Bot", "callback_data": "about"}],
            [{"text": "👨‍💻 Developer", "url": "https://t.me/yourusername"}]
        ]
    }

def get_back_button():
    """Back button"""
    return {
        "inline_keyboard": [
            [{"text": "🔙 Back to Menu", "callback_data": "back"}]
        ]
    }

# ==================== API FUNCTIONS ====================
def get_chess_player(username):
    """Fetch Chess.com player data"""
    try:
        url = f"{CHESS_API}/{username}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def format_chess_data(data, username):
    """Format chess player data"""
    try:
        last_online = datetime.datetime.fromtimestamp(
            data.get('last_online', 0)
        ).strftime('%Y-%m-%d %H:%M:%S')
        joined = datetime.datetime.fromtimestamp(
            data.get('joined', 0)
        ).strftime('%Y-%m-%d')
        
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

def get_ip_info(ip):
    """Fetch IP location data"""
    try:
        url = f"{IP_API}?ip={ip}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('status'):
                return result.get('data')
        return None
    except:
        return None

def format_ip_data(data, ip):
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
• Trust Score: {data.get('threat', {}).get('scores', {}).get('trust_score', 'N/A')}%
"""
        return msg
    except:
        return "❌ Error parsing IP data"

# ==================== WEBHOOK HANDLER ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive updates from Telegram"""
    data = request.get_json()
    
    if not data:
        return "No data", 400
    
    # Handle callback queries (button clicks)
    if "callback_query" in data:
        callback = data["callback_query"]
        callback_id = callback["id"]
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user_data = callback.get("data", "")
        
        # Answer callback immediately
        answer_callback(callback_id)
        
        # Handle different callback data
        if user_data == "chess":
            edit_message(
                chat_id, 
                message_id,
                "♟️ **Chess Player Info**\n\nSend me a Chess.com username.\n\nExample: `jim` or `hikaru`",
                get_back_button()
            )
            # Store user mode in memory (simple dict)
            user_sessions[chat_id] = "chess"
            
        elif user_data == "ip":
            edit_message(
                chat_id,
                message_id,
                "🌍 **IP Location Finder**\n\nSend me an IP address.\n\nExample: `161.185.160.93`",
                get_back_button()
            )
            user_sessions[chat_id] = "ip"
            
        elif user_data == "about":
            about_text = """
🤖 **About This Bot**

✅ **Features:**
• Chess.com Player Stats
• IP Location Finder
• Fast & Reliable

📌 **Commands:**
/start - Show Main Menu
/help - Get Help
"""
            edit_message(
                chat_id,
                message_id,
                about_text,
                get_back_button()
            )
            
        elif user_data == "back":
            edit_message(
                chat_id,
                message_id,
                "🏠 **Main Menu**\n\nChoose an option:",
                get_main_keyboard()
            )
            if chat_id in user_sessions:
                del user_sessions[chat_id]
        
        return "ok", 200
    
    # Handle regular messages
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user = message.get("from", {})
        first_name = user.get("first_name", "User")
        
        # Handle /start command
        if text == "/start":
            welcome_msg = f"""
👋 **Hello {first_name}!**

I'm a multi-purpose bot with following features:

♟️ **Chess Player Info** - Get any Chess.com player stats
🌍 **IP Location Finder** - Get location details of any IP

**Click buttons below to get started!**
"""
            send_message(chat_id, welcome_msg, get_main_keyboard())
            return "ok", 200
        
        # Handle /help command
        if text == "/help":
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
            send_message(chat_id, help_text)
            return "ok", 200
        
        # Handle mode-based responses
        mode = user_sessions.get(chat_id)
        
        if mode == "chess":
            data = get_chess_player(text)
            if data:
                msg = format_chess_data(data, text)
                send_message(chat_id, msg, get_back_button())
            else:
                msg = f"❌ Player `{text}` not found.\n\nPlease check the username and try again."
                send_message(chat_id, msg, get_back_button())
                
        elif mode == "ip":
            # Validate IP format
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, text):
                send_message(
                    chat_id,
                    "❌ Invalid IP format!\n\nPlease send a valid IP address.\nExample: `161.185.160.93`",
                    get_back_button()
                )
                return "ok", 200
                
            data = get_ip_info(text)
            if data:
                msg = format_ip_data(data, text)
                send_message(chat_id, msg, get_back_button())
            else:
                msg = f"❌ IP `{text}` not found or invalid."
                send_message(chat_id, msg, get_back_button())
        
        else:
            send_message(
                chat_id,
                "Please use the buttons below to select a feature.",
                get_main_keyboard()
            )
        
        return "ok", 200
    
    return "ok", 200

# ==================== USER SESSIONS ====================
# Simple in-memory storage (for demo)
# Production mein Redis ya database use karein
user_sessions = {}

# ==================== HEALTH CHECK ====================
@app.route('/')
def home():
    return "Bot is running with Flask + Webhook!"

@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "users": len(user_sessions)})

@app.route('/setwebhook')
def set_webhook():
    """Manually set webhook (optional)"""
    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://your-app.onrender.com")
    webhook_url = f"{render_url}/webhook"
    
    url = f"{TELEGRAM_API_URL}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})
    
    return jsonify(response.json())

# ==================== MAIN ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Bot running on port {port}")
    print(f"📱 Set webhook at: {TELEGRAM_API_URL}/setWebhook?url=YOUR_URL/webhook")
    app.run(host="0.0.0.0", port=port)
